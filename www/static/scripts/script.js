function updateInitAppStatus(status) {
    const card = document.getElementById('init-app-card');
    const label = document.getElementById('init-app-status');

    if (status === 'active') {
        card.style.backgroundColor = '#d4edda';
        label.innerText = 'Aktywne';
    } else if (status === 'inactive') {
        card.style.backgroundColor = '#f8d7da';
        label.innerText = 'Nieaktywne';
    } else if (status === 'failed') {
        card.style.backgroundColor = '#f8d7da';
        label.innerText = 'Błąd';
    } else {
        card.style.backgroundColor = '#f8d7da';
        label.innerText = 'Nieznany status';
    }
}

async function fetchStatus() {
    try {
        const res = await fetch('/status');
        const data = await res.json();
        document.getElementById('temp-box').innerText = data.temperature + '°C';
        document.getElementById('uptime-box').innerText = data.uptime;
        document.getElementById('cpu-box').innerText = data.cpu_load;
        document.getElementById('ram-box').innerText = data.ram_usage;
        document.getElementById('disk-box').innerText = data.disk_space;
        updateInitAppStatus(data.init_app_status);
    } catch (e) {
        console.error("Błąd pobierania statusu:", e);
    }
}

fetchStatus();
setInterval(fetchStatus, 5000);