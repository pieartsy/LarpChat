import discord

# intents let me access message content with discord's new privacy permissions
intents = discord.Intents.default()
intents.message_content = True

bot = discord.Bot(intents=intents)
