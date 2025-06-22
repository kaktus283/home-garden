from flask import Flask, render_template, request, redirect
import subprocess
import os
import datetime
import json

app = Flask(__name__)

SETTINGS_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "settings.json")
)


def load_settings():
    try:
        with open(SETTINGS_PATH, "r") as f:
            return json.load(f)
    except Exception:
        return {}


def save_settings(new_data):
    settings = load_settings()
    settings.update(new_data)
    with open(SETTINGS_PATH, "w") as f:
        json.dump(settings, f, indent=2)


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
    return render_template(
        "index.html",
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
    return render_template(
        "index.html",
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


@app.route("/config", methods=["GET", "POST"])
def config():
    settings = load_settings()
    rpi_number = settings.get("device", {}).get("rpi_number", "")
    if isinstance(rpi_number, str) and rpi_number.isdigit():
        rpi_number = int(rpi_number)
    if request.method == "POST":
        rpi_number_form = request.form.get("rpi_number", "")
        try:
            rpi_number_form = int(rpi_number_form)
        except ValueError:
            rpi_number_form = 0

        settings.setdefault("device", {})["rpi_number"] = rpi_number_form
        settings.setdefault("configuration", {})["is_configured"] = True
        save_settings(settings)
        return redirect("/")
    return render_template(
        "config.html",
        rpi_number=rpi_number,
        version=get_version(),
        year=datetime.datetime.now().year,
    )


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


@app.before_request
def check_config():
    if request.endpoint not in ("config", "static"):
        settings = load_settings()
        is_configured = settings.get("configuration", {}).get("is_configured", False)
        if not is_configured:
            return redirect("/config")


if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=5000)
