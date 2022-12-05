import discord
from discord.ext import commands

bot = commands.Bot(command_prefix="!")

#to join paths
import os

#discord bot token
token = os.environ.get('TOKEN')

from posts import Post
from engagement import postEngagement
from botvars import bot

# "social media" platforms
platforms = ["Flitter", "Bloggity", "Xposure"]
# token of my test server
guild_ID = 385833475954966529

@bot.event
async def on_ready():
    bot.add_view(postEngagement()) # Registers a View for persistent listening

@bot.command()
@commands.is_owner()
async def view(ctx):
    await ctx.send_response("view", view=postEngagement())
    

# on every message
@bot.event
async def on_message(message):

    # if the message author is the bot, stop (stops recursive loop of bot replying to itself)
    if message.author.bot:
        return

    if message.channel.category.name == "platforms":
        user = message.author
        postContent = message.content

        if str(message.channel.type) == 'public_thread':
            platform = message.channel.parent
            thread = message.channel

    # if the channel name is one of the platforms (flitter/xposure/bloggity)
        elif message.channel.name.capitalize() in platforms:
             # add these variables
            platform = message.channel
            thread = message.thread

        try:
            await message.delete()
            # make post instance and call makepost function
            post = Post(platform, user, postContent, thread)
            try:
                await post.makePost()
            except:
                await platform.send("That didn't work :(")
                raise Exception("making a post didn't work")
        except:
            pass

        


# a slash command that makes 3 channels with webhooks for the 'platforms'
@bot.slash_command(guild_ids=[guild_ID])
async def channelmaker(
    ctx,
    ):
    '''Make channels and webhooks'''
    await ctx.delete()
    if discord.utils.get(ctx.guild.categories, name="platforms"):
        await ctx.respond("This category already exists!", ephemeral=True)
        postCategory = discord.utils.get(ctx.guild.categories, name="platforms")
    else:
        postCategory = await ctx.guild.create_category(name="platforms", overwrites = {ctx.guild.default_role: discord.PermissionOverwrite(view_channel=False)})
    
    for platform in platforms:
        if discord.utils.get(ctx.guild.channels, name=platform.lower()):
            await ctx.respond(f"The {platform} channel already exists!", ephemeral=True)
            continue
        # otherwise, makes all the channels and webhooks for them
        else:
            postChannel = await ctx.guild.create_text_channel(name=platform, category=postCategory)
            await postChannel.create_webhook(name=platform)

# runs bot
bot.run(token)