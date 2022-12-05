import discord

from engagement import postEngagement

class Post():
    def __init__(self, p, u, c=str, t=None):
        self.platform = p
        self.user = u
        self.postContent = c
        self.thread = t

        self.handle = u.display_name
        self.platformName = p.name.capitalize()

    # sends a post for the bot
    async def makePost(self):
        # formats the post according to what channel/platform you're sending your message/'post' in
        postMade = self.platform_post()
        
        # adds the share/reply/like views/reaction buttons underneath

        view = postEngagement(self.platform, self.handle, self.postContent)
                
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
        if self.platformName == "Flitter":
            return(self.flitterPost())
        elif self.platformName == "Xposure":
            return(self.xposurePost())
        elif self.platformName == "Bloggity":
            return(self.bloggityPost())


    def flitterPost(self):
        # character limit for flitter. if post is more than 280 characters, resends the post in an error message DM telling you to try again.
        if len(self.postContent) >= 280:
            toolong = len(self.postContent) - 280
            err = f"Your Flitter post was {toolong} characters too long - Flit shorter!\n\n>>> {self.postContent}"
            return(err)
        else:
        # formats an embed for the Flitter channel with a blue color
            embed=discord.Embed(description=self.postContent, title=f"@{self.handle}", colour=0x55acee)
            return(embed)

    def bloggityPost(self):
        # formats an embed for the Bloggity channel with a yellow color
        embed=discord.Embed(description=self.postContent, title=f"@{self.handle}",colour=0xffea00)
        return(embed)


    def xposurePost(self):
        # formats an embed for the Xposure channel with a pink color
        embed=discord.Embed(description=self.postContent, title=f"@{self.handle}",colour=0xE1306C)
        return(embed)