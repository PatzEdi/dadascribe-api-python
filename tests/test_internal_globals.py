
import unittest
from dadascribe.internal_globals import ENV_API_NAME

# Mostly just checking that when we modify these, we
# really want to modify them.

class TestInternalGlobals(unittest.TestCase):
    def test_env_api_name(self):
        self.assertEqual(ENV_API_NAME, "DADASCRIBE_API_KEY")


if __name__ == "__main__":
    unittest.main()
