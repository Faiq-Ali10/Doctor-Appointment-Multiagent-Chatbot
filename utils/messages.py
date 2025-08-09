from typing import List
from langchain_core.messages import BaseMessage

def get_message_text(content) -> str:
    """Extract readable text from LangChain message content."""
    if isinstance(content, str):
        return content.strip()

    if isinstance(content, list):
        parts = []
        for part in content:
            if isinstance(part, str):
                parts.append(part)
            elif isinstance(part, dict) and "text" in part:
                parts.append(part["text"])
        return " ".join(parts).strip()

    return str(content).strip()
    
def get_consolidated_response(messages: List[BaseMessage]) -> str:
    """
    Consolidate multiple AI responses into a single coherent answer.
    """
    if not messages:
        return "I apologize, but I couldn't process your request."
    
    information_responses = []
    booking_responses = []
    
    for msg in messages:
        if msg.type == "ai" and msg.content and get_message_text(msg.content):
            content = get_message_text(msg.content)
            name = getattr(msg, 'name', '')
            
            if name == "information_node":
                information_responses.append(content)
            elif name == "booking_node":
                booking_responses.append(content)
    
    response_parts = []
    
    if information_responses:
        info_response = max(information_responses, key=len)
        response_parts.append(info_response)
    
    if booking_responses:
        booking_response = max(booking_responses, key=len)
        if not information_responses or len(booking_response) > 20:
            response_parts.append(booking_response)
    
    # Combine responses
    if response_parts:
        final_response = " ".join(response_parts)
        sentences = final_response.split('. ')
        unique_sentences = []
        for sentence in sentences:
            if sentence.strip() and sentence.strip() not in [s.strip() for s in unique_sentences]:
                unique_sentences.append(sentence.strip())
        
        return '. '.join(unique_sentences)
    
    return "I apologize, but I couldn't process your request. Please try again."