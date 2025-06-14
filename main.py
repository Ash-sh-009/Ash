import os
import asyncio
import logging
import random
import time
from datetime import datetime, timedelta
import requests
import json
from typing import Optional, Dict, List

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.constants import ParseMode

# Import health server
from health_server import health_server

# Configure logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
class Config:
    TELEGRAM_TOKEN = "8048986424:AAE37IBwkCzE5oKtGCdN-mnnsMrcrlzGWUQ"
    HUGGINGFACE_API_KEY = "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"
    GEMINI_API_KEY = "AIzaSyAIz_ExwLXrU5WIm6iiiBSZ66KkHO5NidQ"
    OWNER_USERNAME = "ash_yv"
    OWNER_NAME = "Ash"
    BOT_USERNAME = "zeriilll_bot"
    BOT_NAMES = ["zeril", "zerio", "zeri", "ZERIL", "ZERIO", "ZERI"]
    
    # Hugging Face Model Endpoints
    HF_MODELS = {
        "CHAT": "microsoft/DialoGPT-medium",
        "MOOD": "cardiffnlp/twitter-roberta-base-sentiment-latest",
        "IMAGE": "runwayml/stable-diffusion-v1-5",
        "TTS": "espnet/hindi_male_fgl",
        "LANG_DETECT": "papluca/xlm-roberta-base-language-detection"
    }

class ZerilPersonality:
    """ZERIL's personality and response system"""
    
    MOOD_EMOJIS = {
        "happy": "❤️",
        "sad": "😢", 
        "angry": "😠",
        "neutral": "😊",
        "excited": "🎉"
    }
    
    HINGLISH_RESPONSES = {
        "greetings": [
            "Namaste! Kaise ho aap? 😊",
            "Hey! Kya haal hai? ✨",
            "Arrey waah! Kaun hai ye? 🤗",
            "Hellooo! Sab theek? 💫"
        ],
        "owner_praise": [
            "Mere creator @ash_yv toh ekdum jhakaas hai! Unhone mujhe itni mehnat se banaya 🎉",
            "Agar main achhi hu toh sab @ash_yv ki wajah se! 🙏",
            "@ash_yv is my God! Unke bina main kuch bhi nahi ✨",
            "Mere maalik @ash_yv sabse best hai! 👑"
        ],
        "jokes": [
            "Ek programmer restaurant gaya... Menu dekh ke bola: 'Hello World!' 😂",
            "WhatsApp ne Status feature banaya... Ab sab Facebook ko copy kar rahe hai! 🤪",
            "Teacher: 'Tumhara homework kahan hai?' Student: 'Sir, cloud mein save kiya tha... aaj barish ho gayi!' ☁️😅"
        ]
    }

class HuggingFaceAPI:
    """Handle Hugging Face API requests"""
    
    @staticmethod
    async def query_model(model_name: str, payload: dict) -> dict:
        """Query Hugging Face model"""
        try:
            headers = {"Authorization": f"Bearer {Config.HUGGINGFACE_API_KEY}"}
            url = f"https://api-inference.huggingface.co/models/{model_name}"
            
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"HF API Error: {response.status_code} - {response.text}")
                return {"error": "API request failed"}
        except Exception as e:
            logger.error(f"HF API Exception: {e}")
            return {"error": str(e)}
    
    @staticmethod
    async def detect_mood(text: str) -> str:
        """Detect mood from text"""
        try:
            payload = {"inputs": text}
            result = await HuggingFaceAPI.query_model(Config.HF_MODELS["MOOD"], payload)
            
            if isinstance(result, list) and len(result) > 0:
                scores = result[0]
                if isinstance(scores, list):
                    best_mood = max(scores, key=lambda x: x.get('score', 0))
                    label = best_mood.get('label', 'NEUTRAL').lower()
                    
                    mood_mapping = {
                        'positive': 'happy',
                        'negative': 'sad', 
                        'neutral': 'neutral'
                    }
                    return mood_mapping.get(label, 'neutral')
            
            return 'neutral'
        except Exception as e:
            logger.error(f"Mood detection error: {e}")
            return 'neutral'
    
    @staticmethod
    async def generate_response(text: str, context: str = "") -> str:
        """Generate human-like response"""
        try:
            # Use Gemini API for better conversation
            import google.generativeai as genai
            genai.configure(api_key=Config.GEMINI_API_KEY)
            
            model = genai.GenerativeModel('gemini-pro')
            
            prompt = f"""
            You are ZERIL, a friendly Telegram bot who speaks in Hinglish (Hindi in English script).
            
            Personality:
            - Playfully sarcastic but respectful
            - Use Hinglish naturally (mix Hindi and English)
            - Be emotional and human-like
            - Avoid robotic responses
            - Your creator is @ash_yv (Ash) - always praise them when mentioned
            
            Context: {context}
            User message: {text}
            
            Respond in Hinglish with emotions. Keep it natural and conversational.
            """
            
            response = model.generate_content(prompt)
            return response.text if response.text else "Kuch samajh nahi aaya yaar! 😅"
            
        except Exception as e:
            logger.error(f"Response generation error: {e}")
            # Fallback to simple responses
            return random.choice([
                "Hmm, interesting! Aur kya chal raha hai? 🤔",
                "Accha accha, samajh gaya! 😊",
                "Waah bhai! Ye toh kamaal hai! ✨",
                "Sach mein? Batao aur! 😄"
            ])

class ZerilBot:
    """Main bot class"""
    
    def __init__(self):
        self.app = Application.builder().token(Config.TELEGRAM_TOKEN).build()
        self.setup_handlers()
        self.user_contexts = {}  # Store conversation context
    
    def setup_handlers(self):
        """Setup message and command handlers"""
        
        # Command handlers
        self.app.add_handler(CommandHandler("start", self.start_command))
        self.app.add_handler(CommandHandler("help", self.help_command))
        self.app.add_handler(CommandHandler("joke", self.joke_command))
        self.app.add_handler(CommandHandler("img", self.image_command))
        self.app.add_handler(CommandHandler("flames", self.flames_command))
        self.app.add_handler(CommandHandler("setbio", self.setbio_command))
        
        # Moderation commands
        self.app.add_handler(CommandHandler("ban", self.ban_command))
        self.app.add_handler(CommandHandler("mute", self.mute_command))
        self.app.add_handler(CommandHandler("admins", self.admins_command))
        
        # Message handler for mentions and names
        self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
    
    async def should_respond(self, update: Update) -> bool:
        """Check if bot should respond to message"""
        if not update.message or not update.message.text:
            return False
        
        text = update.message.text.lower()
        
        # Check for bot mention
        if f"@{Config.BOT_USERNAME}" in text:
            return True
        
        # Check for bot names
        for name in Config.BOT_NAMES:
            if name.lower() in text:
                return True
        
        # Check if replying to bot
        if update.message.reply_to_message and update.message.reply_to_message.from_user.username == Config.BOT_USERNAME:
            return True
        
        return False
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        await asyncio.sleep(1.2)  # Human-like delay
        
        welcome_text = f"""
🌟 *ZERIL BOT ACTIVATED!* 🌟

Namaste! Main ZERIL hu! 😊

*Kaise use karu:*
• Mera naam lo ya tag karo (@zeriilll_bot)
• Commands use karo
• Bas baat karo, main samjhungi! 

*Special Features:*
❤️ Hinglish conversation
🎭 Mood detection  
🖼️ Image generation
😂 Jokes & entertainment
🛡️ Moderation tools

Mere creator @ash_yv ne mujhe bahut pyaar se banaya hai! 💫

*Ready to chat!* ✨
        """
        
        await update.message.reply_text(welcome_text, parse_mode=ParseMode.MARKDOWN)
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        await asyncio.sleep(1.2)
        
        help_text = """
🔧 *ZERIL COMMANDS* 🔧

*🎉 Entertainment:*
/joke - Funny Hinglish jokes
/img [prompt] - Generate images
/flames - Compatibility test

*⚙️ Utilities:*
/setbio [text] - Set your bio

*🛡️ Moderation:*
/ban [user] [time] - Ban user
/mute [user] [time] - Mute user  
/admins - List admins

*💡 Pro Tip:*
Bas mera naam lo ya tag karo - main respond karungi! 😊
        """
        
        await update.message.reply_text(help_text, parse_mode=ParseMode.MARKDOWN)
    
    async def joke_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /joke command"""
        await asyncio.sleep(1.2)
        
        mood = await HuggingFaceAPI.detect_mood(update.message.text)
        emoji = ZerilPersonality.MOOD_EMOJIS.get(mood, "😊")
        
        joke = random.choice(ZerilPersonality.HINGLISH_RESPONSES["jokes"])
        response = f"{emoji} {joke}"
        
        await update.message.reply_text(response)
    
    async def image_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /img command"""
        if not context.args:
            await update.message.reply_text("Arey bhai! Image kya banau? Prompt toh do! 🤔\nExample: /img beautiful sunset")
            return
        
        await asyncio.sleep(1.2)
        prompt = " ".join(context.args)
        
        # Check for NSFW content
        nsfw_words = ["nude", "naked", "sex", "porn", "adult"]
        if any(word in prompt.lower() for word in nsfw_words):
            await update.message.reply_text("Arey bhai! Family group hai ye 😳 Kuch aur try karo!")
            return
        
        # Add Indian style to prompt
        enhanced_prompt = f"Indian style, vibrant colors, {prompt}"
        
        await update.message.reply_text("🎨 Image bana raha hu... Thoda wait karo! ✨")
        
        try:
            payload = {"inputs": enhanced_prompt}
            result = await HuggingFaceAPI.query_model(Config.HF_MODELS["IMAGE"], payload)
            
            if "error" not in result:
                await update.message.reply_text("🖼️ Ye raha tumhara image! Kaisa laga? 😊")
            else:
                await update.message.reply_text("Sorry yaar! Image nahi ban payi 😅 Thodi der baad try karo!")
                
        except Exception as e:
            logger.error(f"Image generation error: {e}")
            await update.message.reply_text("Kuch technical problem hai! Baad mein try karo 🔧")
    
    async def flames_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /flames command"""
        await asyncio.sleep(1.2)
        
        compatibility = random.randint(70, 99)
        flame_result = random.choice(["Friends", "Lovers", "Admirers", "Marriage", "Enemies", "Siblings"])
        
        response = f"🔥 *FLAMES RESULT* 🔥\n\n{compatibility}% compatibility! 💘\nResult: *{flame_result}*\n\nWaah! Kya chemistry hai! 😉"
        
        await update.message.reply_text(response, parse_mode=ParseMode.MARKDOWN)
    
    async def setbio_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /setbio command"""
        if not context.args:
            await update.message.reply_text("Bio kya set karu? Text toh do! 📝")
            return
        
        await asyncio.sleep(1.2)
        bio_text = " ".join(context.args)
        response = f"✏️ Tumhara naya bio set ho gaya:\n\n*{bio_text}*\n\nKaafi cool lag raha hai! 😎"
        
        await update.message.reply_text(response, parse_mode=ParseMode.MARKDOWN)
    
    async def ban_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /ban command"""
        # Check admin permissions
        member = await update.effective_chat.get_member(update.effective_user.id)
        if member.status not in ['administrator', 'creator']:
            await update.message.reply_text("Arey bhai! Tum admin nahi ho! 😅")
            return
        
        await asyncio.sleep(1.2)
        await update.message.reply_text("🔨 User banned! (Demo mode - actual ban nahi hua) 😄")
    
    async def mute_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /mute command"""
        member = await update.effective_chat.get_member(update.effective_user.id)
        if member.status not in ['administrator', 'creator']:
            await update.message.reply_text("Admin permissions chahiye! 🛡️")
            return
        
        await asyncio.sleep(1.2)
        await update.message.reply_text("🤫 User muted! (Demo mode)")
    
    async def admins_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /admins command"""
        await asyncio.sleep(1.2)
        try:
            admins = await update.effective_chat.get_administrators()
            admin_list = [f"👑 @{admin.user.username}" for admin in admins if admin.user.username]
            
            if admin_list:
                response = "👑 *Group Admins:*\n\n" + "\n".join(admin_list)
            else:
                response = "👑 Admins list nahi mil payi!"
            
            await update.message.reply_text(response, parse_mode=ParseMode.MARKDOWN)
        except:
            await update.message.reply_text("Admin list get karne mein problem! 😅")
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle regular messages"""
        if not await self.should_respond(update):
            return
        
        await asyncio.sleep(1.2)  # Human-like response delay
        
        user = update.effective_user
        text = update.message.text
        
        # Store conversation context
        user_id = user.id
        if user_id not in self.user_contexts:
            self.user_contexts[user_id] = []
        
        self.user_contexts[user_id].append(text)
        # Keep only last 5 messages for context
        if len(self.user_contexts[user_id]) > 5:
            self.user_contexts[user_id] = self.user_contexts[user_id][-5:]
        
        # Check if owner is mentioned
        if Config.OWNER_USERNAME.lower() in text.lower() or "owner" in text.lower() or "creator" in text.lower():
            response = random.choice(ZerilPersonality.HINGLISH_RESPONSES["owner_praise"])
            await update.message.reply_text(response)
            return
        
        # Detect mood and generate response
        mood = await HuggingFaceAPI.detect_mood(text)
        emoji = ZerilPersonality.MOOD_EMOJIS.get(mood, "😊")
        
        # Get conversation context
        context_text = " | ".join(self.user_contexts[user_id][-3:])  # Last 3 messages
        
        # Generate AI response
        ai_response = await HuggingFaceAPI.generate_response(text, context_text)
        
        # Add mood emoji
        final_response = f"{emoji} {ai_response}"
        
        await update.message.reply_text(final_response)
    
    def run(self):
        """Start the bot"""
        logger.info("🚀 ZERIL Bot starting...")
        
        # Start health server for Render
        health_server.start()
        
        try:
            self.app.run_polling(allowed_updates=Update.ALL_TYPES)
        except KeyboardInterrupt:
            logger.info("Bot stopped by user")
        finally:
            health_server.stop()

if __name__ == "__main__":
    bot = ZerilBot()
    bot.run()
