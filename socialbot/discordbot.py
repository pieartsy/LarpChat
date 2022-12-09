import discord
import sqlite3
from discord import option, Attachment

#to join paths
import os

from posts import Post
from engagement import postEngagement
from botvars import bot

#discord bot token
token = os.environ.get('TOKEN')

# "social media" platforms
platforms = ["Flitter", "Bloggity", "Xposure"]

# Registers a View for persistent listening
@bot.event
async def on_ready():
    bot.add_view(postEngagement()) 
    print("View registered")

# on every message
@bot.event
async def on_message(message):
    """Listens to see if a message should be converted into a Post depending on what channel it's in.
    
    Raises:
        If message was deleted already, skips deleting it and converting into a Post again.
        Quits if sending a Post doesn't work.
    
    Returns:
        A Post object
    """
    # if the message author is the bot, stop (stops recursive loop of bot replying to itself)
    if message.author.bot:
        return

    # if the channel name is one of the platforms (flitter/xposure/bloggity)
    if message.channel.category.name == "platforms":
        user = message.author
        postContent = message.content

        #Checks to see if the message was sent in a thread...
        if str(message.channel.type) == 'public_thread':
            platform = message.channel.parent
            thread = message.channel

        # ...or a normal channel
        elif message.channel.name.capitalize() in platforms:
            platform = message.channel
            thread = message.thread

        # skips over deleting an original message and duplicate posting if an original message was already deleted. this is relevant for the share/reply views in postEngagement.
        try:
            await message.delete()
            # make post instance and call makepost function
            post = Post(platform, user, postContent, thread)
            # general try/except to just signal something's wrong with my code
            try:
                await post.makePost()
            except:
                raise Exception("making a post didn't work")
        except:
            pass

@bot.slash_command()
async def channelmaker(
    ctx,
    ):
    """Makes a category, channels, and webhooks for the 'platforms'."""

    if discord.utils.get(ctx.guild.categories, name="platforms"):
        await ctx.respond("This category already exists!", ephemeral=True)
        postCategory = discord.utils.get(ctx.guild.categories, name="platforms")
    else:
        postCategory = await ctx.guild.create_category(name="platforms") #overwrites = {ctx.guild.default_role: discord.PermissionOverwrite(view_channel=False)})
    
    for platform in platforms:
        if discord.utils.get(ctx.guild.channels, name=platform.lower()):
            await ctx.respond(f"The {platform} channel already exists!", ephemeral=True)
            continue
        # otherwise, makes all the channels and webhooks for them
        else:
            postChannel = await ctx.guild.create_text_channel(name=platform, category=postCategory)
            await postChannel.create_webhook(name=platform)

@bot.slash_command()
@option("handle", description="Enter the handle for your account on this platform")
@option("propic", description="Upload one image to add a profile picture", required=False)
async def account(
    ctx: discord.ApplicationContext,
    handle: str,
    ):
    """Reads and modifies the 'platform handles' that each server user has, stored in an sqlite3 database.
    
    Args:
        handle: A string
        propic: An attachment [not fully functional yet]
    """

    platform = ctx.channel.name.capitalize()

    # opens up a sqlite3 server and checks to see if account table was made already. if not, creates fields for it
    connection = sqlite3.connect("user_accounts.db")
    cursor = connection.cursor()
    if cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='account'") == None:
        cursor.execute("CREATE TABLE account (userid INTEGER, serverid INTEGER, platform STRING, handle STRING, propic STRING, PRIMARY KEY (userid, serverid, platform))")

    # autodetects if you're in a platform channel and sets your handle for that platform
    if platform in platforms:

        # composite primary key
        uniqueAccountVals = (ctx.user.id, ctx.guild_id, platform)

        # checks if handle already exists in platform
        findHandle = cursor.execute("SELECT handle FROM account WHERE platform = ?", (platform,)).fetchone()[0]

        # checks if user already has a handle associated with them on this platform
        findAccount = cursor.execute("SELECT handle FROM account WHERE (userid, serverid, platform) = (?, ?, ?)", (uniqueAccountVals)).fetchone()[0]

        # if the handle doesn't exist at all in the platform, add the handle for the user in the database
        if findHandle != handle and findAccount == None:
            cursor.execute("INSERT INTO account (userid, serverid, platform, handle) VALUES (?, ?, ?, ?)", tuple([*uniqueAccountVals, handle]),)
            await ctx.respond(content=f"You set your {platform} handle to {handle}.", ephemeral=True)
        # if the handle doesn't exist but the user had a different handle, update the user's handle
        elif findHandle != handle and findAccount:
            cursor.execute("UPDATE account SET handle = ? WHERE (userid, serverid, platform) = (?, ?, ?)", tuple([handle, *uniqueAccountVals]),)
            await ctx.respond(content=f"You set your {platform} handle to {handle}.", ephemeral=True)
        # if the handle exists and matches the user's handle, remind them that's their handle already
        elif findHandle == findAccount:
            await ctx.respond(content=f"You already set your handle to {handle}, silly!", ephemeral=True)
        # if the handle exists in the database but is not the user's handle, tell them it's taken
        elif findHandle == handle:
            await ctx.respond(content=f"Sorry! The handle {handle} is already taken on {platform}. Be more creative!", ephemeral=True)
        
        # commit changes and close server
        connection.commit()
        connection.close()

    # use a platform channel for the command
    else:
        await ctx.send_response(content=f"This command can only be used in platform channels.", ephemeral=True)
    #
    #if len(ctx.message.attachments) == 1 and ctx.attachments == propic:
     #   if propic.content_type == "image":
      #      await ctx.send(platform, handle, propic)
       # else:
        #    await ctx.send("Your profile picture needs to be, yknow...a picture.", ephemeral=True)
    #else:
     #   await ctx.send("One attachment at a time, please.", ephemeral=True)



# runs bot
bot.run(token)