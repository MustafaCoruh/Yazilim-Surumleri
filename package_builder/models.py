from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path


class Software(StrEnum):
    SYY = "SYY"
    DM = "DM"
    AKY = "AKY"


class Aircraft(StrEnum):
    ANKA = "ANKA"
    AKSUNGUR = "AKSUNGUR"
    ANKA3 = "ANKA3"


DEFAULT_STATIONS: tuple[str, ...] = ("SYKI1", "SYKI2", "MYKI15", "MYKI19", "MYKI20")
COMMON_SYKI = "SYKI1-2"
AIRCRAFT_BLOCK_TYPES = {
    Aircraft.ANKA: "OPERATIF",
    Aircraft.AKSUNGUR: "YFYK",
    Aircraft.ANKA3: "ANKA3",
}


def output_stations(software: Software, stations: tuple[str, ...]) -> tuple[str, ...]:
    if software is Software.SYY:
        return stations
    return (COMMON_SYKI,) + tuple(station for station in stations if station not in ("SYKI1", "SYKI2"))


@dataclass(frozen=True)
class BuildRequest:
    software: Software
    bin_directory: Path
    output_directory: Path
    aircraft: Aircraft | None = None
    stations: tuple[str, ...] = ()
    create_zip: bool = False
