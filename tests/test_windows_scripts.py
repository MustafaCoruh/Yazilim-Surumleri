from pathlib import Path


def test_launcher_prefers_standalone_executable_before_python():
    script = Path("calistir.bat").read_text(encoding="utf-8")
    executable_check = script.index('if exist "release\\SurumIstasyonu.exe"')
    python_lookup = script.index("where py")
    assert executable_check < python_lookup


def test_launcher_recreates_a_nonportable_virtual_environment():
    script = Path("calistir.bat").read_text(encoding="utf-8")
    assert 'rmdir /s /q ".venv"' in script
    assert "%PYTHON_CMD% -m venv .venv" in script
