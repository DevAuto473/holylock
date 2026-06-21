#!/usr/bin/env python3
import sys, os, time, json, signal, subprocess
from urllib.parse import urlparse

try:
    from focus_lock_ui import ASCII_ART
except ImportError:
    ASCII_ART = "\n    [ Locked ] The last door\n"

STATE_FILE = "/etc/focus_lock.json"

def print_ui():
    print(ASCII_ART)

def ignore_signals():
    for sig in [signal.SIGINT, signal.SIGTERM, signal.SIGHUP]:
        try: signal.signal(sig, signal.SIG_IGN)
        except OSError: pass

def extract_domain(url):
    url = url.strip()
    if not url: return ""
    if not url.startswith(('http://', 'https://')): url = 'http://' + url
    try:
        domain = urlparse(url).netloc or urlparse(url).path
        return domain.replace('www.', '').split('/')[0].split(':')[0]
    except: return url

def restart_dns():
    subprocess.run(["systemctl", "restart", "systemd-resolved.service"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)

def block_websites(websites):
    unblock_websites(websites, quiet=True)
    if not websites: return
    with open("/etc/hosts", "a") as f:
        for d in websites:
            for ip in ["127.0.0.1", "::1"]:
                f.write(f"{ip} {d}\n{ip} www.{d}\n")
    restart_dns()

def unblock_websites(websites, quiet=False):
    if not quiet: print("\nUnlocking websites. Done.")
    if not os.path.exists("/etc/hosts"): return
    with open("/etc/hosts", "r") as f: lines = f.readlines()
    with open("/etc/hosts", "w") as f:
        for line in lines:
            if not any(s in line for s in websites): f.write(line)
    restart_dns()

def daemon_mode():
    ignore_signals()
    while True:
        if not os.path.exists(STATE_FILE):
            sys.exit(0)
        try:
            with open(STATE_FILE, "r") as f:
                state = json.load(f)
        except: sys.exit(1)

        now = time.time()
        active = {k: v for k, v in state.items() if v > now}
        expired = [k for k, v in state.items() if v <= now]

        if expired:
            unblock_websites(expired, quiet=True)

        if not active:
            if os.path.exists(STATE_FILE): os.remove(STATE_FILE)
            sys.exit(0)

        if len(active) != len(state):
            with open(STATE_FILE, "w") as f: json.dump(active, f)

        block_websites(list(active.keys()))

        next_wakeup = min(active.values())
        sleep_time = next_wakeup - time.time()
        if sleep_time > 0:
            time.sleep(sleep_time)

def interactive_mode():
    print_ui()

    active_locks = {}
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r") as f: active_locks = json.load(f)
            now = time.time()
            active_locks = {k: v for k, v in active_locks.items() if v > now}
        except: pass

    if active_locks:
        print("You have some active locks right now.")
        print("1. Check remaining time")
        print("2. Lock a new website")
        choice = input("Your choice (1/2): ").strip()

        if choice == "1":
            now = time.time()
            print("\nHere is your current situation:")
            for site, end_t in active_locks.items():
                rem = int(end_t - now)
                d, rem = divmod(rem, 86400)
                h, rem = divmod(rem, 3600)
                m, s = divmod(rem, 60)
                print(f"- {site}: {d} days, {h} hours, {m} minutes, {s} seconds left.")
            print("\nGet back to work.")
            sys.exit(0)
        elif choice != "2":
            print("Invalid input. Exiting.")
            sys.exit(0)

    new_locks = {}
    while True:
        print("\nLet's lock something.")
        site_in = input("Enter website: ").strip()
        domain = extract_domain(site_in)

        if not domain:
            print("Invalid website. Try again.")
            continue

        try:
            m = float(input("Minutes: ").strip() or "0")
            s = float(input("Seconds: ").strip() or "0")
            d = float(input("Days: ").strip() or "0")
            total = (d * 86400) + (m * 60) + s
        except ValueError:
            print("Those are not numbers. Try again.")
            continue

        if total <= 0:
            print("Time must be greater than zero.")
            continue

        end_time = time.time() + total

        if domain in active_locks and active_locks[domain] > end_time:
            print(f"Nice try. {domain} is already locked for longer. Keeping the original time.")
            new_locks[domain] = active_locks[domain]
        else:
            new_locks[domain] = end_time

        more = input("\nDo you want to lock another website? (y/n): ").strip().lower()
        if more != 'y':
            break

    if not new_locks:
        print("Nothing to lock.")
        sys.exit(0)

    confirm = input("\nFinal warning. No turning back. Lock them? (y/n): ")
    if confirm.lower() != 'y':
        print("Cancelled.")
        sys.exit(0)

    active_locks.update(new_locks)
    with open(STATE_FILE, "w") as f:
        json.dump(active_locks, f)

    subprocess.run(["systemctl", "restart", "focus-lock.service"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
    print("\nLocked down. Focus.")

def main():
    if os.geteuid() != 0:
        print("You must run this as root (sudo).")
        sys.exit(1)

    if not sys.stdout.isatty():
        daemon_mode()
    else:
        interactive_mode()

if __name__ == "__main__":
    main()
