from __future__ import annotations

import json
import re
import tempfile
from pathlib import Path

from .errors import ValidationError
from .models import COMMON_SYKI, DEFAULT_STATIONS

STATION_PATTERN = re.compile(r"^[A-Z][A-Z0-9]{2,19}$")
FORBIDDEN_STATIONS = {"SYKI", "MYK19", COMMON_SYKI}


class StationStore:
    def __init__(self, root: Path):
        self.root = Path(root)
        self.path = self.root / "stations.json"

    def list(self) -> tuple[str, ...]:
        if not self.path.exists():
            return DEFAULT_STATIONS
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise ValidationError(f"YKİ ayarları okunamadı: {exc}") from exc
        if (
            not isinstance(data, list)
            or not all(isinstance(item, str) and self._valid(item) for item in data)
            or len(data) != len(set(data))
        ):
            raise ValidationError("YKİ ayarları geçersiz.")
        return tuple(data)

    @staticmethod
    def _valid(station: str) -> bool:
        return station not in FORBIDDEN_STATIONS and STATION_PATTERN.fullmatch(station) is not None

    def add(self, station: str) -> tuple[str, ...]:
        station = station.strip().upper()
        if not self._valid(station):
            raise ValidationError(
                "YKİ adı 3-20 karakter, büyük harf ve rakamlardan oluşmalıdır; "
                "SYKI, MYK19 ve SYKI1-2 kullanılamaz."
            )
        stations = self.list()
        if station in stations:
            raise ValidationError(f"YKİ zaten kayıtlı: {station}")
        updated = stations + (station,)
        self.root.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=self.root, delete=False) as stream:
            json.dump(updated, stream, ensure_ascii=False, indent=2)
            temporary = Path(stream.name)
        temporary.replace(self.path)
        return updated
