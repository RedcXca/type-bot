import os
import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv
from storage import Storage
from datetime import datetime, timedelta
from utils import sort_key, get_date, strip_year, format_tz, get_reminder_time_utc, get_event_utc_datetime, parse_backlog_filter, matches_date_filter

os.makedirs("self", exist_ok=True)
with open("self/bot.pid", "a") as f:
    f.write(str(os.getpid()) + "\n")

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=['type ', 'Type ', 'TYPE '], intents=intents, help_command=None)

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send('```Unknown command. Type `type help` for a list of commands.```')
    else:
        raise error
storage = Storage('storage.json')

@bot.event
async def on_ready():
    reminder_loop.start()

@bot.command()
async def help(ctx):
    msg = '''```
🐱🌹 Type Bot Help 🌹🐱
> type add jan 15 10:30 example event
> type list
> type remove 1
> type edit 1 "updated event"
> type append 1 "extra text"
> type backlog feb 2026
> type time HH:MM
> type timezone -5
> type shit
```'''
    await ctx.send(msg)

@bot.command()
async def add(ctx, *, text: str):
    user_id = str(ctx.author.id)
    first_time = False
    events = storage.list_tasks(user_id)
    if not events:
        first_time = True

    date = get_date(text)
    stripped = strip_year(text)

    if not storage.add_task(user_id, stripped, date):
        await ctx.send(f'```Event already exists: {stripped}```')
        return

    # find index of newly added event in sorted list
    events = storage.list_tasks(user_id)
    sorted_events = sorted(events, key=sort_key)
    index = next(i for i, e in enumerate(sorted_events) if e["text"] == stripped) + 1

    await ctx.send(f'```Event added ({index}): {stripped}```')
    if first_time:
        await ctx.send('''```
🐱🌹 Welcome! Set your timezone first: type timezone -5 (for EST) 🌹🐱
> type add jan 15 10:30 example event
> type list
> type remove 1
> type edit 1 "updated event"
> type append 1 "extra text"
> type time HH:MM
> type help
```''')

@bot.command()
async def list(ctx):
    user_id = str(ctx.author.id)
    events = storage.list_tasks(user_id)
    if not events:
        await ctx.send('```No events found.```')
        return
    sorted_events = sorted(events, key=sort_key)
    msg = '\n'.join([f'{i+1}. {e["text"]}' for i, e in enumerate(sorted_events)])
    await ctx.send(f'```{msg}```')

@bot.command()
async def backlog(ctx, *, filter: str = ""):
    if not filter.strip():
        await ctx.send('```Usage: type backlog 2026 or type backlog feb 2026```')
        return

    user_id = str(ctx.author.id)
    events = storage.list_backlog(user_id)
    if not events:
        await ctx.send('```No backlog found.```')
        return

    # Parse filter: "2026" or "feb 2026"
    year, month = parse_backlog_filter(filter)
    events = [e for e in events if matches_date_filter(e.get("date"), year, month)]

    sorted_events = sorted(events, key=sort_key)
    if not sorted_events:
        await ctx.send('```No matching backlog events.```')
        return
    msg = '\n'.join([f'{i+1}. {e["text"]}' for i, e in enumerate(sorted_events)])
    await ctx.send(f'```{msg}```')

@bot.command()
async def remove(ctx, *indices: int):
    user_id = str(ctx.author.id)
    events = storage.list_tasks(user_id)
    if not events:
        await ctx.send('```No events found.```')
        return
    sorted_events = sorted(events, key=sort_key)
    removed = []
    # remove from highest index to lowest to avoid shifting issues
    for index in sorted(set(indices), reverse=True):
        if 0 <= index - 1 < len(sorted_events):
            storage_index = events.index(sorted_events[index - 1])
            event = events[storage_index]
            storage.remove_task(user_id, storage_index)
            removed.append(f"{index}. {event['text']}")
            events.pop(storage_index)
    if removed:
        removed.reverse()
        await ctx.send(f"```Removed events:\n" + "\n".join(removed) + "```")
    else:
        await ctx.send("```Invalid indices.```")

@bot.command()
async def edit(ctx, index: int, *, text: str):
    user_id = str(ctx.author.id)
    events = storage.list_tasks(user_id)
    sorted_events = sorted(events, key=sort_key)
    if 0 <= index - 1 < len(sorted_events):
        event_to_edit = sorted_events[index - 1]
        old_text = event_to_edit["text"]
        storage_index = events.index(event_to_edit)
        date = get_date(text)
        new_text = strip_year(text)
        success = storage.edit_task(user_id, storage_index, new_text, date)
        if success:
            await ctx.send(f'```Event {index} updated:\n{old_text}\n→ {new_text}```')
        else:
            await ctx.send('```Invalid index.```')
    else:
        await ctx.send('```Invalid index.```')

@bot.command()
async def append(ctx, index: int, *, text: str):
    user_id = str(ctx.author.id)
    events = storage.list_tasks(user_id)
    sorted_events = sorted(events, key=sort_key)
    if 0 <= index - 1 < len(sorted_events):
        event = sorted_events[index - 1]
        combined_text = event["text"] + " " + text
        await edit(ctx, index, text=combined_text)
    else:
        await ctx.send('```Invalid index.```')

@bot.command()
async def time(ctx, time: str = ""):
    user_id = str(ctx.author.id)
    data = storage._read()
    tz = data.get(user_id, {}).get("timezone", 0)
    if not time or time.strip() == "":
        reminder_time = data.get(user_id, {}).get("reminder_time", "03:30")
        await ctx.send(f'```Your reminder time is {reminder_time} ({format_tz(tz)}).```')
        return
    try:
        hour, minute = map(int, time.split(':'))
        if 0 <= hour < 24 and 0 <= minute < 60:
            storage.set_reminder_time(user_id, f"{hour:02d}:{minute:02d}")
            await ctx.send(f'```Reminder time set to {hour:02d}:{minute:02d} ({format_tz(tz)}).```')
        else:
            await ctx.send('```Invalid time format. Use HH:MM (e.g., 18:02).```')
    except ValueError as ve:
        await ctx.send('```Invalid time format. Use HH:MM (e.g., 18:02).```')
    except Exception as e:
        await ctx.send(f'```Unknown error: {str(e)}```')

@bot.command()
async def timezone(ctx, offset: str = ""):
    user_id = str(ctx.author.id)
    if not offset or offset.strip() == "":
        data = storage._read()
        tz = data.get(user_id, {}).get("timezone", 0)
        await ctx.send(f'```Your timezone is {format_tz(tz)}.```')
        return
    try:
        tz = float(offset)
        if -12 <= tz <= 14:
            storage.set_timezone(user_id, tz)
            await ctx.send(f'```Timezone set to {format_tz(tz)}.```')
        else:
            await ctx.send('```Invalid timezone. Use an offset like -5 (EST), 5.5 (IST), or -3.5 (NST).```')
    except ValueError:
        await ctx.send('```Invalid timezone. Use an offset like -5 (EST), 5.5 (IST), or -3.5 (NST).```')

@bot.command()
async def shit(ctx):
    await ctx.send('```type shit 🐱🌹```')

@tasks.loop(minutes=1)
async def reminder_loop():
    now_utc = datetime.utcnow()
    data = storage._read()
    for user_id, user_data in data.items():
        tz_offset = user_data.get("timezone", 0)
        reminder_time = user_data.get("reminder_time", "03:30")
        reminder_time_utc = get_reminder_time_utc(reminder_time, tz_offset, now_utc.date())

        # Daily summary at configured time
        if now_utc.strftime("%H:%M") == reminder_time_utc.strftime("%H:%M"):
            events = user_data.get("events", [])
            if events:
                user = await bot.fetch_user(int(user_id))
                sorted_events = sorted(events, key=sort_key)
                msg = '\n'.join([f'{i+1}. {e["text"]} 🐱🌹' for i, e in enumerate(sorted_events)])
                await user.send(f'```Your upcoming events:\n{msg}```')

        # Per-event reminders and auto-archive
        events = user_data.get("events", [])
        to_archive = []
        for event in events:
            try:
                event_utc = get_event_utc_datetime(event, tz_offset)
                if event_utc:
                    # Has time: remind 1 hour before
                    remind_at_utc = event_utc - timedelta(hours=1)
                    if now_utc.strftime("%Y-%m-%d %H:%M") == remind_at_utc.strftime("%Y-%m-%d %H:%M"):
                        user = await bot.fetch_user(int(user_id))
                        await user.send(f'```⏰ In 1 hour: {event["text"]} 🐱🌹```')
                    # Auto-archive if event time has passed
                    if now_utc > event_utc:
                        to_archive.append(event)
                else:
                    # No time: remind 1 day before at user's reminder_time
                    date_str = event.get("date")
                    if not date_str:
                        continue
                    event_date = datetime.strptime(date_str, "%Y-%m-%d")
                    if now_utc.strftime("%H:%M") == reminder_time_utc.strftime("%H:%M"):
                        now_local = now_utc + timedelta(hours=tz_offset)
                        tomorrow_local = now_local.date() + timedelta(days=1)
                        if event_date.date() == tomorrow_local:
                            user = await bot.fetch_user(int(user_id))
                            await user.send(f'```⏰ Tomorrow: {event["text"]} 🐱🌹```')
            except Exception as e:
                print(f"[ERROR] reminder check failed for event {event}: {e}")

        # Archive expired events
        for event in to_archive:
            storage.archive_event(user_id, event)

bot.run(TOKEN)
