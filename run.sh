#!/bin/bash

# Renkler
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}======================================${NC}"
echo -e "${BLUE}        🌐 NetVizör Başlatıcı       ${NC}"
echo -e "${BLUE}======================================${NC}"

# Python kontrolü
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Hata: python3 bulunamadı. Lütfen yükleyin.${NC}"
    exit 1
fi

# Sanal ortam oluştur/kontrol et
if [ ! -d "venv" ]; then
    echo -e "${GREEN}[+] Sanal ortam (venv) oluşturuluyor...${NC}"
    if [ -d "/data/data/com.termux" ] || [ -n "$TERMUX_VERSION" ]; then
        python3 -m venv venv --system-site-packages
    else
        python3 -m venv venv
    fi
fi

# Bağımlılıkları yükle
echo -e "${GREEN}[+] Bağımlılıklar kontrol ediliyor...${NC}"
if [ -d "/data/data/com.termux" ] || [ -n "$TERMUX_VERSION" ]; then
    grep -v "psutil" requirements.txt > termux_requirements.txt
    ./venv/bin/pip install -r termux_requirements.txt
    rm termux_requirements.txt
else
    ./venv/bin/pip install -r requirements.txt
fi

# Mod seçimi
echo ""
echo "NetVizör iki farklı modda çalışabilir:"
echo "  1) Temel Mod    : Bant genişliği, süreçler ve TCP bağlantıları (Root gerekmez)"
echo "  2) Gelişmiş Mod : Temel mod + Paket günlüğü ve DNS takibi (Sudo/Root gerektirir)"
echo ""
read -p "Hangi modda başlatmak istersiniz? (1/2) [Varsayılan: 1]: " MODE_SELECTION

MODE_SELECTION=${MODE_SELECTION:-1}

echo ""
echo -e "${GREEN}[+] NetVizör başlatılıyor... (Tarayıcınız otomatik açılacaktır)${NC}"

# Start server in background
if [ "$MODE_SELECTION" == "2" ]; then
    echo -e "${RED}[!] Gelişmiş mod seçildi. Sudo parolası istenebilir.${NC}"
    sudo ./venv/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 8765 &
else
    ./venv/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 8765 &
fi

SERVER_PID=$!

# Wait for server to start
sleep 2

# Open browser
if command -v xdg-open &> /dev/null; then
    xdg-open http://localhost:8765 &> /dev/null
else
    echo "Lütfen tarayıcınızdan http://localhost:8765 adresine gidin."
fi

# Wait for server to exit
wait $SERVER_PID
