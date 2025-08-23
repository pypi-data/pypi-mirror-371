from importlib import metadata
from typing import Literal

from nonebot import get_plugin_config
from pydantic import BaseModel


class AmritaConfig(BaseModel):
    log_dir: str = "logs"
    admin_group: int
    disabled_builtin_plugins: list[Literal["chat", "manager", "perm", "menu"]] = []
    amrita_log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = (
        "WARNING"
    )
    public_group: int = 0  # Bot对外展示公开群
    bot_name: str = "Amrita"
    rate_limit: int = 5  # Bot请求速率限制(间隔秒)


def get_amrita_config() -> AmritaConfig:
    return get_plugin_config(AmritaConfig)


def get_amrita_version() -> str:
    version = "unknown"
    try:
        version = metadata.version("amrita")
    except metadata.PackageNotFoundError:
        pass
    return version
