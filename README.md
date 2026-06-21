Focus Lock (The Last Door)

A strict and dynamic website blocker for Linux systems designed to eliminate distractions during work or study. It modifies the local hosts file and manages DNS services via systemd to ensure a hard lock with 0% CPU resource consumption.
Features

    Interactive UI: Choose between locking a new website or checking the remaining time for currently active locks.

    Secure Dynamic Locking: Supports blocking multiple websites with independent durations without any time-tampering loopholes.

    Complete Lockout: Blocks both the website via browsers and Electron-based applications (e.g., Discord desktop client).

    Zero-Resource Daemon: Runs efficiently in the background; the system daemon sleeps and wakes up precisely when the closest lock expires.

Supported Distributions

    Fedora

    Debian / Ubuntu / Linux Mint

    Arch Linux / Manjaro

-Prerequisites-

Make sure Git and Python 3 are installed on your system before proceeding:

Fedora:
-
*sudo dnf install git python3 -y*

Debian / Ubuntu / Linux Mint:
-
*sudo apt update && sudo apt install git python3 -y*

Arch Linux:
-
*sudo pacman -Sy git python --noconfirm*

-Installation-

Open your terminal and run the following commands to clone and install the project automatically:
Bash

git clone https://github.com/YOUR_USERNAME/focus-lock.git
cd focus-lock
chmod +x install.sh
sudo ./install.sh

-Usage-

After installation, restart your terminal (or run source ~/.bashrc), then simply type the shortcut command to launch the application at any time:
Bash

*holylock*
---
Important Technical Note

Some modern browsers cache DNS queries locally for a short period. If you lock a website while the browser is open, it is highly recommended to completely restart your browser or clear its internal DNS cache (e.g., via about:networking in Firefox) to enforce the lock immediately.
