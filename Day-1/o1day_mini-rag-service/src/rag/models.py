from typing import List, Optional


class Document:
    def __init__(self, doc_id: str, title: str, content: str, tags: List[str]):
        self.id = doc_id
        self.title = title
        self.content = content
        self.tags = tags

    def __repr__(self):
        return f"Document(doc_id={self.id}, title={self.title}, content={self.content}, tags={self.tags})"
