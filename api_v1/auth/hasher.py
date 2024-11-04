import base64
from datetime import datetime
import hashlib
import hmac
import secrets

from binascii import Error as BinasciiError

from loguru import logger

from config.config import settings
from config.models.user import User
from .exeptions import InvalidAlgorithm
from .types import is_protected_type
from .utils import base36_to_int, int_to_base36


class UserPathHasher:
    """
    Класс конвертирующий из данных пользователя
    в одноразовую строку для пути в URL
    """
    __secret_key = settings.SECRET_KEY
    __key_salt = 'api_v1.auth.hasher.UserPathHasher'

    def __init__(self, user: User) -> None:
        self._user = user
        self.algorithm = 'sha256'

    def _force_bytes(self,
                     s,
                     encoding="utf-8",
                     strings_only=False,
                     errors="strict",
                     ):
        if isinstance(s, bytes):
            if encoding == "utf-8":
                return s
            else:
                return s.decode("utf-8", errors).encode(encoding, errors)
        if strings_only and is_protected_type(s):
            return s
        if isinstance(s, memoryview):
            return bytes(s)
        return str(s).encode(encoding, errors)

    def _salted_hmac(self,
                     key_salt,
                     value,
                     secret=None,
                     *,
                     algorithm="sha1",
                     ):
        """
        Return the HMAC of 'value', using a key generated from key_salt and a
        secret (which defaults to settings.SECRET_KEY). Default algorithm is SHA1,
        but any algorithm name supported by hashlib can be passed.

        A different key_salt should be passed in for every application of HMAC.
        """
        if secret is None:
            secret = settings.SECRET_KEY

        key_salt = self._force_bytes(key_salt)
        secret = self._force_bytes(secret)
        try:
            hasher = getattr(hashlib, algorithm)
        except AttributeError as e:
            raise InvalidAlgorithm(
                "%r is not an algorithm accepted by the hashlib module." % algorithm
            ) from e
        key = hasher(key_salt + secret).digest()
        return hmac.new(key, msg=self._force_bytes(value), digestmod=hasher)

    def _make_token_with_timestamp(self,
                                   user,
                                   timestamp,
                                   secret,
                                   ):
        ts_b36 = int_to_base36(timestamp)
        hash_string = self._salted_hmac(
            self.__key_salt,
            self._make_hash_value(user, timestamp),
            secret=secret,
            algorithm=self.algorithm,
        ).hexdigest()[
            ::2
        ]  # Limit to shorten the URL.
        return "%s-%s" % (ts_b36, hash_string)

    def _make_hash_value(self,
                         user: User,
                         timestamp,
                         ):
        """
        Hash the user's primary key, email (if available), and some user state
        that's sure to change after a password reset to produce a token that is
        invalidated when it's used:
        1. The password field will change upon a password reset (even if the
           same password is chosen, due to password salting).
        2. The last_login field will usually be updated very shortly after
           a password reset.
        Failing those things, settings.PASSWORD_RESET_TIMEOUT eventually
        invalidates the token.

        Running this data through salted_hmac() prevents password cracking
        attempts using the reset token, provided the secret isn't compromised.
        """
        login_timestamp = user.create_date
        return f"{user.id}{user.password}{login_timestamp}{timestamp}{user.email}"

    def _constant_time_compare(self, val1, val2):
        """Return True if the two strings are equal, False otherwise."""
        logger.info(f'_constant_time_compare \nval1 = {val1}\nval2 = {val2}')
        return secrets.compare_digest(self._force_bytes(val1), self._force_bytes(val2))

    @logger.catch(reraise=True)
    def _urlsafe_base64_encode(self, user: User):
        """
        Encode a bytestring to a base64 string for use in URLs. Strip any trailing
        equal signs.
        """
        user_id = user.id
        logger.info(f'user_id = {user_id}')
        s = self._force_bytes(user_id)
        logger.info(f's = {s}')
        return base64.urlsafe_b64encode(s).rstrip(b"\n=").decode("ascii")

    @staticmethod
    def urlsafe_base64_decode(uid):
        """
        Decode a base64 encoded string. Add back any trailing equal signs that
        might have been stripped.
        """
        s = uid.encode()
        try:
            return base64.urlsafe_b64decode(s.ljust(len(s) + len(s) % 4, b"="))
        except (LookupError, BinasciiError) as e:
            raise ValueError(e)

    def make_url_token(self):
        """
        Return a token that can be used once to do a password reset
        for the given user.
        """
        user = self._user
        uid = self._urlsafe_base64_encode(user=user)
        token = self._make_token_with_timestamp(
            user,
            self._num_seconds(self._now()),
            self.__secret_key,
        )
        return f'{uid}/{token}'

    def check_token(self, token):
        """
        Check that a password reset token is correct for a given user.
        """
        user = self._user
        if not (user and token):
            return False
        # Parse the token
        logger.info(f'check_token get user = {user}, token = {token}')
        try:
            ts_b36, _ = token.split("-")
            logger.info(f'ts_b36 = {ts_b36}')
        except ValueError:
            return False

        try:
            ts = base36_to_int(ts_b36)
            logger.info(f'ts = {ts}')
        except ValueError:
            return False

        if not self._constant_time_compare(
            self._make_token_with_timestamp(user, ts, self.__secret_key),
            token,
        ):
            return False

        # Check the timestamp is within limit.
        # if (self._num_seconds(self._now()) - ts) > settings.LIFESPAN_TOKEN:
        #     return False

        return True

    def _now(self):
        # Used for mocking in tests
        return datetime.now()

    def _num_seconds(self, dt):
        return int((dt - datetime(2001, 1, 1)).total_seconds())
