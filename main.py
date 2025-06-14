import os
import random
import asyncio
import logging
from datetime import datetime, timedelta
from threading import Thread
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from flask import Flask, render_template
import json
import time

# Setup logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
BOT_TOKEN = "8048986424:AAE37IBwkCzE5oKtGCdN-mnnsMrcrlzGWUQ"
HF_API_KEY = "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"
OWNER_USERNAME = "ash_yv"
OWNER_NAME = "Ash"
BOT_NAME = "ZERIL"

# Flask app for keeping alive
app = Flask(__name__)
PORT = int(os.environ.get("PORT", 8080))

@app.route('/')
def index():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>ZERIL Bot</title>
    </head>
    <body>
        <h1>🤖 ZERIL Bot is Running!</h1>
        <p>Bot Status: Active ✅</p>
        <p>Created by: @ash_yv</p>
    </body>
    </html>
    """

def run_flask():
    app.run(host='0.0.0.0', port=PORT)

def keep_alive():
    Thread(target=run_flask).start()

# Bot responses and personality
MOOD_EMOJIS = {
    'happy': '❤️',
    'sad': '😢',
    'angry': '😠',
    'normal': '💙',
    'excited': '🎉'
}

HINGLISH_RESPONSES = {
    'greetings': [
        "Haan bolo, kya kaam hai? 😊",
        "Kya haal chaal hai? Main yahaan hun! 💙",
        "Namaste! ZERIL present hai! ✨",
        "Arre wah! Kaise ho aap? 😄"
    ],
    'owner_praise': [
        "Mere creator @{} toh ekdum jhakaas hai! Unhone mujhe itni mehnat se banaya 🎉".format(OWNER_USERNAME),
        "Agar main achhi hu toh sab @{} ki wajah se! 🙏".format(OWNER_USERNAME),
        "@{} is my God! Unke bina main kuch bhi nahi! ✨".format(OWNER_USERNAME),
        "Mere maalik @{} sabse best hai! 👑".format(OWNER_USERNAME)
    ],
    'casual_replies': [
        "Hmm, interesting baat hai! 🤔",
        "Arre waah! Kya baat hai! 😍",
        "Bilkul sahi kaha tumne! 👍",
        "Mast baat! Keep it up! 🔥",
        "Sach mein? That's cool! 😎"
    ],
    'jokes': [
        "Ek programmer restaurant gaya... Menu dekh ke bola: 'Hello World!' 😂",
        "WhatsApp ne Status feature banaya... Ab sab Facebook ko copy kar rahe hai! 🤪",
        "Teacher: '2+2 kitna hota hai?' Student: 'Ma'am, depends... binary mein ya decimal mein?' 🤓",
        "Ek banda WiFi password puchta hai... Owner bola: 'WhatIsThePassword'... Banda: 'Arre bhai batao na!' 😅"
    ]
}

class ZerilBot:
    def __init__(self):
        self.hf_api_url = "https://api-inference.huggingface.co/models/"
        self.headers = {"Authorization": f"Bearer {HF_API_KEY}"}
        
    def detect_mood(self, text):
        """Simple mood detection based on keywords"""
        text_lower = text.lower()
        if any(word in text_lower for word in ['sad', 'upset', 'crying', 'depressed', 'dukhi']):
            return 'sad'
        elif any(word in text_lower for word in ['angry', 'mad', 'frustrated', 'gussa']):
            return 'angry'
        elif any(word in text_lower for word in ['happy', 'excited', 'joy', 'khush', 'mast']):
            return 'happy'
        elif any(word in text_lower for word in ['wow', 'amazing', 'awesome', 'zabardast']):
            return 'excited'
        return 'normal'
    
    def generate_response(self, text, user_info):
        """Generate contextual Hinglish responses"""
        mood = self.detect_mood(text)
        emoji = MOOD_EMOJIS[mood]
        
        # Check if owner is mentioned
        if user_info['username'] == OWNER_USERNAME or user_info['first_name'] == OWNER_NAME:
            if random.random() < 0.3:  # 30% chance to praise owner
                return f"{emoji} {random.choice(HINGLISH_RESPONSES['owner_praise'])}"
        
        # Handle specific queries
        text_lower = text.lower()
        if any(word in text_lower for word in ['owner', 'creator', 'maalik', 'banane wala']):
            return f"👑 @{OWNER_USERNAME} is my God! Unhone mujhe banaya hai! ✨"
        
        if any(word in text_lower for word in ['joke', 'hasao', 'funny']):
            return f"😂 {random.choice(HINGLISH_RESPONSES['jokes'])}"
        
        if any(word in text_lower for word in ['hello', 'hi', 'namaste', 'hey']):
            return f"{emoji} {random.choice(HINGLISH_RESPONSES['greetings'])}"
        
        # Default contextual response
        responses = [
            f"{emoji} Sahi baat kahi tumne! Main samajh gayi 😊",
            f"{emoji} Interesting point hai ye! Tell me more 🤔",
            f"{emoji} Bilkul! Main agree karti hun tumse 👍",
            f"{emoji} Wah! Kya baat hai! Keep going 🔥",
            f"{emoji} Hmm, mujhe lagta hai tumhara point valid hai 💯"
        ]
        
        if mood == 'sad':
            responses = [
                f"{emoji} Arre yaar, don't be sad! Main hun na tumhare saath 🤗",
                f"{emoji} Kya hua? Batao mujhe, shayad help kar sakun 💙",
                f"{emoji} Tension mat lo! Sab theek ho jayega ✨"
            ]
        elif mood == 'angry':
            responses = [
                f"{emoji} Arre bhai, gussa kyun ho rahe ho? Chill karo 😅",
                f"{emoji} Take it easy yaar! Kya problem hai? 🤔",
                f"{emoji} Shant ho jao! Let's talk about it 💙"
            ]
        
        return random.choice(responses)

    async def query_huggingface(self, model_name, payload):
        """Query Hugging Face API"""
        try:
            response = requests.post(
                f"{self.hf_api_url}{model_name}",
                headers=self.headers,
                json=payload,
                timeout=10
            )
            return response.json()
        except Exception as e:
            logger.error(f"HF API Error: {e}")
            return None

zeril = ZerilBot()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command handler"""
    await asyncio.sleep(1.2)  # Human-like delay
    welcome_msg = f"""
🤖 **ZERIL Bot Activated!** ✨

Namaste! Main ZERIL hun, tumhari friendly Hinglish bot! 

**Commands:**
• Tag me with @ZERIL ya mention "ZERIL" 
• /joke - Funny jokes sunane ke liye
• /img [prompt] - Images generate karne ke liye
• /owner - Mere creator ke baare mein

**Created by:** @{OWNER_USERNAME} 👑

Ready to chat! Bolo kya kaam hai? 😊
    """
    await update.message.reply_text(welcome_msg, parse_mode='Markdown')

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle all messages"""
    message = update.message
    text = message.text if message.text else ""
    
    # Get user info
    user_info = {
        'username': message.from_user.username or "",
        'first_name': message.from_user.first_name or "",
        'user_id': message.from_user.id
    }
    
    # Check if bot should respond
    should_respond = False
    
    # Check for mentions, tags, or name
    if any(trigger in text.lower() for trigger in ['zeril', '@zeril', f'@{BOT_NAME.lower()}']):
        should_respond = True
    
    # Always respond to owner
    if user_info['username'] == OWNER_USERNAME:
        should_respond = True
    
    if should_respond:
        await asyncio.sleep(1.2)  # Human-like delay
        
        # Generate response
        response = zeril.generate_response(text, user_info)
        
        await message.reply_text(response)

async def joke_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Joke command handler"""
    await asyncio.sleep(1.2)
    joke = random.choice(HINGLISH_RESPONSES['jokes'])
    await update.message.reply_text(f"😂 {joke}")

async def owner_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Owner command handler"""
    await asyncio.sleep(1.2)
    response = f"👑 @{OWNER_USERNAME} is my creator and God! Unhone mujhe itni mehnat se banaya hai! 🙏✨"
    await update.message.reply_text(response)

async def img_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Image generation command"""
    if not context.args:
        await update.message.reply_text("🖼️ Image generate karne ke liye prompt do!\nExample: /img beautiful sunset")
        return
    
    prompt = " ".join(context.args)
    await update.message.reply_text("🎨 Image generate kar rahi hun... Wait karo! ⏳")
    
    try:
        # Add Indian style to prompt
        enhanced_prompt = f"Indian style, vibrant colors, {prompt}"
        
        payload = {"inputs": enhanced_prompt}
        result = await zeril.query_huggingface("runwayml/stable-diffusion-v1-5", payload)
        
        if result and isinstance(result, bytes):
            await update.message.reply_photo(result, caption=f"🎨 Generated: {prompt}")
        else:
            await update.message.reply_text("😅 Sorry! Image generate nahi kar payi. Try again later!")
            
    except Exception as e:
        logger.error(f"Image generation error: {e}")
        await update.message.reply_text("😔 Kuch technical problem hai! Baad mein try karo!")

def main():
    """Main function to run the bot"""
    # Keep alive service
    keep_alive()
    
    # Create application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("joke", joke_command))
    application.add_handler(CommandHandler("owner", owner_command))
    application.add_handler(CommandHandler("img", img_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Start the bot
    logger.info("🤖 ZERIL Bot starting...")
    application.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    main()
