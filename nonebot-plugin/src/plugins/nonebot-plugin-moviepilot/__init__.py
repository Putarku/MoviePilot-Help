from nonebot.plugin import PluginMetadata

from . import _version

__version__ = _version.__version__


from .config import Config
from .command import *

__plugin_meta__ = PluginMetadata(
    name=f"MoviePilot订阅服务插件\n版本 - {__version__}\n",
    description="MoviePilot订阅查询更新插件\n",
    usage="",

    type="application",

    homepage="",

    config=Config,

    supported_adapters={"~onebot.v11"},
)

