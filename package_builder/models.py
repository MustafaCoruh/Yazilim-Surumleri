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
AIRCRAFT_CONFIG_GROUPS: tuple[str, ...] = ("ANKA / AKSUNGUR", "ANKA3")


def preset_profile(aircraft: Aircraft | None) -> str | None:
    if aircraft is Aircraft.ANKA3:
        return Aircraft.ANKA3.value
    return None


def output_stations(
    software: Software, stations: tuple[str, ...], profile: str | None = None,
) -> tuple[str, ...]:
    if profile == Aircraft.ANKA3.value:
        if software is Software.SYY:
            return tuple(station for station in ("SYKI1", "SYKI2") if station in stations)
        return (COMMON_SYKI,)
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
