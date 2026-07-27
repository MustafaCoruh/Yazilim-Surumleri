from __future__ import annotations

import os
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from .builder import PackageBuilder
from .errors import PackageError
from .models import STATIONS, Aircraft, BuildRequest, Software
from .presets import PresetStore


def application_data_directory() -> Path:
    base = Path(os.environ.get("LOCALAPPDATA", Path.home() / ".local" / "share"))
    return base / "TAI" / "YazilimSurumleri"


class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Yazılım Sürümleri")
        self.geometry("780x540")
        self.minsize(720, 500)
        self.store = PresetStore(application_data_directory())
        self._configure_style()
        self._show_builder()

    def _configure_style(self) -> None:
        style = ttk.Style(self)
        if "vista" in style.theme_names():
            style.theme_use("vista")
        style.configure("Title.TLabel", font=("Segoe UI Semibold", 20))
        style.configure("Hint.TLabel", foreground="#596273")
        style.configure("Accent.TButton", font=("Segoe UI Semibold", 10), padding=(16, 9))
        self.option_add("*Font", "Segoe UI 10")

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
        form.columnconfigure(1, weight=1)

        def software_changed(*_) -> None:
            aircraft_box.configure(state="readonly" if software.get() == Software.AKY.value else "disabled")
        software.trace_add("write", software_changed)
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
            request = BuildRequest(Software(software.get()), Path(bin_path.get()), Path(output_path.get()),
                                   Aircraft(aircraft.get()) if software.get() == Software.AKY.value else None)
            def worker() -> None:
                try:
                    outputs = PackageBuilder(self.store).build(request)
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
        station = tk.StringVar(value=STATIONS[0])
        controls = ttk.Frame(frame)
        controls.pack(fill="x", pady=(0, 15))
        ttk.Label(controls, text="Yazılım").pack(side="left")
        ttk.Combobox(controls, textvariable=software, values=[x.value for x in Software], state="readonly", width=12).pack(side="left", padx=(8, 24))
        ttk.Label(controls, text="YKİ").pack(side="left")
        ttk.Combobox(controls, textvariable=station, values=STATIONS, state="readonly", width=14).pack(side="left", padx=8)
        tree = ttk.Treeview(frame, columns=("software", "station", "path"), show="headings", height=12)
        for column, title, width in (("software", "Yazılım", 90), ("station", "YKİ", 110), ("path", "Kalıcı konum", 470)):
            tree.heading(column, text=title)
            tree.column(column, width=width, anchor="w")
        tree.pack(fill="both", expand=True)

        def refresh() -> None:
            tree.delete(*tree.get_children())
            entries = self.store.list()
            for sw in Software:
                for st in STATIONS:
                    path = entries.get(f"{sw.value}/{st}")
                    tree.insert("", "end", values=(sw.value, st, str(path) if path and path.is_dir() else "— Eksik —"))

        def save() -> None:
            source = filedialog.askdirectory(title="Config klasörünü seçin")
            if not source:
                return
            try:
                self.store.save(Software(software.get()), station.get(), Path(source))
            except (PackageError, OSError) as exc:
                messagebox.showerror("Ön ayar kaydedilemedi", str(exc))
            else:
                refresh()
                messagebox.showinfo("Kaydedildi", "Ön ayar kalıcı veri alanına kopyalandı.")

        ttk.Button(controls, text="Yükle / Güncelle…", style="Accent.TButton", command=save).pack(side="right")
        refresh()


def main() -> None:
    Application().mainloop()


if __name__ == "__main__":
    main()
