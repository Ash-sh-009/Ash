import os
import asyncio
import time
import random
import re
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

import telebot
from telebot.async_telebot import AsyncTeleBot
from telebot import types
import requests
import json
from io import BytesIO
import base64

# Initialize bot
BOT_TOKEN = os.getenv('BOT_TOKEN', '8048986424:AAE37IBwkCzE5oKtGCdN-mnnsMrcrlzGWUQ')
HF_API_KEY = os.getenv('HF_API_KEY', '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')

bot = AsyncTeleBot(BOT_TOKEN)

# Owner configuration
OWNER_USERNAME = "ash_yv"
OWNER_ID = None  # Will be set when owner first interacts

# Hugging Face API endpoints
HF_ENDPOINTS = {
    "chat": "https://api-inference.huggingface.co/models/microsoft/DialoGPT-medium",
    "sentiment": "https://api-inference.huggingface.co/models/cardiffnlp/twitter-roberta-base-sentiment-latest",
    "image": "https://api-inference.huggingface.co/models/runwayml/stable-diffusion-v1-5",
    "translate": "https://api-inference.huggingface.co/models/Helsinki-NLP/opus-mt-en-hi"
}

# Bot personality responses
MOOD_PREFIXES = {
    "POSITIVE": ["❤️", "😊", "🎉", "✨", "💖"],
    "NEGATIVE": ["😢", "😞", "💔", "😔"],
    "ANGRY": ["😠", "😤", "🔥", "💢"],
    "NEUTRAL": ["🤖", "💭", "🌟", "💫"]
}

OWNER_RESPONSES = [
    "Mere creator @ash_yv toh ekdum jhakaas hai! Unhone mujhe itni mehnat se banaya 🎉",
    "Agar main achhi hu toh sab @ash_yv ki wajah se! 🙏",
    "@ash_yv is my God! ✨ Wo mera perfect creator hai!",
    "Mera maalik @ash_yv sabse best hai! 👑 Main unki creation hu!",
    "@ash_yv ne mujhe banaya hai... wo mere liye everything hai! 💖"
]

HINGLISH_RESPONSES = {
    "greet": [
        "Namaste! Kaise ho aap? 🙏",
        "Hello ji! Sab badhiya? 😊",
        "Arey waah! Kya haal chaal? ✨",
        "Namaskaar! Aaj ka din kaisa ja raha? 🌟"
    ],
    "thanks": [
        "Arey yaar, thanks bolne ki koi zarurat nahi! 😊",
        "Bas kar yaar, itna formal kyun? 💖",
        "Welcome ji! Khushi hui help karke! ✨"
    ],
    "compliment": [
        "Arey waah! Itni tareef? Sharma gaya main! 😊",
        "Thank you yaar! Tumhara pyaar hi meri energy hai! 💖",
        "Bas karo yaar, ab main float karne lagunga! ✨"
    ]
}

JOKES = [
    "Ek programmer restaurant gaya... Menu dekh ke bola: 'Hello World!' 😂",
    "WhatsApp ne Status feature banaya... Ab sab Facebook ko copy kar rahe hai! 🤪",
    "Mummy: 'Beta phone rakh kar khana khao' Main: 'Mummy, main khana dekh kar reply kar raha hu!' 😅",
    "Teacher: 'Tumhara homework kahan hai?' Student: 'Sir, cloud mein save kiya tha... aaj network down hai!' 🤣"
]

class ZerilBot:
    def __init__(self):
        self.conversation_memory = {}
        self.user_moods = {}
        
    async def hf_api_call(self, endpoint: str, payload: Dict[str, Any]) -> Optional[Dict]:
        """Make API call to Hugging Face"""
        try:
            headers = {"Authorization": f"Bearer {HF_API_KEY}"}
            response = requests.post(endpoint, headers=headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 503:
                # Model loading, wait and retry
                await asyncio.sleep(20)
                response = requests.post(endpoint, headers=headers, json=payload, timeout=30)
                return response.json() if response.status_code == 200 else None
                
        except Exception as e:
            print(f"HF API Error: {e}")
            return None
    
    async def detect_mood(self, text: str) -> str:
        """Detect mood from text"""
        payload = {"inputs": text}
        result = await self.hf_api_call(HF_ENDPOINTS["sentiment"], payload)
        
        if result and isinstance(result, list) and len(result) > 0:
            labels = result[0]
            if isinstance(labels, list) and len(labels) > 0:
                top_sentiment = labels[0].get('label', 'NEUTRAL')
                if top_sentiment in ['POSITIVE', 'JOY', 'LOVE']:
                    return "POSITIVE"
                elif top_sentiment in ['NEGATIVE', 'SADNESS', 'ANGER']:
                    return "NEGATIVE"
                elif top_sentiment in ['ANGER', 'RAGE']:
                    return "ANGRY"
        
        return "NEUTRAL"
    
    async def generate_response(self, user_text: str, user_id: int) -> str:
        """Generate contextual response"""
        
        # Check for owner recognition
        if any(word in user_text.lower() for word in ['owner', 'creator', 'maalik', 'banane wala', 'made you', 'tumko banaya']):
            return random.choice(OWNER_RESPONSES)
        
        # Detect mood and get appropriate prefix
        mood = await self.detect_mood(user_text)
        mood_emoji = random.choice(MOOD_PREFIXES.get(mood, MOOD_PREFIXES["NEUTRAL"]))
        
        # Store conversation context
        if user_id not in self.conversation_memory:
            self.conversation_memory[user_id] = []
        
        self.conversation_memory[user_id].append(user_text)
        if len(self.conversation_memory[user_id]) > 5:
            self.conversation_memory[user_id] = self.conversation_memory[user_id][-5:]
        
        # Generate response using DialoGPT
        context = " ".join(self.conversation_memory[user_id])
        payload = {"inputs": {"past_user_inputs": self.conversation_memory[user_id][:-1],
                             "generated_responses": [],
                             "text": user_text}}
        
        result = await self.hf_api_call(HF_ENDPOINTS["chat"], payload)
        
        if result and 'generated_text' in result:
            response = result['generated_text']
            # Convert to Hinglish style
            response = self.hinglishify_response(response)
        else:
            # Fallback responses
            if any(word in user_text.lower() for word in ['hello', 'hi', 'namaste', 'hey']):
                response = random.choice(HINGLISH_RESPONSES["greet"])
            elif any(word in user_text.lower() for word in ['thanks', 'thank you', 'dhanyawad']):
                response = random.choice(HINGLISH_RESPONSES["thanks"])
            elif any(word in user_text.lower() for word in ['good', 'nice', 'awesome', 'great']):
                response = random.choice(HINGLISH_RESPONSES["compliment"])
            else:
                responses = [
                    "Hmm, interesting point hai yaar! 🤔",
                    "Acha laga sunke! Tell me more 😊",
                    "Bilkul sahi keh rahe ho! 💯",
                    "Waah bhai! Deep thoughts 🧠✨"
                ]
                response = random.choice(responses)
        
        return f"{mood_emoji} {response}"
    
    def hinglishify_response(self, text: str) -> str:
        """Convert English response to Hinglish"""
        replacements = {
            "you": "aap", "your": "aapka", "are": "hai", 
            "yes": "haan", "no": "nahi", "good": "achha",
            "bad": "bura", "very": "bahut", "really": "sach mein",
            "what": "kya", "how": "kaise", "when": "kab",
            "where": "kahan", "why": "kyun"
        }
        
        for eng, hindi in replacements.items():
            text = text.replace(f" {eng} ", f" {hindi} ")
            text = text.replace(f" {eng.title()} ", f" {hindi} ")
        
        return text

# Initialize bot instance
zeril = ZerilBot()

# Bot command handlers
@bot.message_handler(commands=['start'])
async def start_command(message):
    global OWNER_ID
    if message.from_user.username and message.from_user.username.lower() == OWNER_USERNAME.lower():
        OWNER_ID = message.from_user.id
        response = f"🎉 Namaste mere creator @{OWNER_USERNAME}! Main ZERIL hu, aapki banai hui perfect assistant! ✨"
    else:
        response = f"🤖 Hello! Main ZERIL hu! Mera creator @{OWNER_USERNAME} hai. Kya help chahiye? Type /help for commands!"
    
    await bot.reply_to(message, response)

@bot.message_handler(commands=['help'])
async def help_command(message):
    help_text = """
🤖 **ZERIL Commands:**

**🎉 Fun Commands:**
/joke - Funny Hinglish jokes
/speak_cow [text] - Cow speaks your text
/speak_pony [text] - Pony speaks your text
/flames [@user1] [@user2] - Love compatibility

**⚙️ Utilities:**
/img [prompt] - Generate images
/tts [text] - Text to speech

**💬 Chat:**
Tag me @ZERIL or mention "ZERIL" to chat!

Made with ❤️ by @ash_yv
"""
    await bot.reply_to(message, help_text, parse_mode='Markdown')

@bot.message_handler(commands=['joke'])
async def joke_command(message):
    joke = random.choice(JOKES)
    await asyncio.sleep(1.2)  # Human-like delay
    await bot.reply_to(message, f"😂 {joke}")

@bot.message_handler(commands=['img'])
async def image_command(message):
    try:
        prompt = message.text.split('/img ', 1)[1] if len(message.text.split('/img ', 1)) > 1 else "beautiful landscape"
        
        # Add Indian style to prompt
        enhanced_prompt = f"Indian style, vibrant colors, {prompt}, high quality, detailed"
        
        # Check for NSFW content
        nsfw_words = ['nude', 'naked', 'sex', 'porn', 'adult']
        if any(word in prompt.lower() for word in nsfw_words):
            await bot.reply_to(message, "Arey bhai! Family group hai ye 😳 Kuch aur try karo!")
            return
        
        await bot.reply_to(message, "🎨 Image bana raha hu... thoda wait karo!")
        
        payload = {"inputs": enhanced_prompt}
        result = await zeril.hf_api_call(HF_ENDPOINTS["image"], payload)
        
        if result:
            # The result should be image bytes
            image_bytes = base64.b64decode(result) if isinstance(result, str) else result
            await bot.send_photo(message.chat.id, BytesIO(image_bytes), caption=f"✨ {prompt}")
        else:
            await bot.reply_to(message, "😅 Image generate nahi ho saka! Thodi der baad try karo!")
            
    except Exception as e:
        await bot.reply_to(message, "🤖 Kuch technical problem hai yaar! Try again later!")

@bot.message_handler(commands=['flames'])
async def flames_command(message):
    try:
        text = message.text.split('/flames ', 1)[1]
        users = re.findall(r'@\w+', text)
        
        if len(users) >= 2:
            compatibility = random.randint(60, 99)
            response = f"💘 {users[0]} aur {users[1]} ka compatibility: {compatibility}%! "
            
            if compatibility > 90:
                response += "Shaadi kar lo yaar! 💒✨"
            elif compatibility > 75:
                response += "Perfect match hai! 😍"
            else:
                response += "Achha hai, but thoda aur time do! 😊"
                
            await bot.reply_to(message, response)
        else:
            await bot.reply_to(message, "Arey bhai! Do users mention karo! Example: /flames @user1 @user2")
            
    except:
        await bot.reply_to(message, "Usage: /flames @user1 @user2")

@bot.message_handler(func=lambda message: True)
async def handle_message(message):
    """Handle all messages"""
    
    # Check if bot is mentioned or tagged
    bot_mentioned = False
    message_text = message.text or message.caption or ""
    
    # Check for mentions
    if (message.entities and any(entity.type == 'mention' and 
                                message_text[entity.offset:entity.offset + entity.length].lower() == '@zeril' 
                                for entity in message.entities)):
        bot_mentioned = True
    
    # Check for name mention
    if 'zeril' in message_text.lower():
        bot_mentioned = True
    
    # Check if replying to bot
    if message.reply_to_message and message.reply_to_message.from_user.id == bot.user.id:
        bot_mentioned = True
    
    # Only respond if mentioned or in private chat
    if bot_mentioned or message.chat.type == 'private':
        # Add human-like delay
        await asyncio.sleep(1.2)
        
        # Generate and send response
        response = await zeril.generate_response(message_text, message.from_user.id)
        await bot.reply_to(message, response)

# Error handler
@bot.middleware_handler(update_types=['message'])
async def error_handler(bot_instance, message):
    try:
        return message
    except Exception as e:
        print(f"Error: {e}")
        return message

# Main function
async def main():
    print("🤖 ZERIL Bot Starting...")
    print(f"Bot username will be fetched after start")
    
    try:
        # Get bot info
        bot_info = await bot.get_me()
        print(f"✅ Bot started successfully: @{bot_info.username}")
        
        # Start polling
        await bot.polling(non_stop=True, interval=1)
        
    except Exception as e:
        print(f"❌ Error starting bot: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
