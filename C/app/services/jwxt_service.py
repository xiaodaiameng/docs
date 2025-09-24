from typing import Optional, Tuple

import httpx

from app.core.config import config
from app.core.logger import logger
from app.schemas.jwxt import (
    JWXTExternalLoginResponse,
    JWXTExternalUserInfoResponse,
    JWXTUserInfoAPIResponse,
)
from app.services.password_encryption import decrypt_jwxt_password


class JWXTExternalService:
    """外部教务系统API服务"""

    # 教务系统API基础URL
    BASE_URL = "http://jwxt.gduf.edu.cn/app.do"

    def __init__(self):
        self.timeout = config.jwxt_api_timeout  # 使用配置中的超时时间

    async def authenticate_user(self, student_id: str, password: str) -> JWXTExternalLoginResponse:
        """
        调用外部教务系统登录接口

        Args:
            student_id: 学号
            password: 密码

        Returns:
            登录响应结果
        """
        try:
            url = f"{self.BASE_URL}?method=authUser&xh={student_id}&pwd={password}"

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url)
                response.raise_for_status()

                # 假设返回JSON格式，根据实际API调整
                data = response.json() if response.content else {}

                # 根据实际API响应格式调整
                if "token" in data and data.get("success", False):
                    return JWXTExternalLoginResponse(token=data["token"], success=True, message="登录成功")
                else:
                    return JWXTExternalLoginResponse(token=None, success=False, message=data.get("message", "登录失败"))

        except httpx.TimeoutException:
            logger.error(f"JWXT login timeout for student_id: {student_id}")
            return JWXTExternalLoginResponse(token=None, success=False, message="请求超时，请稍后重试")
        except httpx.HTTPStatusError as e:
            logger.error(f"JWXT login HTTP error for student_id: {student_id}, error: {e}")
            return JWXTExternalLoginResponse(token=None, success=False, message=f"网络错误: {e.response.status_code}")
        except Exception as e:
            logger.error(f"JWXT login error for student_id: {student_id}, error: {e}")
            return JWXTExternalLoginResponse(token=None, success=False, message="系统错误，请联系管理员")

    async def get_user_info(self, student_id: str, token: str) -> JWXTExternalUserInfoResponse:
        """
        调用外部教务系统获取用户信息接口

        Args:
            student_id: 学号
            token: 登录token (如果需要的话)

        Returns:
            用户信息响应结果
        """
        try:
            params = {"method": "getUserInfo", "xh": student_id}
            headers = {"tokens": token}

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(self.BASE_URL, headers=headers, params=params)
                response.raise_for_status()

                data = response.json()

                return JWXTExternalUserInfoResponse(success=True, message="获取用户信息成功", data=data)

        except httpx.TimeoutException:
            logger.error(f"JWXT get user info timeout for student_id: {student_id}")
            return JWXTExternalUserInfoResponse(success=False, message="请求超时，请稍后重试", data=None)
        except httpx.HTTPStatusError as e:
            logger.error(f"JWXT get user info HTTP error for student_id: {student_id}, error: {e}")
            return JWXTExternalUserInfoResponse(success=False, message=f"网络错误: {e.response.status_code}", data=None)
        except Exception as e:
            logger.error(f"JWXT get user info error for student_id: {student_id}, error: {e}")
            return JWXTExternalUserInfoResponse(success=False, message="系统错误，请联系管理员", data=None)

    async def validate_and_get_user_info(
        self, student_id: str, password: str
    ) -> Tuple[bool, Optional[JWXTUserInfoAPIResponse], str]:
        """
        验证账号密码并获取用户信息

        Args:
            student_id: 学号
            password: 密码

        Returns:
            (是否成功, 用户信息数据, 错误信息)
        """
        # 首先尝试登录获取token
        login_result = await self.authenticate_user(student_id, password)

        if not login_result.success:
            return False, None, login_result.message

        # 使用token获取用户信息
        user_info_result = await self.get_user_info(student_id, login_result.token)  # type: ignore

        if not user_info_result.success:
            return False, None, user_info_result.message

        return True, user_info_result.data, "成功"

    async def sync_with_encrypted_password(
        self, student_id: str, encrypted_password: str
    ) -> Tuple[bool, Optional[JWXTUserInfoAPIResponse], str]:
        """
        使用加密密码同步用户信息

        Args:
            student_id: 学号
            encrypted_password: 加密的密码

        Returns:
            (是否成功, 用户信息数据, 错误信息)
        """
        # 解密密码
        password = decrypt_jwxt_password(encrypted_password)
        if not password:
            return False, None, "密码解密失败，请重新绑定账号"

        # 使用解密后的密码进行同步
        return await self.validate_and_get_user_info(student_id, password)


# 创建服务实例
jwxt_external_service = JWXTExternalService()
