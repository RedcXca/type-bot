## Disclaimer
This is not a public bot to invite—it's a template for you to create and run your own personal reminder bot. If you want to use it in your own server, create a bot on the Discord Developer Portal and use your own client ID in the invite link.

# Discord Reminder Bot

A simple Discord bot for personal reminders and task management. Built with Python and discord.py.

## Commands

🐱🌹 **Commands:** 🌹🐱
- `type add "example event"` – Add a new event
- `type list` – List all your events
- `type remove 1` – Remove the event at index 1 (1-indexed)
- `type edit 1 "updated event"` – Edit the event at index 1
- `type time HH:MM (UTC)` – Set your daily reminder time (e.g., 18:02)
- `type shit` – Bot replies with 'type shit 🐱🌹'

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Create a `.env` file with your bot token (get your own token from the Discord Developer Portal):
   ```env
   DISCORD_TOKEN=your_token_here
   ```
3. Run the bot in the background (Windows Command Prompt, no console window):
   ```cmd
   start pythonw bot.py
   ```
   The bot will append its PID (process ID) to `bot.pid` every time it is started. To stop all running bot processes, use:
   ```cmd
   for /f %i in (bot.pid) do taskkill /F /PID %i && del bot.pid
   ```

## File Overview
- `bot.py` – Discord bot logic and commands
- `storage.py` – Handles reading/writing reminders and tasks
- `storage.json` – Stores user data (all data is stored raw locally in an unencrypted JSON file for personal use)

---
