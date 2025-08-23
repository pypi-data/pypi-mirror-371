import abc
from abc import ABC
from pathlib import Path

from _typeshed import Incomplete

from robotooter.models.statuses import RtMedia as RtMedia
from robotooter.models.statuses import RtStatus as RtStatus

class BaseContentCreator(ABC, metaclass=abc.ABCMeta):
    __KEY__: str
    working_directory: Incomplete
    temp_path: Path
    downloaded_files: list[Path]
    def __init__(self, working_directory: Path) -> None: ...
    def create(self) -> list[list[RtStatus]]: ...
    def cleanup(self) -> None: ...
