## Disclaimer
This is not a public bot to invite—it's a template for you to create and run your own personal reminder bot. If you want to use it in your own server, create a bot on the Discord Developer Portal and use your own client ID in the invite link.

# Discord Reminder Bot

A simple Discord bot for personal reminders and task management. Built with Python and discord.py.

## Commands

- `type add jan 15 example event` – add a new event
- `type list` – list all your upcoming events
- `type remove 1` – remove the event at index 1 (moves to backlog)
- `type edit 1 "updated event"` – edit the event at index 1
- `type append 1 "extra text"` – append text to the event at index 1
- `type backlog` – view removed events
- `type time HH:MM` – set your daily reminder time (e.g., 23:30)
- `type time` – view your current reminder time
- `type birthday add feb 4 jason` – add a birthday
- `type birthday list` – list all saved birthdays
- `type timezone -5` – set your timezone offset (e.g., -5 for EST, 9 for JST)

## Date & Time Formats

Events are sorted by date and time. Supported formats:
- `jan 15 dentist` – date only (defaults to current year)
- `jan 15 2026 dentist` – date with year
- `jan 15 10:30 dentist` – date with 24-hour time
- `jan 15 9:30am dentist` – date with 12-hour time
- `jan 15 24:00 deadline` – use 24:00 for end of day (sorts after 23:59)

## Reminders

The bot sends reminders via DM (all times are in your configured timezone):
- **Daily summary** – all your events at your configured reminder time (default: 03:30)
- **1 hour before** – events with a specific time get a reminder 1 hour before
- **1 day before** – events without a time get a reminder the day before (at your daily reminder time)
- **Birthday reminder** – birthdays tomorrow are announced at your daily reminder time

Set your timezone with `type timezone -5` (for EST) so reminders trigger at the right time.

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Create a `.env` file with your bot token (get your own token from the Discord Developer Portal):
   ```env
   DISCORD_TOKEN=your_token_here
   ```
3. Run the bot:
   ```bash
   nohup python3 bot.py &
   ```

## Hosting

This bot runs on a **Google Cloud e2-micro** instance (free tier):
- 2 shared vCPUs
- 1 GB RAM
- 30 GB standard persistent disk
- Debian/Ubuntu OS

A cron job runs every 12 hours to auto-pull new commits and restart the bot. See `deployment-notes.txt` for setup and deploy commands.

## File Overview
- `bot.py` – discord bot logic and commands
- `storage.py` – handles reading/writing reminders and tasks
- `storage.json` – stores user data (all data is stored raw locally in an unencrypted JSON file for personal use)
- `birthdays.json` – stores birthday data
- `example-storage.json` – example storage structure for reference
- `example-birthdays.json` – example birthdays structure for reference
