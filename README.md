# 🤖 ZERIL - Advanced Telegram Bot

ZERIL is an intelligent Telegram bot with personality, built with advanced AI capabilities and Hinglish conversation support.

## 🌟 Features

- **Smart Conversations**: Responds only when mentioned (@ZERIL) or tagged
- **Hinglish Support**: Natural Hindi-English mixed conversation
- **Owner Recognition**: Special responses for creator @ash_yv
- **AI-Powered**: Uses Hugging Face models for intelligent responses
- **Mood Detection**: Adapts responses based on message sentiment
- **Image Generation**: Create images from text prompts
- **Fun Commands**: Jokes, games, and entertainment features

## 🚀 Commands

### Basic Commands
- `/start` - Initialize bot
- `/help` - Show all commands

### Fun Commands
- `/joke` - Get Hinglish jokes
- `/flames @user1 @user2` - Love compatibility checker
- `/img [prompt]` - Generate AI images

### Chat Features
- Tag `@ZERIL` or mention "ZERIL" to start conversation
- Bot responds with context-aware Hinglish replies
- Mood-based emoji prefixes

## 🛠️ Setup for Render Deployment

### 1. Create GitHub Repository
1. Create new repository on GitHub
2. Upload all these files:
   - `main.py`
   - `requirements.txt`
   - `Dockerfile`
   - `render.yaml`
   - `README.md`

### 2. Deploy on Render
1. Go to [render.com](https://render.com)
2. Connect your GitHub account
3. Select "New Web Service"
4. Choose your repository
5. Render will automatically detect the `render.yaml` file
6. Click "Deploy"

### 3. Environment Variables (Auto-configured)
```
BOT_TOKEN=8048986424:AAE37IBwkCzE5oKtGCdN-mnnsMrcrlzGWUQ
HF_API_KEY=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
PORT=8080
```

## 🧠 AI Models Used

- **DialoGPT**: Conversational AI
- **Sentiment Analysis**: Mood detection
- **Stable Diffusion**: Image generation
- All models run on Hugging Face free tier

## 🎯 Bot Behavior

### Activation Rules
- Responds ONLY when:
  - Tagged with @ZERIL
  - Name "ZERIL" mentioned in message
  - Direct message in private chat
- 1.2s response delay for human-like interaction

### Owner Recognition
- Recognizes @ash_yv as creator
- Special praise responses for owner
- Responds to ownership queries with creator information

### Language Style
- Primary: Hinglish (Hindi in English script)
- Examples:
  - "Tumne khana khaya?" = Have you eaten?
  - "Aaj mood kharab hai" = Feeling sad today
- Avoids vulgar/inappropriate language

## 🔧 Technical Details

### Render Free Tier Optimizations
- Lightweight Python 3.11 slim image
- Efficient dependency management
- Health check endpoint for Render
- Automatic model loading with retry logic
- Memory-efficient conversation handling

### Error Handling
- Graceful API failure handling
- Fallback responses when AI models unavailable
- Automatic retry for model loading delays
- Comprehensive error logging

## 📞 Support

Bot created by **@ash_yv** (Ash)

For issues or questions, contact the creator on Telegram.

---

**Note**: This bot is optimized for Render's free tier and should deploy without errors. The health check endpoint ensures Render can monitor the service properly.
