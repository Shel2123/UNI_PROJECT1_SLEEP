import uuid
from typing import List, Tuple, Optional

class Utils():
    def __init__(self, FILE_TO_PARSE: str) -> None:
        self.PARSE_FILE_PATH: str = FILE_TO_PARSE
        self.block_headers = {'#TITLE', '#TEXT', '#METHOD', '#CODE'}


    def generate_key(self, prefix: str ="chart") -> str:
        return f"{prefix}_{uuid.uuid4().hex}"


    def parse_file(self):
        content = []
        block_type = None
        block_content = ''

        with open(self.PARSE_FILE_PATH, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.rstrip('\n')
                stripped_line = line.strip()
                if stripped_line in self.block_headers:
                    if block_type and block_content:
                        content.append((block_type, block_content.strip()))
                        block_content = ''
                    block_type = stripped_line[1:].lower()
                else:
                    block_content += line + '\n'
            if block_type and block_content:
                content.append((block_type, block_content.strip()))
        return content
        