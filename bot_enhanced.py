import json
import logging
import os
import re
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from config import BOT_TOKEN, JSON_FILE_PATH, LOG_LEVEL

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=getattr(logging, LOG_LEVEL.upper())
)
logger = logging.getLogger(__name__)

class AIToolsBotEnhanced:
    def __init__(self, json_file_path=JSON_FILE_PATH):
        self.json_file_path = json_file_path
        self.tools_data = self.load_tools_data()
        self.purposes = self.extract_purposes()
        self.user_states = {}  # Track user states for better UX
    
    def load_tools_data(self):
        """Load tools data from JSON file"""
        try:
            with open(self.json_file_path, 'r', encoding='utf-8') as file:
                return json.load(file)
        except FileNotFoundError:
            logger.error(f"JSON file {self.json_file_path} not found")
            return []
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON in {self.json_file_path}")
            return []
    
    def extract_purposes(self):
        """Extract unique purposes from tools data"""
        purposes = list(set(tool['purpose'] for tool in self.tools_data))
        return sorted(purposes)
    
    def get_tools_by_purpose(self, purpose):
        """Get all tools for a specific purpose"""
        return [tool for tool in self.tools_data if tool['purpose'] == purpose]
    
    def get_stats(self):
        """Get statistics about the tools"""
        total_tools = len(self.tools_data)
        total_categories = len(self.purposes)
        
        category_counts = {}
        for tool in self.tools_data:
            purpose = tool['purpose']
            category_counts[purpose] = category_counts.get(purpose, 0) + 1
        
        return {
            'total_tools': total_tools,
            'total_categories': total_categories,
            'category_counts': category_counts
        }
    
    def detect_natural_language_query(self, text):
        """Detect if the message is a natural language query for tools"""
        # Patterns to detect natural language queries
        patterns = [
            r'tools?\s+for\s+(.+)',
            r'(.+)\s+tools?',
            r'find\s+(.+)\s+tools?',
            r'show\s+(.+)\s+tools?',
            r'(.+)\s+ai\s+tools?',
            r'ai\s+tools?\s+for\s+(.+)',
            r'best\s+(.+)\s+tools?',
            r'(.+)\s+software',
            r'(.+)\s+applications?',
            r'(.+)\s+platforms?'
        ]
        
        text_lower = text.lower().strip()
        
        for pattern in patterns:
            match = re.search(pattern, text_lower)
            if match:
                # Extract the search term
                search_term = match.group(1).strip()
                # Clean up common words
                search_term = re.sub(r'\b(the|a|an|for|with|using|best|top|good)\b', '', search_term).strip()
                if search_term:
                    return search_term
        
        return None
    
    def search_tools_by_query(self, query):
        """Search for tools based on natural language query"""
        query = query.lower()
        matching_tools = []
        
        # Search in tool names, purposes, and links
        for tool in self.tools_data:
            if (query in tool['name'].lower() or 
                query in tool['purpose'].lower() or 
                query in tool['link'].lower()):
                matching_tools.append(tool)
        
        # Also search for partial matches in purpose keywords
        if not matching_tools:
            for tool in self.tools_data:
                purpose_words = tool['purpose'].lower().split()
                query_words = query.split()
                
                # Check if any query word matches any purpose word
                for query_word in query_words:
                    for purpose_word in purpose_words:
                        if query_word in purpose_word or purpose_word in query_word:
                            if tool not in matching_tools:
                                matching_tools.append(tool)
                            break
        
        return matching_tools
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        user_id = update.effective_user.id
        
        if not self.purposes:
            await update.message.reply_text("No tools available at the moment. Please try again later.")
            return
        
        stats = self.get_stats()
        
        message = f"🤖 **Welcome to the AI Tools Board!**\n\n"
        message += f"📊 **Statistics:**\n"
        message += f"• {stats['total_tools']} AI tools available\n"
        message += f"• {stats['total_categories']} categories\n\n"
        
        # Add social media links
        message += f"📱 **Follow us on social media:**\n"
        message += f"📸 Instagram: [Follow @aiwithteja](https://www.instagram.com/aiwithteja?igsh=MWE2dW93dWVseDBrdg==)\n"
        message += f"🎥 YouTube: [Subscribe to TechWith Teja](https://youtube.com/@techwith_teja?si=QSRQw2-r9en8hd9j)\n\n"
        
        message += "🎯 **Choose a category by sending its number:**\n\n"
        
        for i, purpose in enumerate(self.purposes, 1):
            tool_count = stats['category_counts'].get(purpose, 0)
            message += f"{i}. {purpose} ({tool_count} tools)\n"
        
        message += "\n💡 **Tips & Guide for New Users:**\n"
        message += "• Use /help for more commands\n"
        message += "• Use /stats for detailed statistics\n"
        message += "• Use /search <keyword> to find specific tools\n"
        message += "• **NEW**: Type natural queries like:\n"
        message += "  - 'tools for content creation'\n"
        message += "  - 'video editing tools'\n"
        message += "  - 'AI tools for marketing'\n"
        message += "• Type 'exit' to exit the bot\n"
        message += "• Type 'start' to return to this menu"
        
        await update.message.reply_text(message, parse_mode='Markdown')
        
        # Store user state
        self.user_states[user_id] = {'last_action': 'start', 'active': True}
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle user messages (category selection, exit, start, natural language queries)"""
        user_input = update.message.text.strip()
        user_input_lower = user_input.lower()
        user_id = update.effective_user.id
        
        # Handle exit command
        if user_input_lower == 'exit':
            self.user_states[user_id] = {'last_action': 'exit', 'active': False}
            exit_message = "👋 **Thank you for using AI Tools Board!**\n\n"
            exit_message += "🔄 To start again, simply type 'start' or use /start\n\n"
            exit_message += "📱 **Don't forget to follow us:**\n"
            exit_message += "📸 Instagram: [Follow @aiwithteja](https://www.instagram.com/aiwithteja?igsh=MWE2dW93dWVseDBrdg==)\n"
            exit_message += "🎥 YouTube: [Subscribe to TechWith Teja](https://youtube.com/@techwith_teja?si=QSRQw2-r9en8hd9j)\n\n"
            exit_message += "See you soon! 🚀"
            
            await update.message.reply_text(exit_message, parse_mode='Markdown')
            return
        
        # Handle start command (text input)
        if user_input_lower == 'start':
            await self.start_command(update, context)
            return
        
        # Check if user is active (not exited)
        user_state = self.user_states.get(user_id, {'active': True})
        if not user_state.get('active', True):
            await update.message.reply_text(
                "🔄 Welcome back! Type 'start' or use /start to begin using the AI Tools Board."
            )
            return
        
        # Check for natural language queries first
        search_query = self.detect_natural_language_query(user_input)
        if search_query:
            await self.handle_natural_language_search(update, context, search_query, user_input)
            return
        
        # Check if input is a number for category selection
        try:
            selection = int(user_input)
            
            # Validate selection range
            if 1 <= selection <= len(self.purposes):
                selected_purpose = self.purposes[selection - 1]
                tools = self.get_tools_by_purpose(selected_purpose)
                
                if tools:
                    message = f"🔧 **Tools under {selected_purpose}:**\n\n"
                    
                    for i, tool in enumerate(tools, 1):
                        message += f"**{i}. {tool['name']}**\n"
                        message += f"🔗 {tool['link']}\n\n"
                    
                    message += f"📊 **{len(tools)} tools found**\n\n"
                    message += "💡 **Navigation:**\n"
                    message += "• Type 'start' to see all categories again\n"
                    message += "• Type 'exit' to exit the bot\n"
                    message += "• Use /help for more commands"
                    
                    await update.message.reply_text(message, parse_mode='Markdown')
                    
                    # Update user state
                    self.user_states[user_id] = {
                        'last_action': 'category_selected',
                        'selected_purpose': selected_purpose,
                        'active': True
                    }
                else:
                    await update.message.reply_text(f"No tools found under {selected_purpose}.")
            else:
                await update.message.reply_text(
                    f"❌ Invalid selection. Please enter a valid number from 1 to {len(self.purposes)}.\n\n"
                    f"💡 **Quick commands:**\n"
                    f"• Type 'start' to see the categories again\n"
                    f"• Type 'exit' to exit the bot\n"
                    f"• Try natural queries like 'tools for design'"
                )
                
        except ValueError:
            # If not a number and not a natural language query, provide guidance
            await update.message.reply_text(
                "❌ I didn't understand that. Here's what you can do:\n\n"
                "🔢 **Category Selection:** Enter a number (1-" + str(len(self.purposes)) + ")\n"
                "🗣️ **Natural Search:** Try queries like:\n"
                "• 'tools for content creation'\n"
                "• 'video editing tools'\n"
                "• 'AI marketing tools'\n\n"
                "💡 **Quick commands:**\n"
                "• Type 'start' to see all categories\n"
                "• Type 'exit' to exit the bot\n"
                "• Use /help for more commands"
            )
    
    async def handle_natural_language_search(self, update: Update, context: ContextTypes.DEFAULT_TYPE, search_query: str, original_query: str):
        """Handle natural language search queries"""
        matching_tools = self.search_tools_by_query(search_query)
        
        if matching_tools:
            message = f"🔍 **Search results for '{original_query}':**\n\n"
            
            for i, tool in enumerate(matching_tools, 1):
                message += f"**{i}. {tool['name']}**\n"
                message += f"📁 Category: {tool['purpose']}\n"
                message += f"🔗 {tool['link']}\n\n"
            
            message += f"📊 **{len(matching_tools)} tools found**\n\n"
            message += "💡 **Navigation:**\n"
            message += "• Type 'start' to see all categories\n"
            message += "• Try other queries like 'tools for design'\n"
            message += "• Type 'exit' to exit the bot"
            
            await update.message.reply_text(message, parse_mode='Markdown')
            
            # Update user state
            user_id = update.effective_user.id
            self.user_states[user_id] = {
                'last_action': 'natural_search',
                'search_query': search_query,
                'active': True
            }
        else:
            await update.message.reply_text(
                f"❌ No tools found matching '{original_query}'.\n\n"
                f"💡 **Try again with:**\n"
                f"• Different keywords (e.g., 'design', 'video', 'writing')\n"
                f"• Broader terms (e.g., 'content creation' instead of 'video editing')\n"
                f"• Type 'start' to browse categories\n"
                f"• Type 'exit' to exit the bot\n\n"
                f"**Example queries:**\n"
                f"• 'tools for marketing'\n"
                f"• 'AI design tools'\n"
                f"• 'productivity software'"
            )
    
    async def search_tools(self, update: Update, context: ContextTypes.DEFAULT_TYPE, query: str):
        """Search for tools based on query (legacy method for /search command)"""
        query = query.lower()
        matching_tools = []
        
        for tool in self.tools_data:
            if (query in tool['name'].lower() or 
                query in tool['purpose'].lower() or 
                query in tool['link'].lower()):
                matching_tools.append(tool)
        
        if matching_tools:
            message = f"🔍 **Search results for '{query}':**\n\n"
            
            for i, tool in enumerate(matching_tools, 1):
                message += f"**{i}. {tool['name']}**\n"
                message += f"📁 Category: {tool['purpose']}\n"
                message += f"🔗 {tool['link']}\n\n"
            
            message += f"📊 **{len(matching_tools)} tools found**\n\n"
            message += "💡 **Navigation:**\n"
            message += "• Type 'start' to see all categories\n"
            message += "• Type 'exit' to exit the bot"
            
            await update.message.reply_text(message, parse_mode='Markdown')
        else:
            await update.message.reply_text(
                f"❌ No tools found matching '{query}'.\n\n"
                f"💡 **Try again:**\n"
                f"• Use different keywords\n"
                f"• Type 'start' to browse categories\n"
                f"• Type 'exit' to exit the bot"
            )
    
    async def search_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /search command"""
        if context.args:
            query = ' '.join(context.args)
            await self.search_tools(update, context, query)
        else:
            await update.message.reply_text(
                "🔍 **How to search:**\n\n"
                "**Method 1 - Command:**\n"
                "Use: `/search <keyword>`\n\n"
                "**Method 2 - Natural Language (NEW):**\n"
                "Just type queries like:\n"
                "• 'tools for content creation'\n"
                "• 'video editing tools'\n"
                "• 'AI marketing tools'\n\n"
                "**Examples:**\n"
                "• `/search notion` - Find tools with 'notion' in name\n"
                "• `/search productivity` - Find productivity tools\n"
                "• 'tools for design' - Natural language search\n\n"
                "💡 **Quick commands:**\n"
                "• Type 'start' to see all categories\n"
                "• Type 'exit' to exit the bot",
                parse_mode='Markdown'
            )
    
    async def stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /stats command"""
        stats = self.get_stats()
        
        message = f"📊 **AI Tools Board Statistics:**\n\n"
        message += f"🔧 **Total Tools:** {stats['total_tools']}\n"
        message += f"📁 **Total Categories:** {stats['total_categories']}\n\n"
        message += f"📈 **Tools per Category:**\n"
        
        for purpose, count in sorted(stats['category_counts'].items()):
            message += f"• {purpose}: {count} tools\n"
        
        message += "\n💡 **Navigation:**\n"
        message += "• Type 'start' to see all categories\n"
        message += "• Type 'exit' to exit the bot"
        
        await update.message.reply_text(message, parse_mode='Markdown')
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        help_text = """
🤖 **AI Tools Board Bot Help**

**Commands:**
• `/start` - Show all available categories
• `/help` - Show this help message
• `/stats` - Show detailed statistics
• `/search <keyword>` - Search for specific tools

**Text Commands:**
• `start` - Return to main menu
• `exit` - Exit the bot gracefully

**🆕 Natural Language Search:**
Just type what you're looking for:
• `tools for content creation`
• `video editing tools`
• `AI marketing tools`
• `design software`
• `productivity apps`

**How to use:**
1. Send `/start` or type `start` to see all available categories
2. Send the number of the category you want to explore
3. Browse through the AI tools in that category
4. Type `exit` when you're done

**Examples:**
• Send `/start` or type `start`
• Send `1` to see tools in the first category
• Type `tools for design` to find design tools
• Send `/search notion` to find Notion-related tools
• Type `exit` to exit the bot
• Send `/stats` to see statistics

**Features:**
• 🔍 Smart search functionality
• 🗣️ Natural language queries
• 📊 Real-time statistics
• 🎯 Organized categories
• 📱 Mobile-friendly interface
• 🚪 Graceful exit option

**Social Media:**
📸 Instagram: [Follow @aiwithteja](https://www.instagram.com/aiwithteja?igsh=MWE2dW93dWVseDBrdg==)
🎥 YouTube: [Subscribe to TechWith Teja](https://youtube.com/@techwith_teja?si=QSRQw2-r9en8hd9j)

Need help? Just send a message!
        """
        await update.message.reply_text(help_text, parse_mode='Markdown')
    
    async def error_handler(self, update: object, context: ContextTypes.DEFAULT_TYPE):
        """Log errors caused by updates"""
        logger.warning(f'Update {update} caused error {context.error}')
        
        # Send error message to user if possible
        if update and hasattr(update, 'message') and update.message:
            await update.message.reply_text(
                "❌ An error occurred while processing your request. Please try again later.\n\n"
                "💡 **Quick commands:**\n"
                "• Type 'start' to return to main menu\n"
                "• Type 'exit' to exit the bot"
            )

def main():
    """Main function to run the bot"""
    if BOT_TOKEN == 'YOUR_BOT_TOKEN_HERE':
        print("❌ Please set your bot token in the .env file or config.py")
        return
    
    # Create bot instance
    bot = AIToolsBotEnhanced()
    
    # Create application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", bot.start_command))
    application.add_handler(CommandHandler("help", bot.help_command))
    application.add_handler(CommandHandler("stats", bot.stats_command))
    application.add_handler(CommandHandler("search", bot.search_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, bot.handle_message))
    
    # Add error handler
    application.add_error_handler(bot.error_handler)
    
    # Run the bot
    print("🤖 AI Tools Board Bot is starting...")
    print(f"📁 Using JSON file: {JSON_FILE_PATH}")
    print(f"🔧 Total tools loaded: {len(bot.tools_data)}")
    print(f"📊 Categories available: {len(bot.purposes)}")
    print("✅ Bot is running... Press Ctrl+C to stop.")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! Bot is working!")

async def main():
    app = ApplicationBuilder().token("YOUR_BOT_TOKEN_HERE").build()
    app.add_handler(CommandHandler("start", start))
    await app.run_polling()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())