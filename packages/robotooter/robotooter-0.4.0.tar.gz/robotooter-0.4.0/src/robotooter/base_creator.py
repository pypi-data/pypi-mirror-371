from abc import ABC, abstractmethod
from pathlib import Path

import requests

from robotooter.models.statuses import RtMedia, RtStatus


class BaseContentCreator(ABC):
    __KEY__ = ""

    def __init__(self, working_directory: Path):
        self.working_directory = working_directory
        self.temp_path: Path = self.working_directory / "temp"
        self.downloaded_files: list[Path] = []


    def create(self) -> list[list[RtStatus]]:
        self.temp_path.mkdir(parents=True, exist_ok=True)
        return self._create()

    def cleanup(self) -> None:
        for downloaded_file in self.downloaded_files:
            downloaded_file.unlink()

    @abstractmethod
    def _create(self) -> list[list[RtStatus]]:
        pass

    def _download_image(self, url: str, name: str, description: str) -> RtMedia | None:
        if self.temp_path is None or not url:
            return None

        outpath = self.temp_path.joinpath(name)
        data = requests.get(url).content
        outpath.write_bytes(data)
        self.downloaded_files.append(outpath)
        return RtMedia(
            file_path=outpath,
            description=description,
        )
