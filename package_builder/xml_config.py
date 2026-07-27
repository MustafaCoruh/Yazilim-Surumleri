from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from pathlib import Path

from .errors import XmlConfigurationError
from .models import AIRCRAFT_BLOCK_TYPES, Aircraft, Software

INSTALL_ROOT = r"C:\Program Files (x86)\TAI"


def _local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def find_xml_file(config: Path, kind: str, package_name: str) -> Path:
    matches: list[Path] = []
    for path in config.rglob("*"):
        if not path.is_file() or path.stem.casefold() != kind.casefold():
            continue
        try:
            ET.parse(path)
        except (ET.ParseError, OSError):
            continue
        matches.append(path)
    if len(matches) != 1:
        raise XmlConfigurationError(
            f"{package_name}: config içinde XML türünde {kind} dosyası tam olarak bir kez "
            f"bulunmalı (bulunan: {len(matches)})."
        )
    return matches[0]


def _encoding_and_declaration(path: Path) -> tuple[str, bool]:
    raw = path.read_bytes()[:256]
    declaration = raw.lstrip().startswith(b"<?xml")
    match = re.search(br"encoding=[\"']([^\"']+)", raw, re.IGNORECASE)
    return (match.group(1).decode("ascii") if match else "utf-8", declaration)


def _set_exact(root: ET.Element, field: str, value: str, package: str, file: Path) -> None:
    matches: list[ET.Element] = []
    for element in root.iter():
        identity = element.attrib.get("key", element.attrib.get("name", ""))
        if _local_name(element.tag) == field or identity == field:
            matches.append(element)
    if len(matches) != 1:
        raise XmlConfigurationError(
            f"{package}: {file.name} içinde {field} tam olarak bir kez bulunmalı "
            f"(bulunan: {len(matches)})."
        )
    element = matches[0]
    if "value" in element.attrib:
        element.set("value", value)
    else:
        element.text = value


def _update(path: Path, values: dict[str, str], package: str) -> None:
    encoding, declaration = _encoding_and_declaration(path)
    try:
        tree = ET.parse(path)
    except (ET.ParseError, OSError) as exc:
        raise XmlConfigurationError(f"{package}: {path.name} XML dosyası okunamadı: {exc}") from exc
    for field, value in values.items():
        _set_exact(tree.getroot(), field, value, package, path)
    try:
        tree.write(path, encoding=encoding, xml_declaration=declaration)
    except (LookupError, OSError) as exc:
        raise XmlConfigurationError(f"{package}: {path.name} XML dosyası yazılamadı: {exc}") from exc


def configure_package(
    software: Software,
    config: Path,
    package_name: str,
    bin_name: str,
    aircraft: Aircraft | None,
) -> None:
    base = f"{INSTALL_ROOT}\\{package_name}"
    user = find_xml_file(config, "UserConfiguration", package_name)
    user_values = {
        "ConfigFileLocation": f"{base}\\config\\DataFrameworkConfig.xml",
        "ProgramFileLocation": f"{base}\\{bin_name}",
    }
    if software is Software.DM:
        user_values["LogFilesLocation"] = f"{base}\\Logs"
    elif software is Software.AKY:
        user_values["LogFilesLocation"] = f"{base}\\LogAKY"
    _update(user, user_values, package_name)

    if software is Software.SYY:
        app = find_xml_file(config, "AppSettings", package_name)
        tree = ET.parse(app)
        gains_matches = [
            e for e in tree.getroot().iter()
            if _local_name(e.tag) == "GainsFilePath" or e.attrib.get("key") == "GainsFilePath"
        ]
        if len(gains_matches) != 1:
            raise XmlConfigurationError(
                f"{package_name}: {app.name} içinde GainsFilePath tam olarak bir kez bulunmalı "
                f"(bulunan: {len(gains_matches)})."
            )
        gains_value = gains_matches[0].attrib.get("value", gains_matches[0].text or "")
        filename_match = re.search(r"GainsParamsTable_MessageTable_[^\\/]+\.csv$", gains_value)
        if not filename_match:
            raise XmlConfigurationError(f"{package_name}: {app.name} içinde geçerli gains dosya adı bulunamadı.")
        _update(app, {
            "GainsFilePath": f"{base}\\config\\{filename_match.group(0)}",
            "UILayoutsFolder": f"{base}\\config\\UILayoutsFolder",
            "HandoverSettingsFilePath": f"{base}\\config",
        }, package_name)
    elif software is Software.AKY:
        if aircraft is None:
            raise XmlConfigurationError(f"{package_name}: hava aracı seçilmedi.")
        app = find_xml_file(config, "AppSettings", package_name)
        _update(app, {"BlockType": AIRCRAFT_BLOCK_TYPES[aircraft]}, package_name)
