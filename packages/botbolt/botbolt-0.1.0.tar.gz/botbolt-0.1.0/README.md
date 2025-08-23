# botbolt

**botbolt** is a friendlier Python wrapper around **nextcord**, designed to make Discord bot building simple and fast.

> Install (after you publish):  
> `pip install botbolt`

## Quickstart

```py
import botbolt

bot = botbolt.Bot(token="YOUR_TOKEN_HERE", prefix="!")

@bot.event
async def on_ready():
    bot.log("✅ Logged in as {0}".format(bot.user))

@bot.command("ping")
async def ping(ctx):
    await bot.reply(ctx, "pong!")

bot.run()
```

### Features
- Zero-boilerplate intents setup.
- Simple decorators: `@bot.event`, `@bot.command`.
- Handy helpers: `bot.reply(ctx, ...)`, `bot.embed(...)`, `bot.log(...)`.
- Works on top of **nextcord** so you keep its power if you need it.

## Why?
If `discord.py`/`nextcord` feels like too much at first, **botbolt** removes the friction without hiding the power.

## License
MIT © You
