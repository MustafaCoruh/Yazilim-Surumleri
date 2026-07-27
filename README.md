# Yazılım Sürümleri

Windows için SYY, DM ve AKY dağıtım paketlerini güvenli biçimde hazırlayan masaüstü uygulamasıdır.

## Uygulamayı çalıştırma

Depoyu VS Code ile açtıktan sonra en kolay yöntem depo kökündeki `calistir.bat` dosyasına çift tıklamaktır. Betik ilk çalıştırmada `.venv` ortamını oluşturur ve uygulamayı açar; ayrıca paket kurulumu gerekmez. Python 3.11 veya üstünün kurulu olması gerekir.

Daha önce oluşturulmuş `.venv` farklı veya eski bir Python sürümüne aitse klasörü silip `calistir.bat` dosyasını yeniden çalıştırın.

VS Code terminalinden çalıştırmak için:

```powershell
.\calistir.bat
```

Kaynak giriş dosyası depo kökündeki `yazilim_surumleri.py` dosyasıdır. Paketlenmiş uygulamada çalıştırılacak dosya `YazilimSurumleri.exe` olur.

## Kullanım

1. Uygulamayı açıp **Ön Ayar Yönetimi** ekranına geçin.
2. Her yazılım ve YKİ çifti için doğrudan config klasörünü **Yükle / Güncelle** ile seçin. DM ve AKY için SYKI config'i tek `SYKI1-2` ön ayarı olarak yüklenir. Gerekli XML dosyaları ve alanları yükleme sırasında doğrulanır. Ön ayarlar `%LOCALAPPDATA%\TAI\YazilimSurumleri` altında kalıcı olarak tutulur; kaynak klasör sonradan gerekli değildir.
3. **Paket Oluştur** ekranında SYY, DM veya AKY seçin. AKY için ayrıca ANKA, AKSUNGUR ya da ANKA3 seçin.
4. Üretilecek YKİ listesinden tek bir YKİ veya **Tümü** seçeneğini belirleyin.
5. Tam adı `bin_1.2.3` benzeri olan bin klasörünü ve boş bir çıktı konumunu seçip **Paketleri Oluştur** düğmesine basın.
6. Sorulduğunda normal çıktı klasörlerine ek olarak ZIP dosyaları isteyip istemediğinizi belirtin.

SYY her YKİ için ayrı paket üretir. DM ve AKY, tek `SYKI1-2` config ön ayarından ortak `SYKI1-2` paketi ve MYKI'lar için ayrı paketler üretir. Çıktılar her durumda normal klasördür; ZIP seçilirse aynı klasörlerin `.zip` kopyaları da oluşturulur. Eksik ön ayar ve mevcut klasör/ZIP çıktısı varsa işlem başlamadan açık bir hata gösterilir; mevcut çıktılar ezilmez.

## Yeni YKİ ekleme

**Ön Ayar Yönetimi → YKİ Ayarları** ekranında yeni YKİ adını girip **Ekle** düğmesine basın. Yeni YKİ, SYY/DM/AKY ön ayar listelerine ve üretim seçeneklerine otomatik eklenir. `SYKI`, `MYK19` ve sistemin ortak çıktı adı olan `SYKI1-2` yeni YKİ adı olarak kabul edilmez.

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
