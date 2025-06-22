"""
微信服务模块
处理微信小程序登录、用户信息获取等功能
"""

import json
import logging
from typing import Optional, Dict, Any
import httpx
from app.core.config import settings

logger = logging.getLogger(__name__)

class WechatService:
    """微信服务类"""
    
    def __init__(self):
        self.app_id = getattr(settings, 'WECHAT_APP_ID', 'your_app_id')
        self.app_secret = getattr(settings, 'WECHAT_APP_SECRET', 'your_app_secret')
        self.base_url = "https://api.weixin.qq.com"
    
    async def code_to_session(self, js_code: str) -> Optional[Dict[str, Any]]:
        """
        通过微信登录凭证code获取session_key和openid
        
        Args:
            js_code: 微信小程序wx.login()获取的code
            
        Returns:
            包含openid、session_key等信息的字典，失败返回None
        """
        url = f"{self.base_url}/sns/jscode2session"
        params = {
            'appid': self.app_id,
            'secret': self.app_secret,
            'js_code': js_code,
            'grant_type': 'authorization_code'
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params)
                data = response.json()
                
                if 'errcode' in data and data['errcode'] != 0:
                    logger.error(f"微信API错误: {data.get('errmsg', '未知错误')}")
                    return None
                
                logger.info(f"微信登录成功，openid: {data.get('openid', '')[:8]}***")
                return data
                
        except Exception as e:
            logger.error(f"调用微信API失败: {str(e)}")
            return None
    
    def decrypt_user_info(self, encrypted_data: str, iv: str, session_key: str) -> Optional[Dict[str, Any]]:
        """
        解密微信用户敏感数据
        
        Args:
            encrypted_data: 加密数据
            iv: 初始向量
            session_key: 会话密钥
            
        Returns:
            解密后的用户信息，失败返回None
        """
        try:
            from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
            from cryptography.hazmat.backends import default_backend
            import base64
            
            # Base64解码
            encrypted_data = base64.b64decode(encrypted_data)
            iv = base64.b64decode(iv)
            session_key = base64.b64decode(session_key)
            
            # AES解密
            cipher = Cipher(algorithms.AES(session_key), modes.CBC(iv), backend=default_backend())
            decryptor = cipher.decryptor()
            decrypted = decryptor.update(encrypted_data) + decryptor.finalize()
            
            # 去除PKCS7填充
            padding_length = decrypted[-1]
            decrypted = decrypted[:-padding_length]
            
            # 转换为JSON
            user_info = json.loads(decrypted.decode('utf-8'))
            
            logger.info(f"用户信息解密成功: {user_info.get('nickName', '')}")
            return user_info
            
        except Exception as e:
            logger.error(f"解密用户信息失败: {str(e)}")
            return None
    
    def generate_openid_mock(self, code: str) -> str:
        """
        生成模拟OpenID（开发模式使用）
        
        Args:
            code: 微信授权码
            
        Returns:
            模拟的OpenID
        """
        import hashlib
        
        # 使用code生成确定性的模拟openid（不使用时间戳，保证同一code生成同一openid）
        openid = "mock_" + hashlib.md5(code.encode()).hexdigest()[:24]
        
        logger.info(f"生成模拟OpenID: {openid}")
        return openid
    
    async def get_user_info_mock(self, code: str) -> Dict[str, Any]:
        """
        获取模拟用户信息（开发模式使用）
        
        Args:
            code: 微信授权码
            
        Returns:
            模拟的用户信息
        """
        openid = self.generate_openid_mock(code)
        
        return {
            'openid': openid,
            'session_key': 'mock_session_key_' + openid[:8],
            'nickname': '微信用户',
            'avatar_url': '/assets/test/man.png',
            'gender': 1,
            'city': '深圳',
            'province': '广东',
            'country': '中国'
        }
    
    async def verify_session_key(self, openid: str, session_key: str) -> bool:
        """
        验证session_key是否有效
        
        Args:
            openid: 微信用户OpenID
            session_key: 会话密钥
            
        Returns:
            验证结果
        """
        # 在生产环境中，可以通过调用微信API验证session_key
        # 这里简化处理，只检查是否为空
        return bool(openid and session_key)
    
    def extract_user_info(self, wechat_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        从微信数据中提取标准化的用户信息
        
        Args:
            wechat_data: 微信API返回的数据
            
        Returns:
            标准化的用户信息
        """
        return {
            'openid': wechat_data.get('openid', ''),
            'nickname': wechat_data.get('nickName', wechat_data.get('nickname', '')),
            'avatar_url': wechat_data.get('avatarUrl', wechat_data.get('avatar_url', '')),
            'gender': wechat_data.get('gender', 0),
            'city': wechat_data.get('city', ''),
            'province': wechat_data.get('province', ''),
            'country': wechat_data.get('country', '')
        }
    
    async def process_login_code(self, code: str, use_mock: bool = True) -> Optional[Dict[str, Any]]:
        """
        处理微信登录代码，获取用户基本信息
        
        Args:
            code: 微信授权码
            use_mock: 是否使用模拟数据（开发模式）
            
        Returns:
            处理后的用户信息
        """
        if use_mock or not all([self.app_id, self.app_secret]) or \
           self.app_id == 'your_app_id':
            # 开发模式或配置未完成，使用模拟数据
            logger.info("使用模拟微信数据")
            return await self.get_user_info_mock(code)
        else:
            # 生产模式，调用真实微信API
            logger.info("调用真实微信API")
            return await self.code_to_session(code)

# 创建全局微信服务实例
wechat_service = WechatService() 