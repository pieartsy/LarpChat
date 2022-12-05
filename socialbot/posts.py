import discord

from engagement import postEngagement

class Post():
    def __init__(self, p, h=str, c=str, t=None):
        self.platform = p
        self.handle = h
        self.postContent = c
        self.thread = t
        self.platformName = p.name.capitalize()

    # sends a post for the bot
    async def makePost(self):
        print("attempting to post '", self.postContent, "'")
        # formats the post according to what channel/platform you're sending your message/'post' in
        postMade = self.platform_post()
        
        # adds the share/reply/like views/reaction buttons underneath
        try:
            print("attempting to call view for '", self.postContent, "'")
            view = postEngagement(self.platform, self.handle, self.postContent)
        except:
            raise Exception("trying to make a view object didn't work")
                
        webhooks = await self.platform.webhooks()
        #gets specific webhook that matches the platform name
        webhook = discord.utils.get(webhooks, name=self.platformName)
        #if the postContent of the post is an embed and there's a view (ie reaction buttons), send message
        if isinstance(postMade, discord.Embed):
           #if it's within a thread, send it in the thread
            if self.thread:
                print("sending '", self.postContent, "' in thread\n-------")
                await webhook.send(embed=postMade, thread=self.thread)
       #      otherwise send it in the channel
            else:
                print("sending '", self.postContent, "' in channel\n-------")
                await webhook.send(embed=postMade, view=view)
        
        # if the post is not an embed (which implies there's an 'error'), return the error
        else:
            await webhook.send(postMade, ephemeral=True)

    # formats the posts according to each channel 'platform'
    def platform_post(self):
        if self.platformName == "Flitter":
            embed = self.flitterPost()
        elif self.platformName == "Xposure":
            embed = self.xposurePost()
        elif self.platformName == "Bloggity":
            embed = self.bloggityPost()
        return embed

    def flitterPost(self):
        # character limit for flitter. if post is more than 280 characters, resends the post in an ephemeral/error message that tells you to try again. i think this is currently broken due to ephemeral stuff being weird with the library update
        if len(self.postContent) >= 280:
            toolong = len(self.postContent) - 280
            err = f"Your Flitter post was {toolong} characters too long!\n\n_{self.postContent}_\n\nFlit shorter!"
            return(err)
        else:
        # formats an embed for the Flitter channel with a blue color
            embed=discord.Embed(description=self.postContent, title="@" + self.handle, colour=0x55acee)
            return(embed)

    def bloggityPost(self):
        # formats an embed for the Bloggity channel with a yellow color
        embed=discord.Embed(description=self.postContent, title="@" + self.handle, colour=0xffea00)
        return(embed)


    def xposurePost(self):
        # formats an embed for the Xposure channel with a pink color
        embed=discord.Embed(description=self.postContent, title="@" + self.handle, colour=0xE1306C)
        return(embed)



    # idk how to use these
    # async def on_command_error(self, ctx, error):
    #   if isinstance(error, discord.NotFound):
    #      await self.on_command_error(ctx, error.original)
