import discord
from discord import app_commands
from discord.ext import commands


class OnboardingView(discord.ui.View):
    def __init__(self) -> None:
        super().__init__(timeout=None)
        self.current_page = 0
        self.has_seen_last_page = False
        self.pages = [
            {
                "title": "Welcome to Sensei Doro! 🍅",
                "description": (
                    "Your personal Pomodoro timer for productive Discord study sessions!\n\n"
                    "Sensei Doro automatically manages your study group using the Pomodoro Technique. "
                    "Create focused study environments, stay accountable with your peers, "
                    "and boost your productivity!\n\n"
                    "**What is the Pomodoro Technique?**\n"
                    "• Work in focused 25-minute intervals\n"
                    "• Take short 5-minute breaks between sessions\n"
                    "• After 4 sessions, take a longer break\n"
                    "• Stay focused and avoid burnout"
                ),
                "color": discord.Color.brand_red(),
                "fields": [
                    {
                        "name": "🎯 Perfect for",
                        "value": (
                            "• Study groups\n• Learning communities\n• Work teams\n• Anyone wanting to study together\n"
                        ),
                        "inline": True,
                    },
                    {
                        "name": "🌟 Benefits",
                        "value": (
                            "• Distraction-free environment\n"
                            "• Group accountability\n"
                            "• Automatic time management\n"
                            "• Enhanced group productivity"
                        ),
                        "inline": True,
                    },
                ],
            },
            {
                "title": "How It Works 📚",
                "description": (
                    "Getting started with Sensei Doro is simple:\n\n"
                    "**1. Create a Study Environment**\n"
                    "Use `/create` to set up your Pomodoro environment\n\n"
                    "**2. Join a Voice Channel**\n"
                    "Connect to any voice channel in your server\n\n"
                    "**3. Start Your Session**\n"
                    "Click the 🚀 START button in the dashboard\n\n"
                    "**4. Study Together**\n"
                    "Members will be automatically muted during work time to create a distraction-free environment"
                ),
                "color": discord.Color.blue(),
                "fields": [
                    {
                        "name": "⚡ Setup Command",
                        "value": (
                            "• `/create [name] [work_time] [break_time] [repetitions]`\n"
                            'Example: `/create "Study Room" 25 5 4`'
                        ),
                        "inline": False,
                    },
                    {
                        "name": "🎮 Session Controls",
                        "value": "• 🚀 START - Begin session\n• ⏹️ STOP - End session\n• All controls in 📋 dashboard",
                        "inline": True,
                    },
                    {
                        "name": "⚙️ Customization",
                        "value": (
                            "• Work duration (default: 25min)\n"
                            "• Break duration (default: 5min)\n"
                            "• Number of repetitions (default: 4)"
                        ),
                        "inline": True,
                    },
                ],
            },
            {
                "title": "Features & Management ✨",
                "description": (
                    "Sensei Doro comes with powerful features to enhance your group study sessions:\n\n"
                    "**Core Features**\n"
                    "• Automatic member muting during work time\n"
                    "• Group-based Pomodoro sessions\n"
                    "• Customizable work/break intervals\n"
                    "• Easy-to-use dashboard controls\n\n"
                    "**Admin Features**\n"
                    "• Custom role permissions\n"
                    "• Configurable mute settings\n"
                    "• Session management controls\n"
                    "• Data management options"
                ),
                "color": discord.Color.green(),
                "fields": [
                    {
                        "name": "🛠️ Admin Commands",
                        "value": (
                            "• `/config` - Bot settings\n• `/role` - Permission control\n• `/data` - Manage bot data"
                        ),
                        "inline": True,
                    },
                    {
                        "name": "📊 Environment",
                        "value": (
                            "• Dedicated dashboard channel\n"
                            "• Visual session progress\n"
                            "• Easy-to-use buttons\n"
                            "• Group status tracking"
                        ),
                        "inline": True,
                    },
                ],
            },
            {
                "title": "Help Keep Sensei Doro Running 🌟",
                "description": (
                    "To maintain and improve Sensei Doro, we rely on community support. "
                    "Your contribution helps cover server costs, development, "
                    "and ensures the bot stays available 24/7.\n\n"
                    "Choose the option that works best for you:"
                ),
                "color": discord.Color.gold(),
                "fields": [
                    {
                        "name": "🆓 Free Tier",
                        "value": ("**Price:** Free\n• All features\n• Requires voting every 12 hours\n"),
                        "inline": True,
                    },
                    {
                        "name": "👤 User Tier",
                        "value": (
                            "**Price:** $2.99/month\n• All features\n• No need for voting\n• Create multiple sessions\n"
                        ),
                        "inline": True,
                    },
                    {
                        "name": "🏢 Server Tier",
                        "value": (
                            "**Price:** $9.99/month\n"
                            "• No need for voting\n"
                            "• For everyone in the server\n"
                            "• Create unlimited sessions\n"
                            "• Role based access control\n"
                        ),
                        "inline": True,
                    },
                    {
                        "name": "💝 Why Support Us?",
                        "value": (
                            "Your support helps us cover:\n"
                            "• Server costs\n"
                            "• New features\n"
                            "• 24/7 bot availability\n"
                            "Together we can make Sensei Doro even better!"
                        ),
                        "inline": False,
                    },
                ],
            },
        ]

    @discord.ui.button(
        label="⬅️",
        style=discord.ButtonStyle.gray,
        disabled=True,
        custom_id="prev",
    )
    async def previous_button(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        self.current_page = max(0, self.current_page - 1)
        await self.update_page(interaction)

    @discord.ui.button(label="➡️", style=discord.ButtonStyle.primary, custom_id="next")
    async def next_button(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        self.current_page = min(len(self.pages) - 1, self.current_page + 1)
        if self.current_page == len(self.pages) - 1:
            self.has_seen_last_page = True
        await self.update_page(interaction)

    @discord.ui.button(
        label="Continue",
        style=discord.ButtonStyle.success,
        custom_id="continue",
        row=1,
        disabled=True,
    )
    async def continue_button(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        await interaction.response.send_message(
            "Great! You're all set to start using Sensei Doro. Here are some quick tips:\n\n"
            "1. Join the lobby channel and click the 🚀 START button to begin a session\n"
            "2. Invite your friends to join your study session\n"
            "3. Use `/help` to see all available commands\n\n"
            "Happy studying! 🎯✨",
            ephemeral=True,
        )

    async def update_page(self, interaction: discord.Interaction) -> None:
        page = self.pages[self.current_page]

        # Update button states
        self.previous_button.disabled = self.current_page == 0
        self.next_button.disabled = self.current_page == len(self.pages) - 1

        # Only enable Continue button if user has seen all pages
        self.continue_button.disabled = not self.has_seen_last_page
        self.continue_button.style = (
            discord.ButtonStyle.success if not self.continue_button.disabled else discord.ButtonStyle.gray
        )

        embed = discord.Embed(title=page["title"], description=page["description"], color=page["color"])

        # Add fields if they exist
        if "fields" in page:
            for field in page["fields"]:
                embed.add_field(
                    name=field["name"],
                    value=field["value"],
                    inline=field.get("inline", True),
                )

        embed.set_footer(text=f"Page {self.current_page + 1}/{len(self.pages)}")

        await interaction.response.edit_message(embed=embed, view=self)


class Onboarding(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild) -> None:
        """Send welcome message when bot joins a new server"""
        # Try to find the system channel or first available text channel
        target_channel = guild.system_channel or next(
            (channel for channel in guild.text_channels if channel.permissions_for(guild.me).send_messages),
            None,
        )

        if target_channel:
            view = OnboardingView()
            embed = discord.Embed(
                title=view.pages[0]["title"],
                description=view.pages[0]["description"],
                color=view.pages[0]["color"],
            )

            # Add fields if they exist for the first page
            if "fields" in view.pages[0]:
                for field in view.pages[0]["fields"]:
                    embed.add_field(
                        name=field["name"],
                        value=field["value"],
                        inline=field.get("inline", True),
                    )

            embed.set_footer(text="Page 1/4")
            await target_channel.send(embed=embed, view=view)

    @app_commands.command(name="welcome")
    @app_commands.checks.has_permissions(administrator=True)
    async def show_welcome(self, interaction: discord.Interaction) -> None:
        """Show the welcome message and setup guide"""
        view = OnboardingView()
        embed = discord.Embed(
            title=view.pages[0]["title"],
            description=view.pages[0]["description"],
            color=view.pages[0]["color"],
        )

        # Add fields if they exist for the first page
        if "fields" in view.pages[0]:
            for field in view.pages[0]["fields"]:
                embed.add_field(
                    name=field["name"],
                    value=field["value"],
                    inline=field.get("inline", True),
                )

        embed.set_footer(text="Page 1/4")
        await interaction.response.send_message(embed=embed, view=view)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Onboarding(bot))
