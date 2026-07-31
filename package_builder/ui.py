from __future__ import annotations

import os
import threading
import tkinter as tk
import tkinter.font as tkfont
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from .builder import PackageBuilder
from .errors import PackageError
from .icon import ICON_PNG_BASE64
from .models import PRESET_PROFILES, Aircraft, BuildRequest, Software, output_stations
from .presets import PresetStore
from .settings import StationStore


def application_data_directory() -> Path:
    base = Path(os.environ.get("LOCALAPPDATA", Path.home() / ".local" / "share"))
    return base / "TAI" / "YazilimSurumleri"


class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Sürüm İstasyonu")
        self.geometry("780x540")
        self.minsize(720, 500)
        self._icon_image = tk.PhotoImage(data=ICON_PNG_BASE64)
        self.iconphoto(True, self._icon_image)
        self.store = PresetStore(application_data_directory())
        self.station_store = StationStore(application_data_directory())
        self._configure_style()
        self._show_builder()

    def _configure_style(self) -> None:
        style = ttk.Style(self)
        if "vista" in style.theme_names():
            style.theme_use("vista")
        for name in ("TkDefaultFont", "TkTextFont", "TkMenuFont", "TkHeadingFont"):
            tkfont.nametofont(name).configure(family="Segoe UI", size=10)
        style.configure("Title.TLabel", font=("Segoe UI Semibold", 20))
        style.configure("Hint.TLabel", foreground="#596273")
        style.configure("Accent.TButton", font=("Segoe UI Semibold", 10), padding=(16, 9))

    def _clear(self) -> ttk.Frame:
        for child in self.winfo_children():
            child.destroy()
        frame = ttk.Frame(self, padding=28)
        frame.pack(fill="both", expand=True)
        return frame

    def _header(self, frame: ttk.Frame, title: str, subtitle: str, action: str, command) -> None:
        header = ttk.Frame(frame)
        header.pack(fill="x", pady=(0, 25))
        ttk.Label(header, text=title, style="Title.TLabel").pack(anchor="w")
        ttk.Label(header, text=subtitle, style="Hint.TLabel").pack(anchor="w", pady=(4, 0))
        ttk.Button(header, text=action, command=command).pack(side="right", anchor="n", pady=(0, 10))

    def _show_builder(self) -> None:
        frame = self._clear()
        self._header(frame, "Paket Oluştur", "Doğrulanmış ve kuruluma hazır paketler üretin.",
                     "Ön Ayar Yönetimi", self._show_presets)
        form = ttk.LabelFrame(frame, text="Paket bilgileri", padding=20)
        form.pack(fill="x")
        software = tk.StringVar(value=Software.SYY.value)
        aircraft = tk.StringVar(value=Aircraft.ANKA.value)
        bin_path = tk.StringVar()
        output_path = tk.StringVar()
        output_station = tk.StringVar(value="Tümü")
        config_profile = tk.StringVar(value=PRESET_PROFILES[0])

        ttk.Label(form, text="Yazılım").grid(row=0, column=0, sticky="w", padx=(0, 16), pady=9)
        software_box = ttk.Combobox(form, textvariable=software, values=[x.value for x in Software], state="readonly")
        software_box.grid(row=0, column=1, sticky="ew", pady=9)
        ttk.Label(form, text="Hava aracı").grid(row=1, column=0, sticky="w", padx=(0, 16), pady=9)
        aircraft_box = ttk.Combobox(form, textvariable=aircraft, values=[x.value for x in Aircraft], state="disabled")
        aircraft_box.grid(row=1, column=1, sticky="ew", pady=9)
        ttk.Label(form, text="Bin klasörü").grid(row=2, column=0, sticky="w", padx=(0, 16), pady=9)
        ttk.Entry(form, textvariable=bin_path, state="readonly").grid(row=2, column=1, sticky="ew", pady=9)
        ttk.Button(form, text="Seç…", command=lambda: bin_path.set(filedialog.askdirectory() or bin_path.get())).grid(row=2, column=2, padx=(10, 0), pady=9)
        ttk.Label(form, text="Çıktı dizini").grid(row=3, column=0, sticky="w", padx=(0, 16), pady=9)
        ttk.Entry(form, textvariable=output_path, state="readonly").grid(row=3, column=1, sticky="ew", pady=9)
        ttk.Button(form, text="Seç…", command=lambda: output_path.set(filedialog.askdirectory() or output_path.get())).grid(row=3, column=2, padx=(10, 0), pady=9)
        ttk.Label(form, text="Üretilecek YKİ").grid(row=4, column=0, sticky="w", padx=(0, 16), pady=9)
        station_box = ttk.Combobox(form, textvariable=output_station, state="readonly")
        station_box.grid(row=4, column=1, sticky="ew", pady=9)
        ttk.Label(form, text="Config profili").grid(row=5, column=0, sticky="w", padx=(0, 16), pady=9)
        config_profile_box = ttk.Combobox(form, textvariable=config_profile, values=PRESET_PROFILES, state="readonly")
        config_profile_box.grid(row=5, column=1, sticky="ew", pady=9)
        form.columnconfigure(1, weight=1)

        def active_profile() -> str | None:
            if software.get() == Software.AKY.value:
                return "ANKA3" if aircraft.get() == Aircraft.ANKA3.value else None
            return "ANKA3" if config_profile.get() == "ANKA3" else None

        def refresh_outputs(*_) -> None:
            choices = output_stations(Software(software.get()), self.station_store.list(), active_profile())
            station_box.configure(values=("Tümü",) + choices)
            output_station.set("Tümü")

        def software_changed(*_) -> None:
            is_aky = software.get() == Software.AKY.value
            aircraft_box.configure(state="readonly" if is_aky else "disabled")
            config_profile_box.configure(state="disabled" if is_aky else "readonly")
            config_profile.set("ANKA3" if is_aky and aircraft.get() == Aircraft.ANKA3.value else PRESET_PROFILES[0])
            refresh_outputs()
        software.trace_add("write", software_changed)
        aircraft.trace_add("write", lambda *_: software_changed() if software.get() == Software.AKY.value else None)
        config_profile.trace_add("write", refresh_outputs)
        software_changed()
        status = tk.StringVar(value="Hazır")
        progress = ttk.Progressbar(frame, mode="indeterminate")

        def build() -> None:
            if not bin_path.get() or not output_path.get():
                messagebox.showwarning("Eksik bilgi", "Bin klasörünü ve çıktı dizinini seçin.")
                return
            button.configure(state="disabled")
            status.set("Paketler hazırlanıyor…")
            progress.pack(fill="x", pady=(16, 0), before=footer)
            progress.start(12)
            profile_key = active_profile()
            choices = output_stations(Software(software.get()), self.station_store.list(), profile_key)
            selected = choices if output_station.get() == "Tümü" else (output_station.get(),)
            create_zip = messagebox.askyesno("ZIP oluşturulsun mu?", "Normal klasörlere ek olarak ZIP çıktıları da oluşturulsun mu?")
            request = BuildRequest(Software(software.get()), Path(bin_path.get()), Path(output_path.get()),
                                   Aircraft(aircraft.get()) if software.get() == Software.AKY.value else None,
                                   selected, create_zip, profile_key)
            def worker() -> None:
                try:
                    outputs = PackageBuilder(self.store, self.station_store.list()).build(request)
                except (PackageError, OSError) as exc:
                    self.after(0, lambda: messagebox.showerror("Paket oluşturulamadı", str(exc)))
                    self.after(0, lambda: status.set("Hata oluştu"))
                else:
                    self.after(0, lambda: messagebox.showinfo("Tamamlandı", f"{len(outputs)} paket oluşturuldu."))
                    self.after(0, lambda: status.set("Paketler başarıyla oluşturuldu"))
                finally:
                    self.after(0, progress.stop)
                    self.after(0, progress.pack_forget)
                    self.after(0, lambda: button.configure(state="normal"))
            threading.Thread(target=worker, daemon=True).start()

        footer = ttk.Frame(frame)
        footer.pack(fill="x", pady=22)
        ttk.Label(footer, textvariable=status, style="Hint.TLabel").pack(side="left")
        button = ttk.Button(footer, text="Paketleri Oluştur", style="Accent.TButton", command=build)
        button.pack(side="right")

    def _show_presets(self) -> None:
        frame = self._clear()
        self._header(frame, "Ön Ayar Yönetimi", "Config klasörlerini yazılım ve YKİ bazında yönetin.",
                     "Paket Oluştur", self._show_builder)
        software = tk.StringVar(value=Software.SYY.value)
        station = tk.StringVar()
        profile = tk.StringVar(value=PRESET_PROFILES[0])
        controls = ttk.Frame(frame)
        controls.pack(fill="x", pady=(0, 15))
        ttk.Label(controls, text="Yazılım").grid(row=0, column=0, sticky="w", pady=5)
        ttk.Combobox(controls, textvariable=software, values=[x.value for x in Software], state="readonly", width=14).grid(row=0, column=1, sticky="w", padx=(8, 24), pady=5)
        ttk.Label(controls, text="YKİ").grid(row=0, column=2, sticky="w", pady=5)
        station_box = ttk.Combobox(controls, textvariable=station, state="readonly", width=14)
        station_box.grid(row=0, column=3, sticky="w", padx=8, pady=5)
        ttk.Label(controls, text="Config profili").grid(row=1, column=0, sticky="w", pady=5)
        profile_box = ttk.Combobox(controls, textvariable=profile, values=PRESET_PROFILES, state="readonly", width=18)
        profile_box.grid(row=1, column=1, sticky="w", padx=(8, 24), pady=5)
        tree = ttk.Treeview(frame, columns=("software", "profile", "station", "path"), show="headings", height=12)
        for column, title, width in (("software", "Yazılım", 70), ("profile", "Profil", 120), ("station", "YKİ", 90), ("path", "Kalıcı konum", 390)):
            tree.heading(column, text=title)
            tree.column(column, width=width, anchor="w")
        tree.pack(fill="both", expand=True)

        def refresh() -> None:
            tree.delete(*tree.get_children())
            entries = self.store.list()
            for sw in Software:
                for current_profile in PRESET_PROFILES:
                    key_profile = "ANKA3" if current_profile == "ANKA3" else None
                    for st in output_stations(sw, self.station_store.list(), key_profile):
                        key = "/".join(part for part in (sw.value, key_profile, st) if part)
                        path = entries.get(key)
                        tree.insert("", "end", values=(sw.value, current_profile or "—", st, str(path) if path and path.is_dir() else "— Eksik —"))

        def save() -> None:
            source = filedialog.askdirectory(title="Config klasörünü seçin")
            if not source:
                return
            try:
                selected_profile = "ANKA3" if profile.get() == "ANKA3" else None
                self.store.save(Software(software.get()), station.get(), Path(source), selected_profile)
            except (PackageError, OSError) as exc:
                messagebox.showerror("Ön ayar kaydedilemedi", str(exc))
            else:
                refresh()
                messagebox.showinfo("Kaydedildi", "Ön ayar kalıcı veri alanına kopyalandı.")

        ttk.Button(controls, text="YKİ Ayarları", command=self._show_settings).grid(row=1, column=2, padx=(0, 8), pady=5)
        ttk.Button(controls, text="Yükle / Güncelle…", style="Accent.TButton", command=save).grid(row=1, column=3, sticky="e", padx=8, pady=5)
        def refresh_station_choices(*_) -> None:
            selected_profile = "ANKA3" if profile.get() == "ANKA3" else None
            choices = output_stations(Software(software.get()), self.station_store.list(), selected_profile)
            station_box.configure(values=choices)
            station.set(choices[0])
        software.trace_add("write", refresh_station_choices)
        profile.trace_add("write", refresh_station_choices)
        refresh_station_choices()
        refresh()

    def _show_settings(self) -> None:
        frame = self._clear()
        self._header(frame, "YKİ Ayarları", "Yeni istasyonları merkezi YKİ listesine ekleyin.",
                     "Ön Ayar Yönetimi", self._show_presets)
        value = tk.StringVar()
        form = ttk.LabelFrame(frame, text="Yeni YKİ", padding=20)
        form.pack(fill="x")
        ttk.Label(form, text="YKİ adı").grid(row=0, column=0, padx=(0, 12))
        entry = ttk.Entry(form, textvariable=value)
        entry.grid(row=0, column=1, sticky="ew")
        form.columnconfigure(1, weight=1)
        listing = tk.StringVar()
        ttk.Label(frame, textvariable=listing, style="Hint.TLabel", wraplength=680).pack(fill="x", pady=20)

        def refresh() -> None:
            listing.set("Kayıtlı YKİ'ler: " + ", ".join(self.station_store.list()))

        def add() -> None:
            try:
                self.station_store.add(value.get())
            except PackageError as exc:
                messagebox.showerror("YKİ eklenemedi", str(exc))
            else:
                value.set("")
                refresh()
                messagebox.showinfo("YKİ eklendi", "Yeni YKİ ön ayar ve paket ekranlarına eklendi.")

        ttk.Button(form, text="Ekle", style="Accent.TButton", command=add).grid(row=0, column=2, padx=(12, 0))
        entry.focus_set()
        refresh()


def main() -> None:
    Application().mainloop()


if __name__ == "__main__":
    main()
