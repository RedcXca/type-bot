## Disclaimer
This is not a public bot to invite—it's a template for you to create and run your own personal reminder bot. If you want to use it in your own server, create a bot on the Discord Developer Portal and use your own client ID in the invite link.

# Discord Reminder Bot

A simple Discord bot for personal reminders and task management. Built with Python and discord.py.

## Features
- Set a daily reminder time
- Add tasks with date and time
- List tasks (sorted, indexed)
- Remove tasks by index
- All data saved in `events.json`

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
2. Create a `.env` file with your bot token (you must use your own bot token from the Discord Developer Portal):
   ```env
   DISCORD_TOKEN=your_token_here
   ```
3. Run the bot in the background (bash):
   ```bash
   nohup python bot.py &
   ```
   This will keep the bot running even after you close the terminal.

4. To kill the bot process:
   ```bash
   ps aux | grep bot.py
   kill <PID>
   ```
   Replace `<PID>` with the process ID shown in the output.

## File Overview
- `bot.py` – Discord bot logic and commands
- `storage.py` – Handles reading/writing reminders and tasks
- `storage.json` – Stores user data (all data is stored raw locally in an unencrypted JSON file but it's just for personal use)

---
