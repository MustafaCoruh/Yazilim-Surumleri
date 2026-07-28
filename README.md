# Sürüm İstasyonu

Windows için SYY, DM ve AKY dağıtım paketlerini güvenli biçimde hazırlayan masaüstü uygulamasıdır.

## Uygulamayı çalıştırma

Depoyu VS Code ile açtıktan sonra en kolay yöntem depo kökündeki `calistir.bat` dosyasına çift tıklamaktır. Betik ilk çalıştırmada `.venv` ortamını oluşturur ve uygulamayı açar; ayrıca paket kurulumu gerekmez. Python 3.11 veya üstünün kurulu olması gerekir.

`.venv` klasörleri bilgisayara özeldir ve başka bilgisayara kopyalanmamalıdır. Betik taşınmış veya uyumsuz bir `.venv` algılarsa otomatik silip hedef bilgisayardaki Python ile yeniden oluşturur. `release\SurumIstasyonu.exe` mevcutsa Python kullanmadan doğrudan onu açar.

VS Code terminalinden çalıştırmak için:

```powershell
.\calistir.bat
```

Kaynak giriş dosyası depo kökündeki `yazilim_surumleri.py` dosyasıdır. Paketlenmiş uygulamada çalıştırılacak tek dosya `SurumIstasyonu.exe` olur.

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

## Windows programı ve masaüstü kısayolu

Testleri çalıştırıp ikonlu, tek dosyalık Windows programını üretmek için:

```powershell
.\build_windows.ps1
```

Program `release\SurumIstasyonu.exe` altında oluşur. Programı kullanıcıya yalnızca bu dosyayla teslim edebilirsiniz. Kendi bilgisayarınıza `%LOCALAPPDATA%\Programs\SurumIstasyonu` altında kurmak ve masaüstüne ikonlu **Sürüm İstasyonu** kısayolu eklemek için:

```powershell
.\masaustune_kur.ps1
```

Elle PyInstaller çalıştırmak için:

```powershell
pip install -e .[dev]
python -m package_builder.icon assets
pyinstaller --noconfirm --clean --onefile --windowed --name SurumIstasyonu --icon "assets\app_icon.ico" yazilim_surumleri.py
```

Geçici build çıktısı `dist\SurumIstasyonu.exe` konumunda oluşur. GitHub Actions içindeki **Windows** iş akışı da her gönderimde testleri Windows üzerinde çalıştırır ve indirilebilir `SurumIstasyonu-windows` artefaktını üretir.

İkonun düzenlenebilir kaynağı `assets\app_icon.svg` dosyasıdır. PR sistemleri binary dosyaları kabul etmediği için PNG ve ICO Git'e eklenmez; build sırasında metin tabanlı gömülü ikon verisinden otomatik üretilir.

## Başka bilgisayara aktarma

Hedef bilgisayarda Python gerektirmeyen önerilen yöntem yalnızca `release\SurumIstasyonu.exe` dosyasını aktarıp çalıştırmaktır. Kaynak klasörün tamamı aktarılacaksa `.venv`, `build` ve `dist` klasörlerini aktarmayın. Kaynak kodu `calistir.bat` ile çalıştırmak için hedef bilgisayarda Python 3.11 veya üstü kurulu olmalıdır.

`No Python at ...` hatası, başka bilgisayarda oluşturulmuş `.venv` klasörünün taşındığını gösterir. Güncel `calistir.bat` bu klasörü otomatik yeniler. Python kurmak istemiyorsanız geliştirme bilgisayarında `build_windows.ps1` çalıştırıp oluşan `release\SurumIstasyonu.exe` dosyasını hedef bilgisayara yeniden aktarın.
