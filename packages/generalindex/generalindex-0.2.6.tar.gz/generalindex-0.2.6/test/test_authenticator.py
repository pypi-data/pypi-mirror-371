import unittest

from generalindex.Authenticator import Authenticator


class ApiTestCase(unittest.TestCase):

    def test_given_basic_token_when_get_token_then_returns_proper(self):
        auth = Authenticator()
        auth.token = "token"

        self.assertTrue(auth.get_token() is not None)
        self.assertTrue(auth.get_token().get("Authorization") == "Basic token")

    def test_given_prefixed_basic_token_when_get_token_then_returns_proper(self):
        auth = Authenticator()
        auth.token = "basic token"

        self.assertTrue(auth.get_token() is not None)
        self.assertTrue(auth.get_token().get("Authorization") == "basic token")

    def test_given_prefixed_bearer_token_when_get_token_then_returns_proper(self):
        auth = Authenticator()
        auth.token = "bearer token"

        self.assertTrue(auth.get_token() is not None)
        self.assertTrue(auth.get_token().get("Authorization") == "bearer token")

    def test_given_bearer_token_when_get_token_then_returns_proper(self):
        auth = Authenticator()
        token = "dada4rwfsrfe5fscscja9238ds3ea9isfwkh1i7y387y4o87egfho9y03y74fy7yao87doq8373tgeo87gwo8f7tz6xfai6eti6qtdi6atxo6ateq6te"
        auth.token = token

        self.assertTrue(auth.get_token() is not None)
        self.assertTrue(auth.get_token().get("Authorization") == "Bearer " + token)

    def test_given_prefixed_apikey_token_when_get_token_then_returns_proper(self):
        auth = Authenticator()
        auth.token = "apikey token"

        self.assertTrue(auth.get_token() is not None)
        self.assertTrue(auth.get_token().get("Authorization") == "apikey token")

    def test_given_apikey_token_when_get_token_then_returns_proper(self):
        auth = Authenticator()
        auth.token = "NG_123_dcsdc"

        self.assertTrue(auth.get_token() is not None)
        self.assertTrue(auth.get_token().get("Authorization") == "ApiKey NG_123_dcsdc")
