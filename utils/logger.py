import logging
import os
from datetime import datetime

class Logger:
    @staticmethod
    def get_logger(name: str, log_file: str = 'stock_picker.log') -> logging.Logger:
        """
        获取配置好的日志记录器
        Args:
            name: 日志记录器名称
            log_file: 日志文件路径
        Returns:
            配置好的日志记录器
        """
        # 创建日志记录器
        logger = logging.getLogger(name)
        logger.setLevel(logging.INFO)

        # 避免重复添加处理器
        if logger.handlers:
            return logger

        # 创建格式化器
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        # 创建控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)

        # 创建文件处理器
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(formatter)

        # 添加处理器
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)

        return logger

    @staticmethod
    def clean_old_logs(log_file: str = 'stock_picker.log', max_size_mb: int = 10) -> None:
        """
        清理过大的日志文件
        Args:
            log_file: 日志文件路径
            max_size_mb: 日志文件最大大小(MB)
        """
        if os.path.exists(log_file):
            file_size_mb = os.path.getsize(log_file) / (1024 * 1024)
            if file_size_mb > max_size_mb:
                # 重命名旧日志文件
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                old_log_file = f"{log_file}.{timestamp}"
                os.rename(log_file, old_log_file)
                # 创建新的日志文件
                with open(log_file, 'w') as f:
                    pass
                logging.info(f"日志文件已清理，旧文件保存为: {old_log_file}")