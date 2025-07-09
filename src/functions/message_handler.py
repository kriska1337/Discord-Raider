import requests
import time
import random
import threading
import json
import string
import re

class MessageHandler:
    def __init__(self, bot):
        self.bot = bot
        self.config = self.load_config()
        self.spam_mode = "life_questions"
        self.emoji_count = 0
        self.use_random_chars = False
        self.mention_users = False
        self.server_members = []
        self.stop_event = threading.Event()
        self.custom_messages = []

    def load_config(self):
        try:
            with open("config.json", "r", encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            self.bot.ui.print_debug("Config file not found! Using default settings...")
            return {
                "spam_lists": {
                    "life_questions": ["What's your favorite subject in school?"]
                },
                "emojis": ["😊"],
                "random_chars": ["★"]
            }

    def save_custom_spam(self, messages):
        try:
            self.config["custom_spam"] = messages
            with open("config.json", "w", encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
        except:
            pass

    def get_random_string(self, length=None):
        if length is None:
            length = random.randint(3, 8)
        chars = string.ascii_letters + string.digits + string.punctuation + ''.join(self.config.get('random_chars', []))
        result = ''.join(random.choice(chars) for _ in range(length))

        invisible_chars = ['\u200b', '\u200c', '\u200d', '\u2060', '\u180e']
        result = list(result)
        for _ in range(random.randint(1, 3)):
            pos = random.randint(0, len(result))
            result.insert(pos, random.choice(invisible_chars))
        return ''.join(result)

    def get_random_emojis(self):
        if self.emoji_count <= 0:
            return ""
        emojis = self.config.get('emojis', [])
        if not emojis:
            return ""
        count = random.randint(1, self.emoji_count)
        selected = random.sample(emojis, min(count, len(emojis)))
        
        result = []
        for emoji in selected:
            result.append(emoji)
            if random.random() < 0.3:  # 30% chance
                result.append('\u200b')
        
        return ''.join(result)

    def get_server_members(self, token, channel_id):
        if not self.mention_users:
            return []
        
        try:
            
            headers = {
                'Authorization': token,
                'User-Agent': random.choice(self.config.get('user_agents', [self.bot.user_agents[0]])),
            }
            
            
            channel_url = f"https://discord.com/api/v9/channels/{channel_id}"
            response = requests.get(channel_url, headers=headers, timeout=10)
            if response.status_code != 200:
                return []
                
            guild_id = response.json().get('guild_id')
            if not guild_id:
                return []

            members_url = f"https://discord.com/api/v9/guilds/{guild_id}/members?limit=100"
            response = requests.get(members_url, headers=headers, timeout=10)
            if response.status_code != 200:
                return []

            members = response.json()
            member_mentions = []
            
            for member in members:
                if not member.get('user', {}).get('bot', False):
                    user_id = member['user']['id']
                    member_mentions.append(f"<@{user_id}>")
            
            random.shuffle(member_mentions)
            return member_mentions[:random.randint(1, 3)] 
        except:
            return []

    def format_spam_message(self, base_message):
        parts = []
        
        if self.use_random_chars and random.random() < 0.3:
            parts.append(self.get_random_string())
        
        message_chars = list(base_message)
        invisible = ['\u200b', '\u200c', '\u200d', '\u2060', '\u180e']
        for i in range(len(message_chars) - 1):
            if random.random() < 0.1:  
                message_chars.insert(i, random.choice(invisible))
        parts.append(''.join(message_chars))
        
        if self.mention_users and self.server_members:
            num_mentions = random.randint(1, min(3, len(self.server_members)))
            parts.extend(random.sample(self.server_members, num_mentions))
        
        emojis = self.get_random_emojis()
        if emojis:
            parts.append(emojis)
        
        if self.use_random_chars and random.random() < 0.3:
            parts.append(self.get_random_string())
        
        result = []
        for part in parts:
            result.append(part)
            if random.random() < 0.2:  # 20% chance
                result.append(random.choice(invisible))
        
        return ' '.join(result)

    def send_message(self, token, channel_id):
        url = f"https://discord.com/api/v9/channels/{channel_id}/messages"
        headers = {
            'Authorization': token,
            'User-Agent': random.choice(self.config.get('user_agents', [self.bot.user_agents[0]])),
            'Content-Type': 'application/json'
        }
        
        if self.mention_users:
            self.server_members = self.get_server_members(token, channel_id)

        spam_messages = (
            self.custom_messages if self.spam_mode in ["custom", "custom_console"]
            else self.config['spam_lists'].get(self.spam_mode, ["Default message"])
        )
        
        start_time = time.time()
        
        while self.bot.running and token in self.bot.tokens and not self.stop_event.is_set():
            if self.bot.spam_duration and (time.time() - start_time) >= self.bot.spam_duration:
                self.bot.ui.print_debug(f"Spam timeout for {token[:25]}...")
                self.stop_event.set()  
                break

            base_message = random.choice(spam_messages)
            message = self.format_spam_message(base_message)
            nonce = str(random.randint(100000000000000000, 999999999999999999))
            data = {"content": message, "nonce": nonce, "tts": False}

            try:
                if token in self.bot.rate_limit_delays:
                    delay = self.bot.rate_limit_delays[token]
                    if time.time() < delay:
                        time.sleep(delay - time.time())

                response = requests.post(url, headers=headers, json=data, timeout=10)
                if response.status_code == 200:
                    self.bot.ui.print_debug(f"Message sent: {token[:25]}...")
                elif response.status_code == 429:
                    retry_after = response.json().get('retry_after', 5) + random.uniform(0.1, 0.5)
                    self.bot.ui.print_debug(f"Rate limit: waiting {retry_after:.2f}s for {token[:25]}...")
                    self.bot.rate_limit_delays[token] = time.time() + retry_after
                    time.sleep(retry_after)
                    continue
                elif response.status_code == 401:
                    self.bot.ui.print_debug(f"Invalid token: {token[:25]}...")
                    self.bot.remove_token(token)
                    break
                else:
                    self.bot.ui.print_debug(f"Error {response.status_code}: {token[:25]}...")
            except requests.RequestException as e:
                self.bot.ui.print_debug(f"Network error: {token[:25]}... {str(e)}")
                time.sleep(5)
                continue

            time.sleep(max(self.bot.spam_interval, random.uniform(1, 2)))

    def run_spam(self, channel_id, spam_mode="life_questions", emoji_count=0, use_random_chars=False, mention_users=False, custom_messages=None):
        self.spam_mode = spam_mode
        self.emoji_count = emoji_count
        self.use_random_chars = use_random_chars
        self.mention_users = mention_users
        self.stop_event.clear()
        
        if custom_messages:
            self.custom_messages = custom_messages
            if spam_mode == "custom_console":
                self.config["spam_lists"]["custom_console"] = custom_messages
            else:
                self.config["spam_lists"]["custom"] = custom_messages
            self.save_custom_spam(custom_messages)
        
        self.bot.tokens = self.bot.get_tokens()
        if not self.bot.tokens:
            return
            
        self.bot.running = True
        self.bot.active_threads = []
        
        for token in self.bot.tokens:
            thread = threading.Thread(target=self.send_message, args=(token, channel_id))
            self.bot.active_threads.append(thread)
            thread.start()
            time.sleep(random.uniform(0.1, 0.5))

    def stop_spam(self):
        self.stop_event.set()
        self.bot.running = False 