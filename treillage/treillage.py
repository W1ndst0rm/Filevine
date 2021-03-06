from .credential import Credential
from .connection_manager import ConnectionManager
from enum import Enum
from typing import Union


class BaseURL(Enum):
    UNITED_STATES = "https://api.filevine.io"
    CANADA = "https://api.filevine.ca"


class Treillage:
    def __init__(self,
                 credentials_file: str,
                 base_url: Union[str, BaseURL] = BaseURL.UNITED_STATES.value,
                 # Number of parallel connections to each host:port endpoint
                 max_connections: int = None,
                 # Number of tokens added per second to the rate limit pool
                 rate_limit_token_regen_rate: int = None,
                 # Max number of tokens in the rate limit pool
                 rate_limit_max_tokens: int = None):
        self.__credential = Credential.get_credentials(credentials_file)
        if isinstance(base_url, BaseURL):
            self.__base_url = base_url.value
        elif isinstance(base_url, str):
            self.__base_url = base_url
        self.__max_connections = max_connections
        self.__rate_limit_token_regen_rate = rate_limit_token_regen_rate
        self.__rate_limit_max_tokens = rate_limit_max_tokens
        self.__conn = None

    @property
    def conn(self) -> ConnectionManager:
        return self.__conn

    async def __async_init(self):
        self.__conn = await ConnectionManager.create(
            self.__base_url,
            self.__credential,
            self.__max_connections,
            self.__rate_limit_max_tokens,
            self.__rate_limit_token_regen_rate
        )

    @classmethod
    async def create(
            cls,
            credentials_file: str,
            base_url: Union[str, BaseURL] = BaseURL.UNITED_STATES.value,
            max_connections: int = None,
            rate_limit_token_regen_rate: int = None,
            rate_limit_max_tokens: int = None
    ):
        self = Treillage(credentials_file,
                         base_url,
                         max_connections,
                         rate_limit_token_regen_rate,
                         rate_limit_max_tokens)
        await self.__async_init()
        return self

    async def close(self):
        await self.__conn.close()

    async def __aenter__(self):
        await self.__async_init()
        return self

    async def __aexit__(self, exception_type, exception_value, traceback):
        await self.close()
