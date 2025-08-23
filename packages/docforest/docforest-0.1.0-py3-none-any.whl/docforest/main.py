from typing import Dict, List, Literal, Optional

DocStyle = Literal["markdown", "asciidoc"]

style_delimiter_map: Dict[DocStyle, str] = {"markdown": "#", "asciidoc": "="}


class Section:
    def __init__(self, level: int, content: str):
        self.level = level
        self.content = content

    def __repr__(self):
        return f"Section(level={self.level}, content={self.content})"


def chunk_document(content: str, style: DocStyle) -> List[str]:
    if not content.strip():
        return []
    if style not in style_delimiter_map:
        raise ValueError(f"Unsupported style: {style}")

    delimiter = style_delimiter_map[style]

    lines = content.splitlines()
    cur_section: Optional[Section] = None
    section_stack: List[Section] = []
    chunks: List[str] = []

    def get_prev_section_level() -> int:
        return section_stack[-1].level if section_stack else 0

    def flush():
        chunk = "\n".join(section.content for section in section_stack)
        if chunk:
            chunks.append(chunk)

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
