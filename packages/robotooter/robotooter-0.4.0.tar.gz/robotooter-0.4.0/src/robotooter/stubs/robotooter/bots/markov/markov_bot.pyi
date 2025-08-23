import argparse

from _typeshed import Incomplete

from robotooter.bots.base_bot import BaseBot as BaseBot
from robotooter.bots.markov.markov_creator import MarkovContentCreator as MarkovContentCreator
from robotooter.bots.markov.markov_processor import MarkovProcessor as MarkovProcessor
from robotooter.filters.base_filter import BaseFilter as BaseFilter
from robotooter.models.configs import BotConfig as BotConfig
from robotooter.util import download_sources as download_sources

class MarkovBot(BaseBot[BotConfig]):
    NAME: str
    @classmethod
    def create_with_config(cls, config_data: BotConfig, filters: list[BaseFilter]) -> MarkovBot: ...
    @staticmethod
    def new_bot_info() -> str | None: ...
    source_dir: Incomplete
    model_path: Incomplete
    creators: Incomplete
    def __init__(self, config: BotConfig, filters: list[BaseFilter]) -> None: ...
    @property
    def processor(self) -> MarkovProcessor: ...
    @property
    def model_exists(self) -> bool: ...
    def _setup_data(self, args: argparse.Namespace) -> None: ...
