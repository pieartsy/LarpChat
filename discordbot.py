import discord
from discord.interactions import Interaction
from discord.ui import Button, View

#to join paths
import os

#discord bot token
token = os.environ.get('TOKEN')

#token of my test server
guildID = 385833475954966529

# different 'platforms' - discord channels that mimic social media posting
platforms = ['Bloggity', 'Flitter', 'Xposure']

# intents let me access message content with discord's new privacy permissions
intents = discord.Intents.default()
intents.message_content = True

bot = discord.Bot(intents=intents)

#makes post buttons
class postEngagement(View):
    def __init__(self, platform, handle, makepost):
        super().__init__()
        self.platform = platform
        self.handle = handle
        self.makepost = makepost
        # who liked the post (by clicking the heart button)
        self.whoLiked = []
        # thread ID
        self.thread = None

    #A quote retweet/share with comment
    @discord.ui.button(label="share", style=discord.ButtonStyle.green, emoji="🔁")
    async def share (self, button: Button, interaction: Interaction):

        await interaction.response.defer()

    # checks to make sure the comment only occurs for the user who interacted with the button
        def check(m):
            if m.author == interaction.user:
                return m
        # waits for the user to add a comment to the share (sent in the channel as a normal message)
        comment = await bot.wait_for(event='message', check=check)

        if comment:
            # delete the original message sent in the channel <- this is throwing an exception error
            await comment.delete()
            # the formatting on this is janky but basically i want to make prev comments in a codeblock...
            shareComment = f"@{self.handle}\n\t{self.makepost}"
            shareComment = shareComment.replace('py', '').replace('`', '')
            shareBlock = f"{comment.content}```py\n{shareComment}```"
            # sends to the post function but in the qrt format
            await post(self.platform, interaction.user.display_name, shareBlock, None)

    # makes a thread where you can reply to the original post
    @discord.ui.button(label="reply", style=discord.ButtonStyle.primary, emoji="🗨")
    async def reply (self, button: Button, interaction: Interaction):

        # if a thread does not already exist, make a thread called "reply to [initial thread handle]"
        if self.thread == None:
            self.thread = await interaction.message.create_thread(name=f"reply to @{self.handle}")

        await interaction.response.defer()
        
        # checks to make sure the reply only occurs for the user who interacted with the button
        def check(m):
            if m.author == interaction.user:
                return m

        #waits for the user to add a comment to the share (sent in the channel as a normal message)
        reply = await bot.wait_for(event='message', check=check)

        if reply:
            #  delete the original message sent in the channel
            await reply.delete()
            # sends to the post function but posts in the thread instead of the main channel
            await post(self.platform, interaction.user.display_name, reply.content, self.thread)


    #increments if you haven't liked the post and decrements if you have
    @discord.ui.button(label="0", style=discord.ButtonStyle.grey, emoji="❤")
    async def count(self, button: Button, interaction: Interaction):
        # counter
        number = int(button.label) if button.label else 0
        # if the person interacting has not liked the post before (not in whoLiked), increment the counter
        if interaction.user not in self.whoLiked:
            self.whoLiked.append(interaction.user)
            button.label = str(number + 1)
        # if they have liked the post before, remove them from the whoLiked array and decrement the counter
        else:
            self.whoLiked.remove(interaction.user)
            button.label = str(number - 1)

        # Make sure to update the message with our updated counter
        await interaction.response.edit_message(view=self)

# formats the posts according to each channel 'platform'
def platform_post(platform=str, handle=str, makepost=str):
    # character limit for flitter. if post is more than 280 characters, resends the post in an ephemeral/error message that tells you to try again. i think this is currently broken due to ephemeral stuff being weird with the library update
    if platform == "Flitter":
        if len(makepost) >= 280:
            toolong = len(makepost) - 280
            err = f"Your Flitter post was {toolong} characters too long!\n\n_{makepost}_\n\nFlit shorter!"
            return(err)
        else:
        # formats an embed for the Flitter channel with a blue color
            embed=discord.Embed(description=makepost, title="@" + handle, colour=0x55acee)
            return(embed)
    # formats an embed for the Xposure channel with a pink color
    elif platform == "Xposure":
        embed=discord.Embed(description=makepost, title="@" + handle, colour=0xE1306C)
        return(embed)
    # formats an embed for the Bloggity channel with a yellow color
    elif platform == "Bloggity":
        embed=discord.Embed(description=makepost, title="@" + handle, colour=0xffea00)
        return(embed)


# a slash command that makes 3 channels with webhooks for the 'platforms'
@bot.slash_command(guild_ids=[guildID])
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

    

# makes a post for the bot
async def post(platform, handle, makepost, thread=None):

    # formats the post according to what channel/platform you're sending your message/'post' in
    content = platform_post(platform.name.capitalize(), handle, makepost)

    # adds the share/reply/like views/reaction buttons underneath
    view = postEngagement(platform, handle, makepost)
            
    webhooks = await platform.webhooks()
    #gets specific webhook that matches the platform name
    webhook = discord.utils.get(webhooks, name=platform.name.capitalize())
    #if the content of the post is an embed and there's a view (ie reaction buttons), send message
    if isinstance(content, discord.Embed):
        # if it's within a thread, send it in the thread
        if thread:
            await webhook.send(embed=content, thread=thread)
        # otherwise send it in the channel
        else:
            await webhook.send(embed=content, view=view)
    # if the post is not an embed (which implies there's an 'error'), return the error
    else:
        await platform.respond(content, ephemeral=True)

# idk how to use these
# async def on_command_error(self, ctx, error):
 #   if isinstance(error, discord.NotFound):
  #      await self.on_command_error(ctx, error.original)

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
        makepost = message.content
        handle = message.author.display_name
        await message.delete()
 
        # calls post function with given variables
        await post(platform, handle, makepost)


# runs bot
bot.run(token)
