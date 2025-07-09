import os
import sys
import colorama
from colorama import Style
import time
import json
from .theme_manager import ThemeManager

class TerminalUI:
    def __init__(self):
        colorama.init(autoreset=True)
        self.theme_manager = ThemeManager()

    def apply_gradient(self, text, center=False):
        lines = text.splitlines()
        terminal_width = os.get_terminal_size().columns if hasattr(os, 'get_terminal_size') else 80
        
        for line in lines:
            if center:
                padding = (terminal_width - len(line)) // 2
                line = " " * padding + line + " " * (terminal_width - len(line) - padding)
            
            for i, char in enumerate(line):
                progress = i / (len(line) - 1) if len(line) > 1 else 0
                print(self.theme_manager.get_theme_ansi_color(progress) + char, end="")
            print("\033[0m")

    def set_theme(self, theme_name):
        if theme_name in self.theme_manager.config["themes"]:
            self.theme_manager.current_theme = theme_name
            self.theme_manager.config["themes"]["current_theme"] = theme_name
            try:
                with open("config.json", "w", encoding="utf-8") as f:
                    json.dump(self.theme_manager.config, f, indent=4, ensure_ascii=False)
            except Exception as e:
                print(f"Error saving config: {e}")
            return True
        return False

    def get_theme_names(self):
        return [theme for theme in self.theme_manager.config["themes"].keys() if theme != "current_theme"]

    def print_themes_menu(self):
        self.clear_terminal()
        themes = self.get_theme_names()
        menu_text = """
themes
"""
        
        for i, theme in enumerate(themes, 1):
            theme_info = self.theme_manager.config["themes"][theme]
            menu_text += f"         ‹{i:02}› → [{theme_info['name']}]\n"
        
        self.apply_gradient(menu_text, center=True)

    def themed_input(self, prompt):
        return input(f"{self.theme_manager.get_theme_ansi_color(0.5)}kris@menu$~ → {prompt} ~ {Style.RESET_ALL}")

    def loading_animation(self):
        terminal_width = os.get_terminal_size().columns if hasattr(os, 'get_terminal_size') else 80
        base_text = "[/] Loading"
        frames = [
            f"{base_text}.  ",
            f"{base_text}.. ",
            f"{base_text}...",
            f"{base_text}.. ",
            f"{base_text}.  ",
            f"[\\] Loading.. ",
            f"[-] Loading.. ",
            f"[|] Loading.. ",
        ]
        
        for _ in range(3):
            for i, frame in enumerate(frames):
                progress = (i % len(frames)) / len(frames)
                padding = (terminal_width - len(frame)) // 2
                centered_frame = " " * padding + frame
                sys.stdout.write(f"\r{self.theme_manager.get_theme_ansi_color(progress)}{centered_frame}\033[0m")
                sys.stdout.flush()
                time.sleep(0.1)
        sys.stdout.write(f"\r{' ' * terminal_width}\r")
        sys.stdout.flush()

    def clear_terminal(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def print_debug(self, message, center=True):
        self.apply_gradient(f"[DEBUG] {message}", center)

    def print_header(self):
        self.clear_terminal()
        self.loading_animation()
        self.apply_gradient("""

        """)

    def print_menu(self):
        self.clear_terminal()
        self.apply_gradient("""


             ╦╔═╦═╗╦╔═╗  ╦═╗╔═╗╦╔╦╗╔═╗╦═╗ $~[>]  → Maden by kriska1337
             ╠╩╗╠╦╝║╚═╗  ╠╦╝╠═╣║ ║║║╣ ╠╦╝ $~[07] → Exit
             ╩ ╩╩╚═╩╚═╝  ╩╚═╩ ╩╩═╩╝╚═╝╩╚═ $~[13] → Themes

         ‹01› → [Spammer]            ‹07› → [Terminal Clear]  
         ‹02› → [VC Joiner]          ‹08› → [Nickname Changer]
         ‹03› → [VC Leaver]          ‹09› → [Onliner]
         ‹04› → [Exit]               ‹10› → [Bio Changer]
         ‹05› → [Group Call Spammer] ‹11› → [Custom Status]
         ‹06› → [Token Checker]      ‹12› → [Custom Status #2]
         
""") 