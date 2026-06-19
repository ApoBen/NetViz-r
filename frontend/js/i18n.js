const translations = {
    tr: {
        status_connecting: "Bağlanıyor...",
        status_connected: "Bağlı",
        status_disconnected: "Bağlantı Koptu",
        mode_detecting: "Tespit ediliyor...",
        mode_basic: "Temel Mod",
        mode_advanced: "Gelişmiş Mod",
        controls_title: "Kontroller",
        btn_pause: "Durdur",
        btn_resume: "Devam Et",
        btn_export: "Kaydet (.json)",
        language: "Dil:",
        interfaces_title: "Ağ Arayüzleri",
        total_upload: "Toplam Giden",
        total_download: "Toplam Gelen",
        active_conns: "Aktif Bağlantılar",
        bandwidth_chart: "Bant Genişliği",
        process_usage: "Süreç Bazlı Kullanım",
        th_app: "Uygulama",
        th_pid: "PID/Kullanıcı",
        th_speed: "Anlık Hız (G/A)",
        th_total: "Toplam Veri",
        protocol_dist: "Protokol Dağılımı",
        root_required: "Sudo/Root Gerekli",
        live_connections: "Canlı Bağlantılar",
        th_type: "Tip",
        th_local: "Yerel",
        th_remote: "Uzak",
        th_state: "Durum",
        packet_log: "Paket Günlüğü",
        th_proto: "Protokol",
        th_src: "Kaynak",
        th_dst: "Hedef",
        th_size: "Boyut",
        msg_export_success: "Log kaydedildi!",
        msg_export_error: "Hata oluştu"
    },
    en: {
        status_connecting: "Connecting...",
        status_connected: "Connected",
        status_disconnected: "Disconnected",
        mode_detecting: "Detecting...",
        mode_basic: "Basic Mode",
        mode_advanced: "Advanced Mode",
        controls_title: "Controls",
        btn_pause: "Pause",
        btn_resume: "Resume",
        btn_export: "Export (.json)",
        language: "Language:",
        interfaces_title: "Network Interfaces",
        total_upload: "Total Upload",
        total_download: "Total Download",
        active_conns: "Active Conns",
        bandwidth_chart: "Bandwidth",
        process_usage: "Per-Process Usage",
        th_app: "Application",
        th_pid: "PID/User",
        th_speed: "Current Speed",
        th_total: "Total Data",
        protocol_dist: "Protocol Distribution",
        root_required: "Sudo/Root Required",
        live_connections: "Live Connections",
        th_type: "Type",
        th_local: "Local",
        th_remote: "Remote",
        th_state: "State",
        packet_log: "Packet Log",
        th_proto: "Proto",
        th_src: "Source",
        th_dst: "Destination",
        th_size: "Size",
        msg_export_success: "Log exported!",
        msg_export_error: "Export error"
    }
};

let currentLang = localStorage.getItem('netvizor_lang') || 'tr';

function applyTranslations() {
    const texts = document.querySelectorAll('[data-i18n]');
    texts.forEach(el => {
        const key = el.getAttribute('data-i18n');
        if (translations[currentLang][key]) {
            el.textContent = translations[currentLang][key];
        }
    });
}

function setLanguage(lang) {
    if (translations[lang]) {
        currentLang = lang;
        localStorage.setItem('netvizor_lang', lang);
        applyTranslations();
    }
}

// Initialize on load
document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('lang-select').value = currentLang;
    applyTranslations();
    
    document.getElementById('lang-select').addEventListener('change', (e) => {
        setLanguage(e.target.value);
    });
});
