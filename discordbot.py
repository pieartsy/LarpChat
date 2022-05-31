import discord
from discord.interactions import Interaction
from discord.ui import Button, View

#to join paths
import os

#discord bot token
token = os.environ.get('TOKEN')

#token of my test server
guildID = 385833475954966529

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
    #waits for the user to add a comment to the share
        comment = await bot.wait_for(event='message', check=check)

        if comment:
            await comment.delete()
            shareComment = f"@{self.handle}\n\t{self.makepost}"
            shareComment = shareComment.replace('py', '').replace('`', '')
            shareBlock = f"{comment.content}```py\n{shareComment}```"
            await post(self.platform, interaction.user.display_name, interaction.message, shareBlock, None)

    #makes a thread where you can reply to the original post
    @discord.ui.button(label="reply", style=discord.ButtonStyle.primary, emoji="🗨")
    async def reply (self, button: Button, interaction: Interaction):

        if self.thread == None:
            self.thread = await interaction.message.create_thread(name=f"reply to @{self.handle}")
        await interaction.response.defer()
        
        # checks to make sure the reply only occurs for the user who interacted with the button
        def check(m):
            if m.author == interaction.user:
                return m

        reply = await bot.wait_for(event='message', check=check)
        if reply:
            await reply.delete()
            await post(self.platform, interaction.user.display_name, interaction.message, reply.content, self.thread)


    #increments if you haven't liked the post and decrements if you have
    @discord.ui.button(label="0", style=discord.ButtonStyle.grey, emoji="❤")
    async def count(self, button: Button, interaction: Interaction):
        number = int(button.label) if button.label else 0
        if interaction.user not in self.whoLiked:
            self.whoLiked.append(interaction.user)
            button.label = str(number + 1)
        else:
            self.whoLiked.remove(interaction.user)
            button.label = str(number - 1)

        # Make sure to update the message with our updated selves
        await interaction.response.edit_message(view=self)

# formats the posts according to each channel 'platform'
def platform_post(platform=str, handle=str, makepost=str):
    # character limit for flitter
    if platform == "Flitter":
        if len(makepost) >= 280:
            toolong = len(makepost) - 280
            error = f"Your Flitter post was {toolong} characters too long!\n\n_{makepost}_\n\nFlit shorter!"
            return(error)
        else:
            embed=discord.Embed(description=makepost, title="@" + handle, colour=0x55acee)
            return(embed)
    elif platform == "Xposure":
        embed=discord.Embed(description=makepost, title="@" + handle, colour=0xE1306C)
        return(embed)
    elif platform == "Bloggity":
        embed=discord.Embed(description=makepost, title="@" + handle, colour=0xffea00)
        return(embed)


# makes 3 channels with webhooks for the 'platforms'
@bot.slash_command(guild_ids=[guildID])
async def channelmaker(
    ctx,
    ):
    """Make channels and webhooks"""
    await ctx.delete()
    for platform in platforms:
        if discord.utils.get(ctx.guild.channels, name=platform.lower()):
            await ctx.respond("These channels already exist!", ephemeral=True)
            break
        else:
            postChannel = await ctx.guild.create_text_channel(name=platform)
            await postChannel.create_webhook(name=platform)

    

# makes a post for the bot
async def post(platform, handle, msg, makepost, thread=None):

    content = platform_post(platform, handle, makepost)

    view = postEngagement(platform, handle, makepost)
            
    webhooks = await msg.guild.webhooks()
    #gets specific webhook that matches the platform name
    webhook = discord.utils.get(webhooks, name=platform)
    #if the content of the post is an embed and there's a view (ie reaction buttons), send message
    if isinstance(content, discord.Embed):
        if thread:
            await webhook.send(embed=content, thread=thread)
        else:
            await webhook.send(embed=content, view=view)
        # if the post is not an embed (which implies there's an 'error'), return the error
    else:
        # if the ctx is NOT an Interaction (ie is not from postEngagement buttons)
        if not isinstance(content, Interaction):
            await msg.reply(content, ephemeral=True)
        # if it is from postEngagement buttons
        else:
            await msg.reply(content, ephemeral=True)


@bot.event
async def on_message(message):

    if message.author.bot:
        return

    if message.channel.name.capitalize() in platforms:
        platform = message.channel.name.capitalize()
        makepost = message.content
        handle = message.author.display_name
        await message.delete()
        await post(platform, handle, message, makepost)


bot.run(token)
