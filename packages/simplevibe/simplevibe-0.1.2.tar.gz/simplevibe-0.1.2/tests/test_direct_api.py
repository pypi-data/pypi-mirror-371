"""
Tests for direct API access in simpleVibe.
"""
import unittest
from unittest.mock import patch, MagicMock


class TestDirectApi(unittest.TestCase):
    
    @patch('requests.post')
    def test_direct_llama3_access(self, mock_post):
        """Test that llama3 can be imported and called directly."""
        # Set up mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'result': 'Test result',
            'eta': 0.5,
            'input_token_length': 10,
            'output_token_length': 5
        }
        mock_post.return_value = mock_response
        
        # Import llama3 directly
        from simplevibe import llama3
        
        # Call the function
        result = llama3(
            messages=[{"role": "user", "content": "Hello"}],
            temperature=0.7,
            max_new_tokens=10
        )
        
        # Check the result
        self.assertEqual(result['result'], 'Test result')
        self.assertEqual(result['output'], 'Test result')  # Should also have an output field
        
        # Verify the API was called with correct parameters
        mock_post.assert_called_once()
        
    @patch('requests.post')
    def test_error_handling(self, mock_post):
        """Test that llama3 handles errors properly."""
        # Set up mock response for error
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.text = "Bad request"
        mock_post.return_value = mock_response
        
        # Import llama3 directly
        from simplevibe import llama3
        
        # Call the function
        result = llama3(messages=[{"role": "user", "content": "Hello"}])
        
        # Check the result contains error information
        self.assertIn('error', result)
        self.assertIn('output', result)  # Should have an output field for compatibility
        

if __name__ == '__main__':
    unittest.main()
