from vk_handler import VKBot
import os
import logging
import threading
from flask import Flask

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

app = Flask(__name__)

@app.route('/')
def home():
    return "🤖 VK Bot with GigaChat is running!"

@app.route('/health')
def health():
    return "OK"

def run_bot():
    try:
        logging.info("Starting VK Bot...")
        bot = VKBot()
        bot.run()
    except Exception as e:
        logging.error(f"Bot error: {e}")

if __name__ == "__main__":
    # Запускаем бот в отдельном потоке
    bot_thread = threading.Thread(target=run_bot)
    bot_thread.daemon = True
    bot_thread.start()
    
    # Запускаем Flask сервер для Render
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)