# 📸 ShareX to Google Photos Sync

Automatically sync images uploaded from ShareX (to Google Drive) into your Google Photos library using a lightweight Python script and systemd.

---

## Features

- Watch a Google Drive folder for new screenshots (uploaded via ShareX)
- Download new files to a temporary folder
- Upload them to Google Photos
- Automatically delete them from Drive and the local temp folder
- Run in the background using a persistent systemd timer

---

## Prerequisites

- Python 3.8+
- A Google Cloud project with Drive & Photos API enabled
- OAuth 2.0 "Desktop App" credentials (`credentials.json` file)
- ShareX configured to upload to a specific Google Drive folder

---

## Setup Instructions

### 1. Enable APIs in Google Cloud Console

- Visit: [Google Cloud Console](https://console.cloud.google.com/)
- Create a project (if you don’t have one)
- Enable:
  - **Google Drive API**
  - **Google Photos Library API**
- Go to **Credentials** → **Create Credentials** → **OAuth Client ID**
  - Application type: **Desktop App**
- Download the resulting `credentials.json`

---

### 2. Clone the repo

```bash
git clone https://github.com/vcandelario/sharex_sync.git
cd sharex_sync
```

Place your `credentials.json` file inside the project folder.

---

### 3. Install and Set Up the Background Service

Run the installer:

```bash
python3 install_service.py
```

This will:

- Create and install a systemd `.service` and `.timer` under your user
- Start the timer (runs every 15 seconds)
- Launch `main.py` interactively for first-time Google auth & folder ID input

---

### 4. Done!

Now every time you upload an image to your chosen Google Drive folder via ShareX, it will:

- Be automatically uploaded to Google Photos
- Deleted from Drive
- Deleted from your server’s temp folder (`/tmp/sharex_photos`)

---

## Troubleshooting

### First-time setup didn’t ask for a token or folder ID?

Just run `main.py` manually once:

```bash
python3 main.py
```

This will trigger the Google OAuth flow and folder ID prompt.

---

### Stop the service and timer

```bash
systemctl --user stop sharex_sync.timer
systemctl --user stop sharex_sync.service
```

To prevent it from running again:

```bash
systemctl --user disable sharex_sync.timer
```

---

## FAQ

### Why not just use ShareX’s Google Photos support?

Google restricted direct Google Photos API access. ShareX would need to verify their app and undergo a security audit which was not feasible for a volunteer project. This script sidesteps the restriction by using your own credentials and Google Drive.

---

## Optional Cleanup

If you ever want to reset:

```bash
rm token.json folderID.txt
```

Then rerun `main.py`.

---

## License

MIT License.
