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
        
        for m in re.finditer(regex, ron_content, re.DOTALL):
            try:
                k, r, g, b = m.group(1), float(m.group(2)), float(m.group(3)), float(m.group(4))
                colors[k] = (int(r*255), int(g*255), int(b*255))
            except (ValueError, IndexError):
                continue

        base = colors.get("bg_color", colors.get("neutral_0", (30, 30, 30)))
        
        if "primary_container_bg" in colors: 
            surface = colors["primary_container_bg"]
        elif "surface" in colors: 
            surface = colors["surface"]
        elif "neutral_1" in colors and colors["neutral_1"] != base: 
            surface = colors["neutral_1"]
        else:
            surface = tuple(min(255, c + 12) for c in base)

        def lighten(rgb, amt=25): 
            return tuple(min(255, c + amt) for c in rgb)
        
        def s(rgb): 
            return f"{rgb[0]} {rgb[1]} {rgb[2]}"

        hilight = lighten(surface, 30)
        light   = lighten(surface, 10)
        shadow  = base 
        dkshadow = (max(0, base[0]-20), max(0, base[1]-20), max(0, base[2]-20))

        text = colors.get("text_tint", colors.get("foreground", (220, 220, 220)))
        accent = colors.get("accent", colors.get("primary", (0, 120, 215)))
        gray_text = tuple(int((text[i] + surface[i])/2) for i in range(3))

        if wine_version >= 9:
            final_map = {
                "ActiveBorder": s(surface), "ActiveTitle": s(surface), "AppWorkSpace": s(base),
                "Background": s(base), "ButtonAlternateFace": s(surface), "ButtonDkShadow": s(dkshadow),
                "ButtonFace": s(surface), "ButtonHilight": s(hilight), "ButtonLight": s(light),
                "ButtonShadow": s(shadow), "ButtonText": s(text), "GradientActiveTitle": s(surface),
                "GradientInactiveTitle": s(base), "GrayText": s(gray_text), "Hilight": s(accent),
                "HilightText": s(text), "HotTrackingColor": s(accent), "InactiveBorder": s(base),
                "InactiveTitle": s(base), "InactiveTitleText": s(gray_text), "InfoText": s(text),
                "InfoWindow": s(surface), "Menu": s(surface), "MenuBar": s(surface),
                "MenuHilight": s(accent), "MenuText": s(text), "Scrollbar": s(base),
                "TitleText": s(text), "Window": s(base), "WindowFrame": s(light),
                "WindowText": s(text)
            }
            
            lines = [
                "Windows Registry Editor Version 5.00", "",
                f"; Auto-Converted from {theme_name}.ron (Wine 9.0+ Mode)",
                "[HKEY_CURRENT_USER\\Control Panel\\Colors]"
            ]
            for k in sorted(final_map.keys()): 
                lines.append(f"\"{k}\"=\"{final_map[k]}\"")
            
            lines.extend([
                "",
                "[HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\ThemeManager]",
                "\"ThemeActive\"=\"0\"",
                "\"DllName\"=\"\"",
                "\"ColorName\"=\"NormalColor\""
            ])
        else:
            final_map = {
                "ActiveBorder": s(surface), "ActiveTitle": s(surface), "AppWorkSpace": s(base),
                "Background": s(base), "ButtonAlternativeFace": s(surface),
                "ButtonDkShadow": s(dkshadow), "ButtonFace": s(surface), "ButtonHilight": s(hilight),
                "ButtonLight": s(light), "ButtonShadow": s(shadow), "ButtonText": s(text),
                "GradientActiveTitle": s(surface), "GradientInactiveTitle": s(base),
                "GrayText": s(gray_text), "Hilight": s(accent), "HilightText": s(text),
                "InactiveBorder": s(base), "InactiveTitle": s(base), "InactiveTitleText": s(gray_text),
                "InfoText": s(text), "InfoWindow": s(surface), "Menu": s(surface),
                "MenuBar": s(surface), "MenuHilight": s(accent), "MenuText": s(text),
                "Scrollbar": s(base), "TitleText": s(text), "Window": s(base),
                "WindowFrame": s(light), "WindowText": s(text)
            }
            
            lines = [
                "Windows Registry Editor Version 5.00", "",
                f"; Auto-Converted from {theme_name}.ron (Legacy Mode)",
                "[HKEY_CURRENT_USER\\Control Panel\\Colors]"
            ]
            for k in sorted(final_map.keys()): 
                lines.append(f"\"{k}\"=\"{final_map[k]}\"")

        return "\n".join(lines)