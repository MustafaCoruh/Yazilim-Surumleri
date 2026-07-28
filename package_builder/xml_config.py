from __future__ import annotations

import re
import tempfile
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


def _encoding_and_declaration(path: Path) -> tuple[str, bool, bytes]:
    raw = path.read_bytes()[:256]
    if raw.startswith(b"\xef\xbb\xbf"):
        encoding, bom = "utf-8", b"\xef\xbb\xbf"
    elif raw.startswith((b"\xff\xfe", b"\xfe\xff")):
        encoding = "utf-16-le" if raw.startswith(b"\xff\xfe") else "utf-16-be"
        bom = raw[:2]
    else:
        encoding, bom = "utf-8", b""
    inspected = raw.decode(encoding, errors="ignore").lstrip("\ufeff")
    declaration = inspected.lstrip().startswith("<?xml")
    match = re.search(r"encoding=[\"']([^\"']+)", inspected, re.IGNORECASE)
    declared = match.group(1) if match else encoding
    return (encoding if bom in (b"\xff\xfe", b"\xfe\xff") else declared, declaration, bom)


def _find_exact(root: ET.Element, field: str, package: str, file: Path) -> ET.Element:
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
    return matches[0]


def _set_exact(root: ET.Element, field: str, value: str, package: str, file: Path) -> None:
    element = _find_exact(root, field, package, file)
    if "value" in element.attrib:
        element.set("value", value)
    else:
        element.text = value


def validate_config_preset(software: Software, config: Path, label: str) -> None:
    user = find_xml_file(config, "UserConfiguration", label)
    try:
        user_root = ET.parse(user).getroot()
    except (ET.ParseError, OSError) as exc:
        raise XmlConfigurationError(f"{label}: {user.name} XML dosyası okunamadı: {exc}") from exc
    user_fields = ["ConfigFileLocation", "ProgramFileLocation"]
    if software in (Software.DM, Software.AKY):
        user_fields.append("LogFilesLocation")
    for field in user_fields:
        _find_exact(user_root, field, label, user)

    if software is Software.DM:
        return
    app = find_xml_file(config, "AppSettings", label)
    try:
        app_root = ET.parse(app).getroot()
    except (ET.ParseError, OSError) as exc:
        raise XmlConfigurationError(f"{label}: {app.name} XML dosyası okunamadı: {exc}") from exc
    fields = ["GainsFilePath", "UILayoutsFolder", "HandoverSettingsFilePath"] if software is Software.SYY else ["BlockType"]
    for field in fields:
        element = _find_exact(app_root, field, label, app)
        if field == "GainsFilePath":
            current = element.attrib.get("value", element.text or "")
            if not re.search(r"GainsParamsTable_MessageTable_[^\\/]+\.csv$", current):
                raise XmlConfigurationError(f"{label}: {app.name} içinde geçerli gains dosya adı bulunamadı.")


def _update(path: Path, values: dict[str, str], package: str) -> None:
    encoding, declaration, bom = _encoding_and_declaration(path)
    try:
        tree = ET.parse(path)
    except (ET.ParseError, OSError) as exc:
        raise XmlConfigurationError(f"{package}: {path.name} XML dosyası okunamadı: {exc}") from exc
    for field, value in values.items():
        _set_exact(tree.getroot(), field, value, package, path)
    try:
        with tempfile.NamedTemporaryFile(dir=path.parent, prefix=f".{path.name}-", delete=False) as stream:
            temporary = Path(stream.name)
            if bom:
                stream.write(bom)
            tree.write(stream, encoding=encoding, xml_declaration=declaration)
        temporary.replace(path)
    except (LookupError, OSError, UnicodeError) as exc:
        if "temporary" in locals():
            temporary.unlink(missing_ok=True)
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
