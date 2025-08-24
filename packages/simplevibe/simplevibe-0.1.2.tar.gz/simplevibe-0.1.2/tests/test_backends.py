"""
Tests for the different backend options in simpleVibe.
"""
import unittest
import sys
import os

class TestBackendDetection(unittest.TestCase):
    
    def test_backend_detection(self):
        """Test that backend detection function exists and returns a valid value."""
        from simplevibe import get_backend_type
        
        backend = get_backend_type()
        self.assertIn(backend, ['local', 'remote'], 
                     f"Backend type '{backend}' should be either 'local' or 'remote'")

    def test_client_creation_no_error(self):
        """Test that client creation doesn't raise exceptions."""
        try:
            from simplevibe import create_client
            
            # This shouldn't raise an exception, but we don't test functionality
            # as it depends on what packages are installed
            client = create_client()
            self.assertTrue(True, "Client creation should complete without exceptions")
        except Exception as e:
            self.fail(f"Client creation raised exception: {e}")
            
    def test_backend_set_function(self):
        """Test that the backend can be set via the set_backend function."""
        try:
            # Import the function
            from simplevibe import set_backend, create_client
            
            # Set backend to remote
            set_backend('remote')
            
            # Create client should respect the setting
            client = create_client()
            
            # The test passes if we don't get an exception
            self.assertTrue(True, "Setting backend to remote and creating client succeeded")
            
        except Exception as e:
            self.fail(f"Setting backend raised exception: {e}")


if __name__ == '__main__':
    unittest.main()
