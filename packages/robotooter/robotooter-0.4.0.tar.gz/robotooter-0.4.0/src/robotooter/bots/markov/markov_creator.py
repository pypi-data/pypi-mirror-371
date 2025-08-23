from pathlib import Path

import markovify

from robotooter.base_creator import BaseContentCreator
from robotooter.models.statuses import RtStatus


class MarkovContentCreator(BaseContentCreator):
    def __init__(self, working_directory: Path, ) -> None:
        super().__init__(working_directory)
        self.model_path = self.working_directory / "data/model.json"
        self._model: markovify.Text | None = None

    def _create(self) -> list[list[RtStatus]]:
        content = self.generate_toot()
        return [
            [
                RtStatus(text=content)
            ]
        ]

    def generate_toot(self) -> str:
        content = None
        while not content:  # Sometimes we get None, prevent that
            content = self.model.make_sentence()
        return str(content)

    @property
    def model(self) -> markovify.Text:
        if self._model is None:
            json_blob = open(self.model_path, "r").read()
            self._model = markovify.Text.from_json(json_blob)

        return self._model

