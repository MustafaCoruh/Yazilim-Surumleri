# Sürüm İstasyonu – Baştan Sona Ayrıntılı Kullanım Kılavuzu

## 1. Bu kılavuz kimler içindir?

Bu kılavuz daha önce uygulamayı hiç kullanmamış, Python veya yazılım geliştirme bilgisi olmayan bir kullanıcının Sürüm İstasyonu'nu kurup config ön ayarlarını yüklemesi ve paket oluşturması için hazırlanmıştır.

## 2. Size teslim edilmesi gerekenler

Normal kullanıcıya `SurumIstasyonu` adlı klasör teslim edilmelidir. Klasörde aşağıdakiler bulunur:

- `SurumIstasyonu.exe`
- `_internal` klasörü
- PyInstaller tarafından oluşturulan diğer dosyalar

Önemli: Yalnızca EXE dosyasını almayın. `_internal` klasörü EXE ile aynı klasörde kalmalıdır.

## 3. Uygulamayı başka bilgisayara aktarma

1. Geliştirme bilgisayarında `release\SurumIstasyonu` klasörünü bulun.
2. Klasöre sağ tıklayın.
3. Gönder → Sıkıştırılmış klasör seçeneğini seçin.
4. Oluşan ZIP dosyasını USB bellek, ağ paylaşımı veya kurumun izin verdiği yöntemle hedef bilgisayara aktarın.
5. Hedef bilgisayarda ZIP dosyasına sağ tıklayın.
6. Tümünü Ayıkla seçeneğini seçin.
7. Klasörü Masaüstü veya Belgeler gibi yazma izniniz olan bir konuma çıkartın.
8. ZIP içinden doğrudan çalıştırmayın.

## 4. Uygulamayı açma

1. Çıkartılan `SurumIstasyonu` klasörünü açın.
2. `SurumIstasyonu.exe` dosyasına çift tıklayın.
3. Windows güvenlik uyarısı gösterirse kurumunuzun güvenlik kurallarına göre Bilgi → Yine de çalıştır seçeneğini kullanın veya sistem yöneticisine başvurun.
4. Sürüm İstasyonu ana penceresi açılacaktır.

Hedef bilgisayarda Python veya PowerShell kurulması gerekmez.

## 5. İlk kullanım öncesi hazırlanacak klasörler

Paket oluşturmadan önce şunları hazırlayın:

- Paketlenecek `bin_<sürüm>` klasörü.
- İlgili hava aracı, yazılım ve YKİ'ye ait config klasörleri.
- Üretilen paketlerin yazılacağı boş veya düzenli bir çıktı dizini.

Bin klasörü örneği:

`bin_2.5.1`

Config klasörü seçerken `config` klasörünün kendisini seçmeniz gerekir; üst klasörü veya config içindeki tek bir XML dosyasını seçmeyin.

## 6. Config ön ayarlarının anlamı

Config ön ayarı, bir config klasörünün uygulamanın kalıcı veri alanına kopyalanmış halidir. Bir kez yüklendikten sonra paket oluştururken config klasörü tekrar sorulmaz.

İki hava aracı grubu vardır:

- ANKA / AKSUNGUR: Bu iki hava aracı aynı config'leri kullanır.
- ANKA3: Her yazılım için ayrı config kullanır.

## 7. Yüklenmesi gereken config listesi

### 7.1 ANKA / AKSUNGUR – SYY

- SYKI1
- SYKI2
- MYKI15
- MYKI19
- MYKI20

### 7.2 ANKA / AKSUNGUR – DM

- SYKI1-2
- MYKI15
- MYKI19
- MYKI20

### 7.3 ANKA / AKSUNGUR – AKY

- SYKI1-2
- MYKI15
- MYKI19
- MYKI20

### 7.4 ANKA3 – SYY

- SYKI1
- SYKI2

### 7.5 ANKA3 – DM

- Yalnızca SYKI1-2

### 7.6 ANKA3 – AKY

- Yalnızca SYKI1-2

ANKA3 için MYKI config'i yüklenmez ve MYKI paketi üretilmez.

## 8. Config ön ayarı yükleme

Her config için aşağıdaki adımları tekrarlayın:

1. Uygulamayı açın.
2. Sağ üstteki Ön Ayar Yönetimi düğmesine basın.
3. Hava aracı grubu alanından `ANKA / AKSUNGUR` veya `ANKA3` seçin.
4. Yazılım alanından SYY, DM veya AKY seçin.
5. YKİ alanından config'in ait olduğu değeri seçin.
6. Yükle / Güncelle düğmesine basın.
7. Açılan klasör penceresinde doğrudan config klasörünü seçin.
8. Klasör Seç düğmesine basın.
9. Kaydedildi mesajını kontrol edin.
10. Uyarıyla kaydedildi mesajı çıkarsa mesajı okuyun ve not alın. Config yine kaydedilmiştir.
11. Tabloda ilgili satırın Kalıcı konum alanında klasör yolu göründüğünü kontrol edin.

## 9. SYY GainsFilePath davranışı

SYY AppSettings.xml içinde `GainsParamsTable_MessageTable_<sürüm>.csv` biçiminde bir dosya adı bulunursa paket oluşturulurken dosya adı korunur ve paket yolu güncellenir.

Bu kalıp bulunamazsa:

- Config yüklemesi iptal edilmez.
- Uyarı gösterilmez.
- Paket oluşturulabilir.
- GainsFilePath değeri değiştirilmeden bırakılır.
- Diğer SYY XML alanları güncellenmeye devam eder.

## 10. Ön ayar tablosunu okuma

Tablodaki sütunlar:

- Yazılım: SYY, DM veya AKY.
- Profil: ANKA/AKSUNGUR veya ANKA3 grubu.
- YKİ: Config'in ait olduğu istasyon.
- Kalıcı konum: Config'in uygulama veri alanındaki kopyası.

`— Eksik —` görünen satır henüz yüklenmemiştir.

## 11. Yeni YKİ ekleme

1. Ön Ayar Yönetimi ekranını açın.
2. YKİ Ayarları düğmesine basın.
3. Yeni YKİ adını büyük harf ve rakamlarla yazın.
4. Ekle düğmesine basın.
5. Başarı mesajını kontrol edin.
6. Ön Ayar Yönetimi ekranına dönün.
7. Yeni YKİ'nin listede göründüğünü doğrulayın.

`SYKI`, `MYK19` ve `SYKI1-2` yeni istasyon adı olarak girilemez. ANKA3 yalnızca tanımlı SYKI çıktısını desteklediği için yeni YKİ ANKA3 listesine eklenmez.

## 12. Paket oluşturma

1. Paket Oluştur ekranını açın.
2. Hava aracı alanından ANKA, AKSUNGUR veya ANKA3 seçin.
3. Yazılım alanından SYY, DM veya AKY seçin.
4. Bin klasörü satırındaki Seç düğmesine basın.
5. Adı `bin_1.2.3` benzeri olan klasörü seçin.
6. Çıktı dizini satırındaki Seç düğmesine basın.
7. Paketlerin yazılacağı klasörü seçin.
8. Üretilecek YKİ alanından tek bir YKİ veya Tümü seçin.
9. Paketleri Oluştur düğmesine basın.
10. ZIP oluşturulsun mu sorusuna cevap verin.
11. İlerleme göstergesi tamamlanana kadar bekleyin.
12. Uyarılar penceresi çıkarsa hangi alanların veya paketlerin atlandığını okuyun.
13. Tamamlandı penceresinde oluşturulan paket sayısını kontrol edin.

## 13. ZIP seçeneği

ZIP sorusuna Hayır derseniz yalnızca normal klasör oluşur.

ZIP sorusuna Evet derseniz normal klasörün yanında aynı isimli `.zip` dosyası da oluşur. ZIP, normal klasörün yerine geçmez.

## 14. Beklenen çıktı örnekleri

SYY örneği:

`SYY_2.5.1_SYKI1`

DM örneği:

`DM_2.5.1_SYKI1-2`

AKY ANKA3 örneği:

`AKY_2.5.1_ANKA3_SYKI1-2`

Her paket klasörünün içinde şunlar bulunur:

- Seçilen bin klasörü ve içeriği.
- `config` adlı klasör ve config içeriği.

## 15. Uyarılar ne anlama gelir?

Uyarı işlemin tamamen başarısız olduğu anlamına gelmez.

Örnekler:

- Config ön ayarı eksik: Yalnızca o YKİ paketi atlanır.
- XML dosyası eksik: Dosya değiştirilemez, diğer işlemler devam eder.
- XML alanı eksik veya tekrarlı: O alan değiştirilmez, diğer alanlar güncellenir.

Uyarılı paket hedef sistemde kullanılmadan önce ayrıca kontrol edilmelidir.

## 16. Hatalar ve çözümleri

### 16.1 Bin klasörü adı geçersiz

Klasörü `bin_1.2.3` gibi yeniden adlandırın. Harf, boşluk, alt çizgili sürüm veya sondaki nokta kullanmayın.

### 16.2 Mevcut çıktılar ezilmeyecek

Çıktı dizininde aynı adlı klasör veya ZIP vardır. Yeni ve boş bir çıktı dizini seçin ya da mevcut çıktıyı güvenli şekilde başka yere taşıyın. Uygulama mevcut çıktıyı otomatik silmez.

### 16.3 Eksik config ön ayarı

Ön Ayar Yönetimi ekranına gidin ve mesajda belirtilen hava aracı grubu, yazılım ve YKİ için config klasörünü yükleyin.

### 16.4 No Python at ...

Kaynak klasörle birlikte başka bilgisayardan `.venv` taşınmıştır. Normal kullanıcı release klasöründeki EXE'yi çalıştırmalıdır. Kaynaktan çalıştırılacaksa `.venv` silinip `calistir.bat` yeniden çalıştırılmalıdır.

### 16.5 Failed to start embedded Python interpreter

Eski tek dosyalık build kullanılıyor olabilir. Güncel `release\SurumIstasyonu` klasörünü bütün içeriğiyle yeniden aktarın ve `_internal` klasörünü EXE'nin yanında tutun.

### 16.6 Uygulama açılmıyor

- ZIP'in tamamen çıkartıldığını kontrol edin.
- `_internal` klasörünün bulunduğunu kontrol edin.
- Uygulamayı yazma izniniz olan bir klasöre çıkartın.
- Antivirüs karantinasını ve kurum güvenlik kayıtlarını kontrol edin.
- Gerekirse sistem yöneticisine başvurun.

## 17. Config güncelleme

Yeni config geldiğinde eski kaydı manuel silmeyin.

1. Ön Ayar Yönetimi ekranını açın.
2. Aynı hava aracı grubu, yazılım ve YKİ'yi seçin.
3. Yükle / Güncelle düğmesine basın.
4. Yeni config klasörünü seçin.
5. Kaydedildi mesajını doğrulayın.

Uygulama eski ön ayarı güvenli biçimde yenisiyle değiştirir.

## 18. Programı güncelleme

1. Çalışan Sürüm İstasyonu uygulamasını kapatın.
2. Yeni `SurumIstasyonu` dağıtım klasörünü alın.
3. Eski program klasörünü yedekleyin veya kaldırın.
4. Yeni klasörü bütün içeriğiyle aynı konuma kopyalayın.
5. EXE ve `_internal` klasörünün birlikte bulunduğunu kontrol edin.
6. Programı açın.

Config ön ayarları `%LOCALAPPDATA%\TAI\YazilimSurumleri` altında tutulduğu için program klasörü değişse de genellikle korunur.

## 19. Deneme kontrol listesi

- Uygulama açıldı.
- ANKA/AKSUNGUR SYY config'i yüklendi.
- ANKA/AKSUNGUR DM `SYKI1-2` config'i yüklendi.
- ANKA/AKSUNGUR AKY `SYKI1-2` config'i yüklendi.
- ANKA3 SYY SYKI1 ve SYKI2 config'leri yüklendi.
- ANKA3 DM `SYKI1-2` config'i yüklendi.
- ANKA3 AKY `SYKI1-2` config'i yüklendi.
- Geçerli bin klasörü seçildi.
- Tek YKİ paketi oluşturuldu.
- Tümü seçeneği denendi.
- ZIP Hayır seçeneği denendi.
- ZIP Evet seçeneği denendi.
- Çıktı klasöründe bin ve config klasörleri doğrulandı.
- Değiştirilen XML yolları kontrol edildi.
- AKY BlockType değeri kontrol edildi.

## 20. Destek talebinde gönderilecek bilgiler

Sorun yaşandığında şu bilgileri paylaşın:

- Seçilen hava aracı.
- Seçilen yazılım.
- Seçilen YKİ.
- Bin klasörünün tam adı.
- Hata veya uyarı metninin tamamı.
- Hassas bilgiler gizlenerek ilgili XML öğesi.
- Uygulamanın release klasöründen mi, kaynak koddan mı çalıştırıldığı.
- Windows sürümü ve kullanılan güvenlik yazılımı.

Config klasörünün tamamını veya gizli kurum bilgilerini izinsiz paylaşmayın.
