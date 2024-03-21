import unittest
from hex_viewer.hex_viewer import HexViewer

class TestHexViewer(unittest.TestCase):
    def setUp(self):
        self.viewer = HexViewer('sample.hex')

    def test_read_hex_file(self):
        # read file as binary data and return the first 10 bytes as integers, they should be equal to the first 10 bytes of the file in integer format
        expected_bytes = [195, 187, 109, 195, 132, 86, 195, 162, 119, 73] # Replace with the actual expected first 10 byte values
        actual_bytes = self.viewer.decode_hex()[:10]
        self.assertEqual(actual_bytes, expected_bytes)

if __name__ == "__main__":
    #add the test cases to the suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestHexViewer)
    #run the suite
    unittest.TextTestRunner(verbosity=2).run(suite)
    
