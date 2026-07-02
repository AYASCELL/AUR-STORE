# 🛒 AYASCELL - AUR STORE

Arch Linux için basit ve kullanıcı dostu bir yazılım mağazası.  
PyQt6 arayüzü ile paket arama, yükleme, güncelleme ve silme işlemlerini kolayca yapabilirsiniz.

---

## 🚀 Özellikler
- 🔍 Paket arama (AUR ve resmi depolar)
- 📦 Paket yükleme
- ♻️ Paket güncelleme
- ❌ Paket silme
- 🔄 Tüm paketleri güncelleme
- 🖥️ Modern PyQt6 arayüzü

---

## 📋 Kurulum Rehberi

### 1. Gerekli Sistem Paketlerini Yükleyin
```bash
sudo pacman -Syu python git base-devel
```
### 2. Proje Dosyalarını İndirin
```bash
git clone https://github.com/AYASCELL/AUR-STORE.git
cd AUR-STORE

```
### 3. Sanal Ortam Oluşturun (Venv klasörü yoksa Çalıştırın)
```bash
python -m venv venv

# Fish shell için
source venv/bin/activate.fish

# Bash/Zsh için
source venv/bin/activate

# Bağımlılıkları yükle
pip install -r requirements.txt
```
### 4. Sanal Ortamı Aktif Edin ve Bağımlılıkları Yükleyin
```bash
# Fish shell için
source venv/bin/activate.fish
# Bash/Zsh için
source venv/bin/activate
# Bağımlılıkları yükle
pip install -r requirements.txt
```
### 5. Uygulamayı Çalıştırın
```bash
python arch_store/main.py
```
### Alternatif olarak:
```bash
./venv/bin/python arch_store/main.py
```

## Görüntüler

<img width="1017" height="751" alt="Ekran Görüntüsü_20260702_152937" src="https://github.com/user-attachments/assets/0a5a8e32-6c5f-4f79-b26d-bc34261b1a73" />

<img width="1022" height="754" alt="Ekran Görüntüsü_20260702_152951" src="https://github.com/user-attachments/assets/35ba54fb-a562-4e4b-9775-0f61be81bfca" />

<img width="1021" height="750" alt="Ekran Görüntüsü_20260702_153024" src="https://github.com/user-attachments/assets/336b2c08-2ffd-40b2-aa3c-a1658b97f2b2" />
