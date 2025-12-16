from abc import ABC, abstractmethod
from pathlib import Path

class BaseConverter(ABC):
    @abstractmethod
    def convert(self, input_path: Path, output_path: Path, **kwargs) -> Path:
        """
        转换文件
        :param input_path: 输入文件路径
        :param output_path: 输出文件路径
        :param kwargs: 其他参数
        :return: 实际输出的文件路径
        """
        pass
