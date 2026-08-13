import re
from typing import List, Optional
from src.parser import DocumentChunk

class DocumentSummarizer:
    """
    Generates attractive executive summaries for uploaded documents using Google GenAI API.
    Strictly enforces word count limit of <= 150 words with structured headings and bold highlights.
    Uses modern google.genai SDK with automatic model fallback to prevent 404 errors.
    """
    
    MAX_WORDS = 150

    @classmethod
    def truncate_to_word_limit(cls, text: str, max_words: int = 150) -> str:
        words = text.split()
        if len(words) <= max_words:
            return text.strip()
        return " ".join(words[:max_words]) + "..."

    @classmethod
    def generate_summary(cls, chunks: List[DocumentChunk], api_key: Optional[str] = None) -> str:
        if not api_key:
            return "API Key Required: Please enter your Google Gemini API Key in the sidebar settings to generate document summaries."

        full_text = " ".join([c.text for c in chunks[:15]]) # Use first ~15 chunks (~3000 words max)
        
        prompt = (
            "You are an expert academic and technical research assistant.\n"
            "Task: Provide a visually attractive, beautifully formatted summary of the document below in STRICTLY LESS THAN 150 WORDS.\n"
            "Formatting Requirements:\n"
            "1. Organize into 3 clear sections using bold titles:\n"
            "   - **Core Objective**: <1-2 sentences on document purpose>\n"
            "   - **Key Findings**: <Bulleted or formatted highlights of key findings & vulnerabilities>\n"
            "   - **Main Conclusion**: <1-2 sentences summarizing takeaways>\n"
            "2. Use **bold highlights** for critical entities, vulnerabilities, and takeaways (e.g., **Sony Pictures**, **geopolitical risks**, **unencrypted data**).\n"
            "3. Keep formatting clean, engaging, professional, and strictly under 150 total words.\n\n"
            f"Document Content:\n{full_text}"
        )

        try:
            from google import genai
            client = genai.Client(api_key=api_key)
            
            candidate_models = [
                "gemini-3.5-flash-lite",
                "gemini-3.1-flash-lite",
                "gemini-2.5-flash-lite",
                "gemini-3.6-flash",
                "gemini-3.5-flash",
                "gemini-3-flash",
                "gemini-2.5-flash",
                "gemini-1.5-flash"
            ]
            summary_text = ""
            last_err = None

            for model_name in candidate_models:
                try:
                    response = client.models.generate_content(
                        model=model_name,
                        contents=prompt,
                    )
                    if response and response.text:
                        summary_text = response.text.strip()
                        break
                except Exception as ex:
                    last_err = ex
                    err_s = str(ex).lower()
                    if any(term in err_s for term in ["quota", "429", "resourceexhausted", "limit", "exceeded", "invalid", "unauthorized"]):
                        raise ex
                    continue

            if not summary_text and last_err:
                raise last_err

            if not summary_text:
                return "Summary Generation Failed: Empty response received from API."
                
            return cls.truncate_to_word_limit(summary_text, cls.MAX_WORDS)
            
        except Exception as e:
            err_str = str(e).lower()
            if any(term in err_str for term in ["quota", "429", "resourceexhausted", "limit", "exceeded"]):
                return "Free API Quota Exhausted: Your Gemini API free tier limit or quota has been reached. Please check your API key, upgrade your quota, or try again later."
            elif any(term in err_str for term in ["invalid", "api_key", "unauthorized", "autherror", "400", "401", "403"]):
                return f"Invalid API Key: The provided API key is invalid or unauthorized. ({e})"
            else:
                return f"API Error: Unable to generate summary. ({e})"
