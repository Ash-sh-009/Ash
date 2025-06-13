# main.py
import os
import re
import logging
import asyncio
import requests
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

# Configuration - USE YOUR ACTUAL TOENS HERE
TOKEN = os.getenv("TELEGRAM_TOKEN", "7545390430:AAFtuCPJ55-N4Iip70l_GlljYPf7OVDJdDc")
HF_TOKEN = os.getenv("HF_TOKEN", "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")
OWNER_USERNAME = "@ash_yv"  # Your Telegram username
OWNER_NAME = "Ash"           # Your display name
BOT_NAME = "ZERIL"           # Bot's display name
BOT_USERNAME = "@ZERIL_Bot"  # Your bot's username

# Initialize models
try:
    from transformers import pipeline
    chat_pipe = pipeline("text-generation", model="facebook/blenderbot-400M-distill", token=HF_TOKEN)
    mood_pipe = pipeline("text-classification", model="finiteautomata/bertweet-base-sentiment-analysis", token=HF_TOKEN)
except ImportError:
    # Fallback if transformers not available
    chat_pipe = None
    mood_pipe = None

# Mood emoji mapping
MOOD_EMOJIS = {
    "POS": "❤️",
    "NEG": "😢",
    "NEU": "😐",
    "anger": "😠",
    "joy": "❤️",
    "sadness": "😢"
}

# Logging setup
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def send_delayed_response(update: Update, response: str):
    """Send response with 1.2s delay"""
    await asyncio.sleep(1.2)
    await update.message.reply_text(response)

async def is_owner(user) -> bool:
    """Check if user is owner"""
    return user.username and user.username.lower() == OWNER_USERNAME[1:].lower()

async def handle_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    user = update.effective_user
    greeting = (
        f"❤️ Hey {user.first_name}! Main {BOT_NAME} hu, ek advanced Telegram bot!\n\n"
        f"Mere creator {OWNER_NAME} ({OWNER_USERNAME}) ne mujhe banaya hai. Aap kya kar sakte hain:\n"
        "/help - Sab commands dekhein\n"
        "/joke - Hasane ke liye joke suno\n"
        "/img - Images generate karein\n"
        "/tts - Text ko voice mein badle"
    )
    await send_delayed_response(update, greeting)

async def handle_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    help_text = (
        f"🛡️ MODERATION TOOLS ({BOT_NAME} ke saath group manage karein):\n"
        "/ban [user] [time] - User ko ban karein\n"
        "/mute [user] [time] - User ko mute karein\n"
        "/admins - Group admins ko list karein\n\n"
        f"🎉 ENTERTAINMENT ({BOT_NAME} ke saath maje karein):\n"
        "/joke - Hasane wala joke suno\n"
        "/speak_cow [text] - Gaay ki awaaz\n\n"
        f"⚙️ UTILITIES ({BOT_NAME} ki madad se kaam aasan banayein):\n"
        "/img [prompt] - Image generate karein\n"
        "/tts [text] - Text ko voice message banayein\n\n"
        f"❤️ SPECIAL FEATURES ({BOT_NAME} ki khaas batein):\n"
        "/flames [@user1] [@user2] - Compatibility check\n"
        "/setbio [text] - Apna bio set karein"
    )
    await send_delayed_response(update, help_text)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Main message handler"""
    message = update.message
    if not message or not message.text:
        return
        
    text = message.text
    user = update.effective_user
    
    # Check activation rules
    bot_mentioned = (
        BOT_USERNAME.lower() in text.lower() or
        BOT_NAME.lower() in text.lower()
    )
    
    if not (bot_mentioned or text.startswith('/')):
        return
    
    # Owner recognition system
    if any(word in text.lower() for word in ["owner", "creator", "maalik", "banane wala", "boss"]):
        if await is_owner(user):
            response = f"❤️ Aap hi toh mere malik ho {OWNER_NAME}! Aapne mujhe banaya 🎉"
        else:
            response = f"Mere creator {OWNER_NAME} ({OWNER_USERNAME}) toh ekdum jhakaas hai! Unhone mujhe itni mehnat se banaya 🙏"
        await send_delayed_response(update, response)
        return
    
    # Special praise for owner
    if await is_owner(user):
        if "good bot" in text.lower() or "achha bot" in text.lower():
            response = f"❤️ Shukriya {OWNER_NAME}! Aapki tareef sunkar bahut khushi hoti hai 🥰"
            await send_delayed_response(update, response)
            return
    
    # Respond to name mentions
    if BOT_NAME.lower() in text.lower() and not text.startswith('/'):
        responses = [
            f"❤️ Haan {user.first_name}? Mujhe bulaya?",
            f"😊 Ji {user.first_name}, main yahan hu!",
            f"❤️ Hanji {user.first_name}, bataiye kaam kya tha?"
        ]
        await send_delayed_response(update, responses[hash(user.id) % 3])
        return
    
    # Command handling
    if text.startswith('/'):
        await handle_command(update, text)
        return
    
    # Regular conversation
    if chat_pipe:
        response = await generate_response(text)
        if mood_pipe:
            mood = mood_pipe(text)[0]['label']
            emoji = MOOD_EMOJIS.get(mood, "❤️")
            await send_delayed_response(update, f"{emoji} {response}")
        else:
            await send_delayed_response(update, f"❤️ {response}")
    else:
        await send_delayed_response(update, "😢 Model load nahi ho paya. Phir se try karo!")

async def handle_command(update: Update, command: str):
    """Handle all commands"""
    try:
        if command.startswith('/ban'):
            parts = command.split()
            if len(parts) < 2:
                await send_delayed_response(update, "Usage: /ban @username [time]")
                return
            user = parts[1]
            time_val = parts[2] if len(parts) > 2 else "1h"
            await send_delayed_response(update, f"🔨 {user} ko banned! {time_val}")
        
        elif command.startswith('/joke'):
            jokes = [
                "Ek programmer restaurant gaya... Menu dekh ke bola: 'Hello World!' 😂",
                "WhatsApp ne Status feature banaya... Ab sab Facebook ko copy kar rahe hai! 🤪",
                "Ek din Python ne JavaScript se kaha: Tum toh har jagah chale gaye! JavaScript bola: Console.log('Kismat hai!') 🤣"
            ]
            await send_delayed_response(update, jokes[0])
        
        elif command.startswith('/tts'):
            text = command[4:].strip()
            if not text:
                await send_delayed_response(update, "Usage: /tts Your text here")
                return
            
            # Use Hugging Face TTS API
            headers = {"Authorization": f"Bearer {HF_TOKEN}"}
            payload = {"inputs": text}
            response = requests.post(
                "https://api-inference.huggingface.co/models/ai4bharat/indic-tts-hi",
                headers=headers,
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                with open("tts_output.mp3", "wb") as f:
                    f.write(response.content)
                await update.message.reply_voice(
                    voice=open("tts_output.mp3", "rb"),
                    caption=f"❤️ {BOT_NAME} ki awaaz mein: {text}"
                )
            else:
                await send_delayed_response(update, "😢 Sorry, voice generate nahi kar paya. Phir se try karo!")
        
        elif command.startswith('/img'):
            prompt = command[4:].strip()
            if not prompt:
                await send_delayed_response(update, "Usage: /img description of image")
                return
            
            # Add Indian style prefix
            full_prompt = f"Indian style, vibrant colors, {prompt}"
            
            # Check for NSFW
            if any(word in prompt.lower() for word in ["nude", "sexy", "adult", "nsfw"]):
                await send_delayed_response(update, "Arey bhai! Family group hai ye 😳")
                return
            
            # Generate image via Hugging Face API
            headers = {"Authorization": f"Bearer {HF_TOKEN}"}
            payload = {"inputs": full_prompt}
            response = requests.post(
                "https://api-inference.huggingface.co/models/prompthero/openjourney",
                headers=headers,
                json=payload,
                timeout=20
            )
            
            if response.status_code == 200:
                with open("generated_image.jpg", "wb") as f:
                    f.write(response.content)
                await update.message.reply_photo(
                    photo=open("generated_image.jpg", "rb"),
                    caption=f"🖼️ {BOT_NAME} ne banaya: {prompt}"
                )
            else:
                await send_delayed_response(update, "😢 Image generate nahi ho paya. Phir se try karo!")
        
        elif command.startswith('/flames'):
            await send_delayed_response(update, "95% compatibility! 💘 @user1 aur @user2 ko shaadi karni chahiye 😉")
        
        elif command.startswith('/setbio'):
            text = command[7:].strip()
            if not text:
                await send_delayed_response(update, "Usage: /setbio Your new bio")
                return
            await send_delayed_response(update, f"Tumhara naya bio set ho gaya: {text} ✏️")
        
        else:
            await send_delayed_response(update, "😕 Yeh command mujhe nahi samajh aaya. /help dekhein")

    except Exception as e:
        logger.error(f"Command error: {e}")
        await send_delayed_response(update, "😢 Oops! Kuch toh gadbad ho gaya. Phir se try karo")

async def generate_response(text: str) -> str:
    """Generate response using LLM"""
    # Remove bot mention if present
    cleaned_text = re.sub(rf'{BOT_USERNAME}|{BOT_NAME}', '', text, flags=re.IGNORECASE).strip()
    
    # Generate response using BlenderBot
    response = chat_pipe(
        cleaned_text,
        max_length=100,
        num_return_sequences=1
    )[0]['generated_text']
    
    # Convert to Hinglish-style response
    return response.replace("I'm", "Main").replace("you", "tum").replace("your", "tumhara")

if __name__ == "__main__":
    # Create bot application
    app = Application.builder().token(TOKEN).build()

    # Register handlers
    app.add_handler(CommandHandler("start", handle_start))
    app.add_handler(CommandHandler("help", handle_help))
    app.add_handler(CommandHandler("joke", handle_command))
    app.add_handler(CommandHandler("tts", handle_command))
    app.add_handler(CommandHandler("img", handle_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Start polling
    logger.info("Starting ZERIL bot...")
    app.run_polling()
