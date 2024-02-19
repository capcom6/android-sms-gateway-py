import abc
import base64
import typing as t


class BaseEncryptor(abc.ABC):
    def __init__(self, passphrase: str, *, iterations: int) -> None:
        self.passphrase = passphrase
        self.iterations = iterations

    @abc.abstractmethod
    def encrypt(self, cleartext: str) -> str:
        ...

    @abc.abstractmethod
    def decrypt(self, encrypted: str) -> str:
        ...


_Encryptor: t.Optional[t.Type[BaseEncryptor]] = None


try:
    from Crypto.Cipher import AES
    from Crypto.Hash import SHA1
    from Crypto.Protocol.KDF import PBKDF2
    from Crypto.Random import get_random_bytes
    from Crypto.Util.Padding import pad, unpad

    class AESEncryptor(BaseEncryptor):
        def encrypt(self, cleartext: str) -> str:
            saltBytes = self._generate_salt()
            key = self._generate_key(saltBytes, self.iterations)

            cipher = AES.new(key, AES.MODE_CBC, iv=saltBytes)

            encrypted_bytes = cipher.encrypt(pad(cleartext.encode(), AES.block_size))

            salt = base64.b64encode(saltBytes).decode("utf-8")
            encrypted = base64.b64encode(encrypted_bytes).decode("utf-8")

            return f"$aes-256-cbc/pbkdf2-sha1$i={self.iterations}${salt}${encrypted}"

        def decrypt(self, encrypted: str) -> str:
            chunks = encrypted.split("$")

            if len(chunks) < 5:
                raise ValueError("Invalid encryption format")

            if chunks[1] != "aes-256-cbc/pbkdf2-sha1":
                raise ValueError("Unsupported algorithm")

            params = self._parse_params(chunks[2])
            if "i" not in params:
                raise ValueError("Missing iteration count")

            iterations = int(params["i"])
            salt = base64.b64decode(chunks[-2])
            encrypted_bytes = base64.b64decode(chunks[-1])

            key = self._generate_key(salt, iterations)
            cipher = AES.new(key, AES.MODE_CBC, iv=salt)

            decrypted_bytes = unpad(cipher.decrypt(encrypted_bytes), AES.block_size)

            return decrypted_bytes.decode("utf-8")

        def _generate_salt(self) -> bytes:
            return get_random_bytes(16)

        def _generate_key(self, salt: bytes, iterations: int) -> bytes:
            return PBKDF2(
                self.passphrase,
                salt,
                count=iterations,
                dkLen=32,
                hmac_hash_module=SHA1,
            )

        def _parse_params(self, params: str) -> t.Dict[str, str]:
            return {k: v for k, v in [p.split("=") for p in params.split(",")]}

    _Encryptor = AESEncryptor
except ImportError:
    ...


def Encryptor(passphrase: str, *, iterations: int = 75_000) -> BaseEncryptor:
    if _Encryptor is None:
        raise ImportError("Please install cryptodome")

    return _Encryptor(passphrase, iterations=iterations)
