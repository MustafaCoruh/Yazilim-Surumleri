from pathlib import Path


def test_launcher_prefers_standalone_executable_before_python():
    script = Path("calistir.bat").read_text(encoding="utf-8")
    executable_check = script.index('if exist "release\\SurumIstasyonu\\SurumIstasyonu.exe"')
    python_lookup = script.index("where py")
    assert executable_check < python_lookup


def test_launcher_recreates_a_nonportable_virtual_environment():
    script = Path("calistir.bat").read_text(encoding="utf-8")
    assert 'rmdir /s /q ".venv"' in script
    assert "%PYTHON_CMD% -m venv .venv" in script


def test_cmd_builder_creates_a_portable_onedir_release_without_powershell():
    script = Path("build_windows.bat").read_text(encoding="utf-8")
    assert "powershell" not in script.lower()
    assert "-m pytest" in script
    assert "-m PyInstaller" in script
    assert "--onedir --noupx" in script
    assert 'release\\SurumIstasyonu\\SurumIstasyonu.exe' in script


def test_cmd_desktop_installer_uses_the_batch_builder():
    script = Path("masaustune_kur.bat").read_text(encoding="utf-8")
    assert "powershell" not in script.lower()
    assert "call build_windows.bat" in script
    assert 'release\\SurumIstasyonu\\SurumIstasyonu.exe' in script
