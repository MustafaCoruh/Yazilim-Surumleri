from __future__ import annotations

import re
import shutil
import tempfile
from pathlib import Path

from .errors import PresetError, ValidationError
from .models import DEFAULT_STATIONS, BuildRequest, Software, output_stations
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
    def __init__(self, presets: PresetStore, stations: tuple[str, ...] = DEFAULT_STATIONS):
        self.presets = presets
        self.stations = stations

    def build(self, request: BuildRequest) -> list[Path]:
        version = version_from_bin(request.bin_directory)
        if request.software is Software.AKY and request.aircraft is None:
            raise ValidationError("AKY için hava aracı seçilmelidir.")
        request.output_directory.mkdir(parents=True, exist_ok=True)
        available = output_stations(request.software, self.stations)
        selected = request.stations or available
        if len(selected) != len(set(selected)):
            raise ValidationError("Aynı YKİ birden fazla kez seçilemez.")
        invalid = [station for station in selected if station not in available]
        if invalid:
            raise ValidationError(f"Geçersiz çıktı YKİ seçimi: {', '.join(invalid)}")
        jobs: list[tuple[str, Path]] = []
        missing: list[str] = []
        for output_station in selected:
            preset = self.presets.get(request.software, output_station)
            if preset is None:
                missing.append(output_station)
                continue
            jobs.append((package_name(request.software, version, output_station, request.aircraft), preset))
        if missing:
            raise PresetError(
                f"{request.software.value} için eksik config ön ayarları: {', '.join(missing)}. "
                "Ön Ayar Yönetimi ekranından yükleyin."
            )
        collisions = [name for name, _ in jobs if (request.output_directory / name).exists()]
        if collisions:
            raise ValidationError(f"Mevcut çıktılar ezilmeyecek: {', '.join(collisions)}")
        zip_collisions = [f"{name}.zip" for name, _ in jobs if request.create_zip and (request.output_directory / f"{name}.zip").exists()]
        if zip_collisions:
            raise ValidationError(f"Mevcut ZIP çıktıları ezilmeyecek: {', '.join(zip_collisions)}")

        staging = Path(tempfile.mkdtemp(prefix=".paket-", dir=request.output_directory))
        completed: list[Path] = []
        package_directories: list[Path] = []
        try:
            for name, preset in jobs:
                package = staging / name
                shutil.copytree(request.bin_directory, package / request.bin_directory.name)
                shutil.copytree(preset, package / "config")
                configure_package(
                    request.software, package / "config", name,
                    request.bin_directory.name, request.aircraft,
                )
                if request.create_zip:
                    shutil.make_archive(str(staging / name), "zip", staging, name)
            for name, _ in jobs:
                destination = request.output_directory / name
                (staging / name).replace(destination)
                completed.append(destination)
                package_directories.append(destination)
                if request.create_zip:
                    zip_destination = request.output_directory / f"{name}.zip"
                    (staging / f"{name}.zip").replace(zip_destination)
                    completed.append(zip_destination)
            return package_directories
        except Exception:
            for destination in completed:
                if destination.is_dir():
                    shutil.rmtree(destination, ignore_errors=True)
                else:
                    destination.unlink(missing_ok=True)
            raise
        finally:
            shutil.rmtree(staging, ignore_errors=True)
