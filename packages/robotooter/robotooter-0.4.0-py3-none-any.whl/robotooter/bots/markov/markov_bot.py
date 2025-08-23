import os
from argparse import Namespace

import markovify

from robotooter.bots.base_bot import BaseBot
from robotooter.bots.markov.markov_creator import MarkovContentCreator
from robotooter.bots.markov.markov_processor import MarkovProcessor
from robotooter.filters.base_filter import BaseFilter
from robotooter.models.configs import BotConfig
from robotooter.util import download_sources


class MarkovBot(BaseBot[BotConfig]):
    NAME = "MarkovBot"

    @classmethod
    def create_with_config(cls, config_data: BotConfig, filters: list[BaseFilter]) -> 'MarkovBot':
        return cls(config_data, filters)

    @staticmethod
    def new_bot_info() -> str | None:
        return "You will need to add `sources.txt` to the working directory"

    def __init__(self, config: BotConfig, filters: list[BaseFilter]) -> None:
        super().__init__(config, filters)
        self.source_dir = self.data_root / "sources"
        self.model_path = self.data_root / "model.json"
        self._model: markovify.Text | None = None

        self.creators = {'markov': MarkovContentCreator}

    def _setup_data(self, args: Namespace) -> None:
        if self.model_exists:
            raise Exception(f"Model file {self.model_path} already exists.")

        download_sources(self.working_directory / "sources.txt", self.source_dir)
        self.processor.preprocess_sources()
        self.processor.build_model()

    @property
    def processor(self) -> MarkovProcessor:
        return MarkovProcessor(self.working_directory, self.plugin_filters)

    @property
    def model_exists(self) -> bool:
        return os.path.exists(self.model_path)
