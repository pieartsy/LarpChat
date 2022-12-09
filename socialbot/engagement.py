import discord
from discord.interactions import Interaction
from discord.ui import Button, View

from botvars import bot

#makes post buttons
class postEngagement(View):

    def __init__(self):
        super().__init__(timeout = None)
        self.whoLiked = []

    #A quote retweet/share with comment
    @discord.ui.button(label="share", style=discord.ButtonStyle.green, emoji="🔁", custom_id="share")
    async def share (self, button: Button, interaction: Interaction):
        
        await interaction.response.defer()

        # waits for the user who clicked the button to add a comment to the share (sent in the channel as a normal message)
        share = await bot.wait_for(event='message', check=lambda m: m.author == interaction.user)

        if share:
            await share.delete()
            # sends to the post function but in the qrt format
            try:
                shareEmbed = f"{share.content}\n\n[**Replying to:**](https://discord.com/channels/{interaction.guild_id}/{interaction.channel_id}/{interaction.message.id})\n\n**{interaction.message.embeds[0].title}**\n{interaction.message.embeds[0].description}"
            except:
                shareEmbed=share.content
                raise Exception("making embed string didn't work")
                
            from posts import Post

            sharePost = Post(interaction.channel, interaction.user, shareEmbed)
            await sharePost.makePost()

    # makes a thread where you can reply to the original post
    @discord.ui.button(label="reply", style=discord.ButtonStyle.primary, emoji="🗨", custom_id="reply")
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

            replyPost = Post(interaction.channel, interaction.user, reply.content, thread)
            await replyPost.makePost()


    #increments if you haven't liked the post and decrements if you have
    @discord.ui.button(label="0", style=discord.ButtonStyle.grey, emoji="❤", custom_id="like")
    async def count(self, button: Button, interaction: Interaction):

        # who liked the post (by clicking the heart button)

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