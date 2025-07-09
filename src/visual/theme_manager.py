import json
import os

class ThemeManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ThemeManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self.load_config()
            self._initialized = True
    
    def load_config(self):
        try:
            with open("config.json", "r", encoding="utf-8") as f:
                self.config = json.load(f)
                self.current_theme = self.config["themes"].get("current_theme", "standard")
        except Exception as e:
            print(f"Error loading theme config: {e}")
            self.config = {"themes": {"current_theme": "standard"}}
            self.current_theme = "standard"
    
    def get_current_theme(self):
        return self.config["themes"].get(self.current_theme, self.config["themes"]["standard"])
    
    def get_theme_colors(self):
        theme = self.get_current_theme()
        return theme["gradient"]["start"], theme["gradient"]["end"]
    
    def get_gradient_color(self, progress):
        start_color, end_color = self.get_theme_colors()
        r = int(start_color[0] + (end_color[0] - start_color[0]) * progress)
        g = int(start_color[1] + (end_color[1] - start_color[1]) * progress)
        b = int(start_color[2] + (end_color[2] - start_color[2]) * progress)
        return r, g, b
    
    def apply_theme_to_text(self, text, progress=0.5):
        r, g, b = self.get_gradient_color(progress)
        return f"\033[38;2;{r};{g};{b}m{text}\033[0m"
    
    def get_theme_ansi_color(self, progress=0.5):
        r, g, b = self.get_gradient_color(progress)
        return f"\033[38;2;{r};{g};{b}m" 