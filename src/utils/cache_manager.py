import redis
from typing import Any, Optional, Dict
import json
import logging
from datetime import timedelta

class CacheManager:
    """Manage caching for fraud detection system."""
    
    def __init__(self, redis_config: Dict[str, Any]):
        """Initialize cache manager.
        
        Args:
            redis_config (Dict[str, Any]): Redis configuration
        """
        self.redis_client = redis.Redis(
            host=redis_config['host'],
            port=redis_config['port'],
            db=redis_config.get('db', 0),
            password=redis_config.get('password')
        )
        self.logger = logging.getLogger(__name__)
        
    def get_cached_prediction(self, transaction_key: str) -> Optional[Dict[str, Any]]:
        """Get cached prediction for a transaction.
        
        Args:
            transaction_key (str): Transaction identifier
            
        Returns:
            Optional[Dict[str, Any]]: Cached prediction if exists
        """
        try:
            cached_data = self.redis_client.get(f"pred:{transaction_key}")
            if cached_data:
                return json.loads(cached_data)
            return None
        except Exception as e:
            self.logger.error(f"Error getting cached prediction: {str(e)}")
            return None
    
    def cache_prediction(self, transaction_key: str, prediction: Dict[str, Any],
                        expire_in: int = 3600):
        """Cache prediction results.
        
        Args:
            transaction_key (str): Transaction identifier
            prediction (Dict[str, Any]): Prediction results
            expire_in (int): Cache expiration time in seconds
        """
        try:
            self.redis_client.setex(
                f"pred:{transaction_key}",
                expire_in,
                json.dumps(prediction)
            )
        except Exception as e:
            self.logger.error(f"Error caching prediction: {str(e)}")
    
    def get_user_profile(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get cached user profile.
        
        Args:
            user_id (int): User identifier
            
        Returns:
            Optional[Dict[str, Any]]: Cached user profile if exists
        """
        try:
            cached_data = self.redis_client.get(f"user:{user_id}")
            if cached_data:
                return json.loads(cached_data)
            return None
        except Exception as e:
            self.logger.error(f"Error getting user profile: {str(e)}")
            return None
    
    def cache_user_profile(self, user_id: int, profile: Dict[str, Any],
                          expire_in: int = 86400):
        """Cache user profile data.
        
        Args:
            user_id (int): User identifier
            profile (Dict[str, Any]): User profile data
            expire_in (int): Cache expiration time in seconds
        """
        try:
            self.redis_client.setex(
                f"user:{user_id}",
                expire_in,
                json.dumps(profile)
            )
        except Exception as e:
            self.logger.error(f"Error caching user profile: {str(e)}")