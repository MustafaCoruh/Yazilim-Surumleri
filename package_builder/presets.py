from __future__ import annotations

import json
import re
import shutil
import tempfile
from pathlib import Path

from .errors import PresetError
from .models import Aircraft, Software
from .xml_config import validate_config_preset


class PresetStore:
    def __init__(self, root: Path):
        self.root = Path(root)
        self._index_path = self.root / "presets.json"

    def _key(self, software: Software, station: str, profile: str | None = None) -> str:
        if not re.fullmatch(r"[A-Z][A-Z0-9]*(?:-[A-Z0-9]+)?", station):
            raise PresetError(f"Geçersiz YKİ: {station}")
        if profile not in (None, Aircraft.ANKA3.value):
            raise PresetError(f"Geçersiz config profili: {profile}")
        parts = [software.value]
        if profile:
            parts.append(profile)
        parts.append(station)
        return "/".join(parts)

    def _read_index(self) -> dict[str, str]:
        if not self._index_path.exists():
            return {}
        try:
            value = json.loads(self._index_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise PresetError(f"Ön ayar dizini okunamadı: {exc}") from exc
        if not isinstance(value, dict):
            raise PresetError("Ön ayar dizini geçersiz.")
        return value

    def list(self) -> dict[str, Path]:
        return {key: self.root / relative for key, relative in self._read_index().items()}

    def get(self, software: Software, station: str, profile: str | None = None) -> Path | None:
        relative = self._read_index().get(self._key(software, station, profile))
        if not relative:
            return None
        path = self.root / relative
        return path if path.is_dir() else None

    def save(self, software: Software, station: str, source: Path, profile: str | None = None) -> Path:
        source = Path(source)
        if not source.is_dir():
            raise PresetError(f"Config klasörü bulunamadı: {source}")
        key = self._key(software, station, profile)
        label = "/".join(part for part in (software.value, profile, station) if part)
        validate_config_preset(software, source, f"{label} ön ayarı")
        destination = self.root / "configs" / software.value
        if profile:
            destination /= profile
        destination /= station
        destination.parent.mkdir(parents=True, exist_ok=True)
        temporary = Path(tempfile.mkdtemp(prefix=f".{station}-", dir=destination.parent))
        backup = destination.with_name(f".{destination.name}.backup")
        try:
            shutil.copytree(source, temporary / "content")
            if backup.exists():
                shutil.rmtree(backup)
            if destination.exists():
                destination.replace(backup)
            try:
                (temporary / "content").replace(destination)
            except Exception:
                if backup.exists():
                    backup.replace(destination)
                raise
            shutil.rmtree(backup, ignore_errors=True)
        finally:
            shutil.rmtree(temporary, ignore_errors=True)
        index = self._read_index()
        index[key] = destination.relative_to(self.root).as_posix()
        self.root.mkdir(parents=True, exist_ok=True)
        temp_index = self._index_path.with_suffix(".tmp")
        temp_index.write_text(json.dumps(index, ensure_ascii=False, indent=2), encoding="utf-8")
        temp_index.replace(self._index_path)
        return destination
