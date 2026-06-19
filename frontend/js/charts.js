// Chart.js global defaults
Chart.defaults.color = '#8b949e';
Chart.defaults.font.family = "'Inter', sans-serif";

let bandwidthChart = null;
let protocolChart = null;

const timeLabels = [];
const uploadData = [];
const downloadData = [];
const maxDataPoints = 60; // 60 seconds history

function initCharts() {
    // Bandwidth Chart (Area Chart)
    const ctxBandwidth = document.getElementById('bandwidthChart').getContext('2d');
    
    // Gradients
    const gradientUp = ctxBandwidth.createLinearGradient(0, 0, 0, 300);
    gradientUp.addColorStop(0, 'rgba(0, 212, 255, 0.5)');
    gradientUp.addColorStop(1, 'rgba(0, 212, 255, 0.0)');
    
    const gradientDown = ctxBandwidth.createLinearGradient(0, 0, 0, 300);
    gradientDown.addColorStop(0, 'rgba(0, 230, 118, 0.5)');
    gradientDown.addColorStop(1, 'rgba(0, 230, 118, 0.0)');

    bandwidthChart = new Chart(ctxBandwidth, {
        type: 'line',
        data: {
            labels: timeLabels,
            datasets: [
                {
                    label: 'Upload (MB/s)',
                    borderColor: '#00d4ff',
                    backgroundColor: gradientUp,
                    borderWidth: 2,
                    pointRadius: 0,
                    fill: true,
                    tension: 0.4,
                    data: uploadData
                },
                {
                    label: 'Download (MB/s)',
                    borderColor: '#00e676',
                    backgroundColor: gradientDown,
                    borderWidth: 2,
                    pointRadius: 0,
                    fill: true,
                    tension: 0.4,
                    data: downloadData
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            animation: false, // Turn off for real-time performance
            interaction: {
                mode: 'index',
                intersect: false,
            },
            scales: {
                x: {
                    display: false // Hide X axis labels for cleaner look
                },
                y: {
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(255, 255, 255, 0.05)'
                    }
                }
            },
            plugins: {
                legend: {
                    position: 'top',
                    labels: { boxWidth: 12 }
                }
            }
        }
    });

    // Protocol Pie Chart
    const ctxProtocol = document.getElementById('protocolChart').getContext('2d');
    protocolChart = new Chart(ctxProtocol, {
        type: 'doughnut',
        data: {
            labels: ['TCP', 'UDP', 'ICMP', 'Other'],
            datasets: [{
                data: [0, 0, 0, 0],
                backgroundColor: [
                    '#00d4ff', // TCP
                    '#00e676', // UDP
                    '#ffc400', // ICMP
                    '#ff3d00'  // Other
                ],
                borderWidth: 0,
                hoverOffset: 4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '70%',
            plugins: {
                legend: {
                    position: 'right',
                    labels: { color: '#f0f2f5', boxWidth: 12 }
                }
            }
        }
    });
}

function updateBandwidthChart(uploadBps, downloadBps) {
    const now = new Date();
    const timeString = now.getHours() + ':' + String(now.getMinutes()).padStart(2, '0') + ':' + String(now.getSeconds()).padStart(2, '0');
    
    // Convert to MB/s
    const uploadMbs = (uploadBps / (1024 * 1024)).toFixed(2);
    const downloadMbs = (downloadBps / (1024 * 1024)).toFixed(2);

    timeLabels.push(timeString);
    uploadData.push(uploadMbs);
    downloadData.push(downloadMbs);

    if (timeLabels.length > maxDataPoints) {
        timeLabels.shift();
        uploadData.shift();
        downloadData.shift();
    }

    bandwidthChart.update();
}

function updateProtocolChart(stats) {
    if (!protocolChart) return;
    protocolChart.data.datasets[0].data = [
        stats.TCP || 0,
        stats.UDP || 0,
        stats.ICMP || 0,
        stats.Other || 0
    ];
    protocolChart.update();
}

document.addEventListener('DOMContentLoaded', initCharts);
