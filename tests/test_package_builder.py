from pathlib import Path
import xml.etree.ElementTree as ET

import pytest

from package_builder.builder import PackageBuilder, package_name, version_from_bin
from package_builder.errors import PresetError, ValidationError, XmlConfigurationError
from package_builder.models import DEFAULT_STATIONS, Aircraft, BuildRequest, Software, output_stations
from package_builder.presets import PresetStore
from package_builder.settings import StationStore
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
    profiles = (None, "ANKA3")
    for profile in profiles:
        for station in output_stations(software, DEFAULT_STATIONS, profile):
            suffix = f"-{profile}" if profile else ""
            source = config(tmp_path / f"source-{station}{suffix}")
            (source / "profile.txt").write_text(profile or "STANDARD", encoding="utf-8")
            store.save(software, station, source, profile)
    binary = tmp_path / "bin_2.5.1"
    binary.mkdir()
    (binary / "program.exe").write_bytes(b"exe")
    return store, binary


@pytest.mark.parametrize("software,count", [(Software.SYY, 5), (Software.DM, 4)])
def test_end_to_end_paths_and_allowed_fields(tmp_path, software, count):
    store, binary = prepare(tmp_path, software)
    outputs = PackageBuilder(store).build(BuildRequest(software, binary, tmp_path / "out", Aircraft.ANKA))
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
        PackageBuilder(store).build(BuildRequest(Software.SYY, binary, tmp_path / "out", Aircraft.ANKA))
    store, binary = prepare(tmp_path / "second", Software.SYY)
    out = tmp_path / "second" / "out"
    (out / "SYY_2.5.1_SYKI1").mkdir(parents=True)
    with pytest.raises(ValidationError, match="ezilmeyecek"):
        PackageBuilder(store).build(BuildRequest(Software.SYY, binary, out, Aircraft.ANKA))


@pytest.mark.parametrize("mode", ["missing", "duplicate"])
def test_xml_exactly_once(tmp_path, mode):
    store, binary = prepare(tmp_path, Software.DM)
    preset = store.get(Software.DM, "MYKI15")
    text = (preset / "UserConfiguration").read_text(encoding="utf-8")
    needle = '<add key="ConfigFileLocation" value="old-c"/>'
    text = text.replace(needle, "" if mode == "missing" else needle + needle)
    (preset / "UserConfiguration").write_text(text, encoding="utf-8")
    with pytest.raises(XmlConfigurationError, match="ConfigFileLocation"):
        PackageBuilder(store).build(BuildRequest(Software.DM, binary, tmp_path / "out", Aircraft.ANKA))
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


def test_single_station_selection_and_optional_zip(tmp_path):
    store, binary = prepare(tmp_path, Software.SYY)
    output = tmp_path / "out"

    results = PackageBuilder(store).build(
        BuildRequest(Software.SYY, binary, output, Aircraft.ANKA, stations=("MYKI19",), create_zip=True)
    )

    assert [path.name for path in results] == ["SYY_2.5.1_MYKI19"]
    assert results[0].is_dir()
    assert (output / "SYY_2.5.1_MYKI19.zip").is_file()
    assert not (output / "SYY_2.5.1_SYKI1").exists()


def test_dm_and_aky_use_one_common_syki_preset(tmp_path):
    for software in (Software.DM, Software.AKY):
        store, binary = prepare(tmp_path / software.value, software)
        request = BuildRequest(
            software, binary, tmp_path / software.value / "out",
            Aircraft.ANKA,
            stations=("SYKI1-2",),
        )
        outputs = PackageBuilder(store).build(request)
        assert len(outputs) == 1
        assert outputs[0].name.endswith("_SYKI1-2")


def test_anka3_uses_its_separate_config_preset(tmp_path):
    store, binary = prepare(tmp_path, Software.AKY)

    standard = PackageBuilder(store).build(
        BuildRequest(Software.AKY, binary, tmp_path / "standard", Aircraft.ANKA, stations=("SYKI1-2",))
    )[0]
    anka3 = PackageBuilder(store).build(
        BuildRequest(Software.AKY, binary, tmp_path / "anka3", Aircraft.ANKA3, stations=("SYKI1",))
    )[0]

    assert (standard / "config" / "profile.txt").read_text(encoding="utf-8") == "STANDARD"
    assert (anka3 / "config" / "profile.txt").read_text(encoding="utf-8") == "ANKA3"


def test_anka3_does_not_fall_back_to_standard_aky_preset(tmp_path):
    store = PresetStore(tmp_path / "data")
    store.save(Software.AKY, "SYKI1", config(tmp_path / "standard"))
    binary = tmp_path / "bin_1.0"
    binary.mkdir()

    with pytest.raises(PresetError, match="ANKA3/SYKI1"):
        PackageBuilder(store).build(
            BuildRequest(Software.AKY, binary, tmp_path / "out", Aircraft.ANKA3, stations=("SYKI1",))
        )


@pytest.mark.parametrize("software", list(Software))
def test_anka3_profile_is_separate_for_every_software_and_only_supports_syki(tmp_path, software):
    store, binary = prepare(tmp_path, software)
    outputs = PackageBuilder(store).build(
        BuildRequest(software, binary, tmp_path / "out", Aircraft.ANKA3)
    )

    assert {output.name.rsplit("_", 1)[-1] for output in outputs} == {"SYKI1", "SYKI2"}
    assert all((output / "config" / "profile.txt").read_text(encoding="utf-8") == "ANKA3" for output in outputs)


def test_anka3_profile_rejects_unsupported_myki_selection(tmp_path):
    store, binary = prepare(tmp_path, Software.SYY)
    with pytest.raises(ValidationError, match="Geçersiz çıktı YKİ seçimi: MYKI19"):
        PackageBuilder(store).build(
            BuildRequest(Software.SYY, binary, tmp_path / "out", Aircraft.ANKA3, stations=("MYKI19",))
        )


@pytest.mark.parametrize("software", list(Software))
def test_missing_aircraft_is_rejected_for_every_software(tmp_path, software):
    store, binary = prepare(tmp_path, software)
    with pytest.raises(ValidationError, match="Hava aracı seçilmelidir"):
        PackageBuilder(store).build(
            BuildRequest(software, binary, tmp_path / "out")
        )


@pytest.mark.parametrize("software", list(Software))
def test_anka_and_aksungur_share_the_same_config_group(tmp_path, software):
    store, binary = prepare(tmp_path, software)
    station = output_stations(software, DEFAULT_STATIONS)[0]
    for aircraft in (Aircraft.ANKA, Aircraft.AKSUNGUR):
        output = PackageBuilder(store).build(
            BuildRequest(software, binary, tmp_path / aircraft.value, aircraft, stations=(station,))
        )[0]
        assert (output / "config" / "profile.txt").read_text(encoding="utf-8") == "STANDARD"


def test_dynamic_station_store_and_output_model(tmp_path):
    stations = StationStore(tmp_path).add("MYKI21")
    assert stations[-1] == "MYKI21"
    assert "MYKI21" in output_stations(Software.SYY, stations)
    assert "MYKI21" in output_stations(Software.DM, stations)
    with pytest.raises(ValidationError):
        StationStore(tmp_path).add("MYK19")


def test_existing_zip_is_not_overwritten(tmp_path):
    store, binary = prepare(tmp_path, Software.SYY)
    output = tmp_path / "out"
    output.mkdir()
    existing = output / "SYY_2.5.1_MYKI20.zip"
    existing.write_bytes(b"keep")

    with pytest.raises(ValidationError, match="ZIP çıktıları ezilmeyecek"):
        PackageBuilder(store).build(
            BuildRequest(Software.SYY, binary, output, Aircraft.ANKA, stations=("MYKI20",), create_zip=True)
        )

    assert existing.read_bytes() == b"keep"
    assert not (output / "SYY_2.5.1_MYKI20").exists()
