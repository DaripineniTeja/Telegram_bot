# 🤖 AI Tools Board Telegram Bot

A comprehensive Telegram bot that acts as an AI Tools Board, helping users discover and explore various AI tools organized by categories.

## ✨ Features

- **📁 Category-based Organization**: Tools are organized by purpose/category
- **🔍 Smart Search**: Search for tools by name, category, or URL
- **📊 Statistics**: View detailed statistics about available tools
- **💡 User-friendly Interface**: Intuitive numbered selection system
- **🔄 Dynamic Loading**: Automatically extracts categories from JSON data
- **❌ Error Handling**: Graceful error handling with helpful messages

## 🚀 Quick Start

### 1. Create a Telegram Bot

1. Open Telegram and search for `@BotFather`
2. Send `/newbot` to create a new bot
3. Follow the instructions to set up your bot
4. Copy the bot token provided by BotFather

### 2. Setup the Project

```bash
# Install Python dependencies
pip install -r requirements.txt

# Copy the environment file
cp .env.example .env

# Edit the .env file and add your bot token
BOT_TOKEN=your_actual_bot_token_here
```

### 3. Run the Bot

```bash
# Basic version
python main.py

# Enhanced version with more features
python bot_enhanced.py
```

## 📁 Project Structure

```
telegram-ai-tools-bot/
├── main.py              # Basic bot implementation
├── bot_enhanced.py      # Enhanced bot with additional features
├── config.py            # Configuration management
├── tools.json           # AI tools database
├── requirements.txt     # Python dependencies
├── .env.example         # Environment variables template
└── README.md           # This file
```

## 🛠️ Configuration

### Environment Variables

Create a `.env` file based on `.env.example`:

```env
BOT_TOKEN=your_telegram_bot_token
JSON_FILE_PATH=tools.json
LOG_LEVEL=INFO
```

### Adding New Tools

Edit the `tools.json` file to add new AI tools:

```json
{
  "name": "Tool Name",
  "purpose": "🎯 Category Name",
  "link": "https://example.com"
}
```

## 📋 Available Commands

- `/start` - Show all available categories
- `/help` - Display help information
- `/stats` - Show detailed statistics (Enhanced version)
- `/search <keyword>` - Search for specific tools (Enhanced version)

## 🎯 Usage Examples

1. **Browse Categories**:
   - Send `/start`
   - Send `1` to see tools in the first category

2. **Search Tools**:
   - Send `/search notion` to find Notion-related tools
   - Send `/search productivity` to find productivity tools

3. **View Statistics**:
   - Send `/stats` to see detailed statistics

## 🔧 Customization

### Adding New Categories

Simply add tools with new `purpose` values to the `tools.json` file. The bot will automatically detect and display new categories.

### Modifying Response Format

Edit the message formatting in the respective handler functions in `main.py` or `bot_enhanced.py`.

## 📊 Current Tool Categories

- 💼 Business & Productivity
- 🧠 Data Analysis & Research
- 🎨 Creative & Design
- 👨‍💻 Development & Programming
- ✍️ Writing & Content

## 🐛 Troubleshooting

### Common Issues

1. **Bot Token Error**: Make sure you've set the correct bot token in the `.env` file
2. **JSON File Not Found**: Ensure `tools.json` exists in the project directory
3. **Permission Errors**: Make sure the bot has permission to send messages

### Logging

The bot includes comprehensive logging. Check the console output for detailed error messages.

## 📝 License

This project is open source and available under the MIT License.

## 🤝 Contributing

Feel free to contribute by:
- Adding new AI tools to the database
- Improving the bot functionality
- Fixing bugs or issues
- Enhancing the user experience

## 🆘 Support

If you encounter any issues:
1. Check the troubleshooting section
2. Review the logs for error messages
3. Ensure all dependencies are installed correctly
4. Verify your bot token is correct

---

**Happy AI tool hunting! 🚀**