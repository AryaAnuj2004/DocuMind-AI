from typing import Tuple, Optional

class APIValidator:
    """
    Validates Google Gemini API keys by issuing a lightweight ping request to Google GenAI service.
    """

    @classmethod
    def validate_api_key(cls, api_key: Optional[str]) -> Tuple[bool, str]:
        """
        Validates the provided API key.
        Returns (True, "API Key Validated") if successful, or (False, "Error message") if invalid.
        """
        if not api_key or not api_key.strip():
            return False, "API Key is empty."

        clean_key = api_key.strip()

        # Simple structural check
        if len(clean_key) < 15:
            return False, "API Key format is invalid (too short)."

        try:
            from google import genai
            client = genai.Client(api_key=clean_key)
            
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
            for model_name in candidate_models:
                try:
                    res = client.models.generate_content(
                        model=model_name,
                        contents="ping"
                    )
                    if res and res.text:
                        return True, "API Key Validated Successfully"
                except Exception as e:
                    err_str = str(e)
                    if "400" in err_str or "API_KEY_INVALID" in err_str or "invalid" in err_str.lower() or "unauthorized" in err_str.lower():
                        return False, "Invalid API Key: Unauthorized or key not recognized by Google AI."
                    elif "429" in err_str or "RESOURCE_EXHAUSTED" in err_str or "quota" in err_str.lower():
                        return True, "API Key Validated (Quota Limit Exceeded)"
                    continue

            return True, "API Key Accepted"
        except Exception as ex:
            ex_str = str(ex)
            if "API_KEY_INVALID" in ex_str or "invalid" in ex_str.lower() or "unauthorized" in ex_str.lower():
                return False, "Invalid API Key: Please check your Google AI Studio API key."
            return True, f"Key set (Validation notice: {ex_str})"
