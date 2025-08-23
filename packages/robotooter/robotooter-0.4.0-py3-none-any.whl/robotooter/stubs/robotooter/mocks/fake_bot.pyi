import argparse

from robotooter.bots.base_bot import BaseBot as BaseBot
from robotooter.bots.base_bot import CommandParam as CommandParam
from robotooter.bots.base_bot import command as command
from robotooter.filters.base_filter import BaseFilter as BaseFilter
from robotooter.models.configs import BotConfig as BotConfig

class FakeBotConfig(BotConfig):
    extra_field_1: str

COUNT_PARAM: CommandParam

class FakeBot(BaseBot[FakeBotConfig]):
    NAME: str
    DESCRIPTION: str
    CONFIG_CLASS = FakeBotConfig
    @classmethod
    def create_with_config(cls, config_data: BotConfig, filters: list[BaseFilter]) -> FakeBot: ...
    @classmethod
    def add_arguments(cls, parser: argparse.ArgumentParser) -> None: ...
    number: int
    def __init__(self, config: FakeBotConfig, filters: list[BaseFilter]) -> None: ...
    def add_one(self, args: argparse.Namespace) -> None: ...
    def set_number(self, args: argparse.Namespace) -> None: ...
    def _setup_data(self, args: argparse.Namespace) -> None: ...
