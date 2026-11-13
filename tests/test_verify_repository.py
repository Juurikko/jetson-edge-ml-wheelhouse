import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from tools import verify_repository


class RedactionTests(unittest.TestCase):
    def test_match_is_reported_without_exposing_its_value(self):
        fixtures = (
            ("github_pat", "github_" + "pat_fake_for_this_test"),
            ("private_linux_home", "/home/" + "tuomas"),
            ("private_hostname", "i5" + "radeon"),
            ("private_key", "-----BEGIN " + "PRIVATE KEY-----"),
        )
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            sample = root / "sample.txt"
            with patch.object(verify_repository, "ROOT", root):
                for category, value in fixtures:
                    with self.subTest(category=category):
                        sample.write_text(f"sample: {value}\n", encoding="utf-8")
                        with self.assertRaises(verify_repository.VerifyError) as raised:
                            verify_repository.verify_redaction([sample])
                        message = str(raised.exception)
                        self.assertIn("sample.txt", message)
                        self.assertIn(category, message)
                        self.assertNotIn(value, message)


if __name__ == "__main__":
    unittest.main()
