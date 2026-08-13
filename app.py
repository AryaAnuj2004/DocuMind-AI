import os
import streamlit as st
from dotenv import load_dotenv

# Load environment variables from .env file if available
load_dotenv()

import base64

import base64

def get_image_base64(filename: str) -> str:
    path = os.path.join(os.path.dirname(__file__), "assets", filename)
    if not os.path.exists(path):
        path = os.path.join(os.path.dirname(__file__), filename)
    if os.path.exists(path):
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    return ""

logo_white_b64 = get_image_base64("DocuMind_logo_white.png")
logo_black_b64 = get_image_base64("DocuMind_logo_black.png")

logo_white_img_tag = f'<img src="data:image/png;base64,{logo_white_b64}" style="width: 44px; height: 44px; border-radius: 8px; border: 1px solid #000000; box-sizing: border-box; vertical-align: middle; margin-right: 14px; object-fit: contain;" />' if logo_white_b64 else ""
logo_black_img_tag_sidebar = f'<img src="data:image/png;base64,{logo_white_b64}" style="width: 36px; height: 36px; border-radius: 6px; border: 1px solid #000000; box-sizing: border-box; vertical-align: middle; margin-right: 10px; object-fit: contain;" />' if logo_black_b64 else ""

from src.parser import DocumentParser, DocumentChunk
from src.summarizer import DocumentSummarizer
from src.retriever import DocumentRetriever
from src.qa_engine import QAEngine
from src.challenge_engine import ChallengeEngine
from src.glossary_engine import GlossaryEngine
from src.mindmap_engine import MindMapEngine
from src.exporter import ExportManager
from src.validator import APIValidator
from src.styles import apply_custom_styles
from src.session_cache import init_session_cache, load_session_from_disk, save_session_to_disk, clear_session_disk_cache, clear_document_content, rotate_session_id

# Constants
MAX_FILE_SIZE_MB = 50
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024

# Favicon Path for Browser Tab Title (DocuMind AI Rounded Border Logo)
favicon_path = os.path.join(os.path.dirname(__file__), "assets", "DocuMind_favicon_rounded.png")
if not os.path.exists(favicon_path):
    favicon_path = os.path.join(os.path.dirname(__file__), "assets", "DocuMind_logo_white_bordered.png")
if not os.path.exists(favicon_path):
    favicon_path = os.path.join(os.path.dirname(__file__), "assets", "DocuMind_logo_white.png")
favicon = favicon_path if os.path.exists(favicon_path) else "🤖"

# Set page configuration
st.set_page_config(
    page_title="DocuMind AI - An Intelligent Document Assistant",
    page_icon=favicon,
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply custom light design system
apply_custom_styles()

# Initialize Session ID & Load Persistent Disk Cache on F5 Page Refresh
init_session_cache()
if not st.session_state.get("session_loaded"):
    load_session_from_disk()
    st.session_state.session_loaded = True

# Initialize Session States
if "chunks" not in st.session_state:
    st.session_state.chunks = []
if "retriever" not in st.session_state:
    st.session_state.retriever = None
if "summary" not in st.session_state:
    st.session_state.summary = ""
if "takeaways" not in st.session_state:
    st.session_state.takeaways = []
if "glossary" not in st.session_state:
    st.session_state.glossary = []
if "mindmap" not in st.session_state:
    st.session_state.mindmap = ""
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "challenge_questions" not in st.session_state:
    st.session_state.challenge_questions = []
if "evaluations" not in st.session_state:
    st.session_state.evaluations = {}
if "uploaded_file_name" not in st.session_state:
    st.session_state.uploaded_file_name = None
if "stored_api_key" not in st.session_state:
    # Read environment variable GEMINI_API_KEY if present for production cloud setup
    st.session_state.stored_api_key = os.environ.get("GEMINI_API_KEY", "")
if "uploader_key" not in st.session_state:
    st.session_state.uploader_key = 0

# Sidebar - Setup & API Configuration
with st.sidebar:
    if logo_white_b64:
        st.markdown(
            f"""
            <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 8px;">
                <img src="data:image/png;base64,{logo_white_b64}" style="width: 38px; height: 38px; border-radius: 7px; border: 1px solid #000000; box-sizing: border-box; object-fit: contain; flex-shrink: 0;" />
                <div>
                    <div style="font-size: 1.25rem; font-weight: 750; color: #0f172a; line-height: 1.1; margin-bottom: 2px;">DocuMind AI</div>
                    <div style="font-size: 0.78rem; color: #64748b; font-weight: 450; line-height: 1.2;">An Intelligent Document Assistant</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        st.title("DocuMind AI")
        st.caption("An Intelligent Document Assistant")
    st.markdown("---")

    st.markdown("### API Settings")
    
    current_key_val = st.session_state.stored_api_key
    api_key_input = st.text_input(
        "Google Gemini API Key *",
        value=current_key_val,
        type="password",
        help="Enter your Gemini API key to enable document comprehension & intelligence."
    )
    
    active_api_key = api_key_input.strip() if api_key_input.strip() else None
    
    if active_api_key:
        if st.session_state.get("validated_api_key") != active_api_key or not st.session_state.get("is_key_valid"):
            with st.spinner("Validating API Key with Google AI..."):
                is_valid, msg = APIValidator.validate_api_key(active_api_key)
                st.session_state.is_key_valid = is_valid
                st.session_state.key_validation_msg = msg
                st.session_state.validated_api_key = active_api_key

        if st.session_state.get("is_key_valid", False):
            st.session_state.stored_api_key = active_api_key
            st.success(f"🔑 {st.session_state.get('key_validation_msg', 'API Key Connected')}")
            save_session_to_disk()
        else:
            st.session_state.stored_api_key = ""
            active_api_key = None
            st.error(f"❌ {st.session_state.get('key_validation_msg', 'Invalid API Key')}")
    else:
        st.session_state.stored_api_key = ""
        st.session_state.validated_api_key = None
        st.session_state.is_key_valid = False
        st.error("🔑 API Key Required")

    st.markdown("---")
    st.markdown("### Document Upload")
    uploaded_file = st.file_uploader(
        "Upload PDF or TXT document",
        type=["pdf", "txt"],
        help="Limit 50MB per file • PDF, TXT",
        key=f"uploader_{st.session_state.uploader_key}"
    )

    if st.session_state.uploaded_file_name and st.session_state.summary:
        st.markdown(f"**Active File:** `{st.session_state.uploaded_file_name}`")
        if st.button("Clear Active Document"):
            clear_document_content()
            st.rerun()

        # Download Report Center in Sidebar if document summary & notes exist
        st.markdown("---")
        st.markdown("### Export Session Notes")
        md_report = ExportManager.generate_markdown_report(
            document_name=st.session_state.uploaded_file_name or "DocuMind_Report",
            summary=st.session_state.summary,
            chat_history=st.session_state.chat_history,
            evaluations=st.session_state.evaluations,
            challenge_questions=st.session_state.challenge_questions,
            takeaways=st.session_state.takeaways,
            glossary=st.session_state.glossary,
            mindmap=st.session_state.mindmap,
            chunks=st.session_state.chunks
        )
        txt_report = ExportManager.generate_txt_report(
            document_name=st.session_state.uploaded_file_name or "DocuMind_Report",
            summary=st.session_state.summary,
            chat_history=st.session_state.chat_history,
            evaluations=st.session_state.evaluations,
            challenge_questions=st.session_state.challenge_questions,
            takeaways=st.session_state.takeaways,
            glossary=st.session_state.glossary,
            mindmap=st.session_state.mindmap,
            chunks=st.session_state.chunks
        )
        
        st.download_button(
            label="Download Markdown (.md)",
            data=md_report,
            file_name=f"{st.session_state.uploaded_file_name or 'DocuMind'}_Report.md",
            mime="text/markdown"
        )
        st.download_button(
            label="Download Text (.txt)",
            data=txt_report,
            file_name=f"{st.session_state.uploaded_file_name or 'DocuMind'}_Report.txt",
            mime="text/plain"
        )

    st.markdown("---")
    st.markdown("**Get a free API key from [Google AI Studio](https://aistudio.google.com/).**")

    # Footer pinned to the very bottom of sidebar
    st.markdown(
        """
        <div class="sidebar-footer-pinned">
            DocuMind AI v1.0<br>
            Powered by RAG & GenAI Engine
        </div>
        """,
        unsafe_allow_html=True
    )

# Main Dashboard Layout Header
st.markdown(
    f"""
    <div class="app-header" style="display: flex; align-items: center;">
        {logo_white_img_tag}
        <div>
            <div class="app-title" style="margin: 0;">DocuMind AI</div>
            <div class="app-subtitle">Deep comprehension, grounded Q&A with citations, and logic evaluation</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# Require API Key Notice Banner if missing
if not active_api_key:
    st.error("🔑 API Key Required: Please enter a valid Google Gemini API Key in the sidebar to activate document summarization, Q&A, and logic evaluation.")

# Process Uploaded Document
if uploaded_file is not None:
    # Size limit validation (50MB max)
    if uploaded_file.size > MAX_FILE_SIZE_BYTES:
        st.error(f"File Size Limit Exceeded: Attached file is {uploaded_file.size / (1024*1024):.1f}MB, which exceeds the maximum allowed limit of {MAX_FILE_SIZE_MB}MB.")
    else:
        # Re-parse if a new file is uploaded and not explicitly cleared by user
        if uploaded_file.name == st.session_state.get("cleared_file_name"):
            pass
        elif st.session_state.uploaded_file_name != uploaded_file.name:
            st.session_state.cleared_file_name = None
            rotate_session_id()  # Anti-Session Fixation protection
            file_bytes = uploaded_file.read()
            chunks = DocumentParser.parse_file(file_bytes, uploaded_file.name)
            
            st.session_state.chunks = chunks
            st.session_state.retriever = DocumentRetriever(chunks)
            st.session_state.uploaded_file_name = uploaded_file.name
            st.session_state.chat_history = []
            st.session_state.evaluations = {}
            st.session_state.summary = ""
            st.session_state.takeaways = []
            st.session_state.glossary = []
            st.session_state.mindmap = ""
            st.session_state.challenge_questions = []
            
            # Clear all previous challenge input fields and form states from session state
            keys_to_clear = [k for k in st.session_state.keys() if k.startswith("input_q_") or k.startswith("form_q_")]
            for k in keys_to_clear:
                del st.session_state[k]

# Check if document AI analysis tasks are active/pending
needs_summary = not st.session_state.summary or "API Key Required" in st.session_state.summary
needs_takeaways = not st.session_state.takeaways or not st.session_state.glossary
needs_mindmap = not st.session_state.mindmap
needs_questions = not st.session_state.challenge_questions or (st.session_state.challenge_questions and st.session_state.challenge_questions[0].get("is_error"))

is_processing_active = bool(st.session_state.chunks and active_api_key and (needs_summary or needs_takeaways or needs_mindmap or needs_questions))

if is_processing_active:
    with st.spinner("Analyzing document content & generating insights..."):
        if needs_summary:
            st.session_state.summary = DocumentSummarizer.generate_summary(
                st.session_state.chunks, api_key=active_api_key
            )
        if needs_takeaways:
            extracted = GlossaryEngine.extract_glossary_and_takeaways(
                st.session_state.chunks, api_key=active_api_key
            )
            st.session_state.takeaways = extracted.get("takeaways", [])
            st.session_state.glossary = extracted.get("glossary", [])
        if needs_mindmap:
            st.session_state.mindmap = MindMapEngine.generate_mindmap_syntax(
                st.session_state.chunks, api_key=active_api_key
            )
        if needs_questions:
            st.session_state.challenge_questions = ChallengeEngine.generate_questions(
                st.session_state.chunks, count=3, api_key=active_api_key
            )
        save_session_to_disk()
        st.rerun()

# Content wrapper below header and spinner
content_wrapper_class = "processing-content-fade" if is_processing_active else ""
st.markdown(f'<div class="{content_wrapper_class}">', unsafe_allow_html=True)

if not st.session_state.chunks:
    st.info("Please upload a PDF or TXT research document in the sidebar to get started.")
    
    # Showcase Feature Cards
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(
            """
            <div class="glass-card">
                <h4 style="color: #0f172a; font-weight: 600; margin-bottom: 6px;">Auto Summary & Glossary</h4>
                <p style="color: #64748b; font-size: 0.88rem; font-weight: 400; margin: 0;">
                    Instant executive summary, 5 bulleted core takeaways, and technical glossary with citations.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )
    with col2:
        st.markdown(
            """
            <div class="glass-card">
                <h4 style="color: #0f172a; font-weight: 600; margin-bottom: 6px;">Ask Anything + Grounding</h4>
                <p style="color: #64748b; font-size: 0.88rem; font-weight: 400; margin: 0;">
                    Free-form Q&A with citation metadata, conversational memory, and source snippet highlighting.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )
    with col3:
        st.markdown(
            """
            <div class="glass-card">
                <h4 style="color: #0f172a; font-weight: 600; margin-bottom: 6px;">Challenge Me Engine</h4>
                <p style="color: #64748b; font-size: 0.88rem; font-weight: 400; margin: 0;">
                    Generates 3 logic-based comprehension questions, grades user answers, and provides document proof.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )
else:
    # Top Metrics Bar
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-value">{len(st.session_state.chunks)}</div>
                <div class="metric-label">Paragraph Chunks</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with m2:
        max_page = max([c.page_num for c in st.session_state.chunks]) if st.session_state.chunks else 1
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-value">{max_page}</div>
                <div class="metric-label">Total Pages</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with m3:
        total_words = sum([len(c.text.split()) for c in st.session_state.chunks])
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-value">{total_words:,}</div>
                <div class="metric-label">Document Word Count</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with m4:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-value">{st.session_state.uploaded_file_name[:15]}...</div>
                <div class="metric-label">Active Document</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # Core Navigation Tabs
    tab_summary, tab_ask, tab_challenge = st.tabs([
        "Auto Summary & Intelligence",
        "Ask Anything",
        "Challenge Me"
    ])

    # TAB 1: AUTO SUMMARY & INTELLIGENCE
    with tab_summary:
        st.markdown("## Executive Document Summary")
        if not active_api_key:
            st.warning("🔑 API Key Required: Please enter your Google Gemini API Key in the sidebar settings to generate document summaries.")
        else:
            summary_text = st.session_state.summary
            
            if "Quota Exhausted" in summary_text:
                st.error(summary_text)
            elif "API Key Required" in summary_text:
                st.warning(summary_text)
            else:
                st.markdown(summary_text)

            st.markdown("---")

            # Core Takeaways Section
            if st.session_state.takeaways:
                st.markdown("## Core Takeaways")
                for idx, item in enumerate(st.session_state.takeaways, 1):
                    st.markdown(f"**{idx}.** {item}")

                st.markdown("---")

            # Concept Glossary Section
            if st.session_state.glossary:
                import html
                st.markdown("## Key Term Glossary")
                g_col1, g_col2 = st.columns(2)
                for idx, g_item in enumerate(st.session_state.glossary):
                    target_col = g_col1 if idx % 2 == 0 else g_col2
                    clean_term = html.escape(str(g_item.get('term', '')))
                    clean_citation = html.escape(str(g_item.get('citation', '')))
                    clean_def = html.escape(str(g_item.get('definition', '')))
                    with target_col:
                        st.markdown(
                            f"""
                            <div class="glass-card" style="margin-bottom: 12px;">
                                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                                    <strong style="color: #0f172a; font-size: 0.95rem;">{clean_term}</strong>
                                    <span class="citation-badge" style="margin: 0;">{clean_citation}</span>
                                </div>
                                <div style="color: #475569; font-size: 0.86rem; line-height: 1.5;">
                                    {clean_def}
                                </div>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

                st.markdown("---")

            # Mermaid Mind Map Section
            if st.session_state.mindmap:
                st.markdown("## Topic Mind Map")
                with st.expander("View Interactive Topic Hierarchy Diagram", expanded=True):
                    st.markdown(f"```mermaid\n{st.session_state.mindmap}\n```")
        
        st.markdown("## Document Preview")
        with st.expander("View Raw Structured Document Chunks"):
            for chunk in st.session_state.chunks[:10]:
                st.markdown(f"**[{chunk.citation_label}]**: {chunk.text}")
                st.markdown("---")

    # TAB 2: ASK ANYTHING MODE
    with tab_ask:
        st.markdown("## Ask Anything")
        if not active_api_key:
            st.warning("🔑 API Key Required: Please enter your Google Gemini API Key in the sidebar settings to ask questions and receive answers.")
        else:
            q_col1, q_col2 = st.columns([3, 1])
            with q_col1:
                st.markdown("Ask any question. Responses are strictly grounded in the document with explicit citations and highlighted snippets.")
            with q_col2:
                if st.session_state.chat_history:
                    if st.button("Clear Chat History"):
                        st.session_state.chat_history = []
                        save_session_to_disk()
                        st.rerun()

            st.markdown("<br>", unsafe_allow_html=True)

            # Display Chat History Messages
            for message in st.session_state.chat_history:
                if message["role"] == "user":
                    with st.chat_message("user"):
                        user_text = message['content'].strip() if isinstance(message.get('content'), str) else str(message.get('content', ''))
                        st.markdown(f"**{user_text}**")
                else:
                    with st.chat_message("assistant"):
                        if "Quota Exhausted" in message["answer"]:
                            st.error(message["answer"])
                        elif "API Key Required" in message["answer"]:
                            st.warning(message["answer"])
                        else:
                            st.markdown(message["answer"])
                            clean_just = html.escape(str(message.get('justification', '')))
                            st.markdown(
                                f"""
                                <div class="citation-badge">Justification: {clean_just}</div>
                                """,
                                unsafe_allow_html=True
                            )
                            if message.get("snippet"):
                                with st.expander("View Supporting Source Snippet"):
                                    st.markdown(
                                        f"""
                                        <div class="snippet-container">
                                            <div class="snippet-title">Source Passage ({message.get('citation_label', 'Document')})</div>
                                            "{message['snippet']}"
                                        </div>
                                        """,
                                        unsafe_allow_html=True
                                    )

            # User Query Chat Input Box
            user_query = st.chat_input("Ask a question about the uploaded document...")
            if user_query:
                # Save user prompt
                st.session_state.chat_history.append({
                    "role": "user",
                    "content": user_query
                })
                
                # Generate Answer
                with st.spinner("Analyzing document content & citations..."):
                    res = QAEngine.answer_question(
                        query=user_query,
                        retriever=st.session_state.retriever,
                        chat_history=st.session_state.chat_history[:-1],
                        api_key=active_api_key
                    )

                # Save assistant response
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "answer": res["answer"],
                    "justification": res["justification"],
                    "snippet": res["snippet"],
                    "citation_label": res["citation_label"]
                })
                
                save_session_to_disk()
                st.rerun()

    # TAB 3: CHALLENGE ME MODE
    with tab_challenge:
        st.markdown("## Challenge Me Mode")

        if not active_api_key:
            st.warning("🔑 API Key Required: Please enter your Google Gemini API Key in the sidebar settings to generate challenge questions and evaluate responses.")
        else:
            st.markdown("Test your comprehension with AI-generated logic questions. Submit your answers for instant evaluation grounded in document evidence.")
            
            c_top1, c_top2 = st.columns([3, 1])
            with c_top1:
                st.markdown(f"**Total Questions Generated:** {len(st.session_state.challenge_questions)}")
            with c_top2:
                if st.button("Generate 3 More Questions"):
                    with st.spinner("Formulating logic-based challenge questions..."):
                        existing_q_texts = [q["question"] for q in st.session_state.challenge_questions if not q.get("is_error")]
                        new_qs = ChallengeEngine.generate_questions(
                            chunks=st.session_state.chunks,
                            count=3,
                            existing_questions=existing_q_texts,
                            api_key=active_api_key
                        )
                        st.session_state.challenge_questions.extend(new_qs)
                        save_session_to_disk()
                        st.rerun()

            st.markdown("---")

            for q_obj in st.session_state.challenge_questions:
                q_id = q_obj["id"]
                question_text = q_obj["question"]
                is_err = q_obj.get("is_error", False)
                
                if is_err or "Quota Exhausted" in question_text or "API Key Required" in question_text:
                    st.error(question_text)
                    continue

                st.markdown(
                    f"""
                    <div class="glass-card">
                        <div style="font-weight: 600; color: #475569; font-size: 0.82rem; text-transform: uppercase; margin-bottom: 4px;">
                            Question: {q_id}
                        </div>
                        <div style="font-size: 0.95rem; font-weight: 500; color: #0f172a;">
                            {question_text}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                # Response Form for this question (bound to uploaded_file_name for clean reset)
                doc_id = st.session_state.uploaded_file_name or "doc"
                form_key = f"form_{doc_id}_q_{q_id}"
                user_input_key = f"input_{doc_id}_q_{q_id}"
                
                with st.form(key=form_key):
                    user_answer = st.text_area(
                        "Your Answer:",
                        key=user_input_key,
                        placeholder="Type your explanation based on the document...",
                        height=85
                    )
                    submit_btn = st.form_submit_button("Submit Answer for Evaluation")

                    if submit_btn:
                        with st.spinner("Evaluating response against document facts..."):
                            eval_res = ChallengeEngine.evaluate_response(
                                question=question_text,
                                user_response=user_answer,
                                chunks=st.session_state.chunks,
                                api_key=active_api_key
                            )
                            st.session_state.evaluations[q_id] = eval_res
                            save_session_to_disk()

                # Display Evaluation if submitted
                if q_id in st.session_state.evaluations:
                    ev = st.session_state.evaluations[q_id]
                    if "Quota Exhausted" in ev.get("feedback", ""):
                        st.error(ev["feedback"])
                    else:
                        status_color = "score-badge-correct" if "Correct" in ev.get("status", "") else "score-badge-partial"
                        st.markdown(
                            f"""
                            <div class="glass-card" style="border-left: 3px solid #059669; margin-top: -6px;">
                                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                                    <span class="{status_color}">Evaluation: {ev.get('status', 'Evaluated')}</span>
                                    <span style="font-weight: 600; font-size: 0.94rem; color: #0f172a;">Score: {ev.get('score', 'N/A')}</span>
                                </div>
                                <div style="margin-bottom: 6px; color: #334155; font-size: 0.88rem;">
                                    <strong>Feedback:</strong> {ev.get('feedback', '')}
                                </div>
                                <div style="margin-bottom: 6px; color: #334155; font-size: 0.88rem;">
                                    <strong>Ideal Answer:</strong> {ev.get('ideal_answer', '')}
                                </div>
                                <div style="color: #334155; font-size: 0.85rem; font-weight: 500;">
                                    <strong>Document Justification:</strong> {ev.get('justification', '')}
                                </div>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                
                st.markdown("<br>", unsafe_allow_html=True)

# Close lower dashboard content fade container wrapper
st.markdown("</div>", unsafe_allow_html=True)
