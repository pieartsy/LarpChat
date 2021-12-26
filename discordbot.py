import discord
from discord.commands import Option

#to join paths
import os

from discord.embeds import Embed

bot = discord.Bot()

#discord bot token
token = os.environ.get('TOKEN')

guildID = 385833475954966529

def platform_post(platform=str, handle=str, makepost=str):
    if platform == "Flitter":
        if len(makepost) >= 280:
            toolong = len(makepost) - 280
            error = f"Your Flitter post was {toolong} characters too long! Flit shorter!"
            return(error)
        else:
            embed=discord.Embed(description=makepost, title="@" + handle, colour=0x55acee)
    elif platform == "XPosure":
        embed=discord.Embed(description=makepost, title="@" + handle, colour=0xE1306C)
    elif platform == "Bloggity":
        embed=discord.Embed(description=makepost, title="@" + handle, colour=0xffea00)
    return(embed)

@bot.slash_command(guild_ids=[guildID])
async def channelmaker(
    ctx,
    ):
    """Make channels and webhooks"""
    platforms = ['Bloggity', 'Flitter', 'XPosure']
    for platform in platforms:
        if discord.utils.get(ctx.guild.channels, name=platform.lower()):
            await ctx.respond("These channels already exist!", ephemeral=True)
            break
        else:
            postChannel = None
            postChannel = await ctx.guild.create_text_channel(name=platform)
            await postChannel.set_permissions(ctx.guild.default_role, send_messages=False)
            await postChannel.create_webhook(name=platform)

@bot.slash_command(guild_ids=[385833475954966529])
async def post(
    ctx,
    platform: Option(str, choices=["Bloggity", "Flitter", "XPosure"]),
    handle: str,
    makepost: Option(str, label="post")
    ):
    """Make a social media post"""
    await ctx.delete()
    content = platform_post(platform, handle, makepost)
    webhooks = await ctx.guild.webhooks()
    webhook = discord.utils.get(webhooks, name=platform)
    if isinstance(content, Embed):
        await webhook.send(embed=content)
    else:
        await ctx.respond(content, ephemeral=True)

#@post.error
#async def post_error(ctx, error):
 #   if isInstance(error, )
        
bot.run(token)