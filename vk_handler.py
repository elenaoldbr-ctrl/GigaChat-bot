import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from ai_client import AIClient
from config import Config
import logging
import time

logger = logging.getLogger(__name__)

class VKBot:
    def __init__(self):
        logger.info("Initializing VK Bot...")
        self.vk_session = vk_api.VkApi(token=Config.VK_GROUP_TOKEN)
        self.longpoll = VkBotLongPoll(self.vk_session, Config.VK_GROUP_ID)
        self.vk = self.vk_session.get_api()
        self.ai_client = AIClient()
        self.user_sessions = {}
        logger.info("VK Bot initialized successfully")
    
    def send_message(self, user_id, message):
        try:
            if len(message) > 4096:
                chunks = [message[i:i+4096] for i in range(0, len(message), 4096)]
                for chunk in chunks:
                    self.vk.messages.send(
                        user_id=user_id,
                        message=chunk,
                        random_id=0
                    )
                    time.sleep(0.5)
            else:
                self.vk.messages.send(
                    user_id=user_id,
                    message=message,
                    random_id=0
                )
            logger.info(f"Message sent to user {user_id}")
        except Exception as e:
            logger.error(f"Error sending message: {e}")
    
    def get_user_session(self, user_id):
        if user_id not in self.user_sessions:
            self.user_sessions[user_id] = []
        return self.user_sessions[user_id]
    
    def handle_commands(self, text, user_id):
        text_lower = text.lower().strip()
        
        if text_lower in ['/start', 'start', 'начать']:
            return "🤖 Привет! Я AI помощник на основе GigaChat. Задавайте любые вопросы!"
        
        elif text_lower in ['/help', 'help', 'помощь']:
            return ("📚 Доступные команды:\n"
                   "/start - начать диалог\n"
                   "/help - помощь\n"
                   "/clear - очистить историю\n\n"
                   "Просто напишите ваш вопрос!")
        
        elif text_lower in ['/clear', 'clear', 'очистить']:
            self.user_sessions[user_id] = []
            return "🗑️ История диалога очищена!"
        
        return None
    
    def run(self):
        logger.info("Bot started listening for messages...")
        
        while True:
            try:
                for event in self.longpoll.listen():
                    if event.type == VkBotEventType.MESSAGE_NEW:
                        message = event.object.message
                        user_id = message['from_id']
                        text = message['text'].strip()
                        
                        if not text:
                            continue
                        
                        logger.info(f"Message from {user_id}: {text}")
                        
                        command_response = self.handle_commands(text, user_id)
                        if command_response:
                            self.send_message(user_id, command_response)
                            continue
                        
                        try:
                            self.vk.messages.setActivity(
                                user_id=user_id,
                                type='typing'
                            )
                        except:
                            pass
                        
                        user_history = self.get_user_session(user_id)
                        response = self.ai_client.send_message(text, user_history)
                        
                        user_history.extend([
                            {"role": "user", "content": text},
                            {"role": "assistant", "content": response}
                        ])
                        
                        if len(user_history) > 6:
                            user_history = user_history[-6:]
                        
                        self.send_message(user_id, response)
                        
            except Exception as e:
                logger.error(f"Error in main loop: {e}")
                time.sleep(10)
