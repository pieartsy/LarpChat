import discord
import sqlite3

from engagement import postEngagement

connection = sqlite3.connect("user_accounts.db")
cursor = connection.cursor()

class Post():
    def __init__(self, p, u, c=str, t=None):
        self.platform = p
        self.user = u
        self.postContent = c
        self.thread = t
        self.platformName = p.name.capitalize()

    def selectHandle(self):
        try:
            handle = cursor.execute("SELECT handle FROM account WHERE (userid, serverid, platform) = (?, ?, ?)", (self.user.id, self.platform.guild.id, self.platformName)).fetchone()[0]
        except:
            handle = self.user.display_name
            
        return(handle)

    # sends a post for the bot
    async def makePost(self):
        # formats the post according to what channel/platform you're sending your message/'post' in
        postMade = self.platform_post()
        
        # adds the share/reply/like views/reaction buttons underneath

        view = postEngagement()
                
        webhooks = await self.platform.webhooks()
        #gets specific webhook that matches the platform name
        webhook = discord.utils.get(webhooks, name=self.platformName)
        #if the postContent of the post is an embed and there's a view (ie reaction buttons), send message
        if isinstance(postMade, discord.Embed):
           #if it's within a thread, send it in the thread
            if self.thread:
                await webhook.send(embed=postMade, thread=self.thread)
       #      otherwise send it in the channel
            else:
                await webhook.send(embed=postMade, view=view)
        # if the post is not an embed (which implies there's an 'error'), return the error
        else:
            await self.user.send(postMade)

    # formats the posts according to each channel 'platform'
    def platform_post(self):
        handle = self.selectHandle()
        if self.platformName == "Flitter":
            return(self.flitterPost(handle))
        elif self.platformName == "Xposure":
            return(self.xposurePost(handle))
        elif self.platformName == "Bloggity":
            return(self.bloggityPost(handle))


    def flitterPost(self, handle):
        # character limit for flitter. if post is more than 280 characters, resends the post in an error message DM telling you to try again.
        if len(self.postContent) >= 280:
            toolong = len(self.postContent) - 280
            err = f"Your Flitter post was {toolong} characters too long - Flit shorter!\n\n>>> {self.postContent}"
            return(err)
        else:
        # formats an embed for the Flitter channel with a blue color
            embed=discord.Embed(description=self.postContent, title=f"@{handle}", colour=0x55acee)
            return(embed)

    def bloggityPost(self, handle):
        # formats an embed for the Bloggity channel with a yellow color
        embed=discord.Embed(description=self.postContent, title=f"@{handle}",colour=0xffea00)
        return(embed)


    def xposurePost(self, handle):
        # formats an embed for the Xposure channel with a pink color
        embed=discord.Embed(description=self.postContent, title=f"@{handle}",colour=0xE1306C)
        return(embed)