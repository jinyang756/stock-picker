import toml
import os
from typing import Dict, Any

class Config:
    _config: Dict[str, Any] = {}
    _loaded: bool = False

    @staticmethod
    def load_config(config_file: str = '.env.toml') -> None:
        """
        加载配置文件
        Args:
            config_file: 配置文件路径
        """
        if Config._loaded:
            return

        try:
            if os.path.exists(config_file):
                with open(config_file, 'r', encoding='utf-8') as f:
                    Config._config = toml.load(f)
                Config._loaded = True
                from utils.logger import Logger
                logger = Logger.get_logger("config")
                logger.info(f"成功加载配置文件: {config_file}")
            else:
                from utils.logger import Logger
                logger = Logger.get_logger("config")
                logger.warning(f"配置文件不存在: {config_file}")
        except Exception as e:
            from utils.logger import Logger
            logger = Logger.get_logger("config")
            logger.error(f"加载配置文件失败: {str(e)}")

    @staticmethod
    def get(key: str, default: Any = None) -> Any:
        """
        获取配置项
        Args:
            key: 配置项键名
            default: 默认值
        Returns:
            配置项值或默认值
        """
        if not Config._loaded:
            Config.load_config()
        return Config._config.get(key, default)

    @staticmethod
    def get_section(section: str) -> Dict[str, Any]:
        """
        获取配置节
        Args:
            section: 配置节名称
        Returns:
            配置节字典
        """
        if not Config._loaded:
            Config.load_config()
        return Config._config.get(section, {})