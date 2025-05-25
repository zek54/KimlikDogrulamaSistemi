# Gelişmiş Kimlik Doğrulama Sistemi

Modern ve güvenli bir kimlik doğrulama sistemi. Hem masaüstü uygulaması hem de web arayüzü ile kullanılabilir.

## Özellikler

- Güvenli şifre yönetimi (PBKDF2 ile hash)
- Güvenlik sorusu ile şifre sıfırlama
- Oturum yönetimi
- Giriş geçmişi takibi
- Şifre gücü kontrolü
- Modern ve kullanıcı dostu arayüz
- Responsive tasarım
- API desteği

## Kurulum

1. Gerekli paketleri yükleyin:
```bash
pip install -r requirements.txt
```

2. Veritabanını oluşturun:
```bash
python web_app.py
```

## Kullanım

### Masaüstü Uygulaması

```bash
python enhanced_auth_system.py
```

### Web Arayüzü

```bash
python web_app.py
```

Tarayıcınızda `http://localhost:5000` adresine gidin.

## API Kullanımı

### Giriş Yapma

```bash
curl -X POST http://localhost:5000/api/login \
  -H "Content-Type: application/json" \
  -d '{"username": "kullanici", "password": "sifre"}'
```

### Kayıt Olma

```bash
curl -X POST http://localhost:5000/api/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "kullanici",
    "email": "kullanici@example.com",
    "password": "sifre",
    "security_question": "İlk evcil hayvanınızın adı nedir?",
    "security_answer": "cevap"
  }'
```

### Şifre Sıfırlama

```bash
curl -X POST http://localhost:5000/api/reset-password \
  -H "Content-Type: application/json" \
  -d '{
    "username": "kullanici",
    "security_answer": "cevap",
    "new_password": "yeni_sifre"
  }'
```

## Güvenlik Özellikleri

- PBKDF2 ile şifre hashleme
- Güvenlik sorusu ile iki faktörlü doğrulama
- Başarısız giriş denemesi limiti
- Oturum süresi kontrolü
- IP adresi takibi
- XSS ve CSRF koruması
- SQL injection koruması
- Güçlü şifre politikası

## Katkıda Bulunma

1. Bu depoyu fork edin
2. Yeni bir branch oluşturun (`git checkout -b feature/yeniOzellik`)
3. Değişikliklerinizi commit edin (`git commit -am 'Yeni özellik: XYZ'`)
4. Branch'inizi push edin (`git push origin feature/yeniOzellik`)
5. Pull Request oluşturun

## Lisans

Bu proje MIT lisansı altında lisanslanmıştır. Detaylar için [LICENSE](LICENSE) dosyasına bakın. 