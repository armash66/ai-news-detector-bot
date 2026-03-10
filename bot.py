import os
import requests
import discord
from discord.ext import commands
from dotenv import load_dotenv

# Load discord token and other vars
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
API_URL = "http://127.0.0.1:8000/api/v1/analyze"

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} - News Intelligence Bot")

@bot.command(name="verify")
async def verify(ctx, *, text: str):
    """Verify a news snippet or claim using the APIs."""
    if len(text) < 20:
        await ctx.send("Please provide at least 20 characters of text to analyze.")
        return

    # Reply with a loading indicator
    msg = await ctx.send("🔄 Analyzing claim with transformer models and checking evidence...")
    
    try:
        response = requests.post(API_URL, json={"text": text, "explain": False}, timeout=60)
        
        if response.status_code == 200:
            data = response.json()
            credibility = data.get("credibility", {})
            score = credibility.get("score", 0)
            verdict = credibility.get("verdict", "Unknown")
            
            # Formulate the response
            if score >= 75:
                color = discord.Color.green()
                icon = "🟢"
            elif score >= 50:
                color = discord.Color.orange()
                icon = "🟠"
            else:
                color = discord.Color.red()
                icon = "🔴"

            embed = discord.Embed(
                title=f"{icon} Analysis Report", 
                description=f"**Verdict:** {verdict}\n**Credibility Score:** {score:.1f}%",
                color=color
            )
            embed.add_field(name="Text Analyzed", value=f"\"{text[:200]}...\"", inline=False)
            
            # Reasons
            reasons = credibility.get("reasons", [])
            if reasons:
                reasons_text = "\n".join(f"• {r}" for r in reasons)
                embed.add_field(name="Analysis Breakdown", value=reasons_text, inline=False)
                
            await msg.edit(content=None, embed=embed)
        else:
            await msg.edit(content=f"❌ Failed to reach the analysis engine: {response.text}")
            
    except Exception as e:
        await msg.edit(content=f"❌ An error occurred connecting to the API: {str(e)}")


if __name__ == "__main__":
    if not TOKEN:
        print("ERROR: DISCORD_TOKEN is not set in .env")
        print("Please add DISCORD_TOKEN=your_token to your .env file and restart.")
    else:
        bot.run(TOKEN)
