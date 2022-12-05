import discord

#to join paths
import os

#discord bot token
token = os.environ.get('TOKEN')

from posts import Post
from botvars import bot

# "social media" platforms
platforms = ["Flitter", "Bloggity", "Xposure"]
# token of my test server
guild_ID = 385833475954966529

# on every message
@bot.event
async def on_message(message):

    # if the message author is the bot, stop (stops recursive loop of bot replying to itself)
    if message.author.bot:
        return

    # if the channel name is one of the platforms (flitter/xposure/bloggity)
    if message.channel.name.capitalize() in platforms:
        # add these variables
        platform = message.channel
        user = message.author
        postContent = message.content
        thread = message.thread

        try:
            await message.delete()
        except:
            pass
 
        # make post instance and call makepost function
        post = Post(platform, user, postContent, thread)
        try:
            print("sending '", postContent, "' from on_message")
            await post.makePost()
        except:
            await platform.send("That didn't work :(")
            raise Exception("making a post didn't work")




# a slash command that makes 3 channels with webhooks for the 'platforms'
@bot.slash_command(guild_ids=[guild_ID])
async def channelmaker(
    ctx,
    ):
    """Make channels and webhooks"""
    await ctx.delete()
    # if at least one platform already exists, says that the channels already exist and does not make them
    for platform in platforms:
        if discord.utils.get(ctx.guild.channels, name=platform.lower()):
            await ctx.respond("These channels already exist!", ephemeral=True)
            break
        # otherwise, makes all the channels and webhooks for them
        else:
            postChannel = await ctx.guild.create_text_channel(name=platform)
            await postChannel.create_webhook(name=platform)

# runs bot
bot.run(token)