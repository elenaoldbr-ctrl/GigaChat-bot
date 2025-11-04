import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # GigaChat переменные
    GIGACHAT_API_KEY = os.getenv('GIGACHAT_API_KEY')
    
    # VK переменные
    VK_GROUP_TOKEN = os.getenv('VK_GROUP_TOKEN')
    VK_GROUP_ID = os.getenv('VK_GROUP_ID')
    API_VERSION = '5.131'
    
    @classmethod
    def validate(cls):
        required = {
            'GIGACHAT_API_KEY': cls.GIGACHAT_API_KEY,
            'VK_GROUP_TOKEN': cls.VK_GROUP_TOKEN,
            'VK_GROUP_ID': cls.VK_GROUP_ID
        }
        
        missing = [name for name, value in required.items() if not value]
        if missing:
            raise ValueError(f"Missing environment variables: {', '.join(missing)}")

Config.validate()