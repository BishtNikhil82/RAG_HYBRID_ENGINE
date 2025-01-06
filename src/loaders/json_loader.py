from langchain.schema import Document
import json

class JsonLoader:
    def __init__(self, file_path: str):
        self.file_path = file_path

    def load(self):
        with open(self.file_path, "r") as file:
            data = json.load(file)

        documents = []
        if isinstance(data, list):
            for item in data:
                content = item.get("content", "")
                if isinstance(content, dict):  # If content is a dictionary, stringify it
                    content = self._flatten_content(content)
                documents.append(
                    Document(
                        page_content=content,
                        metadata=item.get("metadata", {})
                    )
                )
        elif isinstance(data, dict):
            content = data.get("content", "")
            if isinstance(content, dict):  # If content is a dictionary, stringify it
                content = self._flatten_content(content)
            documents.append(
                Document(
                    page_content=content,
                    metadata=data.get("metadata", {})
                )
            )
        else:
            raise ValueError("Unsupported JSON structure. Must be a list or dict.")

        return documents

    def _flatten_content(self, content_dict):
        """
        Flatten a dictionary content into a readable string.
        """
        return " | ".join([f"{key}: {value}" for key, value in content_dict.items()])
