import uuid
from typing import List, Tuple


class Utils:
    """
    Utils class provides helper methods for parsing content from a specified file
    and generating unique keys for chart elements.
    """

    def __init__(self, file_to_parse: str) -> None:
        """
        Initialize with the file path to parse.

        Args:
            file_to_parse (str): The path to the file to be parsed.
        """
        self.PARSE_FILE_PATH: str = file_to_parse
        self.block_headers = {'#TITLE', '#TEXT', '#METHOD', '#CODE'}

    def generate_key(self, prefix: str = "chart") -> str:
        """
        Generate a unique key with a given prefix.

        Args:
            prefix (str, optional): Prefix for the key. Defaults to "chart".

        Returns:
            str: A unique key.
        """
        return f"{prefix}_{uuid.uuid4().hex}"

    def parse_file(self) -> List[Tuple[str, str]]:
        """
        Parse the file for blocks of content denoted by headers (#TITLE, #TEXT, etc.).

        Returns:
            List[Tuple[str, str]]: A list of tuples (block_type, block_content).
        """
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

            # Append the last block if exists
            if block_type and block_content:
                content.append((block_type, block_content.strip()))

        return content
