from package_builder import ui
from package_builder.icon import png_bytes, write_icon_files


def test_windows_fonts_are_configured_as_named_tk_fonts(monkeypatch):
    configured = []

    class Font:
        def configure(self, **values):
            configured.append(values)

    class Style:
        def __init__(self, _application):
            pass

        def theme_names(self):
            return ("vista",)

        def theme_use(self, _theme):
            pass

        def configure(self, _name, **_values):
            pass

    monkeypatch.setattr(ui.ttk, "Style", Style)
    monkeypatch.setattr(ui.tkfont, "nametofont", lambda _name: Font())

    ui.Application._configure_style(object())

    assert configured == [{"family": "Segoe UI", "size": 10}] * 4


def test_application_icon_assets_can_be_generated(tmp_path):
    write_icon_files(tmp_path)
    assert png_bytes().startswith(b"\x89PNG")
    assert (tmp_path / "app_icon.png").read_bytes().startswith(b"\x89PNG")
    assert (tmp_path / "app_icon.ico").read_bytes()[:4] == b"\x00\x00\x01\x00"
