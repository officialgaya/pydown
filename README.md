

# 📥 YouTube Video, Playlist & Live Downloader

### Built using **Python (Flask)** + **yt-dlp** + **HTML/CSS UI**

This project is a lightweight web-based YouTube Downloader created using **Flask (Python)** for the backend and **HTML/CSS** for the frontend. It allows users to download:

✔️ YouTube **Videos**
✔️ YouTube **Playlists**
✔️ YouTube **Audio (MP3)**
✔️ YouTube **Live Videos** (when supported by yt-dlp)

All downloads are stored in the `downloads/` folder on your server.

> ⚠️ **Important:** This tool is intended for downloading content you own or have permission to download. Do NOT use this to violate YouTube Terms of Service or copyright law.

---

## 🚀 Features

* 🎬 Download **single YouTube videos**
* 🎧 Download **audio only (MP3)**
* 📂 Download **full YouTube playlists**
* 📡 Supports many YouTube **live stream recordings**
* 🖥️ Simple & clean **HTML user interface**
* 📁 Files automatically saved to `/downloads`
* 💫 Fully customizable frontend (HTML/CSS/JS)

---

## 🗂️ Project Structure

```
yt_downloader/
├── app.py
├── requirements.txt
└── templates/
    └── index.html
```

* **app.py** — main Flask backend
* **index.html** — frontend UI
* **downloads/** — will be created automatically to store output

---

## 🛠️ Installation

### 1. Clone or download the project

```
git clone https://github.com/yourusername/yt_downloader.git
cd yt_downloader
```

### 2. Install dependencies

```
pip install -r requirements.txt
```

This installs:

* `Flask`
* `yt-dlp`

---

## ▶️ Running the Application

Start the Flask app:

```
python app.py
```

Then open this in your browser:

```
http://127.0.0.1:5000/
```

Paste a YouTube URL → select **Video / Audio / Playlist** → click **Download**.

---

## 📁 Download Location

All output files go into:

```
downloads/
```

This folder is automatically created if it does not exist.

---

## 🧠 How It Works

The backend uses:

```python
import yt_dlp
```

`yt-dlp` handles:

* video/audio extraction
* playlist downloading
* stream parsing
* conversion (MP3 when using audio mode)

Flask receives the URL from the form and triggers the download function.

The frontend (`index.html`) provides a simple UI built with pure HTML/CSS.

---

## 🎨 Customization

You can edit the frontend in:

```
templates/index.html
```

Feel free to add:

* TailwindCSS
* Bootstrap
* Animations
* Dark themes
* Loading bars
* Progress indicators

---

## 🔒 Security Notes

If deploying online:

✔ Add a password to lock access
✔ Use HTTPS
✔ Host behind a firewall
✔ Limit traffic to prevent abuse

---

## 📜 License

This project is provided for **educational purposes**.
Downloading YouTube content you do not own or have rights to may violate **YouTube’s Terms of Service**.

---

## 👨‍💻 Author

**Gayanath Madusankha**
Founder — *GayanathMadusankha (PVT) LTD*
Sri Lanka


