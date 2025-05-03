# 📸 ShareX → Google Photos Sync

Automatically sync screenshots uploaded via [ShareX](https://getsharex.com/) to a specific Google Drive folder and upload them to Google Photos — entirely from a headless Linux server using Python and systemd.

---

## 🚀 How It Works

1. ShareX uploads screenshots to **Google Drive** (via Google Drive destination).
2. This script:
   - Detects images in a **specified Drive folder**
   - Downloads them to your **Linux server**
   - Uploads them to **Google Photos**
   - Cleans up both **Drive** and **local disk**
3. A `systemd` timer runs the script every 15 seconds for near real-time sync.

---

## 🔧 Requirements

- Python 3.8+
- A headless Linux server (local or VPS)
- A Google account
- A Google Cloud project

---

## 📁 Folder Structure

```
sharex_sync/
├── main.py              # The main sync script
├── credentials.json     # Google Cloud OAuth credentials (Desktop type)
├── token.json           # Auto-generated after first run
└── systemd/
    ├── sharex_sync.service
    └── sharex_sync.timer
```

---

## 🧰 Setup Instructions

### 1. Create Google Cloud Project & Credentials

1. Visit [Google Cloud Console](https://console.cloud.google.com/)
2. Enable these APIs:
   - **Google Drive API**
   - **Google Photos Library API**
3. Go to **APIs & Services → Credentials**
4. Click **“Create Credentials” → OAuth Client ID**
5. Choose **“Desktop App”**
6. Download the `credentials.json` and place it in your project folder

---

### 2. Install Dependencies

```bash
pip install --upgrade google-auth google-auth-oauthlib google-api-python-client requests
```

---

### 3. First-Time Authentication

Run:

```bash
python3 main.py
```

- You'll get a link. Open it on any browser (on any device).
- Log in and grant access.
- Paste the code back into the terminal.
- A `token.json` file will be created to persist credentials.

---

### 4. Configure the Script

Open `main.py` and update:

```python
FOLDER_ID = 'your_google_drive_folder_id'
```

- Get the folder ID from the URL:
  ```
  https://drive.google.com/drive/folders/<FOLDER_ID>
  ```

---

## 🖥️ Automation with systemd

### 1. Create Service

```ini
# /etc/systemd/system/sharex_sync.service

[Unit]
Description=Sync ShareX uploads from Google Drive to Google Photos
After=network-online.target
Wants=network-online.target

[Service]
Type=oneshot
WorkingDirectory=/home/youruser/path/to/sharex_sync
ExecStart=/usr/bin/python3 /home/youruser/path/to/sharex_sync/main.py
User=youruser
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
```

---

### 2. Create Timer

```ini
# /etc/systemd/system/sharex_sync.timer

[Unit]
Description=Run ShareX Google Sync every 15 seconds

[Timer]
OnBootSec=10sec
OnUnitActiveSec=15sec
Unit=sharex_sync.service

[Install]
WantedBy=timers.target
```

---

### 3. Enable and Start

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now sharex_sync.timer
```

---

## 📋 FAQ

### 💡 Why not upload directly to Google Photos?

Google's new API policies no longer allow third-party tools (like ShareX) to upload directly to Google Photos. This script bridges that gap.

### 🔐 Is my Google account secure?

Yes. The credentials are stored locally and never leave your machine. Access tokens are securely managed by Google’s official SDK.

### ⏱️ Can I change the sync interval?

Yes — just edit the `sharex_sync.timer` file. 15 seconds is the shortest practical interval for near real-time behavior.

---

## ✅ To-Do / Future Features

- ✅ Retry logic for upload failures
- ⏳ Upload to a specific Google Photos album
- ⏳ ShareX script to automate Drive upload folder selection
- ⏳ Telegram or email notifications

---

## 📄 License

MIT License. Use freely, modify, and contribute!
