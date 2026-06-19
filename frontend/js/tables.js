// Helper to format bytes to human readable
function formatBytes(bytes, decimals = 2) {
    if (!+bytes) return '0 B';
    const k = 1024;
    const dm = decimals < 0 ? 0 : decimals;
    const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return `${parseFloat((bytes / Math.pow(k, i)).toFixed(dm))} ${sizes[i]}`;
}

// Icon mapping for common applications
function getProcessIcon(processName) {
    const p = processName.toLowerCase();
    if (p.includes('chrome')) return '<i class="fa-brands fa-chrome" style="color: #4285F4;"></i>';
    if (p.includes('firefox')) return '<i class="fa-brands fa-firefox" style="color: #FF7139;"></i>';
    if (p.includes('edge')) return '<i class="fa-brands fa-edge" style="color: #0078D7;"></i>';
    if (p.includes('safari')) return '<i class="fa-brands fa-safari" style="color: #00A6DA;"></i>';
    if (p.includes('brave')) return '<i class="fa-brands fa-brave" style="color: #FB542B;"></i>';
    if (p.includes('discord')) return '<i class="fa-brands fa-discord" style="color: #5865F2;"></i>';
    if (p.includes('spotify')) return '<i class="fa-brands fa-spotify" style="color: #1DB954;"></i>';
    if (p.includes('slack')) return '<i class="fa-brands fa-slack" style="color: #4A154B;"></i>';
    if (p.includes('telegram')) return '<i class="fa-brands fa-telegram" style="color: #0088cc;"></i>';
    if (p.includes('skype')) return '<i class="fa-brands fa-skype" style="color: #00AFF0;"></i>';
    if (p.includes('zoom')) return '<i class="fa-solid fa-video" style="color: #2D8CFF;"></i>';
    if (p.includes('steam')) return '<i class="fa-brands fa-steam" style="color: #171a21;"></i>';
    if (p.includes('python')) return '<i class="fa-brands fa-python" style="color: #3776AB;"></i>';
    if (p.includes('node') || p.includes('npm')) return '<i class="fa-brands fa-node-js" style="color: #68A063;"></i>';
    if (p.includes('java')) return '<i class="fa-brands fa-java" style="color: #5382A1;"></i>';
    if (p.includes('docker')) return '<i class="fa-brands fa-docker" style="color: #2496ED;"></i>';
    if (p.includes('git')) return '<i class="fa-brands fa-git-alt" style="color: #F1502F;"></i>';
    if (p.includes('code') || p.includes('vscode')) return '<i class="fa-solid fa-code" style="color: #007ACC;"></i>';
    if (p.includes('wget') || p.includes('curl')) return '<i class="fa-solid fa-download" style="color: #f0f2f5;"></i>';
    if (p.includes('ssh')) return '<i class="fa-solid fa-terminal" style="color: #f0f2f5;"></i>';
    // Fallback generic icon
    return '<i class="fa-solid fa-microchip" style="color: var(--text-secondary);"></i>';
}

function updateProcessTable(processes) {
    const tbody = document.querySelector('#process-table tbody');
    tbody.innerHTML = '';
    
    processes.forEach(proc => {
        const tr = document.createElement('tr');
        
        // Speed column formatting
        const up = formatBytes(proc.upload_speed_bps) + '/s';
        const down = formatBytes(proc.download_speed_bps) + '/s';
        
        // Total data formatting
        const totalSent = formatBytes(proc.total_sent);
        const totalRecv = formatBytes(proc.total_recv);
        
        const icon = getProcessIcon(proc.name);
        
        tr.innerHTML = `
            <td><div style="display: flex; align-items: center; gap: 10px; font-size: 16px;">
                ${icon}
                <strong style="font-size: 13px;">${proc.name}</strong>
            </div></td>
            <td>${proc.pid} <span style="font-size:11px; color:var(--text-secondary)">(${proc.user})</span></td>
            <td><span style="color:var(--accent-blue)">⬆ ${up}</span> &nbsp; <span style="color:var(--accent-green)">⬇ ${down}</span></td>
            <td><span style="color:var(--text-secondary)">⬆ ${totalSent}</span> &nbsp; <span style="color:var(--text-secondary)">⬇ ${totalRecv}</span></td>
        `;
        tbody.appendChild(tr);
    });
}

function updateConnectionsTable(connections) {
    const tbody = document.querySelector('#connections-table tbody');
    tbody.innerHTML = '';
    
    // Sort logic could go here, for now just show top 15
    const displayConns = connections.slice(0, 15);
    
    displayConns.forEach(conn => {
        const tr = document.createElement('tr');
        const stateClass = `status-${conn.status}`;
        
        tr.innerHTML = `
            <td>${conn.type} (${conn.family})</td>
            <td>${conn.laddr}</td>
            <td>${conn.raddr}</td>
            <td class="${stateClass}">${conn.status}</td>
        `;
        tbody.appendChild(tr);
    });
}

function updatePacketTable(packets) {
    const tbody = document.querySelector('#packet-table tbody');
    tbody.innerHTML = '';
    
    packets.forEach(pkt => {
        const tr = document.createElement('tr');
        
        let protoColor = 'var(--text-primary)';
        if(pkt.proto === 'TCP') protoColor = 'var(--accent-blue)';
        if(pkt.proto === 'UDP') protoColor = 'var(--accent-green)';
        if(pkt.proto === 'ICMP') protoColor = 'var(--accent-yellow)';
        
        tr.innerHTML = `
            <td style="color:${protoColor}; font-weight:bold;">${pkt.proto}</td>
            <td>${pkt.src}</td>
            <td>${pkt.dst}</td>
            <td>${pkt.length} B</td>
        `;
        tbody.appendChild(tr);
    });
}

// Global exposure
window.formatBytes = formatBytes;
window.updateProcessTable = updateProcessTable;
window.updateConnectionsTable = updateConnectionsTable;
window.updatePacketTable = updatePacketTable;
