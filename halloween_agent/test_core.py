import unittest
import base64
from core import summarize_image, encode_image, decode_image, ImageProcessingError
import cv2
import numpy as np
import string

class TestCore(unittest.TestCase):
    def setUp(self):
        # Load test image
        self.test_image_path = "/home/garlan/git/agents/agent_super_repo/halloween_agent/readme_imgs/replicate-prediction-mg97m9w7qsrm40cjrngtpa3a4w.png"
        with open(self.test_image_path, "rb") as image_file:
            self.encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
            # Add base64 prefix if not present
            if not self.encoded_string.startswith('data:image'):
                self.encoded_string = f'data:image/jpeg;base64,{self.encoded_string}'
        
        # Also load as numpy array for encode/decode tests
        self.test_image_np = cv2.imread(self.test_image_path)

    def test_encode_decode_image(self):
        # Test encoding
        encoded = encode_image(self.test_image_np)
        self.assertIsInstance(encoded, str)
        self.assertTrue(len(encoded) > 0)

        # Test decoding
        decoded = decode_image(encoded)
        self.assertIsInstance(decoded, np.ndarray)
        self.assertEqual(decoded.shape, self.test_image_np.shape)

        # Test error cases
        with self.assertRaises(ImageProcessingError):
            encode_image(None)
        with self.assertRaises(ImageProcessingError):
            decode_image("")

    def test_summarize_image(self):
        # Test with valid image
        # Print the encoded string to make sure it exists and has correct format
        print("\nEncoded string prefix:")
        print(self.encoded_string[:50] + "...")  # Print first 50 chars
        summary = summarize_image(self.encoded_string)
        
        # Print the LLM response
        print("\nLLM Summary Response:")
        print("-" * 50)
        print(summary)
        print("-" * 50)
        
        # Basic checks
        self.assertIsInstance(summary, str)
        self.assertTrue(len(summary) > 0)
        
        # Check for reasonable English text
        words = summary.split()
        self.assertGreaterEqual(len(words), 5, f"Summary should contain at least 5 words, got {len(words)}: '{summary}'")
        
        # Check for proper text formatting
        self.assertTrue(' ' in summary, f"Summary should contain spaces between words: '{summary}'")
        
        # Check that the text is printable ASCII (English characters)
        self.assertTrue(all(c in string.printable for c in summary), 
                       f"Summary contains non-printable or non-ASCII characters: '{summary}'")

        # Test error case
        with self.assertRaises(Exception):  # Could be LLMProcessingError
            summarize_image("")

if __name__ == '__main__':
    unittest.main()
