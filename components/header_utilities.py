import os

def open_themes_path():
    if not os.path.exists('themes'):
        os.makedirs('themes')
    
    try:
        os.startfile(os.path.join(os.getcwd(), 'themes'))
    except AttributeError:
        import subprocess
        subprocess.call(['open', os.path.join(os.getcwd(), 'themes')])