import os
import threading
from flask import Flask
import discord
from discord.ext import commands
import requests
import io
import time
from datetime import datetime
import pytz


# ==============================
# Token 読み込み（ここが重要）
# ==============================
TOKEN = os.getenv("DISCORD_BOT_TOKEN")

if not TOKEN:
    print("❌ ERROR: DISCORD_BOT_TOKEN が設定されていません")
    raise SystemExit("環境変数 DISCORD_BOT_TOKEN が None のため終了します")
else:
    print(f"✅ DISCORD_BOT_TOKEN 読み込み成功（長さ: {len(TOKEN)}）")


BASE_IMAGE_URL = (
    "https://raw.githubusercontent.com/"
    "gamebearonline-web/spl3_X_Bot/main/Thumbnail/Thumbnail.png"
)


# ==============================
# Discord BOT の設定
# ==============================
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)


@bot.tree.command(
    name="schedule",
    description="最新のスケジュール画像を送信します（日時入り）"
)
async def schedule(interaction: discord.Interaction):
    await interaction.response.defer()

    # JST 時刻（正確版）
    jst = pytz.timezone("Asia/Tokyo")
    now = datetime.now(jst)
    time_str = now.strftime("🗓️ %Y年%-m月%-d日　🕛 %-H時時点")

    # キャッシュ防止
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
    print(f"🔵 Logged in as {bot.user}")

    try:
        await bot.tree.sync()
        print("🟢 Slash commands synced")
    except Exception as e:
        print(f"🔴 Slash command sync error: {e}")


# ==============================
# Flask（Railway Ping 用）
# ==============================
app = Flask(__name__)

@app.route("/")
def home():
    return "Discord Bot Running OK"


# ==============================
# Discord Bot 起動（別スレッド）
# ==============================
def run_discord_bot():
    bot.run(TOKEN)


if __name__ == "__main__":
    # Discord Bot を別スレッドで起動
    thread = threading.Thread(target=run_discord_bot)
    thread.daemon = True
    thread.start()

    # Railway が要求する PORT で Flask 起動
    port = int(os.environ.get("PORT", 5000))
    print(f"🌐 Flask listening on port {port}")
    app.run(host="0.0.0.0", port=port)
