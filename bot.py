import os
import threading
from flask import Flask
import discord
from discord.ext import commands
import requests
import io
import time
from datetime import datetime

TOKEN = os.getenv("DISCORD_BOT_TOKEN")
BASE_IMAGE_URL = "https://raw.githubusercontent.com/gamebearonline-web/spl3_X_Bot/main/Thumbnail/Thumbnail.png"

# ==============================
# Discord BOT の設定
# ==============================
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)


@bot.tree.command(
    name="schedule",
    description="最新のスケジュール画像を送信します（日時入り）"
)
async def schedule(interaction: discord.Interaction):
    await interaction.response.defer()

    # JST 現在時刻
    now = datetime.utcnow().replace(hour=datetime.utcnow().hour + 9)
    time_str = now.strftime("🗓️ %Y年%-m月%-d日　🕛 %-H時更新")

    image_url = f"{BASE_IMAGE_URL}?t={int(time.time())}"

    try:
        img_bytes = requests.get(image_url, timeout=10).content
        file = discord.File(io.BytesIO(img_bytes), filename="schedule.png")
    except Exception as e:
        await interaction.followup.send(f"画像取得に失敗：{e}")
        return

    await interaction.followup.send(content=time_str, file=file)


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    await bot.tree.sync()
    print("Slash commands synced")


# ==============================
# Flask（Render のヘルスチェック用）
# ==============================
app = Flask(__name__)

@app.route("/")
def home():
    return "Running OK"


# ==============================
# Discord BOT を別スレッドで起動
# ==============================
def run_discord_bot():
    bot.run(TOKEN)


if __name__ == "__main__":
    # Discord bot スレッドを起動
    thread = threading.Thread(target=run_discord_bot)
    thread.start()

    # Flask を Render が必要とする PORT で起動
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
