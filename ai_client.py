import requests
import json
import base64
from config import Config
import logging

logger = logging.getLogger(__name__)

class AIClient:
    def __init__(self):
        self.api_key = Config.GIGACHAT_API_KEY
        self.base_url = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"
        self.auth_url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
        logger.info("GigaChat client initialized")
    
    def get_access_token(self):
        """Получение access token для GigaChat API с Basic авторизацией"""
        try:
            # Кодируем API ключ в Base64 для Basic авторизации
            credentials = base64.b64encode(f"{self.api_key}:".encode()).decode()
            
            auth_headers = {
                "Content-Type": "application/x-www-form-urlencoded",
                "Accept": "application/json",
                "RqUID": "6f0b1291-c7f3-43c3-bb82-2cae6db6f3b2",  # Любой уникальный ID
                "Authorization": f"Basic {credentials}"
            }
            auth_data = "scope=GIGACHAT_API_PERS"
            
            logger.info("Requesting GigaChat access token...")
            response = requests.post(
                self.auth_url,
                headers=auth_headers,
                data=auth_data,
                timeout=30,
                verify=False  # Для избежания SSL ошибок
            )
            
            logger.info(f"Auth response status: {response.status_code}")
            
            if response.status_code == 200:
                token_data = response.json()
                access_token = token_data.get('access_token')
                if access_token:
                    logger.info("Successfully received GigaChat access token")
                    return access_token
                else:
                    logger.error("No access_token in auth response")
                    return None
            else:
                logger.error(f"GigaChat auth error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"GigaChat token error: {e}")
            return None
    
    def send_message(self, message, conversation_history=None):
        if conversation_history is None:
            conversation_history = []
        
        # Получаем актуальный токен
        access_token = self.get_access_token()
        if not access_token:
            return "❌ Ошибка авторизации GigaChat. Проверьте API ключ."
        
        # Формируем заголовки для основного запроса
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json"
        }
        
        # Формируем сообщения для GigaChat
        messages = conversation_history + [
            {"role": "user", "content": message}
        ]
        
        payload = {
            "model": "GigaChat",  # Можно также использовать "GigaChat-Plus"
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 2000,
            "stream": False
        }
        
        try:
            logger.info(f"Sending request to GigaChat API (message length: {len(message)})")
            
            response = requests.post(
                self.base_url, 
                headers=headers, 
                json=payload,
                timeout=60,
                verify=False  # Для избежания SSL ошибок
            )
            
            logger.info(f"API response status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                reply = result['choices'][0]['message']['content']
                logger.info(f"Successfully received response (length: {len(reply)})")
                return reply
            elif response.status_code == 401:
                error_msg = "🔑 Ошибка авторизации. Токен устарел."
                logger.error("GigaChat token expired")
            elif response.status_code == 429:
                error_msg = "🚫 Слишком много запросов. Попробуйте позже."
                logger.error("GigaChat rate limit")
            else:
                error_msg = f"❌ Ошибка GigaChat API: {response.status_code}"
                logger.error(f"GigaChat API error: {response.status_code} - {response.text}")
                
        except requests.exceptions.Timeout:
            error_msg = "⏰ Время ожидания ответа истекло. Попробуйте еще раз."
            logger.error("GigaChat API timeout")
        except Exception as e:
            error_msg = f"⚠️ Ошибка соединения: {str(e)}"
            logger.error(f"GigaChat connection error: {e}")
        
        return error_msg