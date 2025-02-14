
import discord
from discord.ext import commands, pages

help1 = discord.Embed(
            title="Help",
            description="""
                You can navigate through the help pages using the buttons below.    
                
                To get more help, give feedback or propose ideas:
                [Join the Support Server](https://discord.gg/4gZxCAK9mb)
                
                A list of all commands available:
                """,
            color=0x00ff00)
help1.add_field(name="Setup", value="`/create`")
help1.add_field(name="Admin", value="""`/role`
                                       `/config`""")


class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.pages = [
            [
                help1,
                discord.Embed(
                    title="Or help me :)",
                    description="""
                        [✌ Invite](https://discord.com/oauth2/authorize?client_id=928304609636794388&permissions=21048400&scope=bot%20applications.commands) - [⬆ Vote](https://top.gg/bot/928304609636794388/vote) - [☕ Buy me a coffee](https://ko-fi.com/shroominic)
                        """,
                    color=0x00ff00)],
            [
                discord.Embed(
                    title="Setup",
                    description="""
                        First, you need to create a new session using this command:
                        
                        `/create [name] [work_time] [break_time] [repetitions]`
                        
                        It will create a new category with text and voice channels on your server.
                        
                        (default: /create Pomodoro 25 5 4)
                        """,
                    color=0x00ff00)],
            [
                discord.Embed(
                    title="Session commands",
                    description="""
                        - **Start the session:**
                            `click on * 🚀 START *`
                            
                        If you have multiple sessions, you need to use the /session command inside #chat.
                        """,
                    color=0x00ff00)],
            [
                discord.Embed(
                    title="Admin commands",
                    description="""
                        - **General configuration:** 
                            `/config <'mute_admins'| > <true/false> (more coming)`
                            
                        - **Set your guild roles for command permissions:** 
                            `/role <'admin'|'moderator'> <@your_role>` 
                            
                        - **Delete/Reset all data Sensei Doro knows about this guild:** 
                            `/data <'delete'|'reset'>`
                    """,
                    color=0x00ff00)],
        ]

    @commands.slash_command()
    async def help(self, ctx):
        """
        Show the help page.
        """
        paginator = pages.Paginator(
            pages=self.pages, show_disabled=False)
        await paginator.respond(ctx.interaction, ephemeral=False)

