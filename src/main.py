import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.app import StockPickerApp


def main() -> None:
    """主函数"""
    app = StockPickerApp()
    app.run()


if __name__ == "__main__":
    main()