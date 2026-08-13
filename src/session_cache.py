import os
import json
import secrets
import hashlib
import time
import streamlit as st

CACHE_DIR = ".session_cache"
IDLE_TIMEOUT_SECONDS = 1800  # 30 Minutes Inactivity Auto-Expiry

def compute_client_fingerprint() -> str:
    """
    Computes a cryptographic SHA-256 fingerprint bound to the client's request headers.
    Binds session to the user's Browser User-Agent and Host context.
    """
    try:
        ua = ""
        host = ""
        if hasattr(st, "context") and hasattr(st.context, "headers"):
            headers = st.context.headers or {}
            ua = headers.get("user-agent", "")
            host = headers.get("host", "") or headers.get("x-forwarded-for", "")
        raw_identity = f"{ua}|{host}".encode("utf-8")
        return hashlib.sha256(raw_identity).hexdigest()
    except Exception:
        return "default_fingerprint"

def set_session_cookie(sid: str, clear: bool = False):
    """
    Sets or clears the 'documind_sid' browser session cookie on top-level document.
    Keeps Session ID and API Key 100% out of the URL bar (http://localhost:8501/).
    Per RFC 6265 standard, omitting Max-Age and Expires creates a true Browser Session Cookie:
    - Survived across F5 page refreshes within the tab session.
    - Automatically deleted by the browser when the tab or window is closed.
    """
    try:
        if clear:
            cookie_js = "document.cookie = 'documind_sid=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT; SameSite=Lax;';"
        else:
            cookie_js = f"document.cookie = 'documind_sid={sid}; path=/; SameSite=Lax;';"

        # Method 1: Top-level DOM injection via img onerror (executes in main page window context)
        st.markdown(
            f"""<img src="x" onerror="{cookie_js} this.remove();" style="display:none;" />""",
            unsafe_allow_html=True
        )

        # Method 2: Fallback iframe injection via components.html
        import streamlit.components.v1 as components
        components.html(
            f"""
            <script>
                try {{
                    if ("{clear}" === "True") {{
                        window.parent.document.cookie = "documind_sid=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT; SameSite=Lax;";
                    }} else {{
                        window.parent.document.cookie = "documind_sid={sid}; path=/; SameSite=Lax;";
                    }}
                }} catch(e) {{}}
            </script>
            """,
            height=0,
            width=0
        )
    except Exception:
        pass

def init_session_cache():
    """
    Initializes a cryptographically secure session_id using HTTP cookies.
    Session ID and API Key are strictly kept OUT of the browser URL bar.
    F5 page refreshes retain the session via the 'documind_sid' cookie sent in HTTP headers.
    """
    if not os.path.exists(CACHE_DIR):
        os.makedirs(CACHE_DIR, exist_ok=True)

    # Clean any query parameters to ensure clean URL bar at all times
    if hasattr(st, "query_params"):
        try:
            if "sid" in st.query_params:
                del st.query_params["sid"]
            if "api_key" in st.query_params:
                del st.query_params["api_key"]
        except Exception:
            pass

    sid = None

    # Step 1: Read 'documind_sid' cookie from st.context.cookies
    try:
        if hasattr(st, "context") and hasattr(st.context, "cookies"):
            cookie_sid = st.context.cookies.get("documind_sid")
            if cookie_sid and isinstance(cookie_sid, str) and cookie_sid.strip():
                sid = cookie_sid.strip()
    except Exception:
        sid = None

    # Step 2: Check st.session_state for existing session_id
    if not sid and "session_id" in st.session_state and st.session_state.session_id:
        sid = st.session_state.session_id

    # Step 3: Generate a new 256-bit cryptographically secure session token if needed
    if not sid:
        sid = secrets.token_urlsafe(32)

    st.session_state.session_id = sid

    if "client_fingerprint" not in st.session_state:
        st.session_state.client_fingerprint = compute_client_fingerprint()

    # Step 4: Ensure session cookie is set on client browser
    set_session_cookie(sid)

    purge_stale_session_caches()
    return sid

def save_session_to_disk():
    """
    Saves active session state with cryptographic client fingerprint, timestamp, and user inputs.
    """
    sid = st.session_state.get("session_id")
    if not sid:
        return

    if st.session_state.get("session_cleared") and not st.session_state.get("chunks"):
        return

    cache_path = os.path.join(CACHE_DIR, f"session_{sid}.json")
    
    raw_chunks = st.session_state.get("chunks", [])
    serializable_chunks = [c.to_dict() if hasattr(c, "to_dict") else c for c in raw_chunks]

    fingerprint = st.session_state.get("client_fingerprint") or compute_client_fingerprint()

    # Collect user typed input fields (e.g. Challenge Me answers)
    user_inputs = {}
    for k, v in st.session_state.items():
        if isinstance(k, str) and k.startswith("input_") and isinstance(v, str):
            user_inputs[k] = v

    data = {
        "client_fingerprint": fingerprint,
        "last_accessed_at": time.time(),
        "chunks": serializable_chunks,
        "uploaded_file_name": st.session_state.get("uploaded_file_name"),
        "summary": st.session_state.get("summary", ""),
        "takeaways": st.session_state.get("takeaways", []),
        "glossary": st.session_state.get("glossary", []),
        "mindmap": st.session_state.get("mindmap", ""),
        "chat_history": st.session_state.get("chat_history", []),
        "challenge_questions": st.session_state.get("challenge_questions", []),
        "evaluations": st.session_state.get("evaluations", {}),
        "stored_api_key": st.session_state.get("stored_api_key", ""),
        "validated_api_key": st.session_state.get("validated_api_key", ""),
        "is_key_valid": st.session_state.get("is_key_valid", False),
        "key_validation_msg": st.session_state.get("key_validation_msg", ""),
        "user_inputs": user_inputs
    }
    
    try:
        with open(cache_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

def load_session_from_disk():
    """
    Loads saved session state only if client fingerprint matches and session has not expired.
    Restores API key validation state, uploaded document analysis, Q&A chat, and user input fields.
    """
    sid = st.session_state.get("session_id", "")
    if not sid and hasattr(st, "context") and hasattr(st.context, "cookies"):
        sid = st.context.cookies.get("documind_sid", "")
        if sid:
            st.session_state.session_id = sid

    if not sid:
        return False
        
    cache_path = os.path.join(CACHE_DIR, f"session_{sid}.json")
    
    if os.path.exists(cache_path):
        try:
            with open(cache_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Security Check 1: Session Inactivity Timeout (30 Mins)
            last_accessed = data.get("last_accessed_at", 0)
            if last_accessed and (time.time() - last_accessed > IDLE_TIMEOUT_SECONDS):
                os.remove(cache_path)
                return False

            # Security Check 2: Client Fingerprint Binding (Anti-Hijacking)
            stored_fingerprint = data.get("client_fingerprint")
            current_fingerprint = st.session_state.get("client_fingerprint") or compute_client_fingerprint()
            if stored_fingerprint and current_fingerprint and (stored_fingerprint != current_fingerprint):
                return False
                
            from src.parser import DocumentChunk
            raw_chunks = data.get("chunks", [])
            chunks = []
            for item in raw_chunks:
                if isinstance(item, dict):
                    chunks.append(DocumentChunk(**item))
                else:
                    chunks.append(item)

            st.session_state.chunks = chunks
            st.session_state.uploaded_file_name = data.get("uploaded_file_name")
            st.session_state.summary = data.get("summary", "")
            st.session_state.takeaways = data.get("takeaways", [])
            st.session_state.glossary = data.get("glossary", [])
            st.session_state.mindmap = data.get("mindmap", "")
            st.session_state.chat_history = data.get("chat_history", [])
            st.session_state.challenge_questions = data.get("challenge_questions", [])
            st.session_state.evaluations = data.get("evaluations", {})
            
            if data.get("stored_api_key"):
                st.session_state.stored_api_key = data.get("stored_api_key")
            if data.get("validated_api_key"):
                st.session_state.validated_api_key = data.get("validated_api_key")
            if "is_key_valid" in data:
                st.session_state.is_key_valid = data.get("is_key_valid")
            if data.get("key_validation_msg"):
                st.session_state.key_validation_msg = data.get("key_validation_msg")

            user_inputs = data.get("user_inputs", {})
            for k, v in user_inputs.items():
                if k not in st.session_state:
                    st.session_state[k] = v
            
            if st.session_state.chunks and not st.session_state.get("retriever"):
                from src.retriever import DocumentRetriever
                st.session_state.retriever = DocumentRetriever(st.session_state.chunks)
            return True
        except Exception:
            return False
    return False

def rotate_session_id():
    """
    Rotates the session ID to prevent Session Fixation attacks when a new document is uploaded.
    """
    old_sid = st.session_state.get("session_id")
    if old_sid:
        clear_session_disk_cache()
    new_sid = secrets.token_urlsafe(32)
    st.session_state.session_id = new_sid
    set_session_cookie(new_sid)
    return new_sid

def clear_document_content():
    """
    Clears active document content, chunks, analysis, Q&A history, and file input fields,
    while preserving the active session ID, session cookie, and validated API key settings.
    """
    st.session_state.chunks = []
    st.session_state.retriever = None
    st.session_state.uploaded_file_name = None
    st.session_state.summary = ""
    st.session_state.takeaways = []
    st.session_state.glossary = []
    st.session_state.mindmap = ""
    st.session_state.chat_history = []
    st.session_state.challenge_questions = []
    st.session_state.evaluations = {}

    # Clear typed input fields for questions/forms
    keys_to_clear = [k for k in st.session_state.keys() if isinstance(k, str) and (k.startswith("input_") or k.startswith("form_"))]
    for k in keys_to_clear:
        del st.session_state[k]

    # Reset file uploader widget key to clear file input field
    st.session_state.uploader_key = st.session_state.get("uploader_key", 0) + 1

    # Save updated session cache to disk with cleared document fields
    save_session_to_disk()

def clear_session_disk_cache():
    """
    Removes disk cache files and clears browser session cookie when user explicitly clears document session.
    """
    st.session_state.session_cleared = True
    sid = st.session_state.get("session_id")
    if sid:
        json_path = os.path.join(CACHE_DIR, f"session_{sid}.json")
        pkl_path = os.path.join(CACHE_DIR, f"session_{sid}.pkl")
        for path in [json_path, pkl_path]:
            if os.path.exists(path):
                try:
                    os.remove(path)
                except Exception:
                    pass
    if hasattr(st, "query_params") and "sid" in st.query_params:
        try:
            del st.query_params["sid"]
        except Exception:
            pass
    set_session_cookie("", clear=True)

def purge_stale_session_caches(max_age_seconds: int = IDLE_TIMEOUT_SECONDS):
    """
    Purges disk cache files older than max_age_seconds (30 minutes idle timeout).
    """
    if os.path.exists(CACHE_DIR):
        now = time.time()
        try:
            for fname in os.listdir(CACHE_DIR):
                if fname.startswith("session_"):
                    fpath = os.path.join(CACHE_DIR, fname)
                    try:
                        if os.path.isfile(fpath) and (now - os.path.getmtime(fpath) > max_age_seconds):
                            os.remove(fpath)
                    except Exception:
                        pass
        except Exception:
            pass

