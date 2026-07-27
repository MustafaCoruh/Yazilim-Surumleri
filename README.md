# Yazılım Sürümleri

Windows için SYY, DM ve AKY dağıtım paketlerini güvenli biçimde hazırlayan masaüstü uygulamasıdır.

## Uygulamayı çalıştırma

Depoyu VS Code ile açtıktan sonra en kolay yöntem depo kökündeki `calistir.bat` dosyasına çift tıklamaktır. Betik ilk çalıştırmada `.venv` ortamını oluşturur ve uygulamayı açar; ayrıca paket kurulumu gerekmez. Python 3.11 veya üstünün kurulu olması gerekir.

VS Code terminalinden çalıştırmak için:

```powershell
.\calistir.bat
```

Kaynak giriş dosyası depo kökündeki `yazilim_surumleri.py` dosyasıdır. Paketlenmiş uygulamada çalıştırılacak dosya `YazilimSurumleri.exe` olur.

## Kullanım

1. Uygulamayı açıp **Ön Ayar Yönetimi** ekranına geçin.
2. Her yazılım ve YKİ çifti için config klasörünü **Yükle / Güncelle** ile kaydedin. Gerekli XML dosyaları ve alanları yükleme sırasında doğrulanır. Ön ayarlar `%LOCALAPPDATA%\TAI\YazilimSurumleri` altında kalıcı olarak tutulur; kaynak klasör sonradan gerekli değildir.
3. **Paket Oluştur** ekranında SYY, DM veya AKY seçin. AKY için ayrıca ANKA, AKSUNGUR ya da ANKA3 seçin.
4. Tam adı `bin_1.2.3` benzeri olan bin klasörünü ve boş bir çıktı konumunu seçip **Paketleri Oluştur** düğmesine basın.

SYY beş YKİ için ayrı paket üretir. DM ve AKY, SYKI1/SYKI2 için ortak `SYKI1-2` paketi ve üç MYKI için ayrı paket üretir. Ortak pakette SYKI1 ve SYKI2 ön ayarlarının içerikleri aynı olmalıdır. Eksik ön ayar ve mevcut çıktı varsa işlem başlamadan açık bir hata gösterilir; mevcut paketler ezilmez.

## Geliştirme ve test

Python 3.11 veya üstü gereklidir.

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e .[dev]
pytest
python -m package_builder
```

## Windows dağıtımı

Testleri çalıştırıp Windows paketini ve ZIP dosyasını tek komutla üretmek için:

```powershell
.\build_windows.ps1
```

ZIP çıktısı `release\YazilimSurumleri-windows.zip` altında oluşur. Elle PyInstaller çalıştırmak için:

```powershell
pip install -e .[dev]
pyinstaller --noconfirm --clean --windowed --name YazilimSurumleri yazilim_surumleri.py
```

Çalıştırılabilir uygulama `dist\YazilimSurumleri\YazilimSurumleri.exe` konumunda oluşur. Dağıtım için `dist\YazilimSurumleri` klasörünü bütünüyle teslim edin.
GitHub Actions içindeki **Windows** iş akışı her gönderimde testleri Windows üzerinde çalıştırır ve aynı klasörü indirilebilir `YazilimSurumleri-windows` artefaktı olarak üretir.
