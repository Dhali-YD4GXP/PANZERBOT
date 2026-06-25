#!/bin/bash
# Script untuk setup dependensi Panzerbot di Raspberry Pi

echo "=== Memulai Instalasi Dependensi Panzerbot ==="

# 1. Update sistem paket
echo "[1/3] Memperbarui daftar paket apt..."
sudo apt-get update -y

# 2. Instal pemutar audio mpg123 (untuk memutar file mp3)
echo "[2/3] Menginstal mpg123 (untuk pemutar audio MP3)..."
sudo apt-get install -y mpg123 aplay

# 3. Instal dependensi Python
echo "[3/3] Menginstal dependensi Python via pip..."
if command -v pip3 &> /dev/null; then
    pip3 install -r requirements.txt
else
    echo "pip3 tidak ditemukan. Menginstal python3-pip terlebih dahulu..."
    sudo apt-get install -y python3-pip
    pip3 install -r requirements.txt
fi

echo "=== Setup Selesai! ==="
echo "Anda dapat menjalankan backend dengan: python3 src/main.py"
