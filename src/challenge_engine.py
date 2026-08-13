import json
import re
from typing import List, Dict, Any, Optional
from src.parser import DocumentChunk

class ChallengeEngine:
    """
    Challenge Me Mode Engine:
    - Generates logic and comprehension-focused questions from document content.
    - Evaluates user answers with feedback and document grounded justifications.
    - Uses modern google.genai SDK with multi-model fallback sequence.
    """

    @classmethod
    def generate_questions(
        cls,
        chunks: List[DocumentChunk],
        count: int = 3,
        existing_questions: Optional[List[str]] = None,
        api_key: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Generates logic-based questions from document using Gemini API.
        """
        if not chunks:
            return []

        if not api_key:
            return [{
                "id": 1,
                "question": "API Key Required: Please enter your Google Gemini API Key in the sidebar settings to generate challenge questions.",
                "hint": "Provide a valid GEMINI_API_KEY in the sidebar.",
                "target_citation": "N/A",
                "is_error": True
            }]

        existing_str = ", ".join(existing_questions) if existing_questions else "None"
        sample_chunks = chunks[:12] # Sample representative chunks
        context_text = "\n\n".join([f"[{c.citation_label}]\n{c.text}" for c in sample_chunks])

        prompt = (
            "You are an academic examiner and logic tutor.\n"
            f"Task: Generate exactly {count} distinct, logic-based or comprehension-focused challenge questions based on the document text provided below.\n"
            "Requirements:\n"
            "1. Questions MUST test deep understanding, logical relationships, cause-and-effect, or core arguments (NOT trivial word searches).\n"
            "2. DO NOT duplicate any of these previously generated questions: {existing_str}\n"
            "3. Respond ONLY with a valid JSON array containing objects with keys: 'question', 'hint', 'target_citation'.\n"
            "Example JSON format:\n"
            "[\n"
            "  {\"question\": \"What logical link exists between X and Y?\", \"hint\": \"Consider section 2\", \"target_citation\": \"Page 2, Paragraph 1\"}\n"
            "]\n\n"
            f"Document Context:\n{context_text}"
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
            raw_text = ""
            last_err = None

            for model_name in candidate_models:
                try:
                    response = client.models.generate_content(
                        model=model_name,
                        contents=prompt,
                    )
                    if response and response.text:
                        raw_text = response.text.strip()
                        break
                except Exception as ex:
                    last_err = ex
                    err_s = str(ex).lower()
                    if any(term in err_s for term in ["quota", "429", "resourceexhausted", "limit", "exceeded", "invalid", "unauthorized"]):
                        raise ex
                    continue

            if not raw_text and last_err:
                raise last_err

            # Clean JSON string code blocks if present
            raw_text = re.sub(r'^```json\s*', '', raw_text, flags=re.MULTILINE)
            raw_text = re.sub(r'^```\s*', '', raw_text, flags=re.MULTILINE).strip()

            parsed = json.loads(raw_text)
            
            formatted_questions = []
            start_id = len(existing_questions or []) + 1
            for idx, item in enumerate(parsed):
                formatted_questions.append({
                    "id": start_id + idx,
                    "question": item.get("question", f"Question {start_id + idx}"),
                    "hint": item.get("hint", "Review the document text."),
                    "target_citation": item.get("target_citation", "Document text"),
                    "is_error": False
                })
            return formatted_questions

        except Exception as e:
            err_str = str(e).lower()
            if any(term in err_str for term in ["quota", "429", "resourceexhausted", "limit", "exceeded"]):
                err_msg = "Free API Quota Exhausted: Your Gemini API free tier limit or quota has been reached. Please check your API key, upgrade your quota, or try again later."
            elif any(term in err_str for term in ["invalid", "api_key", "unauthorized", "autherror", "400", "401", "403"]):
                err_msg = f"Invalid API Key: The provided API key is invalid or unauthorized. ({e})"
            else:
                err_msg = f"API Error: Unable to generate challenge questions. ({e})"

            return [{
                "id": 1,
                "question": err_msg,
                "hint": "Check your API Key settings in the sidebar.",
                "target_citation": "API Error",
                "is_error": True
            }]

    @classmethod
    def evaluate_response(
        cls,
        question: str,
        user_response: str,
        chunks: List[DocumentChunk],
        api_key: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Evaluates a user's answer against document text using Gemini API.
        """
        if not api_key:
            return {
                "status": "API Key Missing",
                "score": "0%",
                "feedback": "API Key Required: Please enter your Google Gemini API Key in the sidebar settings to evaluate responses.",
                "ideal_answer": "N/A",
                "justification": "N/A"
            }

        if not user_response.strip():
            return {
                "status": "No Answer Provided",
                "score": "0%",
                "feedback": "Please enter an answer to submit for evaluation.",
                "ideal_answer": "N/A",
                "justification": "N/A"
            }

        sample_text = "\n\n".join([f"[{c.citation_label}]\n{c.text}" for c in chunks[:10]])

        prompt = (
            "You are an expert academic evaluator grading a student's answer based strictly on a reference document.\n"
            f"Question: {question}\n"
            f"Student Answer: {user_response}\n\n"
            f"Document Context:\n{sample_text}\n\n"
            "Task:\n"
            "1. Grade the student's answer as: 'Correct', 'Partially Correct', or 'Incorrect'.\n"
            "2. Provide a score percentage (e.g. 100%, 70%, 20%).\n"
            "3. Provide clear constructive Feedback highlighting what was right or missing.\n"
            "4. Provide the Ground-Truth Ideal Answer based on the document.\n"
            "5. Provide the Justification citing specific document locations (Page/Paragraph).\n\n"
            "Output MUST be in strict JSON format:\n"
            "{\n"
            "  \"status\": \"Correct\",\n"
            "  \"score\": \"90%\",\n"
            "  \"feedback\": \"...\",\n"
            "  \"ideal_answer\": \"...\",\n"
            "  \"justification\": \"...\"\n"
            "}"
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
            raw_text = ""
            last_err = None

            for model_name in candidate_models:
                try:
                    response = client.models.generate_content(
                        model=model_name,
                        contents=prompt,
                    )
                    if response and response.text:
                        raw_text = response.text.strip()
                        break
                except Exception as ex:
                    last_err = ex
                    err_s = str(ex).lower()
                    if any(term in err_s for term in ["quota", "429", "resourceexhausted", "limit", "exceeded", "invalid", "unauthorized"]):
                        raise ex
                    continue

            if not raw_text and last_err:
                raise last_err

            raw_text = re.sub(r'^```json\s*', '', raw_text, flags=re.MULTILINE)
            raw_text = re.sub(r'^```\s*', '', raw_text, flags=re.MULTILINE).strip()

            parsed = json.loads(raw_text)
            return parsed

        except Exception as e:
            err_str = str(e).lower()
            if any(term in err_str for term in ["quota", "429", "resourceexhausted", "limit", "exceeded"]):
                err_msg = "Free API Quota Exhausted: Your Gemini API free tier limit or quota has been reached. Please check your API key, upgrade your quota, or try again later."
            elif any(term in err_str for term in ["invalid", "api_key", "unauthorized", "autherror", "400", "401", "403"]):
                err_msg = f"Invalid API Key: The provided API key is invalid or unauthorized. ({e})"
            else:
                err_msg = f"API Error during evaluation. ({e})"

            return {
                "status": "Evaluation Failed",
                "score": "0%",
                "feedback": err_msg,
                "ideal_answer": "N/A",
                "justification": "API Error"
            }
