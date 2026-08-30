# Sürüm İstasyonu

Windows için SYY, DM ve AKY dağıtım paketlerini güvenli biçimde hazırlayan masaüstü uygulamasıdır.

## Uygulamayı çalıştırma

Depoyu VS Code ile açtıktan sonra en kolay yöntem depo kökündeki `calistir.bat` dosyasına çift tıklamaktır. Betik ilk çalıştırmada `.venv` ortamını oluşturur ve uygulamayı açar; ayrıca paket kurulumu gerekmez. Python 3.11 veya üstünün kurulu olması gerekir.

`.venv` klasörleri bilgisayara özeldir ve başka bilgisayara kopyalanmamalıdır. Betik taşınmış veya uyumsuz bir `.venv` algılarsa otomatik silip hedef bilgisayardaki Python ile yeniden oluşturur. `release\SurumIstasyonu\SurumIstasyonu.exe` mevcutsa Python kullanmadan doğrudan onu açar.

VS Code terminalinden çalıştırmak için:

```powershell
.\calistir.bat
```

Kaynak giriş dosyası depo kökündeki `yazilim_surumleri.py` dosyasıdır. Paketlenmiş uygulama `release\SurumIstasyonu` klasöründeki `SurumIstasyonu.exe` ile açılır.

## Kullanım

1. Uygulamayı açıp **Ön Ayar Yönetimi** ekranına geçin.
2. Her yazılım ve YKİ çifti için doğrudan config klasörünü **Yükle / Güncelle** ile seçin. Her yazılımda `ANKA / AKSUNGUR` ortak config grubu ile `ANKA3` config grubu ayrı saklanır. ANKA ve AKSUNGUR aynı config'i kullanır. ANKA3 config'leri her yazılım için ayrıca yüklenir. ANKA3 için SYY'de `SYKI1` ve `SYKI2` ayrı; DM ve AKY'de yalnızca ortak `SYKI1-2` ön ayarı bulunur. ANKA3 için MYKI ön ayarı gösterilmez ve üretilemez. Gerekli XML dosyaları ve alanları yükleme sırasında doğrulanır. Ön ayarlar `%LOCALAPPDATA%\TAI\YazilimSurumleri` altında kalıcı olarak tutulur; kaynak klasör sonradan gerekli değildir.
3. **Paket Oluştur** ekranında önce ANKA, AKSUNGUR veya ANKA3 hava aracını; ardından SYY, DM veya AKY yazılımını seçin. Hava aracı seçimi kullanılacak config grubunu otomatik belirler.
4. Üretilecek YKİ listesinden tek bir YKİ veya **Tümü** seçeneğini belirleyin.
5. Tam adı `bin_1.2.3` benzeri olan bin klasörünü ve boş bir çıktı konumunu seçip **Paketleri Oluştur** düğmesine basın.
6. Sorulduğunda normal çıktı klasörlerine ek olarak ZIP dosyaları isteyip istemediğinizi belirtin.

SYY her YKİ için ayrı paket üretir. DM ve AKY, tek `SYKI1-2` config ön ayarından ortak `SYKI1-2` paketi ve MYKI'lar için ayrı paketler üretir. Çıktılar her durumda normal klasördür; ZIP seçilirse aynı klasörlerin `.zip` kopyaları da oluşturulur. Eksik ön ayar ve mevcut klasör/ZIP çıktısı varsa işlem başlamadan açık bir hata gösterilir; mevcut çıktılar ezilmez.

SYY, DM ve AKY ön ayarları yüklenirken **Hava aracı grubu** alanından `ANKA / AKSUNGUR` veya `ANKA3` seçilir. ANKA3 grubu seçildiğinde SYY için `SYKI1` ve `SYKI2`, DM ve AKY için yalnızca `SYKI1-2` bulunur. Paket ekranında ANKA3 hava aracı seçildiğinde yalnızca ilgili yazılımın ANKA3 grubuna yüklenen config kullanılır; ANKA/AKSUNGUR config'ine geri düşülmez.

SYY `GainsFilePath` değeri XML içinde `value` niteliğinde, doğrudan metin olarak veya iç içe `<value>` öğesinde bulunabilir. Değer içinde `GainsParamsTable_MessageTable_<sürüm>.csv` dosya adı bulunursa gerçek dosya adı korunarak paket yolu güncellenir. Bu kalıp bulunamazsa config yüklenirken uyarı verilmez ve paket üretiminde `GainsFilePath` değiştirilmeden bırakılır.

Config dosyası, beklenen XML alanı veya seçilen bir ön ayar bulunamazsa işlem tamamen iptal edilmez. Uygulama bulunan paketleri üretmeye devam eder, bulunamayan alanı değiştirmeden veya eksik ön ayara ait çıktıyı atlayarak kullanıcıya toplu **Uyarılar** penceresi gösterir. Gains dosya kalıbının bulunamaması sessizce atlanır. Geçersiz bin adı ve mevcut çıktı çakışması gibi güvenli üretimi imkânsız kılan durumlar hata olarak kalır.

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

Testleri çalıştırıp ikonlu Windows programını üretmek için:

```bat
build_windows.bat
```

Bu yöntem yalnızca Komut İstemi (`cmd.exe`) ve Python gerektirir; PowerShell gerekmez. PowerShell bulunan bilgisayarlarda alternatif olarak `.\build_windows.ps1` kullanılabilir.

Program `release\SurumIstasyonu\SurumIstasyonu.exe` altında oluşur. Aynı klasördeki `_internal` dizini Python çalışma zamanı ve Tk kitaplıklarını içerdiğinden silinmemeli veya EXE'den ayrılmamalıdır. Kendi bilgisayarınıza `%LOCALAPPDATA%\Programs\SurumIstasyonu` altında kurmak ve masaüstüne ikonlu **Sürüm İstasyonu** kısayolu eklemek için:

```bat
masaustune_kur.bat
```

PowerShell olmayan bilgisayarlarda da bu betik program klasörünü kullanıcı alanına kurar ve Windows Script Host üzerinden masaüstü kısayolu oluşturur. PowerShell bulunan bilgisayarlarda `.\masaustune_kur.ps1` alternatif olarak aynı kurulumu yapar.

Elle PyInstaller çalıştırmak için:

```powershell
pip install -e .[dev]
python -m package_builder.icon assets
pyinstaller --noconfirm --clean --onedir --noupx --windowed --name SurumIstasyonu --icon "assets\app_icon.ico" yazilim_surumleri.py
```

Geçici build çıktısı `dist\SurumIstasyonu` konumunda oluşur. GitHub Actions içindeki **Windows** iş akışı da her gönderimde testleri Windows üzerinde çalıştırır ve indirilebilir `SurumIstasyonu-windows` artefaktını üretir.

İkonun düzenlenebilir kaynağı `assets\app_icon.svg` dosyasıdır. PR sistemleri binary dosyaları kabul etmediği için PNG ve ICO Git'e eklenmez; build sırasında metin tabanlı gömülü ikon verisinden otomatik üretilir.

## Başka bilgisayara aktarma

Hedef bilgisayarda Python gerektirmeyen önerilen yöntem `release\SurumIstasyonu` klasörünü içeriğiyle birlikte aktarıp içindeki `SurumIstasyonu.exe` dosyasını çalıştırmaktır. `_internal` klasörü mutlaka EXE'nin yanında kalmalıdır. Kaynak klasörün tamamı aktarılacaksa `.venv`, `build` ve `dist` klasörlerini aktarmayın. Kaynak kodu `calistir.bat` ile çalıştırmak için hedef bilgisayarda Python 3.11 veya üstü kurulu olmalıdır.

`No Python at ...` hatası, başka bilgisayarda oluşturulmuş `.venv` klasörünün taşındığını gösterir. `Failed to start embedded Python interpreter` hatası ise eski tek-dosyalık build'in geçici dizinde gömülü Python'u başlatamadığını gösterir. Güncel build klasörlü ve sıkıştırmasız üretildiğinden kurumsal güvenlik/antivirüs ortamlarında daha güvenilirdir. Eski `dist`, `build` ve `release` çıktılarını kullanmayın; `build_windows.bat` ile yeniden üretin.
