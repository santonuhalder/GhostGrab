<div align="center">

```
 ██████╗ ██╗  ██╗ ██████╗ ███████╗████████╗ ██████╗ ██████╗  █████╗ ██████╗
██╔════╝ ██║  ██║██╔═══██╗██╔════╝╚══██╔══╝██╔════╝ ██╔══██╗██╔══██╗██╔══██╗
██║  ███╗███████║██║   ██║███████╗   ██║   ██║  ███╗██████╔╝███████║██████╔╝
██║   ██║██╔══██║██║   ██║╚════██║   ██║   ██║   ██║██╔══██╗██╔══██║██╔══██╗
╚██████╔╝██║  ██║╚██████╔╝███████║   ██║   ╚██████╔╝██║  ██║██║  ██║██████╔╝
 ╚═════╝ ╚═╝  ╚═╝ ╚═════╝ ╚══════╝   ╚═╝    ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═════╝
```

### 👻 Download private Telegram videos & media in original quality.
### Also supports **1800+ websites** — silently, swiftly, completely.

<br/>

[![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-0078D4?style=for-the-badge&logo=windows&logoColor=white)](https://github.com/santonuhalder/GhostGrab)
[![License](https://img.shields.io/github/license/santonuhalder/GhostGrab?style=for-the-badge&color=brightgreen)](LICENSE)
[![Stars](https://img.shields.io/github/stars/santonuhalder/GhostGrab?style=for-the-badge&color=yellow&logo=github)](https://github.com/santonuhalder/GhostGrab/stargazers)
[![Forks](https://img.shields.io/github/forks/santonuhalder/GhostGrab?style=for-the-badge&color=orange&logo=github)](https://github.com/santonuhalder/GhostGrab/network/members)

</div>

---

## 🌑 What is GhostGrab?

**GhostGrab** is a powerful, feature-packed media downloader built for people who need more than the average tool can offer. It combines the raw downloading capability of **yt-dlp** with full **Telegram API integration via Telethon**, wrapped inside a sleek, dark **CustomTkinter GUI** — giving you a desktop-grade experience without ever touching the command line.

Whether you're trying to save a video from a **private Telegram group**, pull content off **YouTube, TikTok, Instagram, Twitter**, or grab media from any of **1800+ supported platforms**, GhostGrab handles it all — in **original quality**, with **zero watermarks**, and **zero compromise**.

> *Ghost in. Grab it. Get out.*

---

## ✨ Features

| Category | Details |
|---|---|
| 👻 **Private Telegram** | Download from private groups, channels, and DMs using your own API credentials |
| 🌐 **1800+ Sites** | YouTube, TikTok, Instagram, Twitter/X, Reddit, Vimeo, Facebook, Dailymotion & more |
| 🎯 **Original Quality** | Always downloads in the best available resolution — no re-encoding, no loss |
| 📦 **Batch Downloads** | Paste multiple URLs and let GhostGrab queue and handle them all |
| 📊 **Live Progress Bar** | Real-time download progress with MB counter — right inside the GUI |
| 🍪 **Cookies Support** | Bypass login walls using your browser's exported cookies file |
| 🌐 **Proxy Support** | Route all traffic through your preferred proxy for privacy or geo-unblocking |
| 🔐 **2FA Support** | Full two-factor authentication support for secure Telegram account access |
| 🖤 **Modern Dark GUI** | Beautiful, responsive dark-mode interface built with CustomTkinter |
| 💾 **Session Saved** | Connect Telegram once — credentials and session saved, never asked again |

---

## ⚙️ How It Works

**Step 1 — 🔗 Paste Your URL**
Drop in a single link or a batch of URLs — Telegram links, YouTube, Instagram, or any of the 1800+ supported sites.

**Step 2 — 🛠️ Configure Your Options**
Choose your output folder, set quality preferences, load cookies or a proxy if needed. For Telegram, enter your API credentials once and you're permanently set.

**Step 3 — 👻 GhostGrab Does the Rest**
Hit **Download** and watch the progress bar fill up. Your media arrives in original quality, organized and ready.

---

## 📋 Requirements

- **Python** `3.9` or higher
- **pip** (comes with Python)
- A **Telegram account** *(only required for Telegram downloads)*

### Python Dependencies

```
customtkinter
yt-dlp
telethon
requests
Pillow
```

> All dependencies are listed in `requirements.txt` and install with a single command.

---

## 🚀 Installation

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/santonuhalder/GhostGrab.git
cd GhostGrab
```

### 2️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

> **Linux users** — also install tkinter if not already present:
> ```bash
> sudo apt install python3-tk
> ```

### 3️⃣ Launch GhostGrab

```bash
python ghostgrab.py
```

> 💡 **Windows tip:** Double-click `ghostgrab.py` if Python is in your PATH, or create a `.bat` file:
> ```bat
> @echo off
> python ghostgrab.py
> pause
> ```

---

## 📡 Telegram Setup

To download from **private Telegram groups and channels**, you need your own free Telegram API credentials. This is a **one-time, 2-minute setup**.

> ⚠️ These credentials are **yours** — they authorize GhostGrab to act as your Telegram client. Never share your `api_id` or `api_hash` with anyone.

---

**Step 1** — Go to [https://my.telegram.org/apps](https://my.telegram.org/apps) and log in with your Telegram phone number.

**Step 2** — Click **"API development tools"**.

**Step 3** — Click **"Create new application"** and fill in the form:
- **App title:** GhostGrab *(or anything)*
- **Short name:** ghostgrab
- **Platform:** Desktop

**Step 4** — Submit. You'll receive:
- `api_id` — a short numeric ID (e.g. `12345678`)
- `api_hash` — a long alphanumeric string

**Step 5** — Open GhostGrab → **📡 Telegram** tab → enter your `api_id`, `api_hash`, and phone number.

**Step 6** — Click **Connect** → enter the verification code Telegram sends to your phone → done.

✅ **Connected. Session saved. Never asked again.**

Now paste any private `t.me` link in the Download tab and hit Download.

```
Supported Telegram URL formats:
  https://t.me/c/1234567890/42    ← private channel message
  https://t.me/channelname/99     ← public channel message
```

---

## 🌍 Supported Sites

GhostGrab supports **1800+ websites** via yt-dlp. Here are some of the most popular:

<div align="center">

| 🎬 Video | 📸 Social | 🎵 Music | 🗣️ Other |
|---|---|---|---|
| YouTube | Instagram | SoundCloud | Reddit |
| Vimeo | Twitter / X | Bandcamp | Dailymotion |
| TikTok | Facebook | Mixcloud | Twitch |
| Bilibili | Snapchat | Audiomack | Rumble |
| Odysee | Pinterest | YouTube Music | PeerTube |
| **Telegram** | LinkedIn | Spotify* | **1800+ more…** |

</div>

> \* Audio extraction only where permitted.

For the full list of supported sites, run:
```bash
yt-dlp --list-extractors
```

---

## 🖼️ Screenshots

<div align="center">

> 📸 **Screenshots coming soon**

![Dark Modern GUI](https://img.shields.io/badge/UI-Dark%20Modern%20GUI-1a1a2e?style=for-the-badge&logo=windows-terminal&logoColor=white)
![Built with CustomTkinter](https://img.shields.io/badge/Built%20with-CustomTkinter-5C5CFF?style=for-the-badge&logo=python&logoColor=white)
![Telegram Ready](https://img.shields.io/badge/Telegram-Private%20Download-26A5E4?style=for-the-badge&logo=telegram&logoColor=white)

*A clean, minimal dark interface — no clutter, just results.*

</div>

---

## 🔧 Configuration

### 🍪 Cookies — Bypass Login Walls

Some platforms require you to be logged in (Instagram, Twitter/X, YouTube members, OnlyFans, etc). Export your browser cookies and point GhostGrab to them:

```
⚙ Settings tab → Cookies file → Browse → Select cookies.txt
```

To export cookies, use the **"Get cookies.txt LOCALLY"** browser extension (available for Chrome and Firefox).

---

### 🌐 Proxy

Route your traffic through a proxy for privacy or geo-unblocking:

```
⚙ Settings tab → Proxy → Enter proxy URL
```

Supported formats:
```
http://user:pass@host:port
socks5://host:port
socks5://127.0.0.1:1080
```

---

### 🎯 Quality Options

| Option | Description |
|---|---|
| `Best` | Highest available resolution *(default, recommended)* |
| `4K / 2160p` | Ultra HD — only if the source has it |
| `1080p` | Full HD |
| `720p` | HD |
| `480p` | Standard |
| `Audio Only` | Extracts audio as MP3 |

---

## ❓ FAQ

<details>
<summary><b>🤔 Is GhostGrab safe to use with my Telegram account?</b></summary>

Yes. GhostGrab uses the **official Telegram MTProto API** through Telethon. Your credentials are stored locally on your machine and never transmitted anywhere except Telegram's own servers. Think of it as a third-party Telegram client — exactly like Telegram Desktop works.

</details>

<details>
<summary><b>🤔 Why does it ask for a verification code on first login?</b></summary>

Telegram requires identity verification the first time a new client connects. Enter the code sent to your Telegram app or SMS. If you have **2FA enabled**, you'll also need your cloud password. After the first login, a session file is saved locally — you won't need to log in again.

</details>

<details>
<summary><b>🤔 A site I want to download from isn't working — what do I do?</b></summary>

First, make sure yt-dlp is up to date:
```bash
pip install -U yt-dlp
```
Extractors are updated frequently. If it still doesn't work, [open an issue](https://github.com/santonuhalder/GhostGrab/issues) with the URL and the error message from the log box.

</details>

---

## 👤 Author

<div align="center">

### Santonu Halder

[![GitHub](https://img.shields.io/badge/GitHub-@santonuhalder-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/santonuhalder)

*If GhostGrab saved you time or helped you out — drop a ⭐ on the repo.*
*It means more than you know.*

</div>

---

## ⚠️ Disclaimer

**GhostGrab is intended for personal, educational, and archival use only.**

- Only download content you have the **legal right** to access or own.
- The author is **not responsible** for any misuse, ToS violations, or copyright infringement caused by use of this tool.
- Downloading **copyrighted content without permission** may be illegal in your country.
- Use of Telegram API credentials is governed by [Telegram's Terms of Service](https://core.telegram.org/api/terms).
- This tool is **not affiliated with** Telegram, YouTube, TikTok, or any other platform it supports.

> Always use responsibly. 👻

---

## 📄 License

```
MIT License

Copyright (c) 2025 Santonu Halder

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
```

---

<div align="center">

**Made with 🖤 by [Santonu Halder](https://github.com/santonuhalder)**

*Ghost in. Grab it. Get out.*

[![Star this repo](https://img.shields.io/github/stars/santonuhalder/GhostGrab?style=social)](https://github.com/santonuhalder/GhostGrab)

</div>
