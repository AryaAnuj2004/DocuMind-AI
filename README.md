# DocuMind AI — An Intelligent Document Assistant

DocuMind AI is an AI-powered document analysis and interaction tool built with Google Gemini AI and Streamlit. It enables users to upload PDF and TXT documents, generate executive summaries, ask context-grounded questions with precise page citations, extract domain-specific terminology, create visual mind maps, and test their understanding through interactive knowledge challenges.

The system combines document parsing, retrieval-augmented generation (RAG), contextual retrieval, and AI-powered analysis to provide reliable, document-grounded responses while maintaining traceability to the original source content.

---

## ✨ Features

- 📄 **Document Upload & Parsing**: Supports PDF and TXT files with high-fidelity text extraction and page-level chunk tracking.
- 🧠 **AI Executive Summaries**: Generates concise executive summaries along with important key takeaways from uploaded documents.
- 💬 **Grounded Q&A**: Ask natural-language questions and receive context-aware answers based on the uploaded document.
- 📑 **Precise Page Citations**: Provides page references and relevant source snippets to help users verify generated answers.
- 🔍 **RAG-Based Retrieval**: Retrieves relevant document content before generating answers, improving contextual accuracy and reducing unsupported responses.
- 🗺️ **Interactive Mind Maps**: Automatically converts document concepts and relationships into visual mind maps using Mermaid diagrams.
- 📚 **Glossary & Jargon Extraction**: Identifies technical terms, acronyms, and domain-specific terminology and generates their definitions.
- 🎯 **Knowledge Challenge**: Automatically generates multiple-choice and conceptual questions based on document content and evaluates user responses.
- 🔄 **Context-Aware Interaction**: Supports document-based conversations and follow-up questions using retrieved contextual information.
- 📤 **Multi-Format Export**: Export summaries, Q&A history, glossaries, mind maps, and quiz evaluations in Markdown and HTML formats.
- 🌐 **Interactive Streamlit Interface**: Provides a clean and intuitive interface for uploading documents, analyzing content, asking questions, and exploring generated insights.

---

## 📁 Project Structure

```text
DocuMind AI
├── app.py                   # Main Streamlit web application interface
├── requirements.txt         # Project dependencies
├── .env.example             # Example environment configuration template
├── .gitignore               # Git ignore configuration file
├── assets/                  # Application logos and brand assets
│   ├── DocuMind_favicon_rounded.png
│   └── DocuMind_logo_white.png
└── src/                     # Core backend engine modules
    ├── parser.py            # PDF & TXT document parsing & chunking engine
    ├── summarizer.py        # Executive summary & takeaway generator
    ├── retriever.py         # TF-IDF & vector similarity search retriever
    ├── qa_engine.py         # RAG-based Q&A engine with citations
    ├── challenge_engine.py  # Quiz generation & automated evaluation engine
    ├── glossary_engine.py   # Jargon & domain terminology extraction
    ├── mindmap_engine.py    # Structured mind map generator (Mermaid)
    ├── exporter.py          # Report export manager (Markdown, HTML)
    ├── session_cache.py     # Disk-backed session persistence manager
    ├── validator.py         # Gemini API key validation engine
    └── styles.py            # Custom Streamlit CSS design system
```

---

## 🛠️ Tech Stack

- **Frontend / Framework**: [Streamlit](https://streamlit.io/)
- **LLM Provider**: [Google Gemini API](https://ai.google.dev/) (`google-genai` / `google-generativeai`)
- **Document Processing**: `pypdf`, `pdfplumber`
- **Vector Retrieval**: `scikit-learn` (TF-IDF & Cosine Similarity)
- **Environment Management**: `python-dotenv`

---

## 🚀 Quick Start

### 1. Prerequisites
Ensure you have **Python 3.9+** installed on your system.

### 2. Navigate to Project Directory
```bash
cd "DocuMind AI"
```

### 3. Create & Activate a Virtual Environment

**Windows (PowerShell):**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**macOS / Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Configure API Keys
Copy `.env.example` to create a `.env` file in the project root:
```bash
cp .env.example .env
```
Open `.env` and add your **Google Gemini API Key**:
```env
GEMINI_API_KEY=your_actual_gemini_api_key_here
```
*(Alternatively, you can enter your API key directly within the app sidebar at runtime).*

---

## 🏃 Running the Application

Launch the Streamlit web application with:

```bash
streamlit run app.py
```

The app will open automatically in your default browser at `http://localhost:8501`.

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
