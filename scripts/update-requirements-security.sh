#!/bin/bash
# Security Update Script for Requirements
# Updates requirements.in with security fixes from requirements-fixed.txt

set -e

echo "🔒 Requirements Security Update Script"
echo "======================================"
echo ""

# Check if we're in the right directory
if [ ! -f "backend/requirements.in" ]; then
    echo "❌ Error: backend/requirements.in not found"
    echo "Please run this script from the project root directory"
    exit 1
fi

# Backup current requirements.in
echo "📦 Creating backup..."
cp backend/requirements.in backend/requirements.in.backup
echo "✅ Backup created: backend/requirements.in.backup"
echo ""

# Security updates to apply
echo "🔍 Security updates to apply:"
echo ""
echo "Package              Current    → Fixed      CVE/Issue"
echo "─────────────────────────────────────────────────────────────"
echo "python-multipart     0.0.12     → 0.0.18     CVE-2024-53981"
echo "python-jose          3.3.0      → 3.5.0      PYSEC-2024-232, PYSEC-2024-233"
echo "cryptography         43.0.3     → 46.0.5     CVE-2024-12797"
echo "aiohttp              3.11.7     → 3.13.3     Multiple CVEs"
echo "requests             2.32.3     → 2.32.4     CVE-2024-47081"
echo ""

# Ask for confirmation
read -p "Apply these security updates? (y/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Update cancelled"
    rm backend/requirements.in.backup
    exit 0
fi

echo ""
echo "📝 Updating requirements.in..."

# Update the file
cd backend

# Create a temporary file with updates
cat requirements.in | \
    sed 's/python-multipart==0.0.12/python-multipart==0.0.18  # Security: CVE-2024-53981/' | \
    sed 's/python-jose\[cryptography\]==3.3.0/python-jose[cryptography]==3.5.0  # Security: PYSEC-2024-232, PYSEC-2024-233/' | \
    sed 's/cryptography==43.0.3/cryptography==46.0.5  # Security: CVE-2024-12797/' | \
    sed 's/aiohttp==3.11.7/aiohttp==3.13.3  # Security: Multiple CVEs/' | \
    sed 's/requests==2.32.3/requests==2.32.4  # Security: CVE-2024-47081/' \
    > requirements.in.new

# Replace the file
mv requirements.in.new requirements.in

echo "✅ requirements.in updated"
echo ""

# Recompile
echo "🔨 Recompiling requirements.txt..."
if command -v pip-compile &> /dev/null; then
    pip-compile requirements.in
    echo "✅ requirements.txt recompiled"
else
    echo "⚠️  pip-compile not found. Install with: pip install pip-tools"
    echo "Then run: cd backend && pip-compile requirements.in"
fi

echo ""
echo "📋 Next steps:"
echo "1. Review the changes: git diff backend/requirements.in backend/requirements.txt"
echo "2. Test the new requirements: pip install -r backend/requirements.txt"
echo "3. Run tests: pytest backend/tests/"
echo "4. If all tests pass, delete requirements-fixed.txt"
echo "5. Commit the changes"
echo ""
echo "To restore backup: mv backend/requirements.in.backup backend/requirements.in"
echo ""
echo "✅ Security update complete!"
