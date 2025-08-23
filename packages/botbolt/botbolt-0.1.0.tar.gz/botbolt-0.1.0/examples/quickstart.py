import botbolt

# Replace with your bot token (keep it secret!)
TOKEN = "YOUR_TOKEN"

bot = botbolt.Bot(token=TOKEN, prefix="!", intents="default")

@bot.event
async def on_ready():
    bot.log(f"Bot is logged in as {bot.user}")

@bot.command("ping")
async def ping(ctx):
    await bot.reply(ctx, "pong!")

# Slash command example:
@bot.slash("hello", "Say hello")
async def hello(interaction):
    await interaction.response.send_message("Hi from botbolt!")

bot.run()
