"""
Unit tests for diff_parser utility
"""
import pytest
from app.utils.diff_parser import DiffParser


class TestDiffParser:
    """Test suite for DiffParser utility"""
    
    def test_parse_empty_diff(self):
        """Test parsing empty diff returns empty list"""
        result = DiffParser.parse_diff("")
        assert result == []
    
    def test_parse_simple_addition(self):
        """Test parsing diff with simple addition"""
        diff = """diff --git a/test.py b/test.py
new file mode 100644
index 0000000..1234567
--- /dev/null
+++ b/test.py
@@ -0,0 +1,3 @@
+def hello():
+    print("Hello")
+    return True
"""
        result = DiffParser.parse_diff(diff)
        
        assert len(result) == 1
        assert result[0]['new_path'] == 'test.py'
        assert result[0]['status'] == 'added'
        assert result[0]['additions'] == 3
        assert result[0]['deletions'] == 0
    
    def test_parse_simple_deletion(self):
        """Test parsing diff with simple deletion"""
        diff = """diff --git a/old.py b/old.py
deleted file mode 100644
index 1234567..0000000
--- a/old.py
+++ /dev/null
@@ -1,2 +0,0 @@
-def old_function():
-    pass
"""
        result = DiffParser.parse_diff(diff)
        
        assert len(result) == 1
        assert result[0]['status'] == 'deleted'
        assert result[0]['deletions'] == 2
        assert result[0]['additions'] == 0
    
    def test_parse_modification(self):
        """Test parsing diff with modifications"""
        diff = """diff --git a/file.py b/file.py
index 1234567..abcdefg 100644
--- a/file.py
+++ b/file.py
@@ -1,5 +1,6 @@
 def function():
-    old_line = 1
+    new_line = 1
+    another_line = 2
     unchanged = 3
     return True
"""
        result = DiffParser.parse_diff(diff)
        
        assert len(result) == 1
        assert result[0]['status'] == 'modified'
        assert result[0]['additions'] == 2
        assert result[0]['deletions'] == 1
    
    def test_parse_multiple_files(self):
        """Test parsing diff with multiple files"""
        diff = """diff --git a/file1.py b/file1.py
index 1234567..abcdefg 100644
--- a/file1.py
+++ b/file1.py
@@ -1,2 +1,3 @@
 line1
+line2
 line3
diff --git a/file2.py b/file2.py
new file mode 100644
index 0000000..1234567
--- /dev/null
+++ b/file2.py
@@ -0,0 +1,1 @@
+new file content
"""
        result = DiffParser.parse_diff(diff)
        
        assert len(result) == 2
        assert result[0]['new_path'] == 'file1.py'
        assert result[1]['new_path'] == 'file2.py'
        assert result[1]['status'] == 'added'
    
    def test_get_changed_lines(self):
        """Test extracting changed line numbers"""
        diff = """diff --git a/test.py b/test.py
index 1234567..abcdefg 100644
--- a/test.py
+++ b/test.py
@@ -1,3 +1,4 @@
 line1
+line2
 line3
+line4
"""
        result = DiffParser.get_changed_lines(diff)
        
        assert 'test.py' in result
        assert 2 in result['test.py']
        assert 4 in result['test.py']
    
    def test_calculate_change_stats(self):
        """Test calculating change statistics"""
        diff = """diff --git a/file1.py b/file1.py
index 1234567..abcdefg 100644
--- a/file1.py
+++ b/file1.py
@@ -1,2 +1,3 @@
 line1
+line2
 line3
diff --git a/file2.py b/file2.py
index 1234567..abcdefg 100644
--- a/file2.py
+++ b/file2.py
@@ -1,3 +1,2 @@
 line1
-line2
 line3
"""
        stats = DiffParser.calculate_change_stats(diff)
        
        assert stats['files_changed'] == 2
        assert stats['additions'] == 1
        assert stats['deletions'] == 1
        assert stats['total_changes'] == 2
    
    def test_filter_changes_by_extension(self):
        """Test filtering changes by file extension"""
        diff = """diff --git a/file1.py b/file1.py
index 1234567..abcdefg 100644
--- a/file1.py
+++ b/file1.py
@@ -1,1 +1,2 @@
 line1
+line2
diff --git a/file2.js b/file2.js
index 1234567..abcdefg 100644
--- a/file2.js
+++ b/file2.js
@@ -1,1 +1,2 @@
 line1
+line2
diff --git a/file3.md b/file3.md
index 1234567..abcdefg 100644
--- a/file3.md
+++ b/file3.md
@@ -1,1 +1,2 @@
 line1
+line2
"""
        result = DiffParser.filter_changes_by_extension(diff, ['.py', '.js'])
        
        assert len(result) == 2
        assert result[0]['new_path'] == 'file1.py'
        assert result[1]['new_path'] == 'file2.js'
    
    def test_extract_added_code(self):
        """Test extracting only added code lines"""
        diff = """diff --git a/test.py b/test.py
index 1234567..abcdefg 100644
--- a/test.py
+++ b/test.py
@@ -1,3 +1,5 @@
 line1
+added_line1
 line2
+added_line2
 line3
"""
        result = DiffParser.extract_added_code(diff)
        
        assert 'test.py' in result
        assert len(result['test.py']) == 2
        assert 'added_line1' in result['test.py']
        assert 'added_line2' in result['test.py']
    
    def test_parse_rename(self):
        """Test parsing renamed file"""
        diff = """diff --git a/old_name.py b/new_name.py
similarity index 100%
rename from old_name.py
rename to new_name.py
"""
        result = DiffParser.parse_diff(diff)
        
        assert len(result) == 1
        assert result[0]['status'] == 'renamed'
        assert result[0]['old_path'] == 'old_name.py'
        assert result[0]['new_path'] == 'new_name.py'
    
    def test_parse_hunk_with_context(self):
        """Test parsing hunk with context information"""
        diff = """diff --git a/test.py b/test.py
index 1234567..abcdefg 100644
--- a/test.py
+++ b/test.py
@@ -10,5 +10,6 @@ def my_function():
 line1
 line2
+added_line
 line3
 line4
"""
        result = DiffParser.parse_diff(diff)
        
        assert len(result) == 1
        assert len(result[0]['hunks']) == 1
        hunk = result[0]['hunks'][0]
        assert hunk['old_start'] == 10
        assert hunk['new_start'] == 10
        assert hunk['context'] == 'def my_function():'
