import os
import subprocess

THEMES_PATH = os.path.join(os.getcwd(), 'themes')

def run_revert_command(console):
    revert_path = os.path.join(THEMES_PATH, 'revert.reg')
    console.system("Reverting to default theme...")
    try:
        os.system(f'wine regedit {revert_path}')
        console.system("Successfully reverted to default theme")
    except Exception as e:
        console.error(f"Error executing revert command: {e}")

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