from package_builder import ui


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
