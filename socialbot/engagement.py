import discord
from discord.interactions import Interaction
from discord.ui import Button, View

from botvars import bot

class postEngagement(View):
    """A persistent view that makes engagement buttons under each Post."""
    def __init__(self):
        """The constructor, gains from the View object.
        
        Attributes: whoLiked is an int keeping track of who clicked the Like button
        
        Returns a View object.
        """
        super().__init__(timeout = None)
        self.whoLiked = []

    @discord.ui.button(label="share", style=discord.ButtonStyle.green, emoji="🔁", custom_id="share")
    async def share (self, button: Button, interaction: Interaction):
        """A quote retweet/share with comment.
        """

        # waits for the user who clicked the button to add a comment to the share (sent in the channel as a normal message)
        await interaction.response.defer()
        share = await bot.wait_for(event='message', check=lambda m: m.author == interaction.user)

        if share:
            print("trying to delete share of ", share.content)
            try:   
                await share.delete()
                print("deleted share")
            except:
                pass
            else:
                # a formatted embed for quote replies
                shareEmbed = f"{share.content}\n\n[**Replying to:**](https://discord.com/channels/{interaction.guild_id}/{interaction.channel_id}/{interaction.message.id})\n\n**{interaction.message.embeds[0].title}**\n{interaction.message.embeds[0].description}"
                    
                from posts import Post
                
                # makes a Post object that's an embedded reply
                sharePost = Post(interaction.channel, interaction.user, shareEmbed)
                await sharePost.makePost()


    @discord.ui.button(label="reply", style=discord.ButtonStyle.primary, emoji="🗨", custom_id="reply")
    async def reply (self, button: Button, interaction: Interaction):
        """Makes a thread where you can reply to the original post."""

        #waits for the user who clicked the button to add a comment to the share (sent in the channel as a normal message)
        await interaction.response.defer()
        reply = await bot.wait_for(event='message', check = lambda m: m.author == interaction.user)

        if reply:
            print("trying to delete reply of ", reply.content)
            try:   
                await reply.delete()
                print("deleted reply")
            except:
                pass
            else:
                from posts import Post

                # if the messsage does not have a created thread already, make a thread to post in
                if interaction.message.thread == None:
                    thread = await interaction.message.create_thread(name=f"replies")
                # otherwise set to existing created thread
                else:
                    thread = interaction.message.thread

                # makes a Post object but in a thread
                replyPost = Post(interaction.channel, interaction.user, reply.content, thread)
                await replyPost.makePost()


    @discord.ui.button(label="0", style=discord.ButtonStyle.grey, emoji="❤", custom_id="like")
    async def count(self, button: Button, interaction: Interaction):
        """A counter that increments if you haven't liked the post and decrements if you have"""

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