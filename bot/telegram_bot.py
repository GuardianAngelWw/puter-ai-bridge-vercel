import os
import logging
import requests
from telegram import Update, ForceReply
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Get token from environment variable
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
if not TELEGRAM_TOKEN:
    raise ValueError("TELEGRAM_TOKEN environment variable not set")

# CONFIGURE THESE VALUES
BRIDGE_URL = os.environ.get("BRIDGE_URL", "https://your-vercel-deployment-url.vercel.app")
SESSION_ID = os.environ.get("SESSION_ID", "your-session-id")

# Bridge API client
class PuterBridgeAPI:
    def __init__(self, bridge_url=None, session_id=None):
        self.bridge_url = bridge_url
        self.session_id = session_id
        self.connected = False
        
        # If both URL and session ID are provided on init, try to connect
        if self.bridge_url and self.session_id:
            success, _ = self.connect(self.bridge_url, self.session_id)
            if success:
                logger.info(f"Auto-connected to bridge at {self.bridge_url}")
        
    def connect(self, bridge_url, session_id):
        """Connect to a bridge session"""
        self.bridge_url = bridge_url
        self.session_id = session_id
            
        # Test the connection
        try:
            response = requests.post(
                f"{self.bridge_url}/api/connect",
                json={"sessionId": self.session_id}
            )
            
            if response.status_code == 200:
                self.connected = True
                return True, "Connected to Puter AI bridge"
            return False, f"Failed to connect: {response.text}"
        except Exception as e:
            return False, f"Connection error: {str(e)}"
        
    def get_status(self):
        """Get bridge connection status"""
        if not self.bridge_url:
            return False, "Bridge URL not configured"
            
        try:
            response = requests.get(f"{self.bridge_url}/api/status")
            if response.status_code == 200:
                return True, response.json()
            return False, f"Error: {response.status_code} - {response.text}"
        except Exception as e:
            return False, f"Status error: {str(e)}"
        
    def chat(self, prompt, options=None):
        """Send a chat request through the bridge"""
        if not self.connected:
            return False, "Not connected to bridge"
            
        try:
            response = requests.post(
                f"{self.bridge_url}/api/chat",
                json={
                    "prompt": prompt,
                    "options": options or {},
                    "sessionId": self.session_id
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('error'):
                    return False, f"API error: {result['error']}"
                if result.get('data') and result.get('success'):
                    return True, result['data']
                return True, result
            return False, f"Error: {response.status_code} - {response.text}"
            
        except Exception as e:
            return False, f"API Error: {str(e)}"
            
    def vision(self, prompt, image_url):
        """Send a vision request through the bridge"""
        if not self.connected:
            return False, "Not connected to bridge"
            
        try:
            response = requests.post(
                f"{self.bridge_url}/api/vision",
                json={
                    "prompt": prompt,
                    "imageURL": image_url,
                    "sessionId": self.session_id
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('error'):
                    return False, f"API error: {result['error']}"
                if result.get('data') and result.get('success'):
                    return True, result['data']
                return True, result
            return False, f"Error: {response.status_code} - {response.text}"
            
        except Exception as e:
            return False, f"Vision API Error: {str(e)}"

# Initialize bridge API with hardcoded values
bridge_api = PuterBridgeAPI(BRIDGE_URL, SESSION_ID)

# User sessions - automatically mark all users as connected since we have hardcoded credentials
user_sessions = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    user_id = update.effective_user.id
    
    # Auto-connect the user
    user_sessions[user_id] = {"connected": True}
    
    await update.message.reply_html(
        f"Hi {user.mention_html()}! I'm the Puter AI Telegram Bot.\n\n"
        f"I'm {'already connected' if bridge_api.connected else 'not connected'} to the Puter AI bridge.\n\n"
        f"You can use these commands:\n"
        f"/chat - Chat with AI\n"
        f"/vision - Analyze images (send image with caption)\n"
        f"/bridge_status - Check bridge connection status",
        reply_markup=ForceReply(selective=True),
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text(
        "Available commands:\n"
        "/start - Start the bot\n"
        "/help - Show this help message\n"
        "/connect_bridge <url> <session_id> - Connect to Puter AI bridge\n"
        "/bridge_status - Check bridge connection status\n"
        "/chat <message> - Chat with AI\n"
        "/vision - Analyze images (send image with caption)"
    )

async def connect_bridge(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Connect to Puter AI Bridge"""
    if not context.args or len(context.args) < 2:
        await update.message.reply_text(
            f"The bot is currently {'connected' if bridge_api.connected else 'not connected'} to:\n"
            f"Bridge URL: {bridge_api.bridge_url}\n"
            f"Session ID: {bridge_api.session_id}\n\n"
            f"To change, use: /connect_bridge <url> <session_id>"
        )
        return
    
    bridge_url = context.args[0]
    session_id = context.args[1]
    
    await update.message.reply_text("Connecting to bridge...")
    success, message = bridge_api.connect(bridge_url, session_id)
    
    if success:
        user_id = update.effective_user.id
        user_sessions[user_id] = {"connected": True}
    
    await update.message.reply_text(message)

async def bridge_status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Check bridge connection status"""
    if not bridge_api.connected:
        await update.message.reply_text(
            f"Not connected to bridge.\n"
            f"URL: {bridge_api.bridge_url}\n"
            f"Session ID: {bridge_api.session_id}"
        )
        return
        
    success, status = bridge_api.get_status()
    
    if success:
        status_text = "Connected to bridge\n"
        status_text += f"URL: {bridge_api.bridge_url}\n"
        status_text += f"Session ID: {bridge_api.session_id}"
        
        # Add additional status info if available
        if isinstance(status, dict):
            if 'status' in status:
                status_text += f"\nBridge status: {status['status']}"
            if 'stats' in status:
                stats = status['stats']
                status_text += f"\nActive sessions: {stats.get('authenticatedSessions', 'N/A')}"
                
        await update.message.reply_text(status_text)
    else:
        await update.message.reply_text(f"Error checking status: {status}")

def check_connection(user_id):
    """Check if user is connected to bridge"""
    if not bridge_api.connected:
        return False
    
    # If user isn't in sessions dict, add them automatically
    if user_id not in user_sessions:
        user_sessions[user_id] = {"connected": True}
        
    return user_sessions[user_id].get("connected", False)

async def chat_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Chat with Puter AI"""
    user_id = update.effective_user.id
    
    if not check_connection(user_id):
        await update.message.reply_text(
            "Not connected to Puter AI bridge. Try restarting the bot or checking the bridge status."
        )
        return
    
    if not context.args:
        await update.message.reply_text("Please provide a message to chat about: /chat your message here")
        return
    
    prompt = " ".join(context.args)
    await update.message.reply_text("Processing your request...")
    
    success, response = bridge_api.chat(prompt)
    
    if success:
        # Format response based on actual API structure
        if isinstance(response, dict) and "text" in response:
            await update.message.reply_text(response["text"])
        elif isinstance(response, dict) and "message" in response and "content" in response["message"]:
            await update.message.reply_text(response["message"]["content"])
        else:
            await update.message.reply_text(str(response))
    else:
        await update.message.reply_text(f"Error: {response}")

async def vision_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle image analysis with Puter Vision API"""
    user_id = update.effective_user.id
    
    if not check_connection(user_id):
        await update.message.reply_text(
            "Not connected to Puter AI bridge. Try restarting the bot or checking the bridge status."
        )
        return
    
    if not update.message.photo:
        await update.message.reply_text("Please send an image with a caption for analysis")
        return
    
    # Get the largest photo
    photo = update.message.photo[-1]
    prompt = update.message.caption or "Describe this image"
    
    # Get image file
    file = await context.bot.get_file(photo.file_id)
    image_url = file.file_path  # Telegram provides a URL to download the file
    
    await update.message.reply_text("Analyzing image...")
    
    success, response = bridge_api.vision(prompt, image_url)
    
    if success:
        # Format response based on actual API structure
        if isinstance(response, dict) and "text" in response:
            await update.message.reply_text(response["text"])
        elif isinstance(response, dict) and "message" in response and "content" in response["message"]:
            await update.message.reply_text(response["message"]["content"])
        else:
            await update.message.reply_text(str(response))
    else:
        await update.message.reply_text(f"Error: {response}")

async def text_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle regular text messages as chat"""
    user_id = update.effective_user.id
    
    if not check_connection(user_id):
        await update.message.reply_text(
            "Not connected to Puter AI bridge. Try restarting the bot or checking the bridge status."
        )
        return
    
    prompt = update.message.text
    await update.message.reply_text("Processing your request...")
    
    success, response = bridge_api.chat(prompt)
    
    if success:
        # Format response based on actual API structure
        if isinstance(response, dict) and "text" in response:
            await update.message.reply_text(response["text"])
        elif isinstance(response, dict) and "message" in response and "content" in response["message"]:
            await update.message.reply_text(response["message"]["content"])
        else:
            await update.message.reply_text(str(response))
    else:
        await update.message.reply_text(f"Error: {response}")

def main() -> None:
    """Start the bot."""
    # Create the Application
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # Command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("connect_bridge", connect_bridge))
    application.add_handler(CommandHandler("bridge_status", bridge_status))
    application.add_handler(CommandHandler("chat", chat_command))
    
    # Message handlers
    application.add_handler(MessageHandler(filters.PHOTO & ~filters.COMMAND, vision_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_message_handler))

    # Start the Bot
    application.run_polling()

if __name__ == "__main__":
    main()