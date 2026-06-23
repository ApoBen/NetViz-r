let ws;
let isPaused = false;
let currentMode = "Basic";

// DOM Elements
const wsStatusDot = document.getElementById('ws-status-dot');
const wsStatusText = document.getElementById('ws-status-text');
const modeBadge = document.getElementById('mode-badge');
const btnPause = document.getElementById('btn-pause');
const btnExport = document.getElementById('btn-export');
const exportMsg = document.getElementById('export-msg');
const interfacesContainer = document.getElementById('interfaces-container');

const totalUploadEl = document.getElementById('total-upload');
const totalDownloadEl = document.getElementById('total-download');
const activeConnsEl = document.getElementById('active-connections');

function initWebSocket() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws`;
    
    wsStatusDot.className = 'dot';
    wsStatusText.textContent = 'Bağlanıyor...';
    
    ws = new WebSocket(wsUrl);
    
    ws.onopen = () => {
        wsStatusDot.className = 'dot connected';
        wsStatusText.textContent = translations[currentLang]?.status_connected || 'Bağlı';
        checkStatus(); // Fetch mode and pause status
    };
    
    ws.onclose = () => {
        wsStatusDot.className = 'dot disconnected';
        wsStatusText.textContent = translations[currentLang]?.status_disconnected || 'Bağlantı Koptu';
        // Auto reconnect
        setTimeout(initWebSocket, 3000);
    };
    
    ws.onerror = (err) => {
        console.error('WebSocket error:', err);
        wsStatusDot.className = 'dot disconnected';
        wsStatusText.textContent = translations[currentLang]?.status_disconnected || 'Disconnected';
    };
    
    ws.onmessage = (event) => {
        if (isPaused) return; // Ignore updates if paused locally
        
        try {
            const msg = JSON.parse(event.data);
            handleMessage(msg);
        } catch (e) {
            console.error("Invalid WS message", e);
        }
    };
}

function handleMessage(msg) {
    switch (msg.type) {
        case 'bandwidth':
            // Update Headers
            totalUploadEl.textContent = `${window.formatBytes(msg.data.total_upload_speed_bps)}/s`;
            totalDownloadEl.textContent = `${window.formatBytes(msg.data.total_download_speed_bps)}/s`;
            
            // Update Chart
            updateBandwidthChart(msg.data.total_upload_speed_bps, msg.data.total_download_speed_bps);
            
            // Update Interfaces Sidebar
            updateInterfaces(msg.data.interfaces);
            break;
            
        case 'connections':
            activeConnsEl.textContent = msg.data.total;
            updateConnectionsTable(msg.data.connections);
            break;
            
        case 'processes':
            updateProcessTable(msg.data.processes);
            break;
            
        case 'packets':
            updateProtocolChart(msg.data.stats);
            updatePacketTable(msg.data.recent);
            break;
            
        case 'dns':
            break;
            
        case 'alert':
            showToast(msg.data.title, msg.data.message, msg.data.level, msg.data.app_name);
            break;
    }
}

function showToast(title, message, level, appName) {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = `toast level-${level}`;
    
    // Header
    const header = document.createElement('div');
    header.className = 'toast-header';
    
    let icon = '⚠️';
    if (level === 'high') icon = '🚨';
    if (level === 'low') icon = 'ℹ️';
    
    const iconSpan = document.createElement('span');
    iconSpan.textContent = `${icon} ${title}`;
    const closeBtn = document.createElement('button');
    closeBtn.className = 'toast-close';
    closeBtn.innerHTML = '&times;';
    header.appendChild(iconSpan);
    header.appendChild(closeBtn);
    
    // Body
    const body = document.createElement('div');
    body.className = 'toast-body';
    body.textContent = message;
    
    toast.appendChild(header);
    toast.appendChild(body);
    
    // Actions (Whitelist)
    if (appName && level !== 'high') { // allow whitelist for medium alerts like bandwidth spike
        const actions = document.createElement('div');
        actions.className = 'toast-actions';
        const btn = document.createElement('button');
        btn.className = 'toast-btn';
        btn.textContent = 'Beyaz Listeye Ekle';
        btn.onclick = () => {
            addToWhitelist(appName);
            toast.remove();
        };
        actions.appendChild(btn);
        toast.appendChild(actions);
    }
    
    // Close event
    closeBtn.onclick = () => toast.remove();
    
    container.appendChild(toast);
    
    // Animate in
    setTimeout(() => toast.classList.add('show'), 10);
    
    // Auto remove after 6 seconds unless high
    if (level !== 'high') {
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => toast.remove(), 300);
        }, 6000);
    }
}

async function addToWhitelist(appName) {
    try {
        const res = await fetch('/api/whitelist', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({app_name: appName})
        });
        if (!res.ok) return;
        showToast("Bilgi", `${appName} beyaz listeye eklendi.`, "low");
    } catch(e) {
        console.error("Whitelist error", e);
    }
}

function updateInterfaces(interfaces) {
    interfacesContainer.innerHTML = `<h3><span data-i18n="interfaces_title">${translations[currentLang]?.interfaces_title || 'Ağ Arayüzleri'}</span></h3>`;
    
    for (const [name, stats] of Object.entries(interfaces)) {
        if (stats.total_sent === 0 && stats.total_recv === 0) continue; // Skip dead interfaces
        
        const div = document.createElement('div');
        div.className = 'interface-item';
        div.style.marginBottom = '12px';
        div.style.padding = '8px';
        div.style.background = 'rgba(255,255,255,0.05)';
        div.style.borderRadius = '8px';
        div.style.fontSize = '12px';
        
        const nameDiv = document.createElement('div');
        nameDiv.style.fontWeight = 'bold';
        nameDiv.style.marginBottom = '4px';
        nameDiv.style.color = 'var(--text-primary)';
        nameDiv.textContent = name;
        
        const statsDiv = document.createElement('div');
        statsDiv.style.display = 'flex';
        statsDiv.style.justifyContent = 'space-between';
        statsDiv.innerHTML = `
                <span style="color:var(--accent-blue)">⬆ ${window.formatBytes(stats.upload_speed_bps)}/s</span>
                <span style="color:var(--accent-green)">⬇ ${window.formatBytes(stats.download_speed_bps)}/s</span>
        `;
        
        div.appendChild(nameDiv);
        div.appendChild(statsDiv);
        interfacesContainer.appendChild(div);
    }
}

// Update process table
function updateProcessTable(processes) {
    const tbody = document.getElementById('process-table').querySelector('tbody');
    tbody.innerHTML = '';
    
    // Sort processes by download speed
    processes.sort((a, b) => b.download_speed - a.download_speed);
    
    processes.forEach(proc => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>
                <div class="process-app">
                    <img src="https://ui-avatars.com/api/?name=${proc.name}&background=random&color=fff&size=24" class="app-icon" onerror="this.style.display='none'">
                    <span>${proc.name}</span>
                </div>
            </td>
            <td><span class="pid">${proc.pid}</span> <span class="username">${proc.username}</span></td>
            <td>
                <div class="speed-indicator"><span class="up-arrow">↑</span> ${formatBytes(proc.upload_speed)}/s</div>
                <div class="speed-indicator"><span class="down-arrow">↓</span> ${formatBytes(proc.download_speed)}/s</div>
            </td>
            <td>
                <div><span class="up-arrow">↑</span> ${formatBytes(proc.total_upload)}</div>
                <div><span class="down-arrow">↓</span> ${formatBytes(proc.total_download)}</div>
            </td>
        `;
        tbody.appendChild(tr);
    });
}

// Settings Modal Logic
document.addEventListener('DOMContentLoaded', () => {
    const btnSettings = document.getElementById('btn-settings');
    const settingsModal = document.getElementById('settings-modal');
    const closeSettings = document.getElementById('close-settings');
    const toggleSql = document.getElementById('toggle-sql');
    
    if(btnSettings && settingsModal) {
        btnSettings.addEventListener('click', () => {
            settingsModal.style.display = 'block';
            // Fetch current settings
            fetch('/api/settings')
                .then(res => res.json())
                .then(data => {
                    toggleSql.checked = data.sql_enabled;
                })
                .catch(err => console.error("Error fetching settings:", err));
        });
        
        closeSettings.addEventListener('click', () => {
            settingsModal.style.display = 'none';
        });
        
        window.addEventListener('click', (e) => {
            if (e.target == settingsModal) {
                settingsModal.style.display = 'none';
            }
        });
        
        // Handle Toggle Switch
        toggleSql.addEventListener('change', (e) => {
            const isEnabled = e.target.checked;
            fetch('/api/settings/sql', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ enabled: isEnabled })
            })
            .then(res => res.json())
            .then(data => {
                if(data.status === 'success') {
                    showToast(
                        t('toast_success'), 
                        isEnabled ? 'SQL Logging Enabled' : 'SQL Logging Disabled', 
                        'low'
                    );
                }
            })
            .catch(err => {
                console.error("Error updating SQL setting:", err);
                toggleSql.checked = !isEnabled; // revert on error
                showToast(t('toast_error'), 'Failed to update setting', 'high');
            });
        });
    }
});

async function checkStatus() {
    try {
        const res = await fetch('/api/status');
        if (!res.ok) return;
        const data = await res.json();
        
        currentMode = data.mode;
        isPaused = data.is_paused;
        
        // Update Badge
        modeBadge.textContent = currentMode;
        if (currentMode.startsWith("Advanced")) {
            modeBadge.className = "badge advanced";
            // Unlock advanced features
            document.querySelectorAll('.advanced-feature').forEach(el => el.classList.remove('locked'));
        } else {
            modeBadge.className = "badge basic";
            // Lock advanced features
            document.querySelectorAll('.advanced-feature').forEach(el => el.classList.add('locked'));
        }
        
        updatePauseButtonUI();
    } catch (e) {
        console.error("Status fetch error", e);
    }
}

function updatePauseButtonUI() {
    if (isPaused) {
        btnPause.innerHTML = `<span class="icon">▶️</span> <span data-i18n="btn_resume">${translations[currentLang]?.btn_resume || 'Devam Et'}</span>`;
        btnPause.style.background = 'rgba(0, 230, 118, 0.2)';
        btnPause.style.color = 'var(--accent-green)';
        btnPause.style.borderColor = 'rgba(0, 230, 118, 0.4)';
    } else {
        btnPause.innerHTML = `<span class="icon">⏸️</span> <span data-i18n="btn_pause">${translations[currentLang]?.btn_pause || 'Durdur'}</span>`;
        btnPause.style.background = '';
        btnPause.style.color = '';
        btnPause.style.borderColor = '';
    }
}

// Event Listeners
btnPause.addEventListener('click', async () => {
    const endpoint = isPaused ? '/api/resume' : '/api/pause';
    try {
        const res = await fetch(endpoint, { method: 'POST' });
        if (!res.ok) return;
        const data = await res.json();
        if (data.status) {
            isPaused = !isPaused;
            updatePauseButtonUI();
        }
    } catch (e) {
        console.error("Pause toggle error", e);
    }
});

btnExport.addEventListener('click', async () => {
    btnExport.disabled = true;
    exportMsg.textContent = "Kaydediliyor...";
    exportMsg.style.color = "var(--text-secondary)";
    
    try {
        const res = await fetch('/api/export', { method: 'POST' });
        if (!res.ok) return;
        const data = await res.json();
        
        if (data.status === 'success') {
            exportMsg.textContent = translations[currentLang]?.msg_export_success || "Log kaydedildi!";
            exportMsg.style.color = "var(--accent-green)";
        } else {
            exportMsg.textContent = "Hata: " + data.message;
            exportMsg.style.color = "var(--accent-red)";
        }
    } catch (e) {
        exportMsg.textContent = "Bağlantı hatası!";
        exportMsg.style.color = "var(--accent-red)";
    }
    
    setTimeout(() => {
        exportMsg.textContent = "";
        btnExport.disabled = false;
    }, 4000);
});

// Start
document.addEventListener('DOMContentLoaded', () => {
    initWebSocket();
});
