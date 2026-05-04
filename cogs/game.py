import discord
from discord import app_commands
from discord.ext import commands
import random

from services.word_service import WordService


class DifficultyView(discord.ui.View):
    def __init__(self, cog):
        super().__init__(timeout=30)
        self.cog = cog
        self.selected_members = []

    async def start_game(self, interaction, difficulty: str):

        await interaction.response.defer()

        members = self.selected_members  # 👈 теперь используем выбранных

        impostor = random.choice(members)
        word = self.cog.word_service.get_random_word(difficulty)

        for m in members:
            try:
                if m == impostor:
                    await m.send("🤫 ТИ ІМПОСТЕР!")
                else:
                    await m.send(f"🎨 Ти малюєш слово: **{word}**")
            except:
                pass

        for item in self.children:
            item.disabled = True

        await interaction.edit_original_response(
            content=f"🎮 Game Started! Players: {len(members)}",
            view=self
        )

    @discord.ui.button(label="Easy", style=discord.ButtonStyle.success)
    async def easy(self, interaction, button):
        await self.start_game(interaction, "easy")

    @discord.ui.button(label="Medium", style=discord.ButtonStyle.primary)
    async def medium(self, interaction, button):
        await self.start_game(interaction, "medium")

    @discord.ui.button(label="Hard", style=discord.ButtonStyle.danger)
    async def hard(self, interaction, button):
        await self.start_game(interaction, "hard")


class PlayerSelect(discord.ui.Select):
    def __init__(self, members):
        options = [
            discord.SelectOption(label=m.display_name, value=str(m.id))
            for m in members
        ]

        super().__init__(
            placeholder="Вибери гравців (залиш незмінним якщо гратимуть всі)...",
            min_values=0,
            max_values=len(options),
            options=options
        )

    async def callback(self, interaction: discord.Interaction):
        self.view.selected_players = self.values
        await interaction.response.defer()


class PlayerSelectView(discord.ui.View):
    def __init__(self, cog, members):
        super().__init__(timeout=60)
        self.cog = cog
        self.members = members
        self.selected_players = None  # 👈 None = все выбраны

        self.add_item(PlayerSelect(members))

    @discord.ui.button(label="Продовжити", style=discord.ButtonStyle.success)
    async def continue_btn(self, interaction: discord.Interaction, button: discord.ui.Button):

        # 👇 если пользователь НЕ выбирал — берём всех
        if not self.selected_players:
            selected_members = self.members
        else:
            selected_members = [
                m for m in self.members if str(m.id) in self.selected_players
            ]

        if len(selected_members) < 3:
            await interaction.response.send_message(
                "❌ Потрібно мінімум 3 гравця",
                ephemeral=True
            )
            return

        view = DifficultyView(self.cog)
        view.selected_members = selected_members

        await interaction.response.edit_message(
            content=f"🎮 Обери складність (гравців: {len(selected_members)}):",
            view=view
        )


class Game(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.word_service = WordService()

    @app_commands.command(name="start_game", description="Start Drawing Imposter game")
    async def start_game(self, interaction: discord.Interaction):

        if not interaction.user.voice:
            await interaction.response.send_message(
                "Ти повинен бути в голосовому каналі.",
                ephemeral=True
            )
            return

        channel = interaction.user.voice.channel
        members = [m for m in channel.members if not m.bot]

        view = PlayerSelectView(self, members)

        await interaction.response.send_message(
            "👥 Обери гравців:",
            view=view
        )