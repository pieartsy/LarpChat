import discord
from discord.interactions import Interaction
from discord.ui import Button, View

from botvars import bot

#makes post buttons
class postEngagement(View):

    def __init__(self, p, h, c):
        print("attempting view for", c)
        super().__init__()
        self.platform = p
        self.handle = h
        self.postContent = c
        
        # who liked the post (by clicking the heart button)
        self.whoLiked = []


    #A quote retweet/share with comment
    @discord.ui.button(label="share", style=discord.ButtonStyle.green, emoji="🔁")
    async def share (self, button: Button, interaction: Interaction):

        await interaction.response.defer()

        # waits for the user who clicked the button to add a comment to the share (sent in the channel as a normal message)
        comment = await bot.wait_for(event='message', check=lambda m: m.author == interaction.user)

        if comment:
            print("attempting to delete awaited comment")
            await comment.delete()
            # the formatting on this is janky but basically i want to make prev comments in a codeblock...
            shareComment = f"@{self.handle}\n\t{self.postContent}"
            shareComment = shareComment.replace('py', '').replace('`', '')
            shareBlock = f"{comment.content}```py\n{shareComment}```"
            # sends to the post function but in the qrt format
            from posts import Post
            commentPost = Post(self.platform, interaction.user, shareBlock)

            print("attempting to share ", self.postContent)
            await commentPost.makePost()

    # makes a thread where you can reply to the original post
    @discord.ui.button(label="reply", style=discord.ButtonStyle.primary, emoji="🗨")
    async def reply (self, button: Button, interaction: Interaction):

        await interaction.response.defer()

        #waits for the user who clicked the button to add a comment to the share (sent in the channel as a normal message)
        reply = await bot.wait_for(event='message', check = lambda m: m.author == interaction.user)

        if reply:
            # sends to the post function but posts in the thread instead of the main channel
            await reply.delete()
            from posts import Post

            if interaction.message.thread == None:
                thread = await interaction.message.create_thread(name=f"replies")
            else:
                thread = interaction.message.thread

            replyPost = Post(self.platform, interaction.user, reply.content, thread)
            print("attempting to make reply to ", self.postContent, "with ", reply.content) 
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