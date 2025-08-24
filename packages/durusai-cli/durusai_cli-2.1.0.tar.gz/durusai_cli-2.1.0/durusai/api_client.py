"""
REST API клиент для DurusAI
"""
import httpx
import asyncio
from typing import Optional, Dict, Any, AsyncIterator
import json
from datetime import datetime, timedelta
import time

from .config import Config
from .exceptions import (
    DurusAIAPIError, 
    AuthenticationError, 
    NetworkError, 
    ServerError,
    ValidationError
)


class DurusAIClient:
    """REST API клиент для взаимодействия с DurusAI backend"""
    
    def __init__(self, config: Optional[Config] = None):
        self.config = config or Config()
        self.base_url = self.config.get_api_endpoint().rstrip('/')
        self.timeout = self.config.get("settings.timeout", 30)
        self.retry_count = self.config.get("settings.retry_count", 3)
        
        # HTTP клиент с настройками
        self.client = httpx.Client(
            base_url=self.base_url,
            timeout=self.timeout,
            headers={
                "User-Agent": "DurusAI-CLI/1.0.0",
                "Accept": "application/json",
                "Content-Type": "application/json"
            }
        )
        
        self._access_token: Optional[str] = None
        self._refresh_token: Optional[str] = None
        self._token_expires_at: Optional[datetime] = None
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
    
    def close(self):
        """Закрыть HTTP клиент"""
        self.client.close()
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> httpx.Response:
        """Выполнить HTTP запрос с повторами"""
        # Для всех API v1 эндпоинтов не добавляем /cli префикс
        if endpoint.startswith("/api/v1/"):
            url = endpoint
        else:
            url = f"/cli{endpoint}" if not endpoint.startswith("/cli") else endpoint
        
        for attempt in range(self.retry_count):
            try:
                response = self.client.request(method, url, **kwargs)
                
                # Проверяем статус ответа
                if response.status_code < 400:
                    return response
                elif response.status_code == 401:
                    raise AuthenticationError("Неверные учетные данные или токен истек")
                elif response.status_code == 422:
                    error_detail = "Неверный формат данных"
                    try:
                        error_data = response.json()
                        if "detail" in error_data:
                            error_detail = str(error_data["detail"])
                    except:
                        pass
                    raise ValidationError(error_detail)
                elif response.status_code >= 500:
                    raise ServerError(f"Ошибка сервера: {response.status_code}")
                else:
                    raise DurusAIAPIError(f"HTTP {response.status_code}: {response.text}")
                    
            except httpx.RequestError as e:
                if attempt == self.retry_count - 1:
                    raise NetworkError(f"Ошибка сети: {e}")
                
                # Экспоненциальная задержка между повторами
                time.sleep(2 ** attempt)
        
        raise NetworkError("Превышено количество попыток подключения")
    
    def _set_auth_header(self):
        """Установить заголовок авторизации"""
        if self._access_token:
            self.client.headers["Authorization"] = f"Bearer {self._access_token}"
        elif "Authorization" in self.client.headers:
            del self.client.headers["Authorization"]
    
    def set_tokens(self, access_token: str, refresh_token: Optional[str] = None, expires_in: int = 3600):
        """Установить токены аутентификации"""
        self._access_token = access_token
        self._refresh_token = refresh_token
        self._token_expires_at = datetime.utcnow() + timedelta(seconds=expires_in - 60)  # 60 секунд буфера
        self._set_auth_header()
    
    def clear_tokens(self):
        """Очистить токены"""
        self._access_token = None
        self._refresh_token = None
        self._token_expires_at = None
        if "Authorization" in self.client.headers:
            del self.client.headers["Authorization"]
    
    def _is_token_expired(self) -> bool:
        """Проверить истек ли токен"""
        if not self._token_expires_at:
            return True
        return datetime.utcnow() >= self._token_expires_at
    
    async def _refresh_token_if_needed(self):
        """Обновить токен если необходимо"""
        if self._is_token_expired() and self._refresh_token:
            try:
                await self.refresh_token(self._refresh_token)
            except Exception:
                # Если обновление не удалось, очищаем токены
                self.clear_tokens()
    
    # API методы
    
    async def login(self, username: str, password: str) -> Dict[str, Any]:
        """Аутентификация пользователя"""
        data = {
            "username": username,
            "password": password
        }
        
        response = self._make_request("POST", "/api/v1/auth/login", json=data)
        result = response.json()
        
        # Сохраняем токены
        self.set_tokens(
            access_token=result["access_token"],
            refresh_token=result.get("refresh_token"),
            expires_in=result.get("expires_in", 3600)
        )
        
        return result
    
    async def refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        """Обновление access токена"""
        data = {"refresh_token": refresh_token}
        
        response = self._make_request("POST", "/api/v1/auth/refresh", json=data)
        result = response.json()
        
        # Обновляем токен
        self.set_tokens(
            access_token=result["access_token"],
            refresh_token=refresh_token,  # refresh token остается тем же
            expires_in=result.get("expires_in", 3600)
        )
        
        return result
    
    def get_user_info_sync(self) -> Dict[str, Any]:
        """Синхронное получение информации о текущем пользователе"""
        response = self._make_request("GET", "/api/v1/auth/me")
        return response.json()
    
    async def get_user_info(self) -> Dict[str, Any]:
        """Получить информацию о текущем пользователе"""
        return self.get_user_info_sync()
    
    def query_sync(self, prompt: str, model: Optional[str] = None, stream: bool = False, 
                   context: Optional[Dict[str, Any]] = None, max_tokens: Optional[int] = None,
                   temperature: Optional[float] = None) -> Dict[str, Any]:
        """Синхронная отправка запроса к AI"""
        data = {
            "prompt": prompt,
            "stream": stream
        }
        
        if model:
            data["model"] = model
        if context:
            data["context"] = context
        if max_tokens:
            data["max_tokens"] = max_tokens
        if temperature is not None:
            data["temperature"] = temperature
        
        response = self._make_request("POST", "/api/v1/cli/query", json=data)
        return response.json()
    
    async def query(self, prompt: str, model: Optional[str] = None, stream: bool = False, 
                   context: Optional[Dict[str, Any]] = None, max_tokens: Optional[int] = None,
                   temperature: Optional[float] = None) -> Dict[str, Any]:
        """Асинхронный запрос к AI (обертка над sync версией)"""
        return self.query_sync(prompt, model, stream, context, max_tokens, temperature)
    
    async def stream_query(self, prompt: str, model: Optional[str] = None,
                          context: Optional[Dict[str, Any]] = None,
                          max_tokens: Optional[int] = None,
                          temperature: Optional[float] = None) -> AsyncIterator[str]:
        """Отправить streaming запрос к AI"""
        await self._refresh_token_if_needed()
        
        data = {
            "prompt": prompt,
            "stream": True
        }
        
        if model:
            data["model"] = model
        if context:
            data["context"] = context
        if max_tokens:
            data["max_tokens"] = max_tokens
        if temperature is not None:
            data["temperature"] = temperature
        
        with self.client.stream("POST", "/cli/api/v1/cli/stream", json=data) as response:
            if response.status_code != 200:
                raise DurusAIAPIError(f"Stream error: {response.status_code}")
            
            for line in response.iter_lines():
                if line.startswith("data: "):
                    try:
                        data_str = line[6:]  # Убираем "data: "
                        data = json.loads(data_str)
                        
                        if data.get("done"):
                            break
                        elif "content" in data:
                            yield data["content"]
                        elif "error" in data:
                            raise DurusAIAPIError(data["error"])
                            
                    except json.JSONDecodeError:
                        continue
    
    def get_models_sync(self) -> Dict[str, Any]:
        """Синхронное получение списка доступных моделей"""
        response = self._make_request("GET", "/api/v1/cli/models")
        return response.json()
    
    async def get_models(self) -> Dict[str, Any]:
        """Получить список доступных моделей"""
        return self.get_models_sync()
    
    def get_stats_sync(self) -> Dict[str, Any]:
        """Синхронное получение статистики использования"""
        response = self._make_request("GET", "/api/v1/cli/stats")
        return response.json()
    
    async def get_stats(self) -> Dict[str, Any]:
        """Получить статистику использования"""
        return self.get_stats_sync()
    
    def get_history_sync(self, page: int = 1, per_page: int = 20) -> Dict[str, Any]:
        """Синхронное получение истории запросов"""
        params = {"page": page, "per_page": per_page}
        response = self._make_request("GET", "/api/v1/cli/history", params=params)
        return response.json()
    
    async def get_history(self, page: int = 1, per_page: int = 20) -> Dict[str, Any]:
        """Получить историю запросов"""
        return self.get_history_sync(page, per_page)
    
    def health_check_sync(self) -> Dict[str, Any]:
        """Синхронная проверка здоровья API"""
        response = self._make_request("GET", "/api/v1/health")
        return response.json()
    
    async def health_check(self) -> Dict[str, Any]:
        """Проверить здоровье API"""
        return self.health_check_sync()


# Синхронная версия для удобства использования в CLI
class SyncDurusAIClient:
    """Синхронная обертка над асинхронным клиентом"""
    
    def __init__(self, config: Optional[Config] = None):
        self.client = DurusAIClient(config)
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.client.close()
    
    def _run_async(self, coro):
        """Запустить асинхронную операцию"""
        try:
            # Пытаемся получить существующий event loop
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # Если loop уже запущен, создаем новый task
                # Это не идеально, но работает для большинства случаев
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, coro)
                    return future.result()
            else:
                return loop.run_until_complete(coro)
        except RuntimeError:
            # Нет event loop, создаем новый
            return asyncio.run(coro)
    
    def login(self, username: str, password: str) -> Dict[str, Any]:
        """Синхронная версия login"""
        data = {
            "username": username,
            "password": password
        }
        
        response = self.client._make_request("POST", "/api/v1/auth/login", json=data)
        result = response.json()
        
        # Сохраняем токены
        self.client.set_tokens(
            access_token=result["access_token"],
            refresh_token=result.get("refresh_token"),
            expires_in=result.get("expires_in", 3600)
        )
        
        return result
    
    def get_user_info(self) -> Dict[str, Any]:
        return self.client.get_user_info_sync()
    
    def query(self, prompt: str, **kwargs) -> Dict[str, Any]:
        return self.client.query_sync(prompt, **kwargs)
    
    def get_models(self) -> Dict[str, Any]:
        return self.client.get_models_sync()
    
    def get_stats(self) -> Dict[str, Any]:
        return self.client.get_stats_sync()
    
    def get_history(self, page: int = 1, per_page: int = 20) -> Dict[str, Any]:
        return self.client.get_history_sync(page, per_page)
    
    def health_check(self) -> Dict[str, Any]:
        return self.client.health_check_sync()
    
    def set_tokens(self, access_token: str, refresh_token: Optional[str] = None, expires_in: int = 3600):
        self.client.set_tokens(access_token, refresh_token, expires_in)
    
    def clear_tokens(self):
        self.client.clear_tokens()