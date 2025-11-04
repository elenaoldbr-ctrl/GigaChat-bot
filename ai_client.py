def get_access_token(self):
    """Получение access token для GigaChat API с Basic авторизацией"""
    try:
        # Для GigaChat API ключ уже в правильном формате для Basic auth
        credentials = self.api_key.strip()
        
        auth_headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
            "RqUID": "6f0b1291-c7f3-43c3-bb82-2cae6db6f3b2",
            "Authorization": f"Basic {credentials}"
        }
        auth_data = "scope=GIGACHAT_API_PERS"
        
        logger.info("Requesting GigaChat access token...")
        response = requests.post(
            self.auth_url,
            headers=auth_headers,
            data=auth_data,
            timeout=30,
            verify=False
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
