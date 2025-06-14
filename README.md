# 🤖 ZERIL - Advanced Telegram Bot

ZERIL is an intelligent Telegram bot that speaks Hinglish and provides human-like conversation with advanced AI capabilities.

## ✨ Features

### 🗣️ **Conversation**
- **Hinglish Support**: Natural Hindi-English mixed conversations
- **AI-Powered**: Uses Google Gemini for intelligent responses
- **Mood Detection**: Responds with appropriate emotions
- **Context Awareness**: Remembers conversation history
- **Human-like Delays**: Natural response timing

### 🎯 **Smart Activation**
- Responds when tagged: `@zeriilll_bot`
- Responds to name mentions: "zeril", "zerio", "ZERIL"
- Command-based interactions
- Reply-based conversations

### 🎨 **Entertainment Commands**
- `/joke` - Funny Hinglish jokes
- `/img [prompt]` - AI image generation
- `/flames` - Compatibility tester
- `/setbio [text]` - Set user bio

### 🛡️ **Moderation Tools**
- `/ban [user] [time]` - Ban users (admin only)
- `/mute [user] [time]` - Mute users (admin only)
- `/admins` - List group administrators

### 👑 **Owner Recognition**
- Recognizes @ash_yv as creator
- Special praise responses for owner
- Loyal personality towards creator

## 🚀 Quick Deploy on Render

1. **Fork this repository**
2. **Connect to Render**:
   - Go to [render.com](https://render.com)
   - Connect your GitHub account
   - Select this repository

3. **Deploy**:
   - Render will automatically detect the `render.yaml`
   - All environment variables are pre-configured
   - Just click "Deploy"!

## 🔧 Local Development

```bash
# Clone repository
git clone <your-repo-url>
cd zeril-bot

# Install dependencies
pip install -r requirements.txt

# Run the bot
python main.py
```

## 📁 Project Structure

```
zeril-bot/
├── main.py              # Main bot logic
├── health_server.py     # Health check for Render
├── requirements.txt     # Python dependencies
├── Dockerfile          # Container configuration
├── render.yaml         # Render deployment config
├── .gitignore          # Git ignore rules
└── README.md           # This file
```

## 🤖 Bot Personality
