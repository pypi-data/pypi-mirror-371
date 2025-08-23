from .enums import DocStyle
from typing import Dict, List, Optional

style_delimiter_map: Dict[DocStyle, str] = {
    DocStyle.MARKDOWN: "#",
    DocStyle.ASCIIDOC: "=",
}


class Section:
    def __init__(self, level: int, content: str):
        self.level = level
        self.content = content

    def __repr__(self):
        return f"Section(level={self.level}, content={self.content})"


class DocForest:
    def __init__(self, style: DocStyle):
        self.style = style

    def _validate_style(self, style: DocStyle):
        if style not in style_delimiter_map:
            raise ValueError(f"Unsupported style: {style}")

    def chunk(self, content: str) -> List[str]:
        if not content.strip():
            return []
        self._validate_style(self.style)

        cur_section: Optional[Section] = None
        section_stack: List[Section] = []
        chunks: List[str] = []

        def get_prev_section_level() -> int:
            return section_stack[-1].level if section_stack else 0

        def flush():
            chunk = "\n".join(section.content for section in section_stack)
            if chunk:
                chunks.append(chunk)

        lines = content.splitlines()
        delimiter = style_delimiter_map[self.style]

        for line in lines:
            if line.startswith(delimiter):
                cur_level = len(line) - len(line.lstrip(delimiter))
                cur_section = Section(cur_level, line)
                if cur_level <= get_prev_section_level():
                    flush()
                    while cur_level <= get_prev_section_level():
                        section_stack.pop()
                section_stack.append(cur_section)
            elif cur_section is not None:
                cur_section.content += "\n" + line

        flush()
        return chunks
