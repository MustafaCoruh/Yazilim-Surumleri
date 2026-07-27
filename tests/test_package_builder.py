from pathlib import Path
import xml.etree.ElementTree as ET

import pytest

from package_builder.builder import PackageBuilder, package_name, version_from_bin
from package_builder.errors import PresetError, ValidationError, XmlConfigurationError
from package_builder.models import Aircraft, BuildRequest, Software
from package_builder.presets import PresetStore
from package_builder.xml_config import configure_package


USER = """<?xml version="1.0" encoding="utf-8"?>
<settings><add key="ConfigFileLocation" value="old-c"/><add key="ProgramFileLocation" value="old-p"/>
<add key="LogFilesLocation" value="old-l"/><add key="Untouched" value="same"/></settings>"""
APP = """<?xml version="1.0" encoding="utf-8"?>
<settings><add key="GainsFilePath" value="D:\\old\\GainsParamsTable_MessageTable_7.41.csv"/>
<add key="UILayoutsFolder" value="old-u"/><add key="HandoverSettingsFilePath" value="old-h"/>
<add key="BlockType" value="OLD"/><add key="Untouched" value="same"/></settings>"""


def config(path: Path) -> Path:
    path.mkdir(parents=True)
    (path / "UserConfiguration").write_text(USER, encoding="utf-8")
    (path / "AppSettings.xml").write_text(APP, encoding="utf-8")
    return path


def values(path: Path) -> dict[str, str]:
    root = ET.parse(path).getroot()
    return {item.attrib["key"]: item.attrib["value"] for item in root}


@pytest.mark.parametrize("name,version", [("bin_1", "1"), ("bin_1.20.3", "1.20.3")])
def test_bin_name(tmp_path, name, version):
    directory = tmp_path / name
    directory.mkdir()
    assert version_from_bin(directory) == version


@pytest.mark.parametrize("name", ["bin_1.", "bin_1a2", "Bin_1.2", "bin_", "xbin_1", "bin_1_2"])
def test_invalid_bin_names(tmp_path, name):
    (tmp_path / name).mkdir()
    with pytest.raises(ValidationError):
        version_from_bin(tmp_path / name)


def test_output_names():
    assert package_name(Software.SYY, "1.2", "MYKI19") == "SYY_1.2_MYKI19"
    assert package_name(Software.DM, "1.2", "SYKI1-2") == "DM_1.2_SYKI1-2"
    assert package_name(Software.AKY, "1.2", "MYKI20", Aircraft.ANKA3) == "AKY_1.2_ANKA3_MYKI20"


def prepare(tmp_path: Path, software: Software):
    store = PresetStore(tmp_path / "data")
    for station in ("SYKI1", "SYKI2", "MYKI15", "MYKI19", "MYKI20"):
        store.save(software, station, config(tmp_path / f"source-{station}"))
    binary = tmp_path / "bin_2.5.1"
    binary.mkdir()
    (binary / "program.exe").write_bytes(b"exe")
    return store, binary


@pytest.mark.parametrize("software,count", [(Software.SYY, 5), (Software.DM, 4)])
def test_end_to_end_paths_and_allowed_fields(tmp_path, software, count):
    store, binary = prepare(tmp_path, software)
    outputs = PackageBuilder(store).build(BuildRequest(software, binary, tmp_path / "out"))
    assert len(outputs) == count
    assert any("SYKI1-2" in output.name for output in outputs) == (software is Software.DM)
    target = outputs[0]
    user = values(target / "config" / "UserConfiguration")
    assert user["ConfigFileLocation"].endswith(f"{target.name}\\config\\DataFrameworkConfig.xml")
    assert user["ProgramFileLocation"].endswith(f"{target.name}\\bin_2.5.1")
    assert user["Untouched"] == "same"
    assert (target / "bin_2.5.1" / "program.exe").exists()
    if software is Software.SYY:
        app = values(target / "config" / "AppSettings.xml")
        assert app["GainsFilePath"].endswith("GainsParamsTable_MessageTable_7.41.csv")
        assert app["BlockType"] == "OLD"
    else:
        assert user["LogFilesLocation"].endswith(f"{target.name}\\Logs")


@pytest.mark.parametrize("aircraft,block", [(Aircraft.ANKA, "OPERATIF"), (Aircraft.AKSUNGUR, "YFYK"), (Aircraft.ANKA3, "ANKA3")])
def test_aky_block_type_and_log_path(tmp_path, aircraft, block):
    store, binary = prepare(tmp_path, Software.AKY)
    outputs = PackageBuilder(store).build(BuildRequest(Software.AKY, binary, tmp_path / "out", aircraft))
    app = values(outputs[0] / "config" / "AppSettings.xml")
    user = values(outputs[0] / "config" / "UserConfiguration")
    assert app["BlockType"] == block
    assert app["Untouched"] == "same"
    assert user["LogFilesLocation"].endswith(f"{outputs[0].name}\\LogAKY")


def test_missing_preset_and_collision(tmp_path):
    store = PresetStore(tmp_path / "data")
    binary = tmp_path / "bin_1.0"
    binary.mkdir()
    with pytest.raises(PresetError, match="eksik config"):
        PackageBuilder(store).build(BuildRequest(Software.SYY, binary, tmp_path / "out"))
    store, binary = prepare(tmp_path / "second", Software.SYY)
    out = tmp_path / "second" / "out"
    (out / "SYY_2.5.1_SYKI1").mkdir(parents=True)
    with pytest.raises(ValidationError, match="ezilmeyecek"):
        PackageBuilder(store).build(BuildRequest(Software.SYY, binary, out))


@pytest.mark.parametrize("mode", ["missing", "duplicate"])
def test_xml_exactly_once(tmp_path, mode):
    store, binary = prepare(tmp_path, Software.DM)
    preset = store.get(Software.DM, "MYKI15")
    text = (preset / "UserConfiguration").read_text(encoding="utf-8")
    needle = '<add key="ConfigFileLocation" value="old-c"/>'
    text = text.replace(needle, "" if mode == "missing" else needle + needle)
    (preset / "UserConfiguration").write_text(text, encoding="utf-8")
    with pytest.raises(XmlConfigurationError, match="ConfigFileLocation"):
        PackageBuilder(store).build(BuildRequest(Software.DM, binary, tmp_path / "out"))
    assert not list((tmp_path / "out").glob("DM_*"))


@pytest.mark.parametrize("encoding,bom", [("utf-8-sig", b"\xef\xbb\xbf"), ("utf-16", b"\xff\xfe")])
def test_xml_encoding_declaration_and_extensionless_name_are_preserved(tmp_path, encoding, bom):
    directory = tmp_path / "config"
    directory.mkdir()
    user = directory / "UserConfiguration"
    app = directory / "AppSettings.xml"
    declaration_encoding = "utf-16" if encoding == "utf-16" else "utf-8"
    user.write_text(USER.replace('encoding="utf-8"', f'encoding="{declaration_encoding}"'), encoding=encoding)
    app.write_text(APP.replace('encoding="utf-8"', f'encoding="{declaration_encoding}"'), encoding=encoding)

    configure_package(Software.SYY, directory, "SYY_1.0_SYKI1", "bin_1.0", None)

    assert user.read_bytes().startswith(bom)
    assert app.read_bytes().startswith(bom)
    assert "ConfigFileLocation" in user.read_text(encoding=encoding)
    assert "GainsParamsTable_MessageTable_7.41.csv" in app.read_text(encoding=encoding)


def test_invalid_preset_is_rejected_before_being_saved(tmp_path):
    source = config(tmp_path / "source")
    user = source / "UserConfiguration"
    user.write_text(USER.replace('<add key="LogFilesLocation" value="old-l"/>', ""), encoding="utf-8")
    store = PresetStore(tmp_path / "data")

    with pytest.raises(XmlConfigurationError, match="DM/SYKI1 ön ayarı.*LogFilesLocation"):
        store.save(Software.DM, "SYKI1", source)

    assert store.get(Software.DM, "SYKI1") is None
