import os
import telebot
from PIL import Image, ImageEnhance
from flask import Flask, request

TOKEN = "8949947641:AAGG-NjBDzFnxDKAlKx8rYZ_xIaVvdlB_Kk"
APP_URL = "https://image-enhancer-bot-1.onrender.com"
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
    bot.reply_to(message, "Hi! 👋 Send me a photo, and I'll enhance its sharpness, contrast, and color for you!")

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    try:
        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        image_path = "temp_input.jpg"
        with open(image_path, 'wb') as new_file:
            new_file.write(downloaded_file)
        
        img = Image.open(image_path)
        
        # Enhancements
        enhancer = ImageEnhance.Sharpness(img)
        img = enhancer.enhance(1.8)
        
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(1.2)
        
        enhancer = ImageEnhance.Color(img)
        img = enhancer.enhance(1.15)
        
        enhanced_path = "enhanced_output.jpg"
        img.save(enhanced_path, "JPEG", quality=95)
        
        with open(enhanced_path, 'rb') as photo:
            bot.send_photo(message.chat.id, photo, caption="✨ Here is your enhanced image!")
        
        os.remove(image_path)
        os.remove(enhanced_path)
        
    except Exception as e:
        print(e)
        bot.reply_to(message, "An error occurred while enhancing the image!")

if __name__ == "__main__":
    bot.remove_webhook()
    bot.set_webhook(url=APP_URL + '/' + TOKEN)
    port = int(os.environ.get("PORT", 10000))
    server.run(host="0.0.0.0", port=port)
