import requests
import websocket
import json
import time
import random

class ProfileHandler:
    def __init__(self, bot):
        self.bot = bot
        self.bot_profiles = {}

    def change_nickname(self, token, guild_id, new_nickname):
        url = f"https://discord.com/api/v9/guilds/{guild_id}/members/@me"
        headers = {
            'Authorization': token,
            'User-Agent': random.choice(self.bot.user_agents),
            'Content-Type': 'application/json'
        }
        data = {"nick": new_nickname}
        try:
            response = requests.patch(url, headers=headers, json=data, timeout=10)
            if response.status_code == 200:
                self.bot.ui.print_debug(f"Nickname changed to '{new_nickname}' for {token[:25]}...")
            elif response.status_code == 429:
                retry_after = response.json().get('retry_after', 5)
                self.bot.ui.print_debug(f"Rate limit: waiting {retry_after:.2f}s for {token[:25]}...")
                time.sleep(retry_after)
            else:
                self.bot.ui.print_debug(f"Error {response.status_code} changing nickname: {token[:25]}...")
        except requests.RequestException as e:
            self.bot.ui.print_debug(f"Network error changing nickname: {token[:25]}... {str(e)}")

    def set_online_status(self, token, status_text=None, activity_type="playing"):
        ws_url = "wss://gateway.discord.gg/?v=9&encoding=json"
        ws = websocket.WebSocket()
        try:
            ws.connect(ws_url)
            presence = {
                "status": "online",
                "afk": False
            }
            if status_text:
                activity_types = {
                    "playing": 0,
                    "streaming": 1,
                    "listening": 2,
                    "watching": 3,
                    "custom": 4,
                    "competing": 5
                }
                presence["activities"] = [{
                    "name": status_text,
                    "type": activity_types.get(activity_type, 0)
                }]
            identify_payload = {
                "op": 2,
                "d": {
                    "token": token,
                    "properties": {"$os": "windows", "$browser": "chrome", "$device": "pc"},
                    "presence": presence,
                    "compress": False,
                    "large_threshold": 250
                }
            }
            ws.send(json.dumps(identify_payload))
            response = json.loads(ws.recv())
            if response.get("op") == 10:
                heartbeat_interval = response["d"]["heartbeat_interval"] / 1000
                ws.send(json.dumps({"op": 1, "d": None}))
                self.bot.ui.print_debug(f"Online status set with '{activity_type} {status_text or ''}' for {token[:25]}...")
                self.keep_online(ws, heartbeat_interval, token)
            else:
                raise Exception("Invalid WebSocket response")
        except Exception as e:
            self.bot.ui.print_debug(f"Status setting error: {token[:25]}... {str(e)}")

    def set_custom_presence(self, token, status="online", status_text=None, activity_type="playing"):
        ws_url = "wss://gateway.discord.gg/?v=9&encoding=json"
        ws = websocket.WebSocket()
        try:
            ws.connect(ws_url)
            valid_statuses = ["online", "dnd", "idle", "invisible"]
            presence = {
                "status": status if status in valid_statuses else "online",
                "afk": False
            }
            if status_text:
                activity_types = {
                    "playing": 0,
                    "streaming": 1,
                    "listening": 2,
                    "watching": 3,
                    "custom": 4,
                    "competing": 5
                }
                presence["activities"] = [{
                    "name": status_text,
                    "type": activity_types.get(activity_type, 0)
                }]
            identify_payload = {
                "op": 2,
                "d": {
                    "token": token,
                    "properties": {"$os": "windows", "$browser": "chrome", "$device": "pc"},
                    "presence": presence,
                    "compress": False,
                    "large_threshold": 250
                }
            }
            ws.send(json.dumps(identify_payload))
            response = json.loads(ws.recv())
            if response.get("op") == 10:
                heartbeat_interval = response["d"]["heartbeat_interval"] / 1000
                ws.send(json.dumps({"op": 1, "d": None}))
                status_display = status if not status_text else f"{status} ({activity_type} {status_text})"
                self.bot.ui.print_debug(f"Custom status '{status_display}' set for {token[:25]}...")
                self.keep_online(ws, heartbeat_interval, token)
            else:
                raise Exception("Invalid WebSocket response")
        except Exception as e:
            self.bot.ui.print_debug(f"Custom status setting error: {token[:25]}... {str(e)}")

    def keep_online(self, ws, heartbeat_interval, token):
        while self.bot.running and token in self.bot.tokens:
            try:
                ws.send(json.dumps({"op": 1, "d": None}))
                time.sleep(heartbeat_interval)
            except Exception:
                self.bot.ui.print_debug(f"Status maintenance error: {token[:25]}...")
                break
        ws.close()

    def update_profile(self, token, pronoun=None, bio=None):
        url = "https://discord.com/api/v9/users/@me/profile"
        headers = {
            'Authorization': token,
            'User-Agent': random.choice(self.bot.user_agents),
            'Content-Type': 'application/json'
        }
        data = {}
        if pronoun:
            data["pronouns"] = pronoun
        if bio:
            data["bio"] = bio
        try:
            response = requests.patch(url, headers=headers, json=data, timeout=10)
            if response.status_code == 200:
                self.bot.ui.print_debug(f"Profile updated for {token[:25]}... Pronoun: {pronoun}, Bio: {bio}")
                self.bot_profiles[token] = {"pronoun": pronoun, "bio": bio}
            elif response.status_code == 429:
                retry_after = response.json().get('retry_after', 5)
                self.bot.ui.print_debug(f"Rate limit: waiting {retry_after:.2f}s for {token[:25]}...")
                time.sleep(retry_after)
            else:
                self.bot.ui.print_debug(f"Error {response.status_code} updating profile: {token[:25]}...")
        except requests.RequestException as e:
            self.bot.ui.print_debug(f"Network error updating profile: {token[:25]}... {str(e)}") 