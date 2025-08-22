import os
from collections.abc import Iterable, Mapping
from typing import Any, TextIO
from warnings import warn

from cryptography.fernet import Fernet

from .ciphers import Base64, Cipher, Identity, KeyFile, Keys
from .exceptions import ConfigError
from .policy import PolicyCallable, safe_open
from .types import StrPath


def read_entries(fileobj: TextIO) -> dict[str, str]:
    """
    Reads environment variable assignments from a file-like object. Only lines that
    contain an equal sign (=) and do not start with # (comments) are considered. Any
    leading/trailing quotes around the value portion of the assignment are stripped.
    """
    entries: dict[str, str] = {}
    for line in fileobj.readlines():
        line = line.strip()
        if "=" in line and not line.startswith("#"):
            key, value = line.split("=", 1)
            entries[key.strip()] = value.strip().strip("\"'")
    return entries


class BaseSource:
    """
    Minimal interface for implementing a configuration source.
    """

    def __str__(self):
        return self.__class__.__name__

    def __getitem__(self, key: str) -> str:
        raise NotImplementedError()

    def encrypt(self, value: str) -> str:
        raise NotImplementedError()

    def decrypt(self, value: str, ttl: int | None = None) -> str:
        raise NotImplementedError()


class Source(BaseSource):
    default_cipher: type[Cipher] = Base64

    def __init__(
        self,
        environ: Mapping[str, str] | None = None,
        keys: Cipher | StrPath | Iterable[str | bytes | Fernet] | None = None,
        key_file: StrPath | None = None,
    ):
        self._environ = environ or {}
        if key_file is not None:
            warn(
                "The `key_file` argument is deprecated; use `keys` instead.",
                DeprecationWarning,
                stacklevel=3,
            )
            self._cipher = KeyFile(key_file)
        elif keys is None:
            self._cipher = self.default_cipher()
        elif isinstance(keys, Cipher):
            self._cipher = keys
        elif isinstance(keys, (str, os.PathLike)):
            self._cipher = KeyFile(keys)
        elif isinstance(keys, Iterable):
            self._cipher = Keys(keys)
        else:
            raise ConfigError("Unsupported `keys` type.")

    def __getitem__(self, key: str) -> str:
        return self._environ[key]

    def encrypt(self, value: str) -> str:
        return self._cipher.encrypt(value)

    def decrypt(self, value: str, ttl: int | None = None) -> str:
        return self._cipher.decrypt(value, ttl=ttl)


class HostEnv(Source):
    """
    A configuration source that reads from `os.environ`.
    """

    def __init__(self, **kwargs: Any):
        super().__init__(environ=os.environ, **kwargs)


class EnvFile(Source):
    """
    A configuration source that reads from the specified file.
    """

    def __init__(
        self,
        env_file: StrPath,
        policy: PolicyCallable | None = None,
        **kwargs: Any,
    ):
        super().__init__(**kwargs)
        self._env_file = env_file
        self._policy = policy
        self._items = None

    def __str__(self):
        return "{}({})".format(self.__class__.__name__, self._env_file)

    def __getitem__(self, key: str) -> str:
        if self._items is None:
            try:
                with safe_open(self._env_file, policy=self._policy) as fileobj:
                    self._items = read_entries(fileobj)
            except OSError:
                raise KeyError(key)
        return self._items[key]


class EnvDir(Source):
    """
    A configuration source that reads from the specified directory, where each key is
    a separate file inside that directory.
    """

    def __init__(
        self,
        env_dir: StrPath,
        policy: PolicyCallable | None = None,
        **kwargs: Any,
    ):
        super().__init__(**kwargs)
        self._env_dir = env_dir
        self._policy = policy

    def __str__(self):
        return "{}({})".format(self.__class__.__name__, self._env_dir)

    def __getitem__(self, key: str) -> str:
        entry_path = os.path.join(self._env_dir, key)
        try:
            with safe_open(entry_path, policy=self._policy) as fileobj:
                return fileobj.read().strip()
        except OSError:
            raise KeyError(key)


class SecretsDir(EnvDir):
    """
    An EnvDir that always expects plaintext entries. For use with filesystem-mounted
    Kubernetes secrets.
    """

    default_cipher = Identity
