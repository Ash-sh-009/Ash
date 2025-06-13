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

# Configuration with YOUR TOKENS DIRECTLY SET
TOKEN = "7545390430:AAFtuCPJ55-N4Iip70l_GlljYPf7OVDJdDc"  # Your Telegram bot token
HF_TOKEN = "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"        # Your Hugging Face token
OWNER_USERNAME = "@ash_yv"  # Your Telegram username
OWNER_NAME = "Ash"           # Your display name
BOT_NAME = "ZERIL"           # Bot's display name
BOT_USERNAME = "@ZERIL_Bot"  # Your bot's username

# Hugging Face Inference API URLs
CHAT_API_URL = "https://api-inference.huggingface.co/models/facebook/blenderbot-400M-distill"
MOOD_API_URL = "https://api-inference.huggingface.co/models/finiteautomata/bertweet-base-sentiment-analysis"
TTS_API_URL = "https://api-inference.huggingface.co/models/ai4bharat/indic-tts-hi"
IMAGE_API_URL = "https://api-inference.huggingface.co/models/prompthero/openjourney"

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

def query_hf_api(api_url, payload):
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    response = requests.post(api_url, headers=headers, json=payload)
    return response.json()

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
    
    # Regular conversation - using HF Inference API
    # Remove bot mention
    cleaned_text = re.sub(rf'{BOT_USERNAME}|{BOT_NAME}', '', text, flags=re.IGNORECASE).strip()
    response = await generate_response(cleaned_text)
    mood = await detect_mood(cleaned_text)
    emoji = MOOD_EMOJIS.get(mood, "❤️")
    await send_delayed_response(update, f"{emoji} {response}")

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
                TTS_API_URL,
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
                IMAGE_API_URL,
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
    """Generate response using HF Inference API"""
    if not text:
        return "Kuch toh bolo yaar!"
    payload = {"inputs": text}
    try:
        response = query_hf_api(CHAT_API_URL, payload)
        # Extract the generated text from the response
        if isinstance(response, list) and len(response) > 0:
            return response[0]['generated_text']
        elif isinstance(response, dict) and 'generated_text' in response:
            return response['generated_text']
        else:
            return "Mujhe samajh nahi aaya, phir se try karo."
    except Exception as e:
        logger.error(f"Error in generate_response: {e}")
        return "Mera dimag kharaab ho gaya, baad mein try karo."

async def detect_mood(text: str) -> str:
    """Detect mood using HF Inference API"""
    if not text:
        return "NEU"
    payload = {"inputs": text}
    try:
        response = query_hf_api(MOOD_API_URL, payload)
        if isinstance(response, list) and len(response) > 0:
            return response[0]['label']
        return "NEU"
    except Exception as e:
        logger.error(f"Error in detect_mood: {e}")
        return "NEU"

if __name__ == "__main__":
    # Create bot application
    app = Application.builder().token(TOKEN).build()

    # Register handlers
    app.add_handler(CommandHandler("start", handle_start))
    app.add_handler(CommandHandler("help", handle_help))
    app.add_handler(CommandHandler("joke", handle_command))
    app.add_handler(CommandHandler("tts", handle_command))
    app.add_handler(CommandHandler("img", handle_command))
    app.add_handler(CommandHandler("flames", handle_command))
    app.add_handler(CommandHandler("setbio", handle_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Start polling
    logger.info("Starting ZERIL bot...")
    app.run_polling()
