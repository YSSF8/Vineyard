import os
import subprocess
import requests
import threading
import re
import sys

THEMES_PATH = os.path.join(os.getcwd(), 'themes')
_revert_lock = threading.Lock()

def _get_wine_major_version():
    try:
        result = subprocess.run(['wine', '--version'], capture_output=True, text=True)
        match = re.search(r"wine-(\d+)", result.stdout.strip())
        return int(match.group(1)) if match else 8
    except:
        return 8

def run_revert_command(console, root):
    if not _revert_lock.acquire(blocking=False):
        console.system("Revert already in progress, please wait…")
        return

    wine_ver = _get_wine_major_version()
    
    if wine_ver >= 9:
        filename = "revert-modern.reg"
        console.info(f"Detected Wine 9.0+: Using {filename}")
    else:
        filename = "revert.reg"
        console.info(f"Detected Legacy Wine: Using {filename}")

    revert_path = os.path.join(THEMES_PATH, filename)
    os.makedirs(THEMES_PATH, exist_ok=True)

    def worker():
        try:
            if not os.path.isfile(revert_path):
                root.after(0, lambda: console.system(f"{filename} not found - downloading..."))
                
                url = f"https://raw.githubusercontent.com/YSSF8/Vineyard/refs/heads/main/themes/{filename}"
                resp = requests.get(url, timeout=15)
                resp.raise_for_status()
                
                with open(revert_path, "wb") as f:
                    f.write(resp.content)
                
                root.after(0, lambda: console.system(f"Downloaded {filename} successfully"))

            root.after(0, lambda: console.system("Reverting to default theme..."))
            
            exit_code = os.system(f'wine regedit /S "{revert_path}"')
            
            if exit_code == 0:
                root.after(0, lambda: console.system("Successfully reverted to default theme"))
                if wine_ver >= 9:
                    root.after(0, lambda: console.info("Note: Restart apps to see changes."))
            else:
                root.after(0, lambda: console.error(f"wine regedit failed (code: {exit_code})"))
                
        except requests.RequestException as e:
            root.after(0, lambda: console.error(f"Download failed: {e}"))
        except Exception as e:
            root.after(0, lambda: console.error(f"Unexpected error: {e}"))
        finally:
            _revert_lock.release()

    threading.Thread(target=worker, daemon=True).start()

def open_themes_path(console):
    if not os.path.exists('themes'):
        os.makedirs('themes')
    
    console.system("Opening themes directory...")
    try:
        opener = 'open' if sys.platform == 'darwin' else 'xdg-open'
        subprocess.call([opener, THEMES_PATH])
            
        console.system("Successfully opened themes directory")
    except Exception as e:
        console.error(f"Error opening themes directory: {e}")