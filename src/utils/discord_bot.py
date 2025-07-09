import requests
import random
import time
import threading
import json
import websocket
from ..visual.terminal_ui import TerminalUI
from ..functions.voice_handler import VoiceHandler
from ..functions.message_handler import MessageHandler
from ..functions.profile_handler import ProfileHandler

class DiscordBot:
    def __init__(self, token_file, spam_interval=1):
        self.token_file = token_file
        self.spam_interval = spam_interval
        self.spam_duration = None
        self.running = True
        self.active_threads = []
        
       
        self.ui = TerminalUI()
        
       
        self.tokens = self.get_tokens()
        

        self.voice_handler = VoiceHandler(self)
        self.message_handler = MessageHandler(self)
        self.profile_handler = ProfileHandler(self)
        

        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_2_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/120.0.2210.91",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1",
            "Mozilla/5.0 (Android 14; Mobile; rv:121.0) Gecko/121.0 Firefox/121.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 11.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:120.0) Gecko/20100101 Firefox/120.0",
            "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Safari/605.1.15",
            "Mozilla/5.0 (iPad; CPU OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1",
            "Mozilla/5.0 (Android 13; Mobile; rv:119.0) Gecko/119.0 Firefox/119.0",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36 OPR/101.0.0.0",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1823.51",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 12_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36"
        ]
        self.rate_limit_delays = {}

    def get_tokens(self):
        try:
            with open(self.token_file, "r") as f:
                tokens = [line.strip() for line in f if line.strip()]
                if not tokens:
                    self.ui.print_debug("Token file is empty!")
                    return []
                self.ui.print_debug(f"Loaded tokens: {len(tokens)}")
                return tokens
        except FileNotFoundError:
            self.ui.print_debug(f"File {self.token_file} not found!")
            return []

    def check_token(self, token):
        url = "https://discord.com/api/v9/users/@me"
        headers = {
            'Authorization': token,
            'User-Agent': random.choice(self.user_agents),
            'Content-Type': 'application/json'
        }
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                user_data = response.json()
                username = user_data.get('username', 'Unknown')
                self.ui.print_debug(f"Valid token: {token[:25]}... | Username: {username}")
                return True, username
            else:
                self.ui.print_debug(f"Invalid token: {token[:25]}...")
                return False, None
        except requests.RequestException as e:
            self.ui.print_debug(f"Token check error: {token[:25]}... {e}")
            return False, None

    def check_all_tokens(self):
        self.ui.clear_terminal()
        self.ui.print_debug("Token check started...")
        tokens = []
        try:
            with open(self.token_file, "r") as f:
                tokens = [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            self.ui.print_debug(f"File {self.token_file} not found!")
            return []

        if not tokens:
            self.ui.print_debug("Token file is empty!")
            return []

        valid_tokens = []
        for token in tokens:
            is_valid, username = self.check_token(token)
            if is_valid:
                valid_tokens.append(token)
            time.sleep(0.5)

        self.ui.print_debug(f"Check complete. Valid tokens: {len(valid_tokens)}")
        return valid_tokens

    def remove_token(self, token):
        if token in self.tokens:
            self.tokens.remove(token)
            self.ui.print_debug(f"Token {token[:25]}... removed from session")

    def stop(self):
        self.running = False
        self.voice_handler.disconnect_all()
        for thread in self.active_threads:
            thread.join()
        self.ui.print_debug("Program stopped") 