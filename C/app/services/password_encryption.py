import base64
from typing import Optional

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from app.core.config import config
from app.core.logger import logger


class PasswordEncryptionService:
    """密码加密解密服务

    使用AES加密算法，基于环境变量中的密钥进行可逆加密
    确保即使数据库泄露，没有密钥也无法解密密码
    """

    def __init__(self):
        self._init_encryption()

    def _init_encryption(self):
        """初始化加密器"""
        try:
            # 从环境变量获取密钥，如果不存在则生成一个
            encryption_key = config.jwxt_encryption_key

            if not encryption_key:
                # 生成一个新的密钥并警告
                logger.warning(
                    "JWXT_ENCRYPTION_KEY not found in config, generating a new one. "
                    "Please add it to your .env file for production use."
                )
                encryption_key = Fernet.generate_key().decode()
                logger.warning(f"Generated encryption key: {encryption_key}")

            # 如果密钥是字符串，确保它是有效的Fernet密钥格式
            if isinstance(encryption_key, str):
                try:
                    # 尝试直接使用
                    self._fernet = Fernet(encryption_key.encode())
                except Exception:
                    # 如果不是有效的Fernet密钥，则从密码生成
                    self._fernet = self._generate_fernet_from_password(encryption_key)
            else:
                self._fernet = Fernet(encryption_key)

        except Exception as e:
            logger.error(f"Failed to initialize encryption: {e}")
            # 使用默认密钥（仅用于开发环境）
            default_key = "dev_key_not_secure_for_production_use_only"
            self._fernet = self._generate_fernet_from_password(default_key)

    def _generate_fernet_from_password(self, password: str) -> Fernet:
        """从密码生成Fernet密钥"""
        password_bytes = password.encode()
        salt = b"stable_salt_for_jwxt"  # 在生产环境中应该使用随机salt
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password_bytes))
        return Fernet(key)

    def encrypt_password(self, password: str) -> str:
        """加密密码

        Args:
            password: 明文密码

        Returns:
            加密后的密码字符串
        """
        try:
            encrypted_bytes = self._fernet.encrypt(password.encode())
            return base64.urlsafe_b64encode(encrypted_bytes).decode()
        except Exception as e:
            logger.error(f"Failed to encrypt password: {e}")
            raise

    def decrypt_password(self, encrypted_password: str) -> Optional[str]:
        """解密密码

        Args:
            encrypted_password: 加密的密码字符串

        Returns:
            解密后的明文密码，失败返回None
        """
        try:
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_password.encode())
            decrypted_bytes = self._fernet.decrypt(encrypted_bytes)
            return decrypted_bytes.decode()
        except Exception as e:
            logger.error(f"Failed to decrypt password: {e}")
            return None

    def is_encryption_available(self) -> bool:
        """检查加密服务是否可用"""
        return self._fernet is not None


# 创建全局实例
password_encryption_service = PasswordEncryptionService()


def encrypt_jwxt_password(password: str) -> str:
    """加密教务系统密码的便捷函数"""
    return password_encryption_service.encrypt_password(password)


def decrypt_jwxt_password(encrypted_password: str) -> Optional[str]:
    """解密教务系统密码的便捷函数"""
    return password_encryption_service.decrypt_password(encrypted_password)


def is_jwxt_encryption_available() -> bool:
    """检查JWXT密码加密是否可用"""
    return password_encryption_service.is_encryption_available()
