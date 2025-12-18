import json
import zipfile
import logging
from pathlib import Path
from .base import BaseConverter


class EmmxConverter(BaseConverter):
    def convert(self, input_path: Path, output_path: Path, **kwargs) -> Path:
        """
        转换 emmx 文件为 Markdown
        :param input_path: 输入文件路径
        :param output_path: 输出文件路径
        :return: 实际输出的文件路径
        """
        try:
            input_path = Path(input_path)
            output_path = Path(output_path)

            # 确保输出目录存在
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # 提取并解析 JSON
            data = self._extract_json(input_path)

            # 转换为 Markdown
            markdown_content = self._to_markdown(data)

            # 写入文件
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(markdown_content)

            return output_path

        except Exception as e:
            logging.error(f"转换 emmx 失败: {e}")
            raise

    def _extract_json(self, emmx_path: Path) -> dict:
        """
        从 emmx (zip) 中提取核心 JSON 数据
        """
        try:
            with zipfile.ZipFile(emmx_path, "r") as z:
                # 尝试常见的文件名
                targets = ["doc/document.json", "mindmap.json"]
                for target in targets:
                    if target in z.namelist():
                        with z.open(target) as f:
                            return json.load(f)

                # 如果找不到已知文件，列出所有文件帮助调试
                logging.warning(
                    f"在 emmx 中未找到预期的 JSON 文件。包含的文件: {z.namelist()}"
                )
                raise ValueError("不支持的 emmx 格式：找不到 mindmap 数据")
        except zipfile.BadZipFile:
            raise ValueError("文件损坏或不是有效的 emmx (zip) 格式")

    def _to_markdown(self, data: dict) -> str:
        """
        将 JSON 数据转换为 Markdown 字符串
        """
        lines = []

        # 尝试定位根节点
        # 结构可能不同，尝试适配
        root = None

        # 结构 1: doc/document.json -> models -> map
        if "models" in data and "map" in data["models"]:
            root = data["models"]["map"]
        # 结构 2: mindmap.json -> root
        elif "root" in data:
            root = data["root"]
        # 结构 3: 直接是节点 (不太可能，但作为 fallback)
        elif "topic" in data:  # MindMaster 有时使用 'topic' 作为根
            root = data["topic"]
        # 结构 4: data 本身是根节点 (如果提取的是 topic.json)
        elif "children" in data or "text" in data:
            root = data

        if not root:
            # 尝试在 data 中深度搜索包含 'children' 或 'text' 的最大对象？
            # 暂时抛出异常
            logging.debug(f"JSON 数据结构: {data.keys()}")
            raise ValueError("无法识别的 JSON 结构")

        # 处理标题/文件名
        title = "MindMap"
        # 某些结构中 title 可能在其他地方

        lines.append(f"# {title}")
        lines.append("")

        self._parse_node(root, 0, lines)

        return "\n".join(lines)

    def _parse_node(self, node: dict, level: int, lines: list):
        """
        递归解析节点
        """
        if not isinstance(node, dict):
            return

        # 获取文本
        text = ""
        # 尝试不同的键名
        if "topic" in node:  # 有时嵌套一层
            node = node["topic"]

        if "text" in node:  # 常见
            text = node["text"]
            if isinstance(text, dict) and "content" in text:  # 富文本结构
                text = text["content"]
        elif "title" in node:
            text = node["title"]
        elif "content" in node:
            text = node["content"]

        # 清理文本
        if text:
            text = str(text).strip().replace("\n", " ")
            # 生成 Markdown 行
            indent = "  " * level
            lines.append(f"{indent}- {text}")

        # 处理子节点
        children = []
        if "children" in node:
            children = node["children"]
        elif "topics" in node:
            children = node["topics"]
        elif "subtopics" in node:  # XMind 风格，可能出现在某些导出中
            children = node["subtopics"]

        if isinstance(children, list):
            for child in children:
                self._parse_node(child, level + 1, lines)
