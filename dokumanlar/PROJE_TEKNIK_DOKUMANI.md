# Sürüm İstasyonu – Proje ve Teknik Çalışma Dokümanı

## 1. Dokümanın amacı

Bu doküman Sürüm İstasyonu uygulamasının hangi ihtiyacı karşıladığını, geliştirilen bileşenleri, iş kurallarını, paket üretim sürecini, XML değişikliklerini, veri saklama yöntemini, güvenlik önlemlerini, test kapsamını ve Windows dağıtım modelini açıklar.

## 2. Uygulamanın amacı

Sürüm İstasyonu; SYY, DM ve AKY yazılımlarının dağıtım paketlerini Windows ortamında standart, tekrarlanabilir ve güvenli biçimde hazırlamak için geliştirilmiş bir masaüstü uygulamasıdır.

Uygulama aşağıdaki manuel işlemleri otomatikleştirir:

- Hava aracı, yazılım ve YKİ seçimi.
- `bin_<sürüm>` klasör adının doğrulanması ve sürümün çıkarılması.
- Daha önce yüklenmiş config ön ayarının seçilen pakete kopyalanması.
- Yazılıma göre izin verilen XML alanlarının güncellenmesi.
- Standart klasör çıktısı ve isteğe bağlı ZIP oluşturulması.
- Mevcut çıktıların yanlışlıkla ezilmesinin engellenmesi.
- Eksik config veya XML alanlarının kullanıcıya uyarı olarak bildirilmesi.

## 3. Temel kavramlar

### 3.1 Yazılımlar

- SYY
- DM
- AKY

### 3.2 Hava araçları

- ANKA
- AKSUNGUR
- ANKA3

### 3.3 Config grupları

ANKA ve AKSUNGUR aynı config grubunu kullanır. ANKA3 config dosyaları diğer iki hava aracından farklıdır ve her yazılım için ayrıca yüklenir.

- `ANKA / AKSUNGUR`
- `ANKA3`

### 3.4 Varsayılan YKİ listesi

- SYKI1
- SYKI2
- MYKI15
- MYKI19
- MYKI20

Yeni YKİ değerleri uygulama içindeki YKİ Ayarları ekranından eklenebilir. `SYKI`, `MYK19` ve sistemin ortak çıktı anahtarı olan `SYKI1-2` yeni YKİ adı olarak kullanılamaz.

## 4. Çıktı iş kuralları

### 4.1 ANKA ve AKSUNGUR

SYY için SYKI1 ve SYKI2 ayrı; MYKI15, MYKI19 ve MYKI20 ayrı paketlerdir. Sonradan eklenen YKİ değerleri de SYY için ayrı paket olur.

DM ve AKY için SYKI1 ile SYKI2 tek `SYKI1-2` paketinde ele alınır. MYKI15, MYKI19 ve MYKI20 ayrı paketlerdir. Sonradan eklenen YKİ değerleri ayrı paket olur.

### 4.2 ANKA3

SYY için yalnızca SYKI1 ve SYKI2 desteklenir ve ayrı paketler üretilir.

DM ve AKY için yalnızca ortak `SYKI1-2` desteklenir. ANKA3 için MYKI paketleri ve sonradan eklenen YKİ değerleri desteklenmez.

## 5. Paket adlandırma

- SYY: `SYY_<SÜRÜM>_<YKİ>`
- DM: `DM_<SÜRÜM>_<YKİ>`
- AKY: `AKY_<SÜRÜM>_<HAVA_ARACI>_<YKİ>`

Örnekler:

- `SYY_2.5.1_SYKI1`
- `DM_2.5.1_SYKI1-2`
- `AKY_2.5.1_ANKA3_SYKI1-2`

## 6. Bin klasörü doğrulaması

Seçilen klasör adı tam olarak `bin_<noktayla ayrılmış sayısal sürüm>` biçiminde olmalıdır.

Geçerli örnekler:

- `bin_1`
- `bin_1.2`
- `bin_1.2.3`

Geçersiz örnekler:

- `Bin_1.2`
- `bin_1.`
- `bin_1_2`
- `bin_v1.2`
- `xbin_1.2`

## 7. Config ön ayar sistemi

Config klasörleri Ön Ayar Yönetimi ekranından doğrudan seçilir. Uygulama kaynak klasöre bağlantı saklamak yerine klasörün tamamını kalıcı uygulama veri alanına kopyalar.

Windows veri alanı:

`%LOCALAPPDATA%\TAI\YazilimSurumleri`

Ön ayarlar yazılım, config grubu ve YKİ birleşimine göre saklanır. ANKA3 ön ayarları standart ANKA/AKSUNGUR ön ayarlarına geri düşmez.

## 8. Paket üretim akışı

1. Bin klasörü ve sürüm doğrulanır.
2. Hava aracı ve yazılıma göre desteklenen YKİ listesi hesaplanır.
3. Kullanıcının tek YKİ veya Tümü seçimi değerlendirilir.
4. İlgili config ön ayarları bulunur.
5. Eksik ön ayarlar uyarıya dönüştürülür ve ilgili çıktılar atlanır.
6. Mevcut klasör ve ZIP çakışmaları kontrol edilir.
7. Çıktı dizininde geçici hazırlama klasörü oluşturulur.
8. Bin klasörü tüm içeriğiyle paket içine kopyalanır.
9. Config ön ayarı paket içine `config` adıyla kopyalanır.
10. XML dönüşümleri uygulanır.
11. Kullanıcı istemişse ZIP hazırlanır.
12. Tamamlanan paketler hedef dizine taşınır.
13. Hata halinde bu işlemde oluşturulan yarım çıktılar temizlenir.

## 9. XML dosyalarının belirlenmesi

Config içindeki `UserConfiguration` ve `AppSettings` dosyaları uzantılı veya uzantısız olabilir. Aday dosyalar adlarına göre bulunur ve XML ayrıştırıcısıyla gerçekten XML oldukları doğrulanır.

Metinsel genel arama-değiştirme yapılmaz. XML öğeleri `xml.etree.ElementTree` ile ayrıştırılır ve yalnızca izin verilen alanlar güncellenir.

## 10. SYY XML değişiklikleri

### 10.1 UserConfiguration

- `ConfigFileLocation` → `C:\Program Files (x86)\TAI\<çıktı>\config\DataFrameworkConfig.xml`
- `ProgramFileLocation` → `C:\Program Files (x86)\TAI\<çıktı>\<bin-klasörü>`

### 10.2 AppSettings

- `GainsFilePath`
- `UILayoutsFolder`
- `HandoverSettingsFilePath`

`GainsFilePath` içinde `GainsParamsTable_MessageTable_<sürüm>.csv` kalıbı bulunursa dosya adı aynen korunur ve yalnızca ana paket yolu değiştirilir. Kalıp bulunamazsa config yüklemesi sırasında uyarı gösterilmez ve paket üretiminde mevcut `GainsFilePath` değiştirilmeden bırakılır.

`UILayoutsFolder`, `<çıktı>\config\UILayoutsFolder`; `HandoverSettingsFilePath`, `<çıktı>\config` ile biter.

## 11. DM XML değişiklikleri

UserConfiguration içinde:

- `ConfigFileLocation` → `<çıktı>\config\DataFrameworkConfig.xml`
- `ProgramFileLocation` → `<çıktı>\<bin-klasörü>`
- `LogFilesLocation` → `<çıktı>\Logs`

Tüm yollar `C:\Program Files (x86)\TAI\` kökü altındadır.

## 12. AKY XML değişiklikleri

UserConfiguration içinde:

- `ConfigFileLocation` → `<çıktı>\config\DataFrameworkConfig.xml`
- `ProgramFileLocation` → `<çıktı>\<bin-klasörü>`
- `LogFilesLocation` → `<çıktı>\LogAKY`

AppSettings içindeki `BlockType` eşlemesi:

- ANKA → `OPERATIF`
- AKSUNGUR → `YFYK`
- ANKA3 → `ANKA3`

## 13. Uyarı ve hata politikası

İşlemi durdurmadan uyarı üreten durumlar:

- UserConfiguration veya AppSettings dosyasının bulunamaması.
- Beklenen XML alanının bulunamaması veya tekrarlı olması.
- Seçilen bazı YKİ ön ayarlarının eksik olması.

Bu durumlarda bulunamayan alan değiştirilmez veya eksik ön ayara ait çıktı atlanır; diğer paketler üretilmeye devam eder.

İşlemi durduran durumlar:

- Geçersiz bin klasörü adı.
- Bin klasörünün bulunmaması.
- Hava aracının seçilmemesi.
- Desteklenmeyen veya tekrarlı YKİ seçimi.
- Mevcut çıktı klasörü veya ZIP çakışması.
- Dosya kopyalama, okuma veya yazma hatası.
- Bozuk kalıcı ayar indeksi.

## 14. Windows dağıtım modeli

Uygulama PyInstaller ile `--onedir --noupx --windowed` seçenekleri kullanılarak hazırlanır. Tek dosyalık dağıtım yerine klasörlü dağıtım seçilmesinin nedeni kurumsal güvenlik ve antivirüs ortamlarında gömülü Python başlatma sorunlarını azaltmaktır.

Dağıtım yapısı:

`release\SurumIstasyonu\SurumIstasyonu.exe`

EXE yanındaki `_internal` klasörü Python, Tcl/Tk ve diğer çalışma zamanı dosyalarını içerir ve EXE'den ayrılmamalıdır.

## 15. Build ve kurulum araçları

- `build_windows.bat`: PowerShell gerektirmeden test ve Windows build işlemini yapar.
- `build_windows.ps1`: Aynı işlemin PowerShell karşılığıdır.
- `calistir.bat`: Kaynaktan çalıştırır veya hazır release varsa onu açar.
- `masaustune_kur.bat`: Program klasörünü LocalAppData altına kurar ve masaüstü kısayolu oluşturur.
- `masaustune_kur.ps1`: PowerShell ile masaüstü kurulumu yapar.
- GitHub Actions Windows iş akışı: Testleri çalıştırır ve indirilebilir Windows artefaktı oluşturur.

## 16. Test kapsamı

Otomatik testlerde aşağıdaki alanlar kapsanır:

- Geçerli ve geçersiz bin adları.
- Çıktı adları ve yazılıma özgü yollar.
- ANKA/AKSUNGUR ortak config kullanımı.
- ANKA3 ayrı config kullanımı ve YKİ sınırlamaları.
- DM/AKY `SYKI1-2` davranışı.
- AKY BlockType eşlemesi.
- Gains dosya adının korunması ve bulunamadığında sessizce atlanması.
- Yalnızca izin verilen XML alanlarının değiştirilmesi.
- Eksik ve tekrarlı XML öğelerinde uyarıyla devam.
- Eksik ön ayar ve çıktı çakışması.
- Normal klasör ve isteğe bağlı ZIP üretimi.
- Dinamik YKİ ekleme.
- XML encoding, BOM ve uzantısız dosya desteği.
- Windows build/kurulum betiklerinin beklenen komutları içermesi.

## 17. Bilinen operasyonel noktalar

- Gerçek config klasörleriyle kabul testi yapılmalıdır.
- SYY ve DM çıktı adlarında hava aracı bulunmadığından aynı sürüm/YKİ için farklı hava aracı paketleri aynı dizinde ad çakışması oluşturabilir.
- Uyarıyla üretilen paketlerde atlanan XML alanları hedef uygulamada ayrıca kontrol edilmelidir.
- Yeni Windows build alındığında eski `build`, `dist` ve `release` çıktıları kullanılmamalıdır.

## 18. Kaynak kod organizasyonu

- `package_builder/models.py`: Yazılım, hava aracı, YKİ ve çıktı modeli.
- `package_builder/builder.py`: Dosya kopyalama, paketleme, ZIP ve güvenli üretim.
- `package_builder/presets.py`: Kalıcı config ön ayarları.
- `package_builder/settings.py`: Dinamik YKİ ayarları.
- `package_builder/xml_config.py`: XML doğrulama ve dönüşümler.
- `package_builder/ui.py`: Tkinter masaüstü arayüzü.
- `package_builder/errors.py`: Hata ve uyarı türleri.
- `package_builder/icon.py`: Build sırasında PNG/ICO üretimi.
- `tests/`: Birim ve geçici dizin tabanlı uçtan uca testler.

## 19. Sonuç

Sürüm İstasyonu; config ön ayarlarını kalıcı saklayan, hava aracı/yazılım/YKİ iş kurallarını merkezi yöneten, XML dönüşümlerini ayrıştırıcıyla uygulayan, güvenli klasör ve ZIP çıktıları üreten ve Windows üzerinde dağıtılabilen bir paketleme uygulamasıdır. Üretim kullanımına geçmeden önce gerçek SYY, DM ve AKY config örnekleriyle son kabul testinin tamamlanması önerilir.
