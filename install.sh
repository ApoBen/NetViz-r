#!/usr/bin/env bash
# NetVizör Global Installer

GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}======================================${NC}"
echo -e "${BLUE}     🌐 NetVizör Kurulum Sihirbazı   ${NC}"
echo -e "${BLUE}======================================${NC}"

# Check for Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}[!] python3 bulunamadı. Lütfen yükleyin.${NC}"
    exit 1
fi

# Clone directory
INSTALL_DIR="$HOME/.netvizor"
if [ -d "$INSTALL_DIR" ]; then
    echo -e "${GREEN}[+] Eski kurulum güncelleniyor...${NC}"
    cd "$INSTALL_DIR"
    git pull origin main
else
    echo -e "${GREEN}[+] NetVizör indiriliyor...${NC}"
    git clone https://github.com/ApoBen/NetViz-r.git "$INSTALL_DIR"
    cd "$INSTALL_DIR"
fi

# Create Virtual Environment
echo -e "${GREEN}[+] Sanal ortam (venv) oluşturuluyor ve bağımlılıklar yükleniyor...${NC}"
python3 -m venv venv
./venv/bin/pip install -r requirements.txt > /dev/null 2>&1

# Setup global command 'netvizor'
echo -e "${GREEN}[+] Global çalıştırıcı (netvizor) ayarlanıyor...${NC}"

if command -v termux-setup-storage &> /dev/null; then
    # Termux Environment
    BIN_DIR="/data/data/com.termux/files/usr/bin"
else
    # Standard Linux Environment
    BIN_DIR="/usr/local/bin"
    if [ "$EUID" -ne 0 ]; then
        echo -e "${RED}[!] /usr/local/bin dizinine yazmak için sudo yetkisi gerekiyor. Lütfen şifrenizi girin:${NC}"
        SUDO_CMD="sudo "
    else
        SUDO_CMD=""
    fi
fi

# Create the wrapper script
WRAPPER_SCRIPT="#!/usr/bin/env bash
cd \"$INSTALL_DIR\"
./run.sh \"\$@\"
"

echo "$WRAPPER_SCRIPT" > /tmp/netvizor_wrapper
$SUDO_CMD mv /tmp/netvizor_wrapper "$BIN_DIR/netvizor"
$SUDO_CMD chmod +x "$BIN_DIR/netvizor"

echo -e "${GREEN}[+] Kurulum başarıyla tamamlandı! 🎉${NC}"
echo -e "Artık terminalinize sadece ${BLUE}netvizor${NC} yazarak uygulamayı başlatabilirsiniz."
