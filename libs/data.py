#strings
from enum import Enum
from typing import TypeVar, Generic
from attr import dataclass
from dotenv import load_dotenv
import os

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
RELAY_TOKEN = os.getenv("RELAY_TOKEN")
SERVER_ID = "1077518712158035990"
MID_JOURNEY_ID = "936929561302675456"


@dataclass
class Settings:
    bot_token: str
    relay_token: str
    server_id: str
    midjourney_id: str

SETTINGS = Settings(BOT_TOKEN, RELAY_TOKEN, SERVER_ID, MID_JOURNEY_ID)

class MjChannelState(str, Enum):
    AWAITING_GEN = 'AWAITING_GEN'
    AWAITING_TARGET_SET = 'AWAITING_TARGET_SET'
    AWAITING_UPSCALE = 'AWAITING_UPSCALE'
    DONE = 'DONE'
    ERROR = 'ERROR'


@dataclass
class MjChannel:
    request_id: str
    state: str


K = TypeVar('K')
V = TypeVar('V')
class Storage(Generic[K, V]):
    local_storage: dict[K, V] = {}

    def __init__(self):
        pass

    def has(self, key: K) -> bool:
        return key in self.local_storage

    def set(self, key: K, value: V) -> V:
        self.local_storage[key] = value
        return value

    def get(self, key: K) -> V:
        if not self.has(key):
            raise Exception(f"{key} not found on storage")
        return self.local_storage[key]

    def __str__(self) -> str:
        value = ""
        for k, v in self.local_storage.items():
            value = value + f'[{k}]: "{v}",'
        return value
