#!/usr/bin/env python3
"""
GhostGrab - Private Telegram Video Downloader
Author  : Santonu Halder
GitHub  : https://github.com/santonuhalder
Version : 1.0.0
"""

import os, sys, threading, asyncio, json, subprocess, re, webbrowser
from pathlib import Path
from datetime import datetime

import customtkinter as ctk
from tkinter import filedialog, messagebox
import tkinter as tk

# ── Windows asyncio fix ──────────────────────────────────────────────────────
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# ── App constants ────────────────────────────────────────────────────────────
APP_NAME    = "GhostGrab"
APP_VERSION = "1.0.0"
APP_AUTHOR  = "Santonu Halder"
APP_GITHUB  = "https://github.com/santonuhalder/GhostGrab"
APP_EMAIL   = "santonuhalder@github"

CONFIG_FILE    = Path.home() / ".ghostgrab_config.json"
DEFAULT_OUTPUT = str(Path.home() / "Downloads" / "GhostGrab")


# ─── config ──────────────────────────────────────────────────────────────────
def load_config():
    if CONFIG_FILE.exists():
        try:
            return json.loads(CONFIG_FILE.read_text())
        except Exception:
            pass
    return {"output_dir": DEFAULT_OUTPUT, "tg_api_id": "", "tg_api_hash": "",
            "tg_phone": "", "quality": "Best", "format": "mp4",
            "cookies_file": "", "concur": "5", "proxy": ""}

def save_config(cfg):
    CONFIG_FILE.write_text(json.dumps(cfg, indent=2))


# ─── helper scripts ──────────────────────────────────────────────────────────
TG_CONNECT_SCRIPT = """
import sys, asyncio, os

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

async def main():
    try:
        from telethon import TelegramClient
        from telethon.errors import SessionPasswordNeededError

        api_id   = int(sys.argv[1])
        api_hash = sys.argv[2]
        phone    = sys.argv[3]
        session  = sys.argv[4]
        otp_file = sys.argv[5]

        client = TelegramClient(session, api_id, api_hash)
        print("STATUS:connecting", flush=True)
        await client.connect()

        if not await client.is_user_authorized():
            print("STATUS:sending_code", flush=True)
            await client.send_code_request(phone)
            print("STATUS:waiting_otp", flush=True)

            for _ in range(240):
                if os.path.exists(otp_file):
                    code = open(otp_file).read().strip()
                    os.remove(otp_file)
                    break
                await asyncio.sleep(0.5)
            else:
                print("ERROR:Timed out waiting for code (120s). Please try again.", flush=True)
                await client.disconnect()
                return

            try:
                await client.sign_in(phone, code)
            except SessionPasswordNeededError:
                print("STATUS:2fa_needed", flush=True)
                for _ in range(240):
                    if os.path.exists(otp_file):
                        pw = open(otp_file).read().strip()
                        os.remove(otp_file)
                        break
                    await asyncio.sleep(0.5)
                else:
                    print("ERROR:Timed out waiting for 2FA password.", flush=True)
                    await client.disconnect()
                    return
                await client.sign_in(password=pw)
            except Exception as ex:
                print(f"ERROR:{ex}", flush=True)
                await client.disconnect()
                return

        me   = await client.get_me()
        name = f"{me.first_name or ''} {me.last_name or ''}".strip()
        user = me.username or ""
        print(f"OK:{name}:{user}", flush=True)
        await client.disconnect()

    except Exception as ex:
        print(f"ERROR:{ex}", flush=True)
        sys.exit(1)

asyncio.run(main())
"""

TG_DOWNLOAD_SCRIPT = """
import sys, asyncio, os, re

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

async def main():
    try:
        from telethon import TelegramClient, tl

        api_id   = int(sys.argv[1])
        api_hash = sys.argv[2]
        session  = sys.argv[3]
        url      = sys.argv[4]
        outdir   = sys.argv[5]

        client = TelegramClient(session, api_id, api_hash)
        await client.connect()

        if not await client.is_user_authorized():
            print("ERROR:Not logged in. Connect Telegram first.", flush=True)
            await client.disconnect()
            return

        m = re.match(r"https?://t\\.me/c/(\\d+)/(\\d+)", url)
        if m:
            entity = await client.get_entity(tl.types.PeerChannel(int(m.group(1))))
            msg_id = int(m.group(2))
        else:
            m = re.match(r"https?://t\\.me/([^/]+)/(\\d+)", url)
            if m:
                entity = await client.get_entity(m.group(1))
                msg_id = int(m.group(2))
            else:
                print(f"ERROR:Cannot parse URL: {url}", flush=True)
                await client.disconnect()
                return

        msg = await client.get_messages(entity, ids=msg_id)
        if msg is None or not msg.media:
            print("ERROR:No media found in that message.", flush=True)
            await client.disconnect()
            return

        from telethon.tl.types import DocumentAttributeVideo, DocumentAttributeFilename
        fname = f"tg_{msg_id}.mp4"
        if hasattr(msg.media, "document") and msg.media.document:
            for attr in msg.media.document.attributes:
                if isinstance(attr, DocumentAttributeFilename):
                    fname = attr.file_name; break
                if isinstance(attr, DocumentAttributeVideo):
                    fname = f"tg_video_{msg_id}.mp4"
        elif hasattr(msg.media, "photo"):
            fname = f"tg_photo_{msg_id}.jpg"

        os.makedirs(outdir, exist_ok=True)
        outpath = os.path.join(outdir, fname)
        print(f"FILE:{fname}", flush=True)

        last_pct = -1
        def cb(cur, tot):
            nonlocal last_pct
            if not tot: return
            pct = int(cur / tot * 100)
            if pct != last_pct:
                last_pct = pct
                mb_cur = cur / 1048576
                mb_tot = tot / 1048576
                print(f"PROGRESS:{pct}:{mb_cur:.1f}:{mb_tot:.1f}", flush=True)

        await client.download_media(msg, outpath, progress_callback=cb)
        print(f"DONE:{outpath}", flush=True)
        await client.disconnect()

    except Exception as ex:
        print(f"ERROR:{ex}", flush=True)
        sys.exit(1)

asyncio.run(main())
"""


def write_helper_scripts():
    d = Path.home() / ".ghostgrab_helpers"
    d.mkdir(exist_ok=True)
    (d / "tg_connect.py").write_text(TG_CONNECT_SCRIPT)
    (d / "tg_download.py").write_text(TG_DOWNLOAD_SCRIPT)
    return d


HELPERS = write_helper_scripts()


# ═══════════════════════════════════════════════════════════════════════════════
class GhostGrab(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.cfg            = load_config()
        self.is_downloading = False
        self._stop_event    = threading.Event()
        self._tg_connected  = bool(self.cfg.get("_tg_name", ""))
        self._otp_file      = str(Path.home() / ".ghostgrab_otp.tmp")

        self.title(f"👻 {APP_NAME} v{APP_VERSION} — Private Telegram Video Downloader")
        self.geometry("1020x820")
        self.minsize(880, 700)
        self._build_ui()

    # ══════════════ TOP-LEVEL UI ══════════════════════════════════════════════
    def _build_ui(self):
        self.status_var = ctk.StringVar(value="Ready.")

        # ── Header bar
        hdr = ctk.CTkFrame(self, height=62, corner_radius=0, fg_color="#0d1117")
        hdr.pack(fill="x")
        hdr.pack_propagate(False)

        ctk.CTkLabel(hdr, text="👻",
                     font=ctk.CTkFont("Segoe UI", 26)).pack(side="left", padx=(16, 4), pady=10)
        ctk.CTkLabel(hdr, text="GhostGrab",
                     font=ctk.CTkFont("Segoe UI", 22, "bold"),
                     text_color="#58a6ff").pack(side="left", pady=10)
        ctk.CTkLabel(hdr, text=f"v{APP_VERSION}",
                     font=ctk.CTkFont("Segoe UI", 11),
                     text_color="#3fb950").pack(side="left", padx=(6, 16), pady=10)
        ctk.CTkLabel(hdr, text="Private Telegram Video Downloader  ·  1800+ Sites",
                     font=ctk.CTkFont("Segoe UI", 12),
                     text_color="#8b949e").pack(side="left", pady=10)

        # Telegram pill (right side)
        self.tg_pill_var = ctk.StringVar()
        self.tg_pill = ctk.CTkLabel(hdr, textvariable=self.tg_pill_var,
                                    fg_color="#21262d", corner_radius=12,
                                    font=ctk.CTkFont("Segoe UI", 11),
                                    text_color="#8b949e", padx=12, pady=4)
        self.tg_pill.pack(side="right", padx=14)

        # ── Tabs
        self.tabs = ctk.CTkTabview(self, corner_radius=10)
        self.tabs.pack(fill="both", expand=True, padx=14, pady=(8, 4))
        for t in ["⬇  Download", "📡  Telegram", "⚙  Settings", "👤  About", "ℹ  Help"]:
            self.tabs.add(t)

        self._build_download_tab(self.tabs.tab("⬇  Download"))
        self._build_telegram_tab(self.tabs.tab("📡  Telegram"))
        self._build_settings_tab(self.tabs.tab("⚙  Settings"))
        self._build_about_tab(self.tabs.tab("👤  About"))
        self._build_help_tab(self.tabs.tab("ℹ  Help"))

        # ── Status bar
        ctk.CTkLabel(self, textvariable=self.status_var,
                     font=ctk.CTkFont("Consolas", 11),
                     text_color="#8b949e", anchor="w").pack(fill="x", padx=18, pady=(2, 6))

        self._refresh_tg_pill()

    # ══════════════ DOWNLOAD TAB ══════════════════════════════════════════════
    def _build_download_tab(self, p):
        p.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(p, text="Paste Your Link Here:",
                     font=ctk.CTkFont("Segoe UI", 13, "bold"),
                     anchor="w").grid(row=0, column=0, sticky="w", padx=12, pady=(14, 2))

        url_row = ctk.CTkFrame(p, fg_color="transparent")
        url_row.grid(row=1, column=0, sticky="ew", padx=12)
        url_row.grid_columnconfigure(0, weight=1)

        self.url_var = ctk.StringVar()
        self.url_entry = ctk.CTkEntry(
            url_row, textvariable=self.url_var,
            placeholder_text="https://t.me/c/...   or   https://youtube.com/...   or   any site URL",
            height=44, font=ctk.CTkFont("Consolas", 13))
        self.url_entry.grid(row=0, column=0, sticky="ew", padx=(0, 6))
        self.url_var.trace_add("write", self._on_url_change)

        ctk.CTkButton(url_row, text="📋 Paste", width=88, height=44,
                      command=self._paste_url).grid(row=0, column=1)

        # Telegram banner (shown when t.me link detected and not connected)
        self.tg_banner = ctk.CTkFrame(p, fg_color="#2d1b00", corner_radius=8)
        self.tg_banner.grid(row=2, column=0, sticky="ew", padx=12, pady=(6, 0))
        self.tg_banner.grid_columnconfigure(0, weight=1)
        self.tg_banner.grid_remove()

        ctk.CTkLabel(self.tg_banner,
                     text="📡  Telegram link detected — connect Telegram first (2 min setup).",
                     font=ctk.CTkFont("Segoe UI", 12), text_color="#e3b341",
                     anchor="w").grid(row=0, column=0, sticky="w", padx=12, pady=(8, 2))
        ctk.CTkButton(self.tg_banner, text="➜  Open Telegram Setup",
                      fg_color="#9e6a03", hover_color="#bb8009", height=32,
                      font=ctk.CTkFont("Segoe UI", 12, "bold"),
                      command=lambda: self.tabs.set("📡  Telegram")).grid(
            row=1, column=0, sticky="w", padx=12, pady=(2, 10))

        # Batch URLs
        ctk.CTkLabel(p, text="Batch — multiple links (one per line):",
                     font=ctk.CTkFont("Segoe UI", 12), anchor="w").grid(
            row=3, column=0, sticky="w", padx=12, pady=(10, 2))
        self.batch_box = ctk.CTkTextbox(p, height=68, font=ctk.CTkFont("Consolas", 12))
        self.batch_box.grid(row=4, column=0, sticky="ew", padx=12)
        self.batch_box.insert("1.0", "# Extra links here, one per line")

        # Options row
        opt = ctk.CTkFrame(p, fg_color="transparent")
        opt.grid(row=5, column=0, sticky="ew", padx=12, pady=10)

        ctk.CTkLabel(opt, text="Quality:", font=ctk.CTkFont("Segoe UI", 12)).pack(side="left")
        self.quality_var = ctk.StringVar(value=self.cfg.get("quality", "Best"))
        ctk.CTkOptionMenu(opt,
            values=["Best", "4K / 2160p", "1440p", "1080p", "720p", "480p", "360p", "Audio Only"],
            variable=self.quality_var, width=140).pack(side="left", padx=(4, 16))

        ctk.CTkLabel(opt, text="Format:", font=ctk.CTkFont("Segoe UI", 12)).pack(side="left")
        self.fmt_var = ctk.StringVar(value=self.cfg.get("format", "mp4"))
        ctk.CTkOptionMenu(opt,
            values=["mp4", "mkv", "webm", "mov", "mp3", "m4a", "original"],
            variable=self.fmt_var, width=100).pack(side="left", padx=(4, 16))

        self.subs_var  = ctk.BooleanVar(value=False)
        self.thumb_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(opt, text="Subtitles", variable=self.subs_var).pack(side="left", padx=6)
        ctk.CTkCheckBox(opt, text="Thumbnail", variable=self.thumb_var).pack(side="left", padx=6)

        # Save-to row
        out = ctk.CTkFrame(p, fg_color="transparent")
        out.grid(row=6, column=0, sticky="ew", padx=12, pady=(0, 8))
        out.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(out, text="Save to:", font=ctk.CTkFont("Segoe UI", 12)).grid(row=0, column=0, padx=(0, 6))
        self.outdir_var = ctk.StringVar(value=self.cfg.get("output_dir", DEFAULT_OUTPUT))
        ctk.CTkEntry(out, textvariable=self.outdir_var, height=36,
                     font=ctk.CTkFont("Consolas", 12)).grid(row=0, column=1, sticky="ew", padx=(0, 6))
        ctk.CTkButton(out, text="📁 Browse", width=90, height=36,
                      command=self._browse_output).grid(row=0, column=2)

        # Action buttons
        btns = ctk.CTkFrame(p, fg_color="transparent")
        btns.grid(row=7, column=0, pady=8)

        self.dl_btn = ctk.CTkButton(btns, text="⬇  Download", width=210, height=48,
            font=ctk.CTkFont("Segoe UI", 15, "bold"),
            fg_color="#238636", hover_color="#2ea043",
            command=self._start_download)
        self.dl_btn.pack(side="left", padx=8)

        self.stop_btn = ctk.CTkButton(btns, text="⏹ Stop", width=110, height=48,
            fg_color="#da3633", hover_color="#f85149",
            state="disabled", command=self._stop_download)
        self.stop_btn.pack(side="left", padx=8)

        ctk.CTkButton(btns, text="📂 Open Folder", width=150, height=48,
            fg_color="#30363d", hover_color="#484f58",
            command=self._open_folder).pack(side="left", padx=8)

        # Progress
        self.progress_bar = ctk.CTkProgressBar(p, height=10, corner_radius=6)
        self.progress_bar.grid(row=8, column=0, sticky="ew", padx=12, pady=(4, 2))
        self.progress_bar.set(0)

        self.progress_label = ctk.CTkLabel(p, text="", anchor="w",
                                           font=ctk.CTkFont("Consolas", 11),
                                           text_color="#3fb950")
        self.progress_label.grid(row=9, column=0, sticky="w", padx=14)

        # Log box
        ctk.CTkLabel(p, text="Log:", font=ctk.CTkFont("Segoe UI", 12), anchor="w").grid(
            row=10, column=0, sticky="w", padx=12, pady=(6, 2))
        self.log_box = ctk.CTkTextbox(p, height=150, font=ctk.CTkFont("Consolas", 11),
                                      fg_color="#0d1117", text_color="#e6edf3")
        self.log_box.grid(row=11, column=0, sticky="ew", padx=12, pady=(0, 10))
        self._log(f"👻 {APP_NAME} v{APP_VERSION} Ready — Paste A URL And Hit Download.")

    # ══════════════ TELEGRAM TAB ══════════════════════════════════════════════
    def _build_telegram_tab(self, p):
        p.grid_columnconfigure(0, weight=1)
        p.grid_rowconfigure(0, weight=1)

        scroll = ctk.CTkScrollableFrame(p, fg_color="transparent",
                                        scrollbar_button_color="#30363d",
                                        scrollbar_button_hover_color="#484f58")
        scroll.grid(row=0, column=0, sticky="nsew")
        scroll.grid_columnconfigure(0, weight=1)
        p = scroll  # redirect all widgets into scroll

        # Status banner
        self._tg_banner_frame = ctk.CTkFrame(p, corner_radius=10, fg_color="#161b22")
        self._tg_banner_frame.grid(row=0, column=0, sticky="ew", padx=12, pady=(12, 8))
        self._tg_banner_frame.grid_columnconfigure(0, weight=1)

        self._tg_banner_icon  = ctk.CTkLabel(self._tg_banner_frame, text="",
                                              font=ctk.CTkFont("Segoe UI", 28))
        self._tg_banner_icon.grid(row=0, column=0, pady=(14, 2))
        self._tg_banner_title = ctk.CTkLabel(self._tg_banner_frame, text="",
                                              font=ctk.CTkFont("Segoe UI", 16, "bold"))
        self._tg_banner_title.grid(row=1, column=0)
        self._tg_banner_sub   = ctk.CTkLabel(self._tg_banner_frame, text="",
                                              font=ctk.CTkFont("Segoe UI", 11),
                                              text_color="#8b949e")
        self._tg_banner_sub.grid(row=2, column=0, pady=(2, 14))

        # Step 1
        s1 = self._step_card(p, "1", "Get your free API key  (30 seconds, one-time)",
                             "Go to my.telegram.org → sign in → API development tools → Create app\n"
                             "Copy the  API ID  and  API Hash  shown.", row=1)
        ctk.CTkButton(s1, text="🌐  Open my.telegram.org/apps",
                      fg_color="#1f6feb", hover_color="#388bfd", height=38,
                      font=ctk.CTkFont("Segoe UI", 12, "bold"),
                      command=lambda: webbrowser.open("https://my.telegram.org/apps")).grid(
            row=2, column=0, columnspan=2, padx=14, pady=(2, 14), sticky="w")

        # Step 2
        s2 = self._step_card(p, "2", "Enter your credentials",
                             "Paste API ID, API Hash, and your phone number with country code.", row=2)
        self._tg_vars = {}
        for i, (lbl, key, ph, hide) in enumerate([
            ("API ID",   "tg_api_id",   "e.g. 12345678",                   False),
            ("API Hash", "tg_api_hash", "e.g. 0123456789abcdef...",         True),
            ("Phone",    "tg_phone",    "+1 555 555 5555  (with +country)", False),
        ]):
            ctk.CTkLabel(s2, text=lbl + ":", font=ctk.CTkFont("Segoe UI", 12, "bold"),
                         anchor="w").grid(row=3+i*2, column=0, columnspan=2,
                                          sticky="w", padx=14, pady=(8, 2))
            var = ctk.StringVar(value=self.cfg.get(key, ""))
            self._tg_vars[key] = var
            ctk.CTkEntry(s2, textvariable=var, placeholder_text=ph,
                         height=38, show="*" if hide else "",
                         font=ctk.CTkFont("Consolas", 13)).grid(
                row=4+i*2, column=0, columnspan=2, sticky="ew", padx=14)

        # Step 3
        s3 = self._step_card(p, "3", "Connect — Telegram sends a code to your phone",
                             "Click Connect, then enter the verification code that arrives.", row=3)

        self.connect_btn = ctk.CTkButton(s3, text="🔗  Connect to Telegram",
            fg_color="#238636", hover_color="#2ea043", height=44,
            font=ctk.CTkFont("Segoe UI", 13, "bold"),
            command=self._connect_telegram)
        self.connect_btn.grid(row=10, column=0, columnspan=2, padx=14, pady=(6, 8), sticky="w")

        # Telegram log textbox
        self.tg_log_box = ctk.CTkTextbox(s3, height=84,
                                          font=ctk.CTkFont("Consolas", 11),
                                          fg_color="#0d1117", text_color="#e6edf3")
        self.tg_log_box.grid(row=11, column=0, columnspan=2, sticky="ew", padx=14, pady=(0, 6))
        self.tg_log_box.configure(state="disabled")

        # OTP input (hidden)
        self.otp_outer = ctk.CTkFrame(s3, fg_color="#0d2818", corner_radius=8)
        self.otp_outer.grid(row=12, column=0, columnspan=2, sticky="ew", padx=14, pady=(0, 8))
        self.otp_outer.grid_remove()
        ctk.CTkLabel(self.otp_outer,
                     text="📲  Enter the code Telegram sent to your phone:",
                     font=ctk.CTkFont("Segoe UI", 12, "bold"),
                     text_color="#3fb950").grid(row=0, column=0, columnspan=2,
                                                sticky="w", padx=12, pady=(10, 6))
        self.otp_var   = ctk.StringVar()
        self.otp_entry = ctk.CTkEntry(self.otp_outer, textvariable=self.otp_var,
                                      placeholder_text="e.g. 12345",
                                      width=180, height=44,
                                      font=ctk.CTkFont("Consolas", 20))
        self.otp_entry.grid(row=1, column=0, padx=(12, 8), pady=(0, 12))
        ctk.CTkButton(self.otp_outer, text="✔  Submit Code", width=140, height=44,
                      fg_color="#238636", hover_color="#2ea043",
                      font=ctk.CTkFont("Segoe UI", 13, "bold"),
                      command=self._submit_otp).grid(row=1, column=1, padx=(0, 12), pady=(0, 12), sticky="w")
        self.otp_entry.bind("<Return>", lambda _: self._submit_otp())

        # 2FA input (hidden)
        self.twofa_outer = ctk.CTkFrame(s3, fg_color="#1a0d2e", corner_radius=8)
        self.twofa_outer.grid(row=13, column=0, columnspan=2, sticky="ew", padx=14, pady=(0, 14))
        self.twofa_outer.grid_remove()
        ctk.CTkLabel(self.twofa_outer,
                     text="🔑  Two-step verification (2FA) password:",
                     font=ctk.CTkFont("Segoe UI", 12, "bold"),
                     text_color="#d2a8ff").grid(row=0, column=0, columnspan=2,
                                                sticky="w", padx=12, pady=(10, 6))
        self.twofa_var   = ctk.StringVar()
        self.twofa_entry = ctk.CTkEntry(self.twofa_outer, textvariable=self.twofa_var,
                                        placeholder_text="Your 2FA password",
                                        width=220, height=42, show="*",
                                        font=ctk.CTkFont("Consolas", 14))
        self.twofa_entry.grid(row=1, column=0, padx=(12, 8), pady=(0, 12))
        ctk.CTkButton(self.twofa_outer, text="✔  Submit", width=120, height=42,
                      fg_color="#6e40c9", hover_color="#8957e5",
                      font=ctk.CTkFont("Segoe UI", 13, "bold"),
                      command=self._submit_2fa).grid(row=1, column=1, padx=(0, 12), pady=(0, 12), sticky="w")
        self.twofa_entry.bind("<Return>", lambda _: self._submit_2fa())

        # Logout button
        ctk.CTkButton(p, text="🚪 Logout / Switch account",
                      width=210, height=36, fg_color="#30363d", hover_color="#484f58",
                      command=self._logout_telegram).grid(
            row=5, column=0, sticky="w", padx=12, pady=(6, 16))

        self._refresh_tg_status_ui()

    def _step_card(self, parent, number, title, desc, row):
        card = ctk.CTkFrame(parent, fg_color="#161b22", corner_radius=10)
        card.grid(row=row, column=0, sticky="ew", padx=12, pady=5)
        card.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(card, text=f" {number} ", width=36, height=36,
                     fg_color="#1f6feb", corner_radius=18,
                     font=ctk.CTkFont("Segoe UI", 15, "bold"),
                     text_color="white").grid(row=0, column=0, rowspan=2, padx=(14, 10), pady=14)
        ctk.CTkLabel(card, text=title, anchor="w",
                     font=ctk.CTkFont("Segoe UI", 13, "bold")).grid(
            row=0, column=1, sticky="w", padx=(0, 12), pady=(12, 0))
        ctk.CTkLabel(card, text=desc, anchor="w", justify="left",
                     font=ctk.CTkFont("Segoe UI", 11),
                     text_color="#8b949e").grid(
            row=1, column=1, sticky="w", padx=(0, 12), pady=(0, 12))
        return card

    # ══════════════ SETTINGS TAB ══════════════════════════════════════════════
    def _build_settings_tab(self, p):
        p.grid_columnconfigure(0, weight=1)
        r = 0

        def section(title, row):
            ctk.CTkLabel(p, text=title, font=ctk.CTkFont("Segoe UI", 13, "bold"),
                         anchor="w").grid(row=row, column=0, sticky="w", padx=14, pady=(18, 4))

        section("🍪  Cookies file  (for login-protected sites)", r); r += 1
        ck = ctk.CTkFrame(p, fg_color="transparent")
        ck.grid(row=r, column=0, sticky="ew", padx=14); r += 1
        ck.grid_columnconfigure(0, weight=1)
        self.cookies_var = ctk.StringVar(value=self.cfg.get("cookies_file", ""))
        ctk.CTkEntry(ck, textvariable=self.cookies_var, height=36,
                     placeholder_text="path/to/cookies.txt",
                     font=ctk.CTkFont("Consolas", 12)).grid(row=0, column=0, sticky="ew", padx=(0, 6))
        ctk.CTkButton(ck, text="📁", width=40, height=36,
                      command=self._browse_cookies).grid(row=0, column=1)
        ctk.CTkLabel(p, text="  Use 'Get cookies.txt LOCALLY' Chrome/Firefox extension.\n"
                             "  Needed for: Instagram, Facebook, Twitter/X, YouTube members…",
                     font=ctk.CTkFont("Segoe UI", 11), text_color="#8b949e",
                     justify="left", anchor="w").grid(row=r, column=0, sticky="w", padx=14, pady=(2, 4)); r += 1

        section("⚡  Parallel fragment downloads", r); r += 1
        self.concur_var = ctk.StringVar(value=self.cfg.get("concur", "5"))
        ctk.CTkEntry(p, textvariable=self.concur_var, width=80,
                     font=ctk.CTkFont("Consolas", 13)).grid(row=r, column=0, sticky="w", padx=14); r += 1

        section("🌐  Proxy  (optional)", r); r += 1
        self.proxy_var = ctk.StringVar(value=self.cfg.get("proxy", ""))
        ctk.CTkEntry(p, textvariable=self.proxy_var, height=36,
                     placeholder_text="socks5://127.0.0.1:1080   or   http://user:pass@host:port",
                     font=ctk.CTkFont("Consolas", 12)).grid(row=r, column=0, sticky="ew", padx=14); r += 1

        ctk.CTkButton(p, text="💾  Save Settings", width=180, height=40,
                      command=self._save_settings).grid(row=r, column=0, pady=20)

    # ══════════════ ABOUT TAB ═════════════════════════════════════════════════
    def _build_about_tab(self, p):
        p.grid_columnconfigure(0, weight=1)
        p.grid_rowconfigure(0, weight=1)

        scroll = ctk.CTkScrollableFrame(p, fg_color="transparent")
        scroll.grid(row=0, column=0, sticky="nsew")
        scroll.grid_columnconfigure(0, weight=1)

        # Logo / title card
        logo_card = ctk.CTkFrame(scroll, fg_color="#0d1117", corner_radius=16)
        logo_card.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 10))
        logo_card.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(logo_card, text="👻",
                     font=ctk.CTkFont("Segoe UI", 52)).grid(row=0, column=0, pady=(24, 4))
        ctk.CTkLabel(logo_card, text="GhostGrab",
                     font=ctk.CTkFont("Segoe UI", 28, "bold"),
                     text_color="#58a6ff").grid(row=1, column=0)
        ctk.CTkLabel(logo_card, text=f"Version {APP_VERSION}",
                     font=ctk.CTkFont("Segoe UI", 12),
                     text_color="#3fb950").grid(row=2, column=0, pady=(2, 4))
        ctk.CTkLabel(logo_card,
                     text="Private Telegram Video Downloader\nDownload any private channel or group video in original quality.",
                     font=ctk.CTkFont("Segoe UI", 12),
                     text_color="#8b949e", justify="center").grid(row=3, column=0, pady=(4, 24))

        # Author card
        author_card = ctk.CTkFrame(scroll, fg_color="#161b22", corner_radius=12)
        author_card.grid(row=1, column=0, sticky="ew", padx=20, pady=8)
        author_card.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(author_card, text="👤",
                     font=ctk.CTkFont("Segoe UI", 22)).grid(row=0, column=0, padx=(20, 10), pady=18, rowspan=2)
        ctk.CTkLabel(author_card, text="Author",
                     font=ctk.CTkFont("Segoe UI", 11), text_color="#8b949e",
                     anchor="w").grid(row=0, column=1, sticky="w", pady=(16, 0))
        ctk.CTkLabel(author_card, text=APP_AUTHOR,
                     font=ctk.CTkFont("Segoe UI", 16, "bold"),
                     text_color="#e6edf3", anchor="w").grid(row=1, column=1, sticky="w", pady=(0, 16))

        # Links card
        links_card = ctk.CTkFrame(scroll, fg_color="#161b22", corner_radius=12)
        links_card.grid(row=2, column=0, sticky="ew", padx=20, pady=8)
        links_card.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(links_card, text="🔗  Links & Contact",
                     font=ctk.CTkFont("Segoe UI", 13, "bold"),
                     anchor="w").grid(row=0, column=0, columnspan=2, sticky="w", padx=16, pady=(14, 10))

        links = [
            ("🐙  GitHub Repository", APP_GITHUB),
            ("⭐  Star on GitHub", APP_GITHUB),
            ("🐛  Report a Bug", f"{APP_GITHUB}/issues"),
            ("💡  Request a Feature", f"{APP_GITHUB}/issues"),
        ]
        for i, (label, url) in enumerate(links):
            btn = ctk.CTkButton(links_card, text=label,
                                fg_color="#21262d", hover_color="#30363d",
                                text_color="#58a6ff", anchor="w",
                                font=ctk.CTkFont("Segoe UI", 12),
                                height=36,
                                command=lambda u=url: webbrowser.open(u))
            btn.grid(row=i+1, column=0, sticky="ew", padx=16, pady=3)
        # padding at bottom
        ctk.CTkLabel(links_card, text="").grid(row=len(links)+1, column=0, pady=4)

        # Tech stack card
        tech_card = ctk.CTkFrame(scroll, fg_color="#161b22", corner_radius=12)
        tech_card.grid(row=3, column=0, sticky="ew", padx=20, pady=8)
        tech_card.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(tech_card, text="🛠  Built With",
                     font=ctk.CTkFont("Segoe UI", 13, "bold"),
                     anchor="w").grid(row=0, column=0, sticky="w", padx=16, pady=(14, 6))

        tech = [
            ("Python 3",        "Core language"),
            ("CustomTkinter",   "Modern dark GUI framework"),
            ("Telethon",        "Telegram MTProto API client"),
            ("yt-dlp",          "1800+ site video downloader"),
        ]
        for i, (name, desc) in enumerate(tech):
            row_f = ctk.CTkFrame(tech_card, fg_color="transparent")
            row_f.grid(row=i+1, column=0, sticky="ew", padx=16, pady=3)
            row_f.grid_columnconfigure(1, weight=1)
            ctk.CTkLabel(row_f, text=f"• {name}",
                         font=ctk.CTkFont("Segoe UI", 12, "bold"),
                         text_color="#58a6ff", width=160, anchor="w").grid(row=0, column=0)
            ctk.CTkLabel(row_f, text=desc,
                         font=ctk.CTkFont("Segoe UI", 11),
                         text_color="#8b949e", anchor="w").grid(row=0, column=1, sticky="w")
        ctk.CTkLabel(tech_card, text="").grid(row=len(tech)+1, column=0, pady=4)

        # Disclaimer card
        disc_card = ctk.CTkFrame(scroll, fg_color="#2d1b00", corner_radius=12)
        disc_card.grid(row=4, column=0, sticky="ew", padx=20, pady=8)
        disc_card.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(disc_card, text="⚠️  Disclaimer",
                     font=ctk.CTkFont("Segoe UI", 13, "bold"),
                     text_color="#e3b341", anchor="w").grid(
            row=0, column=0, sticky="w", padx=16, pady=(14, 6))
        ctk.CTkLabel(disc_card,
                     text="GhostGrab is intended for personal backup of content\n"
                          "you have the legal right to access. Always respect\n"
                          "copyright, platform terms of service, and privacy laws.\n"
                          "Keep your API keys private and never share them.",
                     font=ctk.CTkFont("Segoe UI", 11),
                     text_color="#e3b341", justify="left", anchor="w").grid(
            row=1, column=0, sticky="w", padx=16, pady=(0, 14))

        # Footer
        ctk.CTkLabel(scroll,
                     text=f"© 2025 {APP_AUTHOR}  ·  MIT License  ·  {APP_GITHUB}",
                     font=ctk.CTkFont("Segoe UI", 10),
                     text_color="#484f58").grid(row=5, column=0, pady=(8, 20))

    # ══════════════ HELP TAB ══════════════════════════════════════════════════
    def _build_help_tab(self, p):
        txt = f"""
👻  {APP_NAME} v{APP_VERSION}  —  Quick Guide
Author: {APP_AUTHOR}  ·  {APP_GITHUB}
══════════════════════════════════════════════════════

▶  DOWNLOAD ANY VIDEO (YouTube, TikTok, Instagram…)
─────────────────────────────────────────────────────
1. Copy the video URL from your browser
2. Paste it in ⬇ Download tab → hit Download
3. Pick quality if needed (default = Best available)

For private / members-only content:
  → Export cookies from your browser (⚙ Settings tab)
  → Use the 'Get cookies.txt LOCALLY' extension

Supports 1800+ sites including: YouTube, Instagram,
TikTok, Twitter/X, Reddit, Facebook, Vimeo, Twitch,
Dailymotion, Bilibili, NicoNico, and many more.

══════════════════════════════════════════════════════

▶  PRIVATE TELEGRAM CHANNELS & GROUPS
───────────────────────────────────────
One-time setup — takes about 2 minutes:

  STEP 1 → Go to  https://my.telegram.org/apps
            Sign in with your Telegram phone number.
            Click "API development tools" → Create app.
            Copy the  API ID  and  API Hash.

  STEP 2 → Open the  📡 Telegram  tab in GhostGrab.
            Paste API ID, API Hash, and your phone
            number (include country code, e.g. +880…).

  STEP 3 → Click  🔗 Connect to Telegram.
            Telegram sends a code to your phone/app.
            Enter it and click Submit.
            ✅ Done — session saved, won't ask again.

Then just paste any t.me link and download normally.

  Supported URL formats:
  https://t.me/c/1234567890/42   ← private channel
  https://t.me/channelname/99    ← public channel

══════════════════════════════════════════════════════

▶  BATCH DOWNLOAD
──────────────────
Paste multiple links in the Batch box (one per line).
They download one after another automatically.

▶  QUALITY OPTIONS
  Best      = highest available (recommended)
  1080p     = Full HD
  4K/2160p  = Ultra HD (only if the source has it)
  Audio Only = extracts MP3

══════════════════════════════════════════════════════
⚠  For personal use only. Keep your API keys private.
   GitHub: {APP_GITHUB}
"""
        box = ctk.CTkTextbox(p, font=ctk.CTkFont("Consolas", 12),
                              fg_color="#0d1117", text_color="#e6edf3", wrap="word")
        box.pack(fill="both", expand=True, padx=10, pady=10)
        box.insert("1.0", txt)
        box.configure(state="disabled")

    # ══════════════ HELPERS ═══════════════════════════════════════════════════
    def _on_url_change(self, *_):
        url = self.url_var.get().strip()
        if "t.me" in url and not self._tg_connected:
            self.tg_banner.grid()
        else:
            self.tg_banner.grid_remove()

    def _paste_url(self):
        try:
            self.url_var.set(self.clipboard_get().strip())
        except Exception:
            pass

    def _browse_output(self):
        d = filedialog.askdirectory(initialdir=self.outdir_var.get())
        if d:
            self.outdir_var.set(d)

    def _browse_cookies(self):
        f = filedialog.askopenfilename(filetypes=[("Text", "*.txt"), ("All", "*.*")])
        if f:
            self.cookies_var.set(f)

    def _open_folder(self):
        folder = self.outdir_var.get()
        os.makedirs(folder, exist_ok=True)
        if sys.platform == "win32":
            os.startfile(folder)
        elif sys.platform == "darwin":
            subprocess.Popen(["open", folder])
        else:
            subprocess.Popen(["xdg-open", folder])

    def _log(self, msg: str):
        ts = datetime.now().strftime("%H:%M:%S")
        self.log_box.configure(state="normal")
        self.log_box.insert("end", f"[{ts}] {msg}\n")
        self.log_box.see("end")
        self.log_box.configure(state="disabled")
        self.status_var.set(msg[:120])

    def _tg_log(self, msg: str):
        ts = datetime.now().strftime("%H:%M:%S")
        self.tg_log_box.configure(state="normal")
        self.tg_log_box.insert("end", f"[{ts}] {msg}\n")
        self.tg_log_box.see("end")
        self.tg_log_box.configure(state="disabled")

    def _set_progress(self, pct, label=""):
        self.progress_bar.set(pct / 100)
        self.progress_label.configure(text=label)

    def _save_settings(self):
        self.cfg.update({
            "output_dir": self.outdir_var.get(), "quality": self.quality_var.get(),
            "format": self.fmt_var.get(), "cookies_file": self.cookies_var.get(),
            "concur": self.concur_var.get(), "proxy": self.proxy_var.get(),
        })
        save_config(self.cfg)
        self._log("✅ Settings saved.")

    def _refresh_tg_pill(self):
        if self._tg_connected:
            name = self.cfg.get("_tg_name", "")
            self.tg_pill_var.set(f"📡 ✅  {name}" if name else "📡 ✅  Connected")
            self.tg_pill.configure(fg_color="#0f2d1a", text_color="#3fb950")
        else:
            self.tg_pill_var.set("📡  Not connected")
            self.tg_pill.configure(fg_color="#21262d", text_color="#8b949e")

    def _refresh_tg_status_ui(self):
        if self._tg_connected:
            name = self.cfg.get("_tg_name", "")
            self._tg_banner_icon.configure(text="✅")
            self._tg_banner_title.configure(
                text=f"Connected{' as ' + name if name else ''}",
                text_color="#3fb950")
            self._tg_banner_sub.configure(
                text="You can now download from any private Telegram channel or group.")
            self.connect_btn.configure(text="✅  Connected — click to re-connect",
                                       fg_color="#21262d", hover_color="#30363d")
        else:
            self._tg_banner_icon.configure(text="⚠️")
            self._tg_banner_title.configure(text="Not connected", text_color="#e3b341")
            self._tg_banner_sub.configure(text="Follow the 3 steps below to connect once.")
            self.connect_btn.configure(text="🔗  Connect to Telegram",
                                       fg_color="#238636", hover_color="#2ea043")
        self._refresh_tg_pill()

    # ══════════════ TELEGRAM CONNECT ══════════════════════════════════════════
    def _save_tg_creds(self):
        for key, var in self._tg_vars.items():
            self.cfg[key] = var.get().strip()
        save_config(self.cfg)

    def _connect_telegram(self):
        self._save_tg_creds()
        api_id   = self.cfg.get("tg_api_id",  "").strip()
        api_hash = self.cfg.get("tg_api_hash", "").strip()
        phone    = self.cfg.get("tg_phone",    "").strip()

        if not api_id or not api_hash:
            messagebox.showerror("Missing credentials",
                "Please fill in API ID and API Hash.\n\n"
                "Get them free from: my.telegram.org/apps")
            return
        if not phone:
            messagebox.showerror("Missing phone number",
                "Enter your phone number with country code.\nExample: +880 1700 000000")
            return

        self.connect_btn.configure(state="disabled", text="⏳  Connecting…")
        self.otp_outer.grid_remove()
        self.twofa_outer.grid_remove()
        self._tg_log("Connecting to Telegram…")
        threading.Thread(target=self._tg_connect_thread, daemon=True).start()

    def _tg_connect_thread(self):
        api_id   = self.cfg["tg_api_id"]
        api_hash = self.cfg["tg_api_hash"]
        phone    = self.cfg["tg_phone"]
        session  = str(Path.home() / ".ghostgrab_tg_session")

        if os.path.exists(self._otp_file):
            os.remove(self._otp_file)

        cmd = [sys.executable, "-u", str(HELPERS / "tg_connect.py"),
               api_id, api_hash, phone, session, self._otp_file]

        try:
            proc = subprocess.Popen(cmd,
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                text=True, bufsize=1,
                env={**os.environ, "PYTHONUNBUFFERED": "1"})

            for raw in proc.stdout:
                line = raw.strip()
                if not line:
                    continue

                if line.startswith("STATUS:connecting"):
                    self.after(0, self._tg_log, "🔗 Connecting to Telegram servers…")
                elif line.startswith("STATUS:sending_code"):
                    self.after(0, self._tg_log, f"📲 Sending code to {phone}…")
                elif line.startswith("STATUS:waiting_otp"):
                    self.after(0, self._tg_log, "📲 Code sent! Enter it in the box below.")
                    self.after(0, self._show_otp)
                elif line.startswith("STATUS:2fa_needed"):
                    self.after(0, self._tg_log, "🔑 2FA password required.")
                    self.after(0, self._hide_otp)
                    self.after(0, self._show_2fa)
                elif line.startswith("OK:"):
                    parts = line[3:].split(":", 1)
                    name  = parts[0]
                    uname = parts[1] if len(parts) > 1 else ""
                    self.cfg["_tg_name"] = name
                    self._tg_connected   = True
                    save_config(self.cfg)
                    self.after(0, self._hide_otp)
                    self.after(0, self._hide_2fa)
                    self.after(0, self._tg_log,
                               f"✅  Connected as {name}" + (f"  (@{uname})" if uname else ""))
                    self.after(0, self._refresh_tg_status_ui)
                    self.after(0, self._on_url_change)
                elif line.startswith("ERROR:"):
                    err = line[6:]
                    self.after(0, self._tg_log, f"❌  {err}")
                    self.after(0, self._hide_otp)
                    self.after(0, self._hide_2fa)
                    self.after(0, self._log, f"❌ Telegram: {err}")
                    self.after(0, lambda e=err: messagebox.showerror("Telegram Error", e))
                else:
                    self.after(0, self._tg_log, line)
                    self.after(0, self._log, f"[tg] {line}")

            proc.wait()
            if proc.returncode != 0 and not self._tg_connected:
                self.after(0, self._tg_log,
                           f"❌  Failed (exit code {proc.returncode}). Check log above.")

        except Exception as ex:
            self.after(0, self._tg_log, f"❌  {ex}")
            self.after(0, lambda e=str(ex): messagebox.showerror("Error", e))
        finally:
            self.after(0, lambda: self.connect_btn.configure(state="normal"))

    def _show_otp(self):
        self.otp_outer.grid()
        self.otp_entry.focus()
        self.tabs.set("📡  Telegram")

    def _hide_otp(self):
        self.otp_outer.grid_remove()

    def _show_2fa(self):
        self.twofa_outer.grid()
        self.twofa_entry.focus()

    def _hide_2fa(self):
        self.twofa_outer.grid_remove()

    def _submit_otp(self):
        code = self.otp_var.get().strip()
        if not code:
            return
        with open(self._otp_file, "w") as f:
            f.write(code)
        self.otp_var.set("")
        self._tg_log("✔ Code submitted — verifying…")

    def _submit_2fa(self):
        pw = self.twofa_var.get().strip()
        if not pw:
            return
        with open(self._otp_file, "w") as f:
            f.write(pw)
        self.twofa_var.set("")
        self._tg_log("✔ Password submitted — verifying…")

    def _logout_telegram(self):
        for path in [Path.home() / ".ghostgrab_tg_session.session",
                     Path.home() / ".ghostgrab_tg_session"]:
            if path.exists():
                path.unlink(missing_ok=True)
        self._tg_connected = False
        self.cfg.pop("_tg_name", None)
        save_config(self.cfg)
        self._tg_log("🚪 Logged out.")
        self._refresh_tg_status_ui()
        self._log("🚪 Telegram session cleared.")

    # ══════════════ DOWNLOAD ENGINE ═══════════════════════════════════════════
    def _start_download(self):
        if self.is_downloading:
            return
        url = self.url_var.get().strip()
        batch = [l.strip() for l in self.batch_box.get("1.0", "end").splitlines()
                 if l.strip() and not l.strip().startswith("#")]
        urls = ([url] if url else []) + batch
        if not urls:
            messagebox.showwarning("No URL", "Paste at least one URL.")
            return
        if any("t.me" in u for u in urls) and not self._tg_connected:
            if messagebox.askyesno("Telegram not connected",
                "A Telegram link was detected but Telegram isn't connected yet.\n\n"
                "Open Telegram setup now?"):
                self.tabs.set("📡  Telegram")
            return

        self.is_downloading = True
        self._stop_event.clear()
        self.dl_btn.configure(state="disabled")
        self.stop_btn.configure(state="normal")
        self.progress_bar.set(0)
        threading.Thread(target=self._download_all, args=(urls,), daemon=True).start()

    def _stop_download(self):
        self._stop_event.set()
        self._log("⏹ Stopping…")

    def _finish_download(self):
        self.is_downloading = False
        self.dl_btn.configure(state="normal")
        self.stop_btn.configure(state="disabled")

    def _download_all(self, urls):
        for i, url in enumerate(urls, 1):
            if self._stop_event.is_set():
                self._log("⏹ Stopped.")
                break
            self._log(f"📥 [{i}/{len(urls)}]  {url}")
            if "t.me" in url:
                self._tg_download(url)
            else:
                self._ytdlp_download(url)
        self.after(0, self._finish_download)
        self.after(0, lambda: self._set_progress(100, "Done ✅"))

    def _ytdlp_download(self, url):
        outdir  = self.outdir_var.get()
        os.makedirs(outdir, exist_ok=True)
        quality = self.quality_var.get()

        if quality == "Audio Only":
            fmtstr = "bestaudio/best"
            post   = ["--extract-audio", "--audio-format", "mp3", "--audio-quality", "0"]
        elif quality == "Best":
            fmtstr = "bestvideo+bestaudio/best"
            post   = []
        else:
            h = re.sub(r"[^\d]", "", quality)
            fmtstr = f"bestvideo[height<={h}]+bestaudio/best[height<={h}]" if h else "bestvideo+bestaudio/best"
            post   = []

        fmt = self.fmt_var.get()
        cmd = [sys.executable, "-m", "yt_dlp",
               "--no-warnings", "--progress", "--newline",
               "-f", fmtstr,
               "-o", os.path.join(outdir, "%(title)s.%(ext)s"),
               "--concurrent-fragments", self.concur_var.get()]
        if fmt not in ("original", ""):
            cmd += ["--merge-output-format", fmt]
        if self.subs_var.get():
            cmd += ["--write-subs", "--write-auto-subs", "--sub-langs", "all"]
        if self.thumb_var.get():
            cmd += ["--write-thumbnail"]
        cookies = self.cookies_var.get().strip()
        if cookies and Path(cookies).exists():
            cmd += ["--cookies", cookies]
        proxy = self.proxy_var.get().strip()
        if proxy:
            cmd += ["--proxy", proxy]
        cmd += post + [url]

        try:
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT, text=True, bufsize=1)
            for line in proc.stdout:
                line = line.rstrip()
                if not line:
                    continue
                m = re.search(r"(\d+\.?\d*)%", line)
                if m:
                    self.after(0, self._set_progress, float(m.group(1)), line[:120])
                else:
                    self.after(0, self._log, line)
                if self._stop_event.is_set():
                    proc.terminate(); break
            proc.wait()
            if proc.returncode == 0:
                self.after(0, self._log, "✅ Download complete!")
            else:
                self.after(0, self._log, f"⚠ yt-dlp exited {proc.returncode}")
        except Exception as ex:
            self.after(0, self._log, f"❌ {ex}")

    def _tg_download(self, url):
        outdir  = self.outdir_var.get()
        session = str(Path.home() / ".ghostgrab_tg_session")
        cmd = [sys.executable, "-u", str(HELPERS / "tg_download.py"),
               self.cfg["tg_api_id"], self.cfg["tg_api_hash"],
               session, url, outdir]
        try:
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT, text=True, bufsize=1,
                                    env={**os.environ, "PYTHONUNBUFFERED": "1"})
            for line in proc.stdout:
                line = line.strip()
                if not line:
                    continue
                if line.startswith("PROGRESS:"):
                    _, pct, mb_cur, mb_tot = line.split(":")
                    self.after(0, self._set_progress, float(pct),
                               f"{mb_cur} MB / {mb_tot} MB  ({pct}%)")
                elif line.startswith("FILE:"):
                    self.after(0, self._log, f"⬇  Downloading: {line[5:]}")
                elif line.startswith("DONE:"):
                    self.after(0, self._log, f"✅ Saved → {line[5:]}")
                elif line.startswith("ERROR:"):
                    self.after(0, self._log, f"❌ {line[6:]}")
                else:
                    self.after(0, self._log, line)
                if self._stop_event.is_set():
                    proc.terminate(); break
            proc.wait()
        except Exception as ex:
            self.after(0, self._log, f"❌ {ex}")


# ─── entry point ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app = GhostGrab()
    app.mainloop()
