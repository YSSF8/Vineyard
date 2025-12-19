import re

# Legacy Keys (Wine < 9.0)
LEGACY_KEYS = [
    "ActiveBorder", "ActiveTitle", "AppWorkSpace", "Background", 
    "ButtonAlternativeFace", "ButtonDkShadow", "ButtonFace", "ButtonHilight", 
    "ButtonLight", "ButtonShadow", "ButtonText", "GradientActiveTitle", 
    "GradientInactiveTitle", "GrayText", "Hilight", "HilightText", 
    "InactiveBorder", "InactiveTitle", "InactiveTitleText", "InfoText", 
    "InfoWindow", "Menu", "MenuBar", "MenuHilight", "MenuText", "Scrollbar", 
    "TitleText", "Window", "WindowFrame", "WindowText"
]

# Modern Keys (Wine 9.0+)
MODERN_KEYS = [
    "ActiveBorder", "ActiveTitle", "AppWorkSpace", "Background", 
    "ButtonAlternateFace", "ButtonDkShadow", "ButtonFace", "ButtonHilight", 
    "ButtonLight", "ButtonShadow", "ButtonText", "GradientActiveTitle", 
    "GradientInactiveTitle", "GrayText", "Hilight", "HilightText", 
    "HotTrackingColor", "InactiveBorder", "InactiveTitle", "InactiveTitleText", 
    "InfoText", "InfoWindow", "Menu", "MenuBar", "MenuHilight", "MenuText", 
    "Scrollbar", "TitleText", "Window", "WindowFrame", "WindowText"
]

class RonConverter:
    @staticmethod
    def convert(ron_content, theme_name, wine_version):
        colors = {}
        regex = r"([a-zA-Z0-9_]+)\s*[:=]\s*(?:Some\s*\()?\s*\(\s*.*?red:\s*([\d\.]+).*?green:\s*([\d\.]+).*?blue:\s*([\d\.]+)"