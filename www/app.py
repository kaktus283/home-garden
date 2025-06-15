from flask import Flask, render_template_string, request
import subprocess
import os
import datetime

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html lang="pl">
<head>
  <meta charset="UTF-8">
  <title>Panel zarządzania Raspberry Pi</title>
  <style>
    body {
      font-family: 'Segoe UI', sans-serif;
      background-color: #f4f6f8;
      padding: 2rem;
      color: #3d3d3d;
    }
    .container {
      max-width: 800px;
      margin: auto;
      background-color: white;
      padding: 2rem;
      border-radius: 12px;
      box-shadow: 0 0 20px rgba(0,0,0,0.05);
    }
    h1, h2 {
      text-align: left;
      margin-bottom: 1rem;
      color: #2c3e50;
    }
    section {
      margin-bottom: 2rem;
    }
    .grid {
      display: flex;
      flex-wrap: wrap;
      gap: 1rem;
      justify-content: center;
    }
    .card {
      flex: 1 1 200px;
      background: #f1f1f1;
      padding: 1rem;
      border-radius: 8px;
      text-align: center;
      font-size: 1.1rem;
      box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
    form {
      display: inline-block;
      margin: 0.5rem;
    }
    .button-row {
      text-align: center;
    }
    button {
      background-color: #3498db;
      color: white;
      border: none;
      padding: 0.8rem 1.2rem;
      border-radius: 8px;
      font-size: 1rem;
      cursor: pointer;
      transition: background-color 0.2s;
      min-width: 220px;
    }
    button:hover {
      background-color: #2980b9;
    }
    .status-box {
      background-color: #fefefe;
      padding: 1rem;
      border-left: 4px solid #3498db;
      margin-top: 1.5rem;
      font-family: monospace;
      white-space: pre-wrap;
    }
    footer {
      text-align: center;
      margin-top: 2rem;
      font-size: 0.9rem;
      color: #777;
    }

    .logo-wrapper {
        background-color: #3d3d3d;
        padding: 10px;
        border-radius: 15px;
        display: inline-block;
    }

    .logo-image {
        max-width: 100%;
        height: auto;
        border-radius: 15px;
        display: block;
    }

    .logo-link {
    display: block;
    text-decoration: none;
  }
  </style>
</head>
<body>
  <div class="container">
    <div class="logo-wrapper">
      <a href="/" class="logo-link">
        <img src="/static/images/logo.png" alt="Raspberry Pi - Control Panel Logo" class="logo-image">
      </a>
    </div>
    <section>
      <h2>📊 Status systemu</h2>
      <div class="grid">
        <div class="card" id="init-app-card">
            🧩 <b>Usługi</b><br>
            <span id="init-app-status">
              {% if init_app_status == 'active' %}
                Aktywne
              {% elif init_app_status == 'inactive' %}
                Nieaktywne
              {% elif init_app_status == 'failed' %}
                Błąd
              {% else %}
                Nieznany status
              {% endif %}
            </span>
          </div>
          <div class="card">🌡️ <b>Temp CPU</b><br><span id="temp-box">{{ temperatura }}°C</span></div>
          <div class="card">⏱️ <b>Uptime</b><br><span id="uptime-box">{{ uptime }}</span></div>
          <div class="card">📈 <b>CPU</b><br><span id="cpu-box">{{ cpu_load }}</span></div>
          <div class="card">💾 <b>RAM</b><br><span id="ram-box">{{ ram_usage }}</span></div>
          <div class="card">🗂️ <b>HDD</b><br><span id="disk-box">{{ disk_space }}</span></div>
      </div>
    </section>

    <section>
      <h2>🧩 Usługi</h2>
      <div class="button-row">
        <form method="POST" action="/restart_program"><button>🔄 <b>Restartuj program</b></button></form>
        <form method="POST" action="/restart_www"><button>🌐 <b>Restartuj WWW</b></button></form>
      </div>
    </section>

    <section>
      <h2>🔧 Aktualizacje</h2>
      <div class="button-row">
        <form method="POST" action="/update"><button>🔁 <b>Aktualizuj i restartuj program</b></button></form><br><br>
        <form method="POST" action="/update_system"><button>⬇️<br><br><b>Aktualizuj system</b><br>(apt update)</button></form>
        <form method="POST" action="/upgrade_system"><button>📦<br><br><b>Uaktualnij pakiety</b><br>(apt full-upgrade)</button></form>
      </div>
    </section>

    <section>
      <h2>💻 Sprzęt</h2>
      <div class="button-row">
        <form method="POST" action="/reboot"><button>⚡ <b>Restart Raspberry Pi</b></button></form>
      </div>
    </section>

    {% if message %}
      <div class="status-box">
        <strong>Status:</strong><br>
        {{ message }}
      </div>
    {% endif %}

    <footer>
      Bartłomiej Wiórkiewicz<br>Wersja {{ version }}<br>© {{ year }} 
    </footer>
  </div>
  <script>
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
        document.getElementById('temp-box').innerText = data.temperatura + '°C';
        document.getElementById('uptime-box').innerText = data.uptime;
        document.getElementById('cpu-box').innerText = data.cpu_load;
        document.getElementById('ram-box').innerText = data.ram_usage;
        document.getElementById('disk-box').innerText = data.disk_space;
        updateInitAppStatus(data.init_app_status);
      } catch (e) {
        console.error("Błąd pobierania statusu:", e);
      }
    }

    setInterval(fetchStatus, 2000);
  </script>
</body>
</html>
"""


def get_version():
    try:
        version_path = os.path.join(os.path.dirname(__file__), "..", "version.txt")
        with open(version_path, "r") as f:
            return f.read().strip()
    except Exception:
        return "Unknown"


def get_service_status(service_name):
    try:

        output = (
            subprocess.check_output(["systemctl", "is-active", service_name])
            .decode()
            .strip()
        )

        return output

    except:
        return "unknown"


def get_system_status():
    # CPU temperature
    try:
        temp = subprocess.check_output(["vcgencmd", "measure_temp"]).decode()
        temperatura = temp.replace("temp=", "").replace("'C\n", "")
    except:
        temperatura = "N/A"

    # Uptime
    uptime_raw = subprocess.getoutput("uptime -p")
    uptime = uptime_raw.removeprefix("up ").strip()

    # CPU load
    with open("/proc/loadavg", "r") as f:
        cpu_load = f.read().split()[0]

    # RAM usage
    meminfo = subprocess.getoutput("free -m").splitlines()
    mem_parts = meminfo[1].split()
    used = int(mem_parts[2])
    total = int(mem_parts[1])
    ram_usage = f"{used} / {total} MB"

    # Disk usage
    disk_info = subprocess.getoutput("df -h /").splitlines()[1].split()
    disk_space = f"{disk_info[2]} użyto z {disk_info[1]}"

    # Service status
    init_app_status = get_service_status("init_app.service")

    return temperatura, uptime, cpu_load, ram_usage, disk_space, init_app_status


def render_with_status(message):
    temperatura, uptime, cpu_load, ram_usage, disk_space, init_app_status = (
        get_system_status()
    )
    return render_template_string(
        HTML,
        temperatura=temperatura,
        uptime=uptime,
        cpu_load=cpu_load,
        ram_usage=ram_usage,
        disk_space=disk_space,
        init_app_status=init_app_status,
        message=message,
        year=datetime.datetime.now().year,
        version=get_version(),
    )


@app.route("/")
def index():
    temperatura, uptime, cpu_load, ram_usage, disk_space, init_app_status = (
        get_system_status()
    )
    return render_template_string(
        HTML,
        temperatura=temperatura,
        uptime=uptime,
        cpu_load=cpu_load,
        ram_usage=ram_usage,
        disk_space=disk_space,
        init_app_status=init_app_status,
        message=None,
        year=datetime.datetime.now().year,
        version=get_version(),
    )


@app.route("/update", methods=["POST"])
def update():
    try:
        subprocess.Popen(["sudo", "systemctl", "start", "updater.service"])
        return """
      <!DOCTYPE html>
      <html>
      <head>
          <meta http-equiv="refresh" content="10; URL=/" />
          <title>Restartowanie...</title>
          <style>
              body { font-family: sans-serif; text-align: center; margin-top: 5em; }
          </style>
      </head>
      <body>
          <h1>🔄 Aktualizacja w trakcie....</h1>
          <p>Strona automatycznie odświeży się za kilka sekund.</p>
          <p>Jeśli to nie nastąpi, <a href="/">kliknij tutaj</a>.</p>
      </body>
      </html>
      """
    except subprocess.CalledProcessError as e:
        return render_with_status(f"❌ Błąd aktualizacji:\n{e}")


@app.route("/restart_program", methods=["POST"])
def restart_program():
    try:
        subprocess.run(["sudo", "systemctl", "restart", "init_app.service"], check=True)
        msg = "🔄 Program został zrestartowany."
    except subprocess.CalledProcessError as e:
        msg = f"❌ Błąd restartu programu:\n{e}"
    return render_with_status(msg)


@app.route("/restart_www", methods=["POST"])
def restart_www():
    try:
        subprocess.Popen(["sudo", "systemctl", "restart", "webapp.service"])
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <meta http-equiv="refresh" content="2; URL=/" />
            <title>Restartowanie...</title>
            <style>
                body { font-family: sans-serif; text-align: center; margin-top: 5em; }
            </style>
        </head>
        <body>
            <h1>🌐 Restartowanie serwera WWW...</h1>
            <p>Strona automatycznie odświeży się za kilka sekund.</p>
            <p>Jeśli to nie nastąpi, <a href="/">kliknij tutaj</a>.</p>
        </body>
        </html>
        """
    except Exception as e:
        return render_with_status(f"❌ Błąd restartu WWW:\n{e}")


@app.route("/update_system", methods=["POST"])
def update_system():
    try:
        result = subprocess.run(
            ["sudo", "apt", "update"], check=True, capture_output=True, text=True
        )
        msg = "✅ `apt update` zakończone:\n\n" + result.stdout
    except subprocess.CalledProcessError as e:
        msg = f"❌ Błąd podczas `apt update`:\n{e.stderr if e.stderr else str(e)}"
    return render_with_status(msg)


@app.route("/upgrade_system", methods=["POST"])
def upgrade_system():
    try:
        result = subprocess.run(
            ["sudo", "apt", "full-upgrade", "-y"],
            check=True,
            capture_output=True,
            text=True,
        )
        msg = "✅ `apt full-upgrade` zakończone:\n\n" + result.stdout
    except subprocess.CalledProcessError as e:
        msg = f"❌ Błąd podczas `apt full-upgrade`:\n{e.stderr if e.stderr else str(e)}"
    return render_with_status(msg)


@app.route("/reboot", methods=["POST"])
def reboot():
    try:
        subprocess.Popen(["sudo", "reboot"])
        msg = "⚡ Raspberry Pi restartuje się..."
    except Exception as e:
        msg = f"❌ Błąd restartu Raspberry Pi:\n{e}"
    return render_with_status(msg)


@app.route("/status")
def status():
    temperatura, uptime, cpu_load, ram_usage, disk_space, init_app_status = (
        get_system_status()
    )
    return {
        "temperatura": temperatura,
        "uptime": uptime,
        "cpu_load": cpu_load,
        "ram_usage": ram_usage,
        "disk_space": disk_space,
        "init_app_status": init_app_status,
    }


if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=5000)
