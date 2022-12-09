import discord
import sqlite3

from engagement import postEngagement

connection = sqlite3.connect("user_accounts.db")
cursor = connection.cursor()

class Post(object):
    """
        Creates a formatted Post based off a user's message in a platform channel.

        Attributes:
            platform (obj): the platform channel of the message
            user (obj): the user sending the message
            postContent (str): the content of the message
            thread (obj): the thread it's in (optional)
            platformName (str): just a nicer formatted version of the platform
    """
    def __init__(self, p, u, c=str, t=None):
        """The constructor to initialize the Post object.
        
        Args:
            p (obj): the platform channel of the message
            u (obj): the user sending the message
            c (str): the content of the message
            t (obj): the thread it's in (optional)
        """
        self.platform = p
        self.user = u
        self.postContent = c
        self.thread = t
        self.platformName = p.name.capitalize()

    async def makePost(self):
        """Sends a formatted Post from the bot."""
        # formats the post according to what channel/platform you're sending your message/'post' in
        postMade = self.platform_post()
        # adds the 'view': share/reply/like views/reaction buttons underneath from the postEngagement class
        view = postEngagement()
        # a list of webhooks in the channel
        webhooks = await self.platform.webhooks()
        #gets specific webhook that matches the platform name
        webhook = discord.utils.get(webhooks, name=self.platformName)

        #if the postContent of the post is an embed and there's a view (ie reaction buttons), send message
        if isinstance(postMade, discord.Embed):
           #if it's within a thread, send it in the thread
            if self.thread:
                await webhook.send(embed=postMade, thread=self.thread)
       #    otherwise send it in the channel
            else:
                await webhook.send(embed=postMade, view=view)
        # if the post is not an embed (which implies there's an 'error'), sends the error in a DM to the user.
        else:
            await self.user.send(postMade)

    def platform_post(self):
        """Formats the posts according to each channel 'platform'.
        
        Returns an embed object.
        """
        #calls the selectHandle function to get the handle
        handle = self.selectHandle()
        #depending on which platform it is, call different functions
        if self.platformName == "Flitter":
            return(self.flitterPost(handle))
        elif self.platformName == "Xposure":
            return(self.xposurePost(handle))
        elif self.platformName == "Bloggity":
            return(self.bloggityPost(handle))

    def selectHandle(self):
        """Gets the handle associated with the server user and specific platform from the sqlite3 database.

        If there's no handle in the queried table, just use the user's display name.
        
        Returns the handle value as a string.
        """
        try:
            handle = cursor.execute("SELECT handle FROM account WHERE (userid, serverid, platform) = (?, ?, ?)", (self.user.id, self.platform.guild.id, self.platformName)).fetchone()[0]
        except:
            handle = self.user.display_name

        return(handle)


    def flitterPost(self, handle):
        """Formats post for Flitter with a blue color, unless it's over 280 characters.

        Args: handle, a string.
        
        Returns an embed object.
        """
        # character limit for flitter. if post is more than 280 characters, resends the post in an error message DM telling you to try again.
        if len(self.postContent) >= 280:
            toolong = len(self.postContent) - 280
            err = f"Your Flitter post was {toolong} characters too long - Flit shorter!\n\n>>> {self.postContent}"
            return(err)
        else:
            embed=discord.Embed(description=self.postContent, title=f"@{handle}", colour=0x55acee)
            return(embed)

    def bloggityPost(self, handle):
        """Formats post for Bloggity with a yellow color.

        Args: handle, a string.
        
        Returns an embed object.
        """
        embed=discord.Embed(description=self.postContent, title=f"@{handle}",colour=0xffea00)
        return(embed)


    def xposurePost(self, handle):
        """Formats post for Xposure with a pink color.

        Args: handle, a string.
        
        Returns an embed object.
        """
        embed=discord.Embed(description=self.postContent, title=f"@{handle}",colour=0xE1306C)
        return(embed)