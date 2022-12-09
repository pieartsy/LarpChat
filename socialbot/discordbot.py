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

@bot.event
async def on_ready():
    bot.add_view(postEngagement()) # Registers a View for persistent listening
    print("View registered")


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
                await platform.send("Making a post didn't work :(")
                raise Exception("making a post didn't work")
        except:
            pass

# a slash command that makes 3 channels with webhooks for the 'platforms'
@bot.slash_command()
async def channelmaker(
    ctx,
    ):
    '''Make channels and webhooks'''
    await ctx.delete()
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

    platform = ctx.channel.name.capitalize()

    connection = sqlite3.connect("user_accounts.db")
    cursor = connection.cursor()
    if cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='account'") == None:
        cursor.execute("CREATE TABLE account (userid INTEGER, serverid INTEGER, platform STRING, handle STRING, propic STRING, PRIMARY KEY (userid, serverid, platform))")


    if platform in platforms:
        uniqueAccountVals = (ctx.user.id, ctx.guild_id, platform)
        
        f = cursor.execute("SELECT handle FROM account WHERE (userid, serverid, platform) = (?, ?, ?)", (uniqueAccountVals)).fetchone()

        if f == None:
            cursor.execute("INSERT INTO account (userid, serverid, platform, handle) VALUES (?, ?, ?, ?)", tuple([*uniqueAccountVals, handle]),)
        else:
            cursor.execute("UPDATE account SET handle = ? WHERE (userid, serverid, platform) = (?, ?, ?)", tuple([handle, *uniqueAccountVals]),)

        connection.commit()
        connection.close()

        await ctx.send_response(content=f"You set your {platform} handle to {handle}.",ephemeral=True)

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