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


STATIONS: tuple[str, ...] = ("SYKI1", "SYKI2", "MYKI15", "MYKI19", "MYKI20")
AIRCRAFT_BLOCK_TYPES = {
    Aircraft.ANKA: "OPERATIF",
    Aircraft.AKSUNGUR: "YFYK",
    Aircraft.ANKA3: "ANKA3",
}


def output_stations(software: Software) -> tuple[tuple[str, tuple[str, ...]], ...]:
    if software is Software.SYY:
        return tuple((station, (station,)) for station in STATIONS)
    return (
        ("SYKI1-2", ("SYKI1", "SYKI2")),
        ("MYKI15", ("MYKI15",)),
        ("MYKI19", ("MYKI19",)),
        ("MYKI20", ("MYKI20",)),
    )


@dataclass(frozen=True)
class BuildRequest:
    software: Software
    bin_directory: Path
    output_directory: Path
    aircraft: Aircraft | None = None
