from typing import List

from langchain_text_splitters import RecursiveCharacterTextSplitter


def chunk_text(text: str, chunk_size: int = 1000, chunk_overlap: int = 200) -> List[str]:
    """Splits text into chunks of a specified size with overlap.
    
    Args:
        text: The full text of the document.
        chunk_size: The maximum number of characters per chunk.
        chunk_overlap: The number of characters to overlap between chunks.
        
    Returns:
        A list of text chunks.
    """
    if not text:
        return []

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        is_separator_regex=False,
    )
    
    chunks = text_splitter.split_text(text)
    return chunks
