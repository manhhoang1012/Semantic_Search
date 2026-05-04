def chunk_text(text: str, max_length: int = 500, overlap: int = 50):
    if not text:
        return []
        
    chunks = []
    start = 0
    text_length = len(text)
    
    while start < text_length:
        end = start + max_length
        
        # If we are not at the end of the text, try to find a nice breaking point
        if end < text_length:
            # Look for a newline or period within the last 100 chars of the chunk
            # If not found, just hard break at max_length
            break_point = end
            for char in ['\n', '.', '!', '?']:
                last_punct = text.rfind(char, start + max_length - 100, end)
                if last_punct != -1 and last_punct > start + overlap:
                    break_point = last_punct + 1
                    break
            
            chunk = text[start:break_point]
            chunks.append(chunk.strip())
            start = break_point - overlap
        else:
            # We are at the end
            chunk = text[start:]
            chunks.append(chunk.strip())
            break
            
    return chunks
