import discord
from discord.ext import commands
from config import TOKEN

intents = discord.Intents.default()
intents.members = True
intents.voice_states = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    print(f"Bot is online as {bot.user}")
    await bot.tree.sync()


async def load_extensions():
    await bot.add_cog(__import__("cogs.game").game.Game(bot))


@bot.event
async def setup_hook():
    await load_extensions()


bot.run(TOKEN)