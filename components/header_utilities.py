import os

THEMES_PATH = os.path.join(os.getcwd(), 'themes')

def run_revert_command():
    revert_path = os.path.join(THEMES_PATH, 'revert.reg')

    try:
        os.system(f'wine regedit {revert_path}')
    except Exception as e:
        print(f"Error executing revert command: {e}")

def open_themes_path():
    if not os.path.exists('themes'):
        os.makedirs('themes')
    
    try:
        os.startfile(THEMES_PATH)
    except AttributeError:
        import subprocess
        subprocess.call(['open', THEMES_PATH])