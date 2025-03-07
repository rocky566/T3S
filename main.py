import os
import json
import logging
from fbchat import Client
from fbchat.models import Message, ThreadType
from config import ADMIN_UID, PREFIX, BOT_NAME, APPSTATE_FILE, LOG_FILE

# Set up logging
logging.basicConfig(filename=LOG_FILE, level=logging.INFO)
logger = logging.getLogger()

# Function to generate appstate.json if it doesn't exist or is invalid
def generate_appstate():
    email = "mowolow638@chansd.com"  # Replace with your Facebook email
    password = "smart chora sahil khan"  # Replace with your Facebook password
    
    client = Client(email, password)
    with open(APPSTATE_FILE, "w") as f:
        json.dump(client.getSession(), f)
    
    logger.info(f"Session cookies saved to {APPSTATE_FILE}")
    client.logout()

# Check if appstate.json exists or is invalid
if not os.path.exists(APPSTATE_FILE):
    logger.warning(f"{APPSTATE_FILE} not found. Generating a new one...")
    generate_appstate()

# Load appstate.json
try:
    with open(APPSTATE_FILE, "r") as f:
        appstate = json.load(f)
except Exception as e:
    logger.error(f"[ERROR]: Failed to load {APPSTATE_FILE}: {e}. Generating a new one...")
    generate_appstate()
    with open(APPSTATE_FILE, "r") as f:
        appstate = json.load(f)

# Custom Client class to handle session cookies login
class SessionClient(Client):
    def __init__(self, session_cookies):
        # Pass cookies to Client class, bypassing the need for email and password
        self.session_cookies = session_cookies
        super().__init__(session_cookies=session_cookies)

# Initialize client with session cookies
try:
    client = SessionClient(session_cookies=appstate)
    logger.info(f"[{BOT_NAME}]: Logged in successfully as {client.uid}!")
except Exception as e:
    logger.error(f"[ERROR]: Failed to log in using session cookies: {e}")
    raise

# Message Listener
class Bot(SessionClient):
    def onMessage(self, author_id, message_object, thread_id, thread_type, **kwargs):
        # Ignore bot's own messages
        if author_id == self.uid:
            return

        message_text = message_object.text or ""
        logger.info(f"[MESSAGE]: Received from {author_id}: {message_text}")

        # Handle Commands
        if message_text.startswith(PREFIX):  # Commands prefixed with "!"
            command = message_text[len(PREFIX):].strip().split()[0]  # Get the command
            if author_id == ADMIN_UID:
                if command == "hello":
                    self.send(Message(text="Hello, Admin!"), thread_id=thread_id, thread_type=thread_type)
                elif command == "stop":
                    self.send(Message(text="Stopping the bot..."), thread_id=thread_id, thread_type=thread_type)
                    logger.info(f"[{BOT_NAME}]: Stopping...")
                    self.logout()
                else:
                    self.send(Message(text=f"Unknown command: {command}"), thread_id=thread_id, thread_type=thread_type)
            else:
                self.send(Message(text="You are not authorized to use commands!"), thread_id=thread_id, thread_type=thread_type)

# Start the bot
if __name__ == "__main__":
    bot = Bot(session_cookies=appstate)
    logger.info(f"[{BOT_NAME}]: Bot is now running!")

    try:
        bot.listen()  # Start listening to messages
    except KeyboardInterrupt:
        logger.info(f"[{BOT_NAME}]: Bot stopped by user.")
        bot.logout()
    except Exception as e:
        logger.error(f"[ERROR]: An unexpected error occurred: {e}")
