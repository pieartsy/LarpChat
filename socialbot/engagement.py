import discord
from discord.interactions import Interaction
from discord.ui import Button, View

from botvars import bot

#makes post buttons
class postEngagement(View):

    def __init__(self, p, h, c):
        print("attempting view")
        super().__init__()
        self.platform = p
        self.handle = h
        self.postContent = c
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
            # the formatting on this is janky but basically i want to make prev comments in a codeblock...
            shareComment = f"@{self.handle}\n\t{self.postContent}"
            shareComment = shareComment.replace('py', '').replace('`', '')
            shareBlock = f"{comment.content}```py\n{shareComment}```"
            # sends to the post function but in the qrt format
            from posts import Post
            commentPost = Post(self.platform, interaction.user.display_name, shareBlock)
            await commentPost.makePost()

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
            # sends to the post function but posts in the thread instead of the main channel
            from posts import Post
            replyPost = Post(self.platform, interaction.user.display_name, reply.content, self.thread)
            await replyPost.makePost()

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