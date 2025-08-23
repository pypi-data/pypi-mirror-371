from pathlib import Path

import markovify
from _typeshed import Incomplete

from robotooter.base_creator import BaseContentCreator as BaseContentCreator
from robotooter.models.statuses import RtStatus as RtStatus

class MarkovContentCreator(BaseContentCreator):
    model_path: Incomplete
    def __init__(self, working_directory: Path) -> None: ...
    def generate_toot(self) -> str: ...
    @property
    def model(self) -> markovify.Text: ...
    def _create(self) -> list[list[RtStatus]]: ...
