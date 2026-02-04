## Disclaimer
This is not a public bot to invite—it's a template for you to create and run your own personal reminder bot. If you want to use it in your own server, create a bot on the Discord Developer Portal and use your own client ID in the invite link.

# Discord Reminder Bot

A simple Discord bot for personal reminders and task management. Built with Python and discord.py.

## Commands

🐱🌹 **Commands:** 🌹🐱
- `type add "jan 15 example event"` – Add a new event
- `type list` – List all your events
- `type remove 1` – Remove the event at index 1 (1-indexed)
- `type edit 1 "updated event"` – Edit the event at index 1
- `type append 1 "extra text"` – Append text to the event at index 1
- `type time HH:MM` – Set your daily reminder time in UTC (e.g., 18:02)
- `type time` – View your current reminder time

## Date & Time Formats

Events are sorted by date and time. Supported formats:
- `jan 15 dentist` – Date only (defaults to current year)
- `jan 15 2026 dentist` – Date with year
- `jan 15 10:30 dentist` – Date with 24-hour time
- `jan 15 9:30am dentist` – Date with 12-hour time
- `jan 15 24:00 deadline` – Use 24:00 for end of day (sorts after 23:59)

## Reminders

The bot sends reminders via DM:
- **Daily summary** – All your events at your configured reminder time (default: 03:30 UTC)
- **1 hour before** – Events with a specific time get a reminder 1 hour before
- **1 day before** – Events without a time get a reminder the day before (at your daily reminder time)

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
   for /f %i in (bot.pid) do taskkill /F /PID %i
   del bot.pid
   ```

## File Overview
- `bot.py` – Discord bot logic and commands
- `storage.py` – Handles reading/writing reminders and tasks
- `storage.json` – Stores user data (all data is stored raw locally in an unencrypted JSON file for personal use)

---
