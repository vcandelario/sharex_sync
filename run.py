import os
import getpass
from pathlib import Path
import subprocess

serviceName = "sharex_sync"
user = getpass.getuser()
scriptPath = os.path.abspath("main.py")
workDir = os.path.dirname(scriptPath)

serviceContent = f"""[Unit]
Description=Sync ShareX uploads from Google Drive to Google Photos
After=network-online.target
Wants=network-online.target

[Service]
Type=oneshot
WorkingDirectory={workDir}
ExecStart=/usr/bin/python3 {scriptPath}
user={user}
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
"""

timerContent = f"""[Unit]
Description=Run ShareX Google Sync every 15 seconds

[Timer]
OnBootSec=10sec
OnUnitActiveSec=15sec
Unit={serviceName}.service

[Install]
WantedBy=timers.target
"""

def install_systemd_files(systemLevel=False):
    if systemLevel:
        basePath = Path("/etc/systemd/system")
    else:
        basePath = Path.home() / ".config/systemd/user"
        basePath.mkdir(parents=True, exist_ok=True)

    servicePath = basePath / f"{serviceName}.service"
    timerPath = basePath / f"{serviceName}.timer"

    servicePath.write_text(serviceContent)
    timerPath.write_text(timerContent)

    subprocess.run(["systemctl", "--user" if not systemLevel else "", "daemon-reload"])
    subprocess.run(["systemctl", "--user" if not systemLevel else "", "enable", "--now", f"{serviceName}.timer"])

    print(f"Successfully Installed and started {serviceName}.timer")

if __name__ == "__main__":
    try:
        install_systemd_files()
    except PermissionError:
        print("Try running with sudo to install system-level services.")