import discord
from discord import app_commands
from discord.ext import commands
import random

from services.word_service import WordService


class DifficultyView(discord.ui.View):
    def __init__(self, cog):
        super().__init__(timeout=30)
        self.cog = cog

    async def start_game(self, interaction, difficulty: str):

        channel = interaction.user.voice.channel
        members = [m for m in channel.members if not m.bot]

        if len(members) < 3:
            await interaction.response.edit_message(
                content="❌ Потрібно мінімум 3 гравця",
                view=None
            )
            return

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

        # 🔒 отключаем кнопки
        for item in self.children:
            item.disabled = True

        await interaction.response.edit_message(
            content=f"🎮 Гра почалась! Складність: **{difficulty}**",
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

        view = DifficultyView(self)

        await interaction.response.send_message(
            "🎮 Обери складність:",
            view=view
        )