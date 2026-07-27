from __future__ import annotations

import re
import shutil
import tempfile
from pathlib import Path

from .errors import PresetError, ValidationError
from .models import BuildRequest, Software, output_stations
from .presets import PresetStore
from .xml_config import configure_package

BIN_PATTERN = re.compile(r"^bin_(\d+(?:\.\d+)*)$")


def version_from_bin(path: Path) -> str:
    match = BIN_PATTERN.fullmatch(Path(path).name)
    if not match:
        raise ValidationError("Bin klasörü adı bin_<noktayla ayrılmış sayısal sürüm> biçiminde olmalıdır.")
    if not Path(path).is_dir():
        raise ValidationError(f"Bin klasörü bulunamadı: {path}")
    return match.group(1)


def package_name(software: Software, version: str, station: str, aircraft=None) -> str:
    if software is Software.AKY:
        if aircraft is None:
            raise ValidationError("AKY için hava aracı seçilmelidir.")
        return f"AKY_{version}_{aircraft.value}_{station}"
    return f"{software.value}_{version}_{station}"


class PackageBuilder:
    def __init__(self, presets: PresetStore):
        self.presets = presets

    def build(self, request: BuildRequest) -> list[Path]:
        version = version_from_bin(request.bin_directory)
        if request.software is Software.AKY and request.aircraft is None:
            raise ValidationError("AKY için hava aracı seçilmelidir.")
        request.output_directory.mkdir(parents=True, exist_ok=True)
        jobs: list[tuple[str, Path]] = []
        missing: list[str] = []
        for output_station, source_stations in output_stations(request.software):
            sources = [self.presets.get(request.software, station) for station in source_stations]
            absent = [station for station, source in zip(source_stations, sources) if source is None]
            if absent:
                missing.extend(absent)
                continue
            selected = sources[0]
            if len(sources) == 2 and not _directories_equal(sources[0], sources[1]):
                raise PresetError(
                    f"{request.software.value} SYKI1 ve SYKI2 ön ayarları ortak çıktı için aynı olmalıdır."
                )
            jobs.append((package_name(request.software, version, output_station, request.aircraft), selected))
        if missing:
            raise PresetError(
                f"{request.software.value} için eksik config ön ayarları: {', '.join(missing)}. "
                "Ön Ayar Yönetimi ekranından yükleyin."
            )
        collisions = [name for name, _ in jobs if (request.output_directory / name).exists()]
        if collisions:
            raise ValidationError(f"Mevcut çıktılar ezilmeyecek: {', '.join(collisions)}")

        staging = Path(tempfile.mkdtemp(prefix=".paket-", dir=request.output_directory))
        completed: list[Path] = []
        try:
            for name, preset in jobs:
                package = staging / name
                shutil.copytree(request.bin_directory, package / request.bin_directory.name)
                shutil.copytree(preset, package / "config")
                configure_package(
                    request.software, package / "config", name,
                    request.bin_directory.name, request.aircraft,
                )
            for name, _ in jobs:
                destination = request.output_directory / name
                (staging / name).replace(destination)
                completed.append(destination)
            return completed
        except Exception:
            for destination in completed:
                shutil.rmtree(destination, ignore_errors=True)
            raise
        finally:
            shutil.rmtree(staging, ignore_errors=True)


def _directories_equal(left: Path, right: Path) -> bool:
    def snapshot(root: Path) -> dict[str, bytes]:
        return {p.relative_to(root).as_posix(): p.read_bytes() for p in root.rglob("*") if p.is_file()}
    return snapshot(left) == snapshot(right)
