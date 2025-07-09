import websocket
import json
import threading
import time
import random

class VoiceHandler:
    def __init__(self, bot):
        self.bot = bot
        self.voice_connections = {}

    def join_voice(self, token, guild_id, channel_id):
        ws_url = "wss://gateway.discord.gg/?v=9&encoding=json"
        ws = websocket.WebSocket()
        try:
            ws.connect(ws_url)
            identify_payload = {
                "op": 2,
                "d": {
                    "token": token,
                    "properties": {"$os": "windows", "$browser": "chrome", "$device": "pc"},
                    "compress": False,
                    "large_threshold": 250
                }
            }
            ws.send(json.dumps(identify_payload))
            response = json.loads(ws.recv())
            if response.get("op") == 10:
                heartbeat_interval = response["d"]["heartbeat_interval"] / 1000
                ws.send(json.dumps({"op": 1, "d": None}))
                voice_state_payload = {
                    "op": 4,
                    "d": {"guild_id": guild_id, "channel_id": channel_id, "self_mute": True, "self_deaf": True}
                }
                ws.send(json.dumps(voice_state_payload))
                self.bot.ui.print_debug(f"Connected to channel {channel_id}: {token[:25]}...")
                self.voice_connections[token] = ws

                while self.bot.running and token in self.bot.tokens:
                    time.sleep(heartbeat_interval)
                    ws.send(json.dumps({"op": 1, "d": None}))
            else:
                raise Exception("Invalid WebSocket response")
        except Exception as e:
            self.bot.ui.print_debug(f"WebSocket error: {token[:25]}... {str(e)}")
            self.bot.remove_token(token)
        finally:
            if token in self.voice_connections:
                try:
                    ws.close()
                except:
                    pass
                del self.voice_connections[token]

    def join_group_call(self, token, channel_id):
        ws_url = "wss://gateway.discord.gg/?v=9&encoding=json"
        ws = websocket.WebSocket()
        try:
            ws.connect(ws_url)
            identify_payload = {
                "op": 2,
                "d": {
                    "token": token,
                    "properties": {"$os": "windows", "$browser": "chrome", "$device": "pc"},
                    "compress": False,
                    "large_threshold": 250
                }
            }
            ws.send(json.dumps(identify_payload))
            response = json.loads(ws.recv())
            if response.get("op") == 10:
                heartbeat_interval = response["d"]["heartbeat_interval"] / 1000
                ws.send(json.dumps({"op": 1, "d": None}))
                voice_state_payload = {
                    "op": 4,
                    "d": {"guild_id": None, "channel_id": channel_id, "self_mute": True, "self_deaf": True}
                }
                ws.send(json.dumps(voice_state_payload))
                self.bot.ui.print_debug(f"Connected to call {channel_id}: {token[:25]}...")
                self.voice_connections[token] = ws

                while self.bot.running and token in self.bot.tokens:
                    time.sleep(heartbeat_interval)
                    ws.send(json.dumps({"op": 1, "d": None}))
            else:
                raise Exception("Invalid WebSocket response")
        except Exception as e:
            self.bot.ui.print_debug(f"WebSocket error: {token[:25]}... {str(e)}")
            self.bot.remove_token(token)
        finally:
            if token in self.voice_connections:
                try:
                    ws.close()
                except:
                    pass
                del self.voice_connections[token]

    def unmute(self, guild_id, channel_id):
        for token, ws in list(self.voice_connections.items()):
            try:
                unmute_payload = {
                    "op": 4,
                    "d": {"guild_id": guild_id, "channel_id": channel_id, "self_mute": False, "self_deaf": False}
                }
                ws.send(json.dumps(unmute_payload))
                self.bot.ui.print_debug(f"Token {token[:25]}... unmuted")
            except Exception as e:
                self.bot.ui.print_debug(f"Unmute error: {token[:25]}... {str(e)}")

    def mute(self, guild_id, channel_id):
        for token, ws in list(self.voice_connections.items()):
            try:
                mute_payload = {
                    "op": 4,
                    "d": {"guild_id": guild_id, "channel_id": channel_id, "self_mute": True, "self_deaf": True}
                }
                ws.send(json.dumps(mute_payload))
                self.bot.ui.print_debug(f"Token {token[:25]}... muted")
            except Exception as e:
                self.bot.ui.print_debug(f"Mute error: {token[:25]}... {str(e)}")

    def disconnect_all(self):
        for token, ws in list(self.voice_connections.items()):
            voice_state_payload = {
                "op": 4,
                "d": {"guild_id": None, "channel_id": None, "self_mute": True, "self_deaf": True}
            }
            try:
                ws.send(json.dumps(voice_state_payload))
                ws.close()
                self.bot.ui.print_debug(f"Disconnected: {token[:25]}...")
            except Exception as e:
                self.bot.ui.print_debug(f"Disconnect error: {token[:25]}... {str(e)}")
            finally:
                if token in self.voice_connections:
                    del self.voice_connections[token]

    def run_voice(self, guild_id, channel_id):
        self.bot.tokens = self.bot.get_tokens()
        if not self.bot.tokens:
            return
        self.bot.running = True
        self.bot.active_threads = []
        for token in self.bot.tokens:
            thread = threading.Thread(target=self.join_voice, args=(token, guild_id, channel_id))
            self.bot.active_threads.append(thread)
            thread.start()
            time.sleep(random.uniform(0.5, 1.5))

    def run_group_call(self, channel_id):
        self.bot.tokens = self.bot.get_tokens()
        if not self.bot.tokens:
            return
        self.bot.running = True
        self.bot.active_threads = []
        for token in self.bot.tokens:
            thread = threading.Thread(target=self.join_group_call, args=(token, channel_id))
            self.bot.active_threads.append(thread)
            thread.start()
            time.sleep(random.uniform(0.5, 1.5)) 