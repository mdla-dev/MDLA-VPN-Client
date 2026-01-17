# MDLA – VPN Manager
A simple and reliable VPN client with support for multiple protocols

## ✨ Features

- 🚀 **Ready-to-use EXE file** — no Python installation required
- 🔒 **Multiple protocols** — VMess, VLESS, Trojan, Shadowsocks, Hysteria2
- 🎯 **Two operating modes** — System Proxy and TUN mode
- 📊 **Traffic monitoring** — real-time speed statistics
- 🌐 **Subscriptions** — automatic server updates
- 🎨 **Modern interface** — dark theme, convenient controls
- 💾 **System tray support** — runs in the background

## 🚀 Quick Start

### Download the ready EXE (Recommended)
1. Go to [Releases](../../releases)
2. Download `MDLA.exe`
3. Run the file
4. Done!

### Run from source code
```bash
git clone https://github.com/your-username/MDLA.git
cd MDLA
pip install -r requirements.txt
python main.py
```

## 📖 How to Use

### 1. Adding Servers

**Via URL:**
- Click `+ Add` → `URL` tab
- Paste server links (vmess://, vless://, ss://, trojan://)
- Click `Add`

**Via subscription:**
- Click `+ Add` → `Subscription` tab
- Enter a name and subscription URL
- Click `Add`

### 2. Connecting
- Select a server from the list
- Click `Connect`
- The application will automatically configure the proxy

### 3. Operating Modes
- **System Proxy** (default) — HTTP/SOCKS5 proxy
- **TUN Mode** — system-wide VPN (requires administrator privileges)

## 🔧 Settings

### Ports
- HTTP proxy: `127.0.0.1:10809`
- SOCKS5 proxy: `127.0.0.1:10808`

### System Tray
- When the window is closed, the application minimizes to the tray
- Right-click the tray icon to manage
- Use `Exit` to fully close the application

## 🛠️ For Developers

### Building the EXE
```bash
python -m PyInstaller --name=MDLA --onefile --windowed --clean \
  --add-data "src;src" --add-data "cores/xray.exe;cores" \
  --add-data "cores/geoip.dat;cores" --add-data "cores/geosite.dat;cores" \
  --add-data "logo.png;." --icon=logo.png \
  --hidden-import=customtkinter --hidden-import=PIL \
  --hidden-import=aiohttp --hidden-import=pystray \
  main.py
```

### Project Structure
```
MDLA/
├── src/                 # Source code
│   ├── config/         # Configuration
│   ├── core/           # Application core
│   └── ui/             # User interface
├── cores/              # Xray Core
├── main.py             # Entry point
├── requirements.txt    # Dependencies
└── logo.png           # Logo
```

## 📋 System Requirements

- **OS:** Windows 10/11 (x64)
- **Storage:** 50 MB of free space
- **Network:** Internet connection

## 🐛 Troubleshooting

**Discord voice chats do not work:**
- Restart Discord after connecting to the VPN
- Change the voice server in Discord settings

**Traffic is not displayed:**
- Make sure the connection is active
- Statistics update every second

**Connection errors:**
- Check the correctness of the server URL
- Try another server

## 📄 License

MIT License — see [LICENSE](LICENSE)

## 🤝 Contributing

Pull Requests and Issues are welcome!

---

<div align="center">
  <p><strong>MDLA</strong> — A simple and reliable VPN for everyone</p>
</div>
