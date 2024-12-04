import uuid


class Utils():
    def __init__(self, FILE_TO_PARSE) -> None:
        self.PARSE_FILE_PATH = FILE_TO_PARSE
    

    def generate_key(self, prefix="chart"):
        return f"{prefix}_{uuid.uuid4().hex}"


    def parse_file(self):
        with open(self.PARSE_FILE_PATH, 'r', encoding='utf-8') as file:
            lines = file.readlines()
        
        content = []
        current_type = None
        current_block = []
        
        for line in lines:
            if current_type == 'code':
                clean_line = line.rstrip('\n')
            else:
                clean_line = line.strip()
            
            if clean_line == '#TEXT':
                if current_block:
                    content.append((current_type, "\n".join(current_block)))
                current_type = 'text'
                current_block = []
            elif clean_line == "#METHOD":
                if current_block:
                    content.append((current_type, "\n".join(current_block)))
                current_type = "method"
                current_block = []
            elif clean_line == "#CODE":
                if current_block:
                    content.append(((current_type, "\n".join(current_block))))
                    current_type = 'code'
                    current_block = []
            else:
                current_block.append(clean_line)
        
        if current_block:
            content.append((current_type, "\n".join(current_block)))
        
        return content
        