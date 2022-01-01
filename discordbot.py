import discord
from discord.commands import Option
from discord.interactions import Interaction
from discord.ui import Button, View

#to join paths
import os

bot = discord.Bot()

#discord bot token
token = os.environ.get('TOKEN')

#token of my test server
guildID = 385833475954966529

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

    #A retweet/share with comment
    @discord.ui.button(label="share", style=discord.ButtonStyle.green, emoji="🔁")
    async def share (self, button: Button, interaction: Interaction):
        await interaction.response.defer()
      # await interaction.followup.send("What say you?", ephemeral=True, delete_after=3.0)

        comment = await bot.wait_for(event='message')
        await comment.delete()
        shareComment = f"> {self.makepost}\n\n ***@{self.handle}*** {comment.content}"
        await post(interaction, self.platform, "handle", shareComment, None)

    #makes a thread where you can reply to the original post
    @discord.ui.button(label="reply", style=discord.ButtonStyle.primary, emoji="🗨")
    async def reply (self, button: Button, interaction: Interaction):
        if self.thread == None:
            self.thread = await interaction.message.create_thread(name=f"reply to @{self.handle}")
        await interaction.response.defer()
#        await interaction.followup.send("What say you?:", ephemeral=True, delete_after=3.0)

        reply = await bot.wait_for(event='message')
        await reply.delete()
        await post(interaction, self.platform, "handle", reply.content, self.thread)


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
    elif platform == "XPosure":
        embed=discord.Embed(description=makepost, title="@" + handle, colour=0xE1306C)
    elif platform == "Bloggity":
        embed=discord.Embed(description=makepost, title="@" + handle, colour=0xffea00)
    return(embed)


# makes 3 channels with webhooks for the 'platforms'
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
            await postChannel.set_permissions(ctx.guild.default_role, send_messages_in_threads=False)
            await postChannel.create_webhook(name=platform)

# makes a post for the bot
@bot.slash_command(guild_ids=[385833475954966529])
async def post(
    ctx,
    platform: Option(str, choices=["Bloggity", "Flitter", "XPosure"]),
    handle: str,
    makepost: Option(str, label="post"),
    thread: Option(int, required=False, default=None)
    ):
    """Make a social media post"""
    #'responds' to slash command ping if the ctx is NOT an Interaction (ie is not from postEngagement buttons).
    if not isinstance(ctx, Interaction):
        await ctx.delete()
    content = platform_post(platform, handle, makepost)
    view = postEngagement(ctx, platform, handle, makepost)
    webhooks = await ctx.guild.webhooks()
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
        if not isinstance(ctx, Interaction):
            await ctx.respond(content, ephemeral=True)
        else:
            await ctx.followup.send(content, ephemeral=True)

bot.run(token)