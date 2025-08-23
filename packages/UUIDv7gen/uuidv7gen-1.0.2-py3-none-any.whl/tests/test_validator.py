import unittest
from uuid7 import UUIDv7, is_valid_uuid7

class TestUUIDv7Validator(unittest.TestCase):
    def test_valid_uuid7(self):
        uuid = str(UUIDv7())
        self.assertTrue(is_valid_uuid7(uuid))

    def test_invalid_format(self):
        self.assertFalse(is_valid_uuid7("not-a-uuid"))
        self.assertFalse(is_valid_uuid7("12345678-1234-1234-1234-1234567890ab"))  # wrong version

    def test_wrong_version(self):
        # Version is not 7
        self.assertFalse(is_valid_uuid7("12345678-1234-4234-8234-1234567890ab"))

    def test_wrong_variant(self):
        # Variant is not 8, 9, a, or b
        self.assertFalse(is_valid_uuid7("12345678-1234-7234-6234-1234567890ab"))

if __name__ == "__main__":
    unittest.main()
