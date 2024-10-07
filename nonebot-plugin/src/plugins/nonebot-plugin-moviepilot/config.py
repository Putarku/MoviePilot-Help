from typing import List

import nonebot
from nonebot import get_plugin_config
from pydantic import BaseModel


__all__ = ["Config", "plugin_config"]

from pydantic_core import Url

_driver = nonebot.get_driver()


class Config(BaseModel):
    """插件设置"""

    """movie pilot连接设置"""
    mp_url: str = "http://localhost:3001"
    mp_token: str = "moviepilot"
    mp_users: List[int] | None = []
    mp_groups: List[int] | None = []
    mp_username: str = "admin"
    mp_password: str | int


plugin_config = get_plugin_config(Config)
