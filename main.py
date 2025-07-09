from src.utils.discord_bot import DiscordBot
from src.visual.terminal_ui import TerminalUI
from src.visual.theme_manager import ThemeManager
from colorama import Style
import time
import signal
import sys
import threading

def signal_handler(sig, frame):
    print("\nExiting gracefully...")
    sys.exit(0)

def check_spam_status(bot):
    while bot.running:
        time.sleep(0.5)
        if not any(thread.is_alive() for thread in bot.active_threads):
            bot.message_handler.stop_spam()
            bot.ui.clear_terminal()
            return

def main():
    signal.signal(signal.SIGINT, signal_handler)
    token_file = "tokens.txt"
    bot = DiscordBot(token_file)
    ui = TerminalUI()
    theme_manager = ThemeManager()
    ui.print_header()

    while True:
        try:
            ui.print_menu()
            choice = ui.themed_input("Choice")

            if choice == "1":
                ui.clear_terminal()
                channel_id = ui.themed_input("Channel ID")
                
                print(f"\n{theme_manager.get_theme_ansi_color(0.5)}Select spam mode:{Style.RESET_ALL}")
                print("1 ~ Aggressive")
                print("2 ~ Life Questions")
                print("3 ~ Promo")
                print("4 ~ Copypasta")
                print("5 ~ Compliments")
                print("6 ~ Random")
                print("7 ~ Custom Config")
                print("8 ~ Custom Console")
                spam_choice = ui.themed_input("Mode")
                
                spam_mode = {
                    "1": "aggressive",
                    "2": "life_questions",
                    "3": "promo",
                    "4": "copypasta",
                    "5": "compliments",
                    "6": "random",
                    "7": "custom",
                    "8": "custom_console"
                }.get(spam_choice, "life_questions")

                if spam_mode == "custom_console":
                    print(f"\n{theme_manager.get_theme_ansi_color(0.5)}Enter custom messages (one per line, press Enter twice to finish):{Style.RESET_ALL}")
                    custom_messages = []
                    while True:
                        msg = input()
                        if not msg:
                            break
                        custom_messages.append(msg)
                    if custom_messages:
                        bot.message_handler.config["spam_lists"]["custom_console"] = custom_messages
                
                emoji_count = int(ui.themed_input("Number of emojis (0-10)") or "0")
                emoji_count = max(0, min(10, emoji_count))
                
                use_random = ui.themed_input("Use random characters? (y/N)").lower() == 'y'
                mention_users = ui.themed_input("Mention users? (y/N)").lower() == 'y'
                
                spam_interval = float(ui.themed_input("Interval"))
                spam_time = ui.themed_input("Spam duration")
                
                bot.spam_interval = spam_interval
                bot.spam_duration = float(spam_time) if spam_time else None
                bot.message_handler.run_spam(
                    channel_id,
                    spam_mode=spam_mode,
                    emoji_count=emoji_count,
                    use_random_chars=use_random,
                    mention_users=mention_users,
                    custom_messages=bot.message_handler.config["spam_lists"].get("custom_console") if spam_mode == "custom_console" else None
                )
                ui.print_debug("Spam started. Type 'stop' to end")
                
                monitor = threading.Thread(target=check_spam_status, args=(bot,))
                monitor.daemon = True
                monitor.start()
                
                if input().lower() == "stop":
                    bot.message_handler.stop_spam()
                ui.clear_terminal()
                continue

            elif choice == "2":
                ui.clear_terminal()
                guild_id = ui.themed_input("Server ID")
                voice_channel_id = ui.themed_input("VC ID")
                bot.voice_handler.run_voice(guild_id, voice_channel_id)
                ui.print_debug("Voice joiner started. Commands: 'unmute', 'mute', 'stop'")
                while True:
                    command = input().lower()
                    if command == "unmute":
                        bot.voice_handler.unmute(guild_id, voice_channel_id)
                    elif command == "mute":
                        bot.voice_handler.mute(guild_id, voice_channel_id)
                    elif command == "stop":
                        bot.stop()
                        break

            elif choice == "3":
                bot.voice_handler.disconnect_all()

            elif choice == "4":
                bot.stop()
                break

            elif choice == "5":
                ui.clear_terminal()
                channel_id = ui.themed_input("Group channel ID")
                bot.voice_handler.run_group_call(channel_id)
                ui.print_debug("Mass function started. Commands: 'unmute', 'mute', 'stop'")
                while True:
                    command = input().lower()
                    if command == "unmute":
                        bot.voice_handler.unmute(None, channel_id)
                    elif command == "mute":
                        bot.voice_handler.mute(None, channel_id)
                    elif command == "stop":
                        bot.stop()
                        break

            elif choice == "6":
                bot.tokens = bot.check_all_tokens()

            elif choice == "7" or choice.lower() == "clear":
                ui.clear_terminal()

            elif choice == "8":
                ui.clear_terminal()
                guild_id = ui.themed_input("Server ID")
                new_nickname = ui.themed_input("New nickname")
                for token in bot.tokens:
                    bot.profile_handler.change_nickname(token, guild_id, new_nickname)

            elif choice == "9":
                ui.clear_terminal()
                for token in bot.tokens:
                    bot.profile_handler.set_online_status(token)
                ui.print_debug("Setting online status...")

            elif choice == "10":
                ui.clear_terminal()
                pronoun = ui.themed_input("New pronoun")
                bio = ui.themed_input("New bio")
                for token in bot.tokens:
                    bot.profile_handler.update_profile(token, pronoun if pronoun else None, bio if bio else None)

            elif choice == "11":
                ui.clear_terminal()
                status_text = ui.themed_input("Status text (e.g. 'Minecraft')")
                activity_type = ui.themed_input("Activity type (playing/streaming/listening/watching/custom/competing) [default: playing]")
                if not activity_type:
                    activity_type = "playing"
                for token in bot.tokens:
                    bot.profile_handler.set_online_status(token, status_text, activity_type)
                ui.print_debug(f"Setting custom status: {activity_type} {status_text}")

            elif choice == "12":
                ui.clear_terminal()
                status = ui.themed_input("Status type (online/dnd/idle/invisible) [default: online]")
                if not status:
                    status = "online"
                status_text = ui.themed_input("Activity text (Enter to skip)")
                activity_type = ui.themed_input("Activity type (playing/streaming/listening/watching/custom/competing) [default: playing]")
                if not activity_type:
                    activity_type = "playing"
                for token in bot.tokens:
                    bot.profile_handler.set_custom_presence(token, status, status_text if status_text else None, activity_type)
                ui.print_debug(f"Setting custom status: {status}")

            elif choice == "13":
                while True:
                    ui.print_themes_menu()
                    theme_choice = ui.themed_input("Choice")
                    try:
                        theme_index = int(theme_choice) - 1
                        theme_names = ui.get_theme_names()
                        if 0 <= theme_index < len(theme_names):
                            theme_name = theme_names[theme_index]
                            ui.set_theme(theme_name)
                            ui.clear_terminal()
                            break
                    except:
                        pass
                continue

        except KeyboardInterrupt:
            print("\nOperation cancelled. Returning to menu...")
            continue
        except Exception as e:
            print(f"\nError occurred: {str(e)}")
            continue

if __name__ == "__main__":
    main() 