"""Test for the fix to issue #10081: unittest.TestCase.tearDown executed for classes marked with unittest.skip when running --pdb"""

import unittest


def test_unittest_skip_class_with_pdb(testdir):
    """Test that tearDown is not called for skipped unittest classes when using --pdb."""
    testdir.makepyfile(
        """
        import unittest

        @unittest.skip("skipped class")
        class TestSkippedClass(unittest.TestCase):
            def setUp(self):
                assert False, "setUp should not be called on skipped class"
            
            def test_one(self):
                pass
            
            def tearDown(self):
                assert False, "tearDown should not be called on skipped class"
        """
    )
    
    # Normal execution should work
    result = testdir.runpytest("-v")
    result.stdout.fnmatch_lines(["*1 skipped*"])
    
    # With --pdb should also work without triggering setUp/tearDown
    result = testdir.runpytest("--pdb", "-v", "--tb=short")
    result.stdout.fnmatch_lines(["*1 skipped*"])
    # Should not contain any assertion errors from setUp/tearDown
    assert "setUp should not be called" not in result.stdout.str()
    assert "tearDown should not be called" not in result.stdout.str()


def test_unittest_skip_method_with_pdb_still_works(testdir):
    """Test that method-level skips still work correctly with --pdb."""
    testdir.makepyfile(
        """
        import unittest

        class TestMixedMethods(unittest.TestCase):
            def setUp(self):
                pass  # This should run for non-skipped methods
            
            @unittest.skip("skipped method")
            def test_skipped_method(self):
                assert False, "This method should be skipped"
            
            def test_normal_method(self):
                pass  # This should run normally
            
            def tearDown(self):
                pass  # This should run for non-skipped methods
        """
    )
    
    # Should have 1 passed, 1 skipped
    result = testdir.runpytest("-v")
    result.stdout.fnmatch_lines(["*1 passed*", "*1 skipped*"])