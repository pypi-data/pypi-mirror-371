#!/usr/bin/env python3
"""
Basic tests for NXLC (NeoAxios Language Counter)
"""

import os
import sys
import tempfile
import unittest
from pathlib import Path

# Add parent directory to path to import nxlc
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

try:
    import nxlc
except ImportError:
    # Skip tests if nxlc module can't be imported
    nxlc = None


@unittest.skipIf(nxlc is None, "nxlc module not available")
class TestNXLC(unittest.TestCase):
    """Test basic NXLC functionality"""

    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)

    def tearDown(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_imports(self):
        """Test that NXLC can be imported"""
        self.assertIsNotNone(nxlc)
        self.assertTrue(hasattr(nxlc, 'main'))
        self.assertTrue(hasattr(nxlc, 'LineCounter'))
        self.assertTrue(hasattr(nxlc, 'LanguageDefinitions'))

    def test_language_definitions(self):
        """Test LanguageDefinitions class"""
        lang_defs = nxlc.LanguageDefinitions()
        
        # Test that we have expected language extensions
        self.assertIn('Python', lang_defs.LANGUAGE_EXTENSIONS)
        self.assertIn('.py', lang_defs.LANGUAGE_EXTENSIONS['Python'])
        
        # Test that we have comment patterns
        self.assertIn('Python', lang_defs.COMMENT_PATTERNS)
        self.assertIn('#', lang_defs.COMMENT_PATTERNS['Python']['single'])

    def test_line_counter_init(self):
        """Test LineCounter initialization"""
        counter = nxlc.LineCounter()
        self.assertIsNotNone(counter.platform)
        self.assertIsNotNone(counter.language_defs)
        self.assertIsInstance(counter.file_line_counts, dict)

    def test_detect_language_basic(self):
        """Test basic language detection"""
        counter = nxlc.LineCounter()
        
        # Test Python file detection
        py_file = self.temp_path / "test.py"
        py_file.write_text("print('hello')")
        self.assertEqual(counter.detect_language(py_file), "Python")
        
        # Test JavaScript file detection
        js_file = self.temp_path / "test.js"
        js_file.write_text("console.log('hello');")
        self.assertEqual(counter.detect_language(js_file), "JavaScript")

    def test_count_lines_basic(self):
        """Test basic line counting"""
        counter = nxlc.LineCounter()
        
        # Create a test Python file
        test_file = self.temp_path / "test.py"
        test_content = '''#!/usr/bin/env python3
# This is a comment
"""
Multi-line comment
"""

def hello():
    print("Hello, World!")  # Inline comment
    return True

if __name__ == "__main__":
    hello()
'''
        test_file.write_text(test_content)
        
        total, code, comment = counter.count_lines_in_file(test_file)
        
        # Should have some lines
        self.assertGreater(total, 0)
        # Should have actual code lines (not 0 due to multiline comment bug)
        self.assertGreater(code, 0, "Code lines should be > 0 (multiline comment bug regression test)")
        self.assertGreater(comment, 0)
        
        # Total should equal code + comment + empty lines (which aren't counted separately)
        self.assertGreaterEqual(total, code + comment)

    def test_analyze_directory_basic(self):
        """Test basic directory analysis"""
        counter = nxlc.LineCounter()
        
        # Create test files
        (self.temp_path / "test.py").write_text("print('python')")
        (self.temp_path / "test.js").write_text("console.log('js');")
        (self.temp_path / "README.md").write_text("# Test Project")
        
        results = counter.analyze_directory(self.temp_path)
        
        # Check basic structure
        self.assertIn('languages', results)
        self.assertIn('total_files', results)
        self.assertIn('total_lines', results)
        
        # Should find our test files
        self.assertGreater(results['total_files'], 0)
        self.assertGreater(results['total_lines'], 0)
        
        # Should detect languages
        languages = results['languages']
        self.assertIn('Python', languages)
        self.assertIn('JavaScript', languages)
        # README.md gets detected as 'README', not 'Markdown' 
        self.assertIn('README', languages)

    def test_security_validation(self):
        """Test security validation functions"""
        # Test linguist path validation
        with self.assertRaises(ValueError):
            nxlc.validate_linguist_path("bad; rm -rf /")
            
        with self.assertRaises(ValueError):
            nxlc.validate_linguist_path("../../../etc/passwd")
            
        # Valid absolute path should not raise
        try:
            nxlc.validate_linguist_path("/usr/bin/linguist")
        except ValueError:
            self.fail("Valid absolute path should not raise ValueError")

    def test_colors_class(self):
        """Test Colors class functionality"""
        # Test enabled colors
        colors_on = nxlc.Colors(enabled=True)
        self.assertTrue(len(colors_on.HEADER) > 0)
        self.assertTrue(len(colors_on.RESET) > 0)
        
        # Test disabled colors
        colors_off = nxlc.Colors(enabled=False)
        self.assertEqual(colors_off.HEADER, '')
        self.assertEqual(colors_off.RESET, '')

    def test_platform_adapters(self):
        """Test platform adapter functionality"""
        adapter = nxlc.get_platform_adapter()
        self.assertIsInstance(adapter, nxlc.PlatformAdapter)
        
        # Test platform name
        platform_name = adapter.get_platform_name()
        self.assertIn(platform_name, ['Unix', 'Windows', 'macOS'])


class TestULCCLI(unittest.TestCase):
    """Test NXLC command-line interface"""

    def test_version_flag(self):
        """Test --version flag"""
        import subprocess
        import sys
        
        # Test by running nxlc.py directly from src directory
        script_path = Path(__file__).parent.parent / "src" / "nxlc.py"
        if not script_path.exists():
            self.skipTest("nxlc.py not found in src directory")
            
        result = subprocess.run(
            [sys.executable, str(script_path), "--version"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        self.assertEqual(result.returncode, 0)
        self.assertIn("NeoAxios Language Counter", result.stdout)

    def test_help_flag(self):
        """Test --help flag"""
        import subprocess
        import sys
        
        # Test by running nxlc.py directly from src directory
        script_path = Path(__file__).parent.parent / "src" / "nxlc.py"
        if not script_path.exists():
            self.skipTest("nxlc.py not found in src directory")
            
        result = subprocess.run(
            [sys.executable, str(script_path), "--help"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        self.assertEqual(result.returncode, 0)
        self.assertIn("NeoAxios Language Counter", result.stdout)
        self.assertIn("usage:", result.stdout)


if __name__ == "__main__":
    unittest.main()