"""
Tests for encrypted database types.

Validates Requirement 8.4: Encrypt all sensitive data at rest using AES-256 encryption
"""
import pytest
from sqlalchemy import Column, String, create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from app.database.encrypted_types import EncryptedString, EncryptedText
from app.services.encryption_service import EncryptionService
import base64

Base = declarative_base()


class EncryptedTestModel(Base):
    """Test model with encrypted fields."""
    __tablename__ = "test_encrypted"
    
    id = Column(String, primary_key=True)
    encrypted_field = Column(EncryptedString(255))
    encrypted_text = Column(EncryptedText)
    normal_field = Column(String(255))


@pytest.fixture
def setup_encryption_key(monkeypatch):
    """Set up encryption key for tests."""
    key = EncryptionService.generate_key()
    monkeypatch.setenv("ENCRYPTION_KEY", key)
    monkeypatch.delenv("AWS_KMS_KEY_ID", raising=False)
    
    # Reset global encryption service
    import app.services.encryption_service as enc_module
    enc_module._encryption_service = None
    
    return key


@pytest.fixture
def db_session(setup_encryption_key):
    """Create in-memory database session for testing."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    yield session
    
    session.close()


class TestEncryptedString:
    """Test EncryptedString database type."""
    
    def test_encrypt_on_write(self, db_session):
        """Test that data is encrypted when written to database."""
        plaintext = "sensitive data"
        
        # Create record
        record = EncryptedTestModel(
            id="test1",
            encrypted_field=plaintext,
            normal_field="normal data"
        )
        db_session.add(record)
        db_session.commit()
        
        # Query raw database to verify encryption
        result = db_session.execute(
            text("SELECT encrypted_field, normal_field FROM test_encrypted WHERE id = 'test1'")
        ).fetchone()
        
        encrypted_value = result[0]
        normal_value = result[1]
        
        # Encrypted field should not be plaintext
        assert encrypted_value != plaintext
        
        # Normal field should be plaintext
        assert normal_value == "normal data"
        
        # Encrypted value should be base64
        try:
            base64.b64decode(encrypted_value)
        except Exception:
            pytest.fail("Encrypted value is not valid base64")
    
    def test_decrypt_on_read(self, db_session):
        """Test that data is decrypted when read from database."""
        plaintext = "sensitive data"
        
        # Create record
        record = EncryptedTestModel(
            id="test2",
            encrypted_field=plaintext,
        )
        db_session.add(record)
        db_session.commit()
        
        # Read record
        retrieved = db_session.query(EncryptedTestModel).filter_by(id="test2").first()
        
        # Should be decrypted automatically
        assert retrieved.encrypted_field == plaintext
    
    def test_encrypt_none_value(self, db_session):
        """Test that None values are preserved."""
        record = EncryptedTestModel(
            id="test3",
            encrypted_field=None,
        )
        db_session.add(record)
        db_session.commit()
        
        # Read record
        retrieved = db_session.query(EncryptedTestModel).filter_by(id="test3").first()
        
        assert retrieved.encrypted_field is None
    
    def test_encrypt_empty_string(self, db_session):
        """Test that empty strings are encrypted."""
        record = EncryptedTestModel(
            id="test4",
            encrypted_field="",
        )
        db_session.add(record)
        db_session.commit()
        
        # Read record
        retrieved = db_session.query(EncryptedTestModel).filter_by(id="test4").first()
        
        assert retrieved.encrypted_field == ""
    
    def test_encrypt_unicode(self, db_session):
        """Test that unicode strings are encrypted correctly."""
        plaintext = "sensitive data with émojis 🔐"
        
        record = EncryptedTestModel(
            id="test5",
            encrypted_field=plaintext,
        )
        db_session.add(record)
        db_session.commit()
        
        # Read record
        retrieved = db_session.query(EncryptedTestModel).filter_by(id="test5").first()
        
        assert retrieved.encrypted_field == plaintext
    
    def test_update_encrypted_field(self, db_session):
        """Test updating encrypted field."""
        # Create record
        record = EncryptedTestModel(
            id="test6",
            encrypted_field="original value",
        )
        db_session.add(record)
        db_session.commit()
        
        # Update record
        record.encrypted_field = "updated value"
        db_session.commit()
        
        # Read record
        retrieved = db_session.query(EncryptedTestModel).filter_by(id="test6").first()
        
        assert retrieved.encrypted_field == "updated value"


class TestEncryptedText:
    """Test EncryptedText database type."""
    
    def test_encrypt_long_text(self, db_session):
        """Test encrypting long text."""
        plaintext = "A" * 10000  # 10KB of text
        
        record = EncryptedTestModel(
            id="test7",
            encrypted_text=plaintext,
        )
        db_session.add(record)
        db_session.commit()
        
        # Read record
        retrieved = db_session.query(EncryptedTestModel).filter_by(id="test7").first()
        
        assert retrieved.encrypted_text == plaintext
    
    def test_encrypt_multiline_text(self, db_session):
        """Test encrypting multiline text."""
        plaintext = "Line 1\nLine 2\nLine 3\n"
        
        record = EncryptedTestModel(
            id="test8",
            encrypted_text=plaintext,
        )
        db_session.add(record)
        db_session.commit()
        
        # Read record
        retrieved = db_session.query(EncryptedTestModel).filter_by(id="test8").first()
        
        assert retrieved.encrypted_text == plaintext


class TestEncryptedTypeSecurity:
    """Security-focused tests for encrypted types."""
    
    def test_different_records_different_ciphertext(self, db_session):
        """Test that same plaintext in different records produces different ciphertext."""
        plaintext = "same sensitive data"
        
        # Create two records with same plaintext
        record1 = EncryptedTestModel(id="test9", encrypted_field=plaintext)
        record2 = EncryptedTestModel(id="test10", encrypted_field=plaintext)
        
        db_session.add(record1)
        db_session.add(record2)
        db_session.commit()
        
        # Query raw database
        result1 = db_session.execute(
            text("SELECT encrypted_field FROM test_encrypted WHERE id = 'test9'")
        ).fetchone()
        result2 = db_session.execute(
            text("SELECT encrypted_field FROM test_encrypted WHERE id = 'test10'")
        ).fetchone()
        
        # Ciphertext should be different (due to random nonce)
        assert result1[0] != result2[0]
        
        # But both should decrypt to same plaintext
        retrieved1 = db_session.query(EncryptedTestModel).filter_by(id="test9").first()
        retrieved2 = db_session.query(EncryptedTestModel).filter_by(id="test10").first()
        
        assert retrieved1.encrypted_field == plaintext
        assert retrieved2.encrypted_field == plaintext
    
    def test_plaintext_not_in_ciphertext(self, db_session):
        """Test that plaintext is not visible in ciphertext."""
        plaintext = "my secret password"
        
        record = EncryptedTestModel(id="test11", encrypted_field=plaintext)
        db_session.add(record)
        db_session.commit()
        
        # Query raw database
        result = db_session.execute(
            text("SELECT encrypted_field FROM test_encrypted WHERE id = 'test11'")
        ).fetchone()
        
        encrypted_value = result[0]
        
        # Plaintext should not be in encrypted value
        assert plaintext not in encrypted_value
        assert plaintext.lower() not in encrypted_value.lower()
    
    def test_decryption_failure_returns_none(self, db_session, monkeypatch):
        """Test that decryption failure returns None (graceful degradation)."""
        # Create record with one key
        plaintext = "sensitive data"
        record = EncryptedTestModel(id="test12", encrypted_field=plaintext)
        db_session.add(record)
        db_session.commit()
        
        # Change encryption key
        new_key = EncryptionService.generate_key()
        monkeypatch.setenv("ENCRYPTION_KEY", new_key)
        
        # Reset global encryption service
        import app.services.encryption_service as enc_module
        enc_module._encryption_service = None
        
        # Try to read record with wrong key
        retrieved = db_session.query(EncryptedTestModel).filter_by(id="test12").first()
        
        # Should return None instead of raising exception
        assert retrieved.encrypted_field is None


class TestEncryptedTypePerformance:
    """Performance tests for encrypted types."""
    
    def test_bulk_insert_performance(self, db_session):
        """Test performance of bulk inserts with encryption."""
        import time
        
        # Insert 100 records
        start = time.time()
        
        for i in range(100):
            record = EncryptedTestModel(
                id=f"perf{i}",
                encrypted_field=f"sensitive data {i}",
            )
            db_session.add(record)
        
        db_session.commit()
        
        elapsed = time.time() - start
        
        # Should complete in reasonable time (< 5 seconds for 100 records)
        assert elapsed < 5.0
    
    def test_bulk_read_performance(self, db_session):
        """Test performance of bulk reads with decryption."""
        import time
        
        # Insert 100 records
        for i in range(100):
            record = EncryptedTestModel(
                id=f"read{i}",
                encrypted_field=f"sensitive data {i}",
            )
            db_session.add(record)
        db_session.commit()
        
        # Read all records
        start = time.time()
        
        records = db_session.query(EncryptedTestModel).filter(
            EncryptedTestModel.id.like("read%")
        ).all()
        
        # Access encrypted fields to trigger decryption
        for record in records:
            _ = record.encrypted_field
        
        elapsed = time.time() - start
        
        # Should complete in reasonable time (< 5 seconds for 100 records)
        assert elapsed < 5.0
        assert len(records) == 100
