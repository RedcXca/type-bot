import discord
from discord.ext import commands, tasks
import os
from dotenv import load_dotenv
from storage import Storage
from datetime import datetime

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='type ', intents=intents)
storage = Storage('storage.json')

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    reminder_loop.start()

@bot.command()
async def setup(ctx, time: str):
    user_id = str(ctx.author.id)
    storage.set_reminder_time(user_id, time)
    await ctx.send(f'Reminder time set to {time}')

@bot.command()
async def add(ctx, *, event: str):
    user_id = str(ctx.author.id)
    first_time = False
    events = storage.list_tasks(user_id)
    if not events:
        first_time = True
    storage.add_task(user_id, {"event": event, "user_id": user_id})
    await ctx.send(f'```Event added: {event}```')
    if first_time:
        await ctx.send('''```
🐱🌹 This bot will ping you every day at 11:30 pm (EST) 🌹🐱
Commands:
> type add "example event"
> type list
> type remove 1
> type edit 1 "updated event"
> type time HH:MM (UTC)
```''')

@bot.command()
async def list(ctx):
    user_id = str(ctx.author.id)
    events = storage.list_tasks(user_id)
    if not events:
        await ctx.send('```No events found.```')
        return
    sorted_events = sorted(events, key=lambda x: x["event"])
    msg = '\n'.join([f'{i+1}. {e["event"]}' for i, e in enumerate(sorted_events)])
    await ctx.send(f'```{msg}```')

@bot.command()
async def remove(ctx, index: int):
    user_id = str(ctx.author.id)
    events = storage.list_tasks(user_id)
    idx = index - 1
    if 0 <= idx < len(events):
        removed_event = events[idx]["event"]
        success = storage.remove_task(user_id, idx)
        if success:
            await ctx.send(f'```Event {index} removed: {removed_event}```')
        else:
            await ctx.send('```Error removing event.```')
    else:
        await ctx.send('```Invalid index.```')
@bot.command()
async def edit(ctx, index: int, *, event: str):
    user_id = str(ctx.author.id)
    success = storage.edit_task(user_id, index - 1, {"event": event, "user_id": user_id})
    if success:
        await ctx.send(f'```Event {index} updated to: {event}```')
    else:
        await ctx.send('```Invalid index.```')

@bot.command()
async def time(ctx, time: str):
    user_id = str(ctx.author.id)
    try:
        hour, minute = map(int, time.split(':'))
        if 0 <= hour < 24 and 0 <= minute < 60:
            storage.set_reminder_time(user_id, f"{hour:02d}:{minute:02d}")
            await ctx.send(f'```Reminder time set to {hour:02d}:{minute:02d} UTC. You will be pinged at this time every day.```')
        else:
            await ctx.send('```Invalid time format. Use HH:MM in UTC (e.g., 18:02).```')
    except Exception:
        await ctx.send('```Invalid time format. Use HH:MM in UTC (e.g., 18:02).```')

@bot.command()
async def shit(ctx):
    await ctx.send('```type shit 🐱🌹```')

@tasks.loop(minutes=1)
async def reminder_loop():
    now_utc = datetime.utcnow()
    data = storage._read()
    for user_id, user_data in data.items():
        reminder_time = user_data.get("reminder_time", "03:30")
        if now_utc.strftime("%H:%M") == reminder_time:
            events = user_data.get("events", [])
            if events:
                user = await bot.fetch_user(int(user_id))
                msg = '\n'.join([f'{i+1}. {e["event"]} 🐱🌹' for i, e in enumerate(sorted(events, key=lambda x: x["event"]))])
                await user.send(f'```Your events for today:\n{msg}```')

bot.run(TOKEN)
