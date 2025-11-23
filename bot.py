import discord
from discord.ext import commands
import requests
import io
import os
import time
from datetime import datetime

TOKEN = os.getenv("DISCORD_BOT_TOKEN")

BASE_IMAGE_URL = "https://raw.githubusercontent.com/gamebearonline-web/spl3_X_Bot/main/Thumbnail/Thumbnail.png"

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)


# ===============================
# Slash Command
# ===============================
@bot.tree.command(
    name="schedule",
    description="最新のスケジュール画像を送信します（日時入り）"
)
async def schedule(interaction: discord.Interaction):

    await interaction.response.defer()

    # --- JST 現在時刻 ---
    now = datetime.utcnow()
    now = now.replace(hour=now.hour + 9)  # UTC → JST
    time_str = now.strftime("🗓️ %Y年%-m月%-d日　🕛 %-H時更新")

    # --- GitHub RAW キャッシュ回避 ---
    image_url = f"{BASE_IMAGE_URL}?t={int(time.time())}"

    try:
        img_bytes = requests.get(image_url, timeout=10).content
        file = discord.File(io.BytesIO(img_bytes), filename="schedule.png")
    except Exception as e:
        await interaction.followup.send(f"画像取得に失敗しました：{e}")
        return

    # ★ メッセージ本文は「日時のみ」
    await interaction.followup.send(
        content=time_str,
        file=file
    )


# ===============================
# BOT 起動
# ===============================
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    await bot.tree.sync()
    print("Slash commands synced")


bot.run(TOKEN)
