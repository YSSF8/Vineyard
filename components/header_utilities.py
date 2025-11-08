import os
import subprocess
import requests
import threading

THEMES_PATH = os.path.join(os.getcwd(), 'themes')
_revert_lock = threading.Lock()

def run_revert_command(console, root):
    if not _revert_lock.acquire(blocking=False):
        console.system("⚠️ Revert already in progress, please wait…")
        return

    revert_path = os.path.join(THEMES_PATH, 'revert.reg')
    os.makedirs(THEMES_PATH, exist_ok=True)

    def worker():
        try:
            if not os.path.isfile(revert_path):
                root.after(0, lambda: console.system("revert.reg not found - downloading..."))
                
                url = "https://raw.githubusercontent.com/YSSF8/Vineyard/refs/heads/main/themes/revert.reg"
                resp = requests.get(url, timeout=15)
                resp.raise_for_status()
                
                with open(revert_path, "wb") as f:
                    f.write(resp.content)
                
                root.after(0, lambda: console.system("Downloaded revert.reg successfully"))

            root.after(0, lambda: console.system("Reverting to default theme..."))
            exit_code = os.system(f'wine regedit "{revert_path}"')
            
            if exit_code == 0:
                root.after(0, lambda: console.system("Successfully reverted to default theme"))
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
        os.startfile(THEMES_PATH)
        console.system("Successfully opened themes directory")
    except AttributeError:
        try:
            subprocess.call(['open', THEMES_PATH])
            console.system("Successfully opened themes directory")
        except Exception as e:
            console.error(f"Error opening themes directory: {e}")