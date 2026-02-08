"""
Tests for the parser factory
"""
import pytest
from app.services.parsers.factory import ParserFactory
from app.services.parsers.python_parser import PythonASTParser
from app.services.parsers.javascript_parser import JavaScriptParser


def test_get_python_parser():
    """Test getting Python parser"""
    parser = ParserFactory.get_parser('python')
    assert parser is not None
    assert isinstance(parser, PythonASTParser)


def test_get_python_parser_by_extension():
    """Test getting Python parser by file extension"""
    parser = ParserFactory.get_parser('py')
    assert parser is not None
    assert isinstance(parser, PythonASTParser)


def test_get_javascript_parser():
    """Test getting JavaScript parser"""
    parser = ParserFactory.get_parser('javascript')
    assert parser is not None
    assert isinstance(parser, JavaScriptParser)
    assert parser.language == 'javascript'


def test_get_typescript_parser():
    """Test getting TypeScript parser"""
    parser = ParserFactory.get_parser('typescript')
    assert parser is not None
    assert isinstance(parser, JavaScriptParser)
    assert parser.language == 'typescript'


def test_get_parser_by_filename_python():
    """Test getting parser by Python filename"""
    parser = ParserFactory.get_parser_by_filename('test.py')
    assert parser is not None
    assert isinstance(parser, PythonASTParser)


def test_get_parser_by_filename_javascript():
    """Test getting parser by JavaScript filename"""
    parser = ParserFactory.get_parser_by_filename('test.js')
    assert parser is not None
    assert isinstance(parser, JavaScriptParser)
    assert parser.language == 'javascript'


def test_get_parser_by_filename_typescript():
    """Test getting parser by TypeScript filename"""
    parser = ParserFactory.get_parser_by_filename('test.ts')
    assert parser is not None
    assert isinstance(parser, JavaScriptParser)
    assert parser.language == 'typescript'


def test_get_parser_by_filename_jsx():
    """Test getting parser by JSX filename"""
    parser = ParserFactory.get_parser_by_filename('component.jsx')
    assert parser is not None
    assert isinstance(parser, JavaScriptParser)


def test_get_parser_by_filename_tsx():
    """Test getting parser by TSX filename"""
    parser = ParserFactory.get_parser_by_filename('component.tsx')
    assert parser is not None
    assert isinstance(parser, JavaScriptParser)


def test_get_parser_unsupported_language():
    """Test getting parser for unsupported language"""
    parser = ParserFactory.get_parser('ruby')
    assert parser is None


def test_get_parser_by_filename_no_extension():
    """Test getting parser for filename without extension"""
    parser = ParserFactory.get_parser_by_filename('README')
    assert parser is None


def test_supported_languages():
    """Test getting list of supported languages"""
    languages = ParserFactory.supported_languages()
    assert 'python' in languages
    assert 'py' in languages
    assert 'javascript' in languages
    assert 'js' in languages
    assert 'typescript' in languages
    assert 'ts' in languages
    assert 'jsx' in languages
    assert 'tsx' in languages


def test_is_language_supported():
    """Test checking if language is supported"""
    assert ParserFactory.is_language_supported('python') is True
    assert ParserFactory.is_language_supported('javascript') is True
    assert ParserFactory.is_language_supported('typescript') is True
    assert ParserFactory.is_language_supported('ruby') is False
    assert ParserFactory.is_language_supported('go') is False


def test_case_insensitive_language():
    """Test that language matching is case-insensitive"""
    parser1 = ParserFactory.get_parser('Python')
    parser2 = ParserFactory.get_parser('PYTHON')
    parser3 = ParserFactory.get_parser('python')
    
    assert parser1 is not None
    assert parser2 is not None
    assert parser3 is not None
    assert type(parser1) == type(parser2) == type(parser3)


def test_extension_with_dot():
    """Test that extensions with leading dot are handled"""
    parser1 = ParserFactory.get_parser('.py')
    parser2 = ParserFactory.get_parser('py')
    
    assert parser1 is not None
    assert parser2 is not None
    assert type(parser1) == type(parser2)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
