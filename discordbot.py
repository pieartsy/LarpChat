import discord
from discord.commands import Option

#to join paths
import os

bot = discord.Bot()

#discord bot token
token = os.environ.get('TOKEN')

def platform_post(platform=str):
    if platform == "Flitter":
        colour = 0x55acee
    elif platform == "XPosure":
        colour = 0xE1306C
    elif platform == "Bloggity":
        colour = 0xffea00
    return(colour)

@bot.slash_command(guild_ids=[385833475954966529])
async def post(
    ctx,
    platform: Option(str, label="platform", choices=["Bloggity", "Flitter", "XPosure"]),
    handle: str,
    makepost: Option(str, label="post")):
    """Make a social media post"""
    await ctx.delete()
    webhook = await ctx.channel.create_webhook(name=platform)
    colour = platform_post(platform)
    embed=discord.Embed(description=makepost, title="@" + handle, colour=colour)
    await webhook.send(embed=embed)
    await webhook.delete()


bot.run(token)