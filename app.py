# ============================================================
# app.py
# Phase 4: Web UI Framework - Streamlit Frontend
# ============================================================
# Drives user visibility through a server-side Streamlit
# interface panel containing file-drop configurations,
# canvas-based visualization rendering views, and
# state-retaining recall assessment panels.
# ============================================================

import streamlit as st
import time
import logging
import os
import sys

# ── Ensure project root is on the Python path ──
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.ingestion import PDFIngestionEngine
from core.rag_store import RAGStore
from core.llm_engine import LLMEngine
from core.visualizer import FlowchartVisualizer
from prompts.templates import PromptTemplates
from telemetry.telemetry_manager import TelemetryManager

# ── Configure Logging ──
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)

# ============================================================
# PAGE CONFIGURATION
# ============================================================
st.set_page_config(
    page_title="AI Study Buddy",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# CUSTOM CSS STYLING
# ============================================================
st.markdown("""
<style>
    /* ── Global Theme ── */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
</style>
""", unsafe_allow_html=True)


# ============================================================
# SESSION STATE INITIALIZATION
# ============================================================
def init_session_state():
    """Initialize all Streamlit session state variables."""
    defaults = {
        # ── Pipeline Components ──
        "ingestion_engine": None,
        "rag_store": None,
        "llm_engine": None,
        "visualizer": None,
        "telemetry": None,
        # ── Document State ──
        "document_loaded": False,
        "document_name": "",
        "document_chunks": [],
        "document_id": None,
        "num_pages": 0,
        # ── Feature Results ──
        "summary_notes": "",
        "flowchart_dot": "",
        "flowchart_image": None,
        "qa_history": [],
        "quiz_questions": "",
        "quiz_submitted": False,
        "quiz_feedback": "",
        # ── UI State ──
        "active_tab": "upload",
        "processing": False,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def initialize_components():
    """Lazy-initialize all pipeline components."""
    if st.session_state.ingestion_engine is None:
        st.session_state.ingestion_engine = PDFIngestionEngine(
            chunk_size=500, chunk_overlap=50
        )
    if st.session_state.rag_store is None:
        st.session_state.rag_store = RAGStore(
            model_name="all-MiniLM-L6-v2",
            cache_dir="cache"
        )
    if st.session_state.llm_engine is None:
        st.session_state.llm_engine = LLMEngine(model_name="llama3.2:1b")
    if st.session_state.visualizer is None:
        st.session_state.visualizer = FlowchartVisualizer(output_dir="cache")
    if st.session_state.telemetry is None:
        st.session_state.telemetry = TelemetryManager()


# ============================================================
# SIDEBAR
# ============================================================
def render_sidebar():
    """Render the application sidebar with info and controls."""
    with st.sidebar:
        st.markdown("""
        <div class="sidebar-info">
            <h4>🎓 AI Study Buddy</h4>
            <p>Your privacy-preserving academic assistant. 
            All processing happens locally on your device.</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")

        # ── System Status ──
        st.markdown("### ⚙️ System Status")

        # Check Ollama connection
        llm = st.session_state.llm_engine
        if llm and llm._check_connection():
            st.success("✅ Ollama Connected")
            st.caption(f"Model: `{llm.model_name}`")
        else:
            st.error("❌ Ollama Not Connected")
            st.caption("Run: `ollama serve` and `ollama pull llama3.2:1b`")

        st.markdown("---")

        # ── Document Info ──
        if st.session_state.document_loaded:
            st.markdown("### 📄 Current Document")
            st.info(f"**{st.session_state.document_name}**")
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Pages", st.session_state.num_pages)
            with col2:
                st.metric("Chunks", len(st.session_state.document_chunks))

            if st.button("🗑️ Clear Document", use_container_width=True):
                reset_document_state()
                st.rerun()
        else:
            st.markdown("### 📄 No Document Loaded")
            st.caption("Upload a PDF to get started.")

        st.markdown("---")

        # ── Study Progress ──
        st.markdown("### 📊 Study Progress")
        telemetry = st.session_state.telemetry
        if telemetry:
            total_docs = telemetry.get_total_documents()
            avg_score = telemetry.get_average_quiz_score()
            st.metric("Documents Studied", total_docs)
            st.metric("Avg Quiz Score", f"{avg_score:.0f}%")

        st.markdown("---")
        st.caption("🔒 All data stays on your device")
        st.caption("Powered by Llama 3.2 1B + FAISS")


def reset_document_state():
    """Reset all document-related session state."""
    st.session_state.document_loaded = False
    st.session_state.document_name = ""
    st.session_state.document_chunks = []
    st.session_state.document_id = None
    st.session_state.num_pages = 0
    st.session_state.summary_notes = ""
    st.session_state.flowchart_dot = ""
    st.session_state.flowchart_image = None
    st.session_state.qa_history = []
    st.session_state.quiz_questions = ""
    st.session_state.quiz_submitted = False
    st.session_state.quiz_feedback = ""
    if st.session_state.rag_store:
        st.session_state.rag_store.clear()


# ============================================================
# HEADER
# ============================================================
def render_header():
    """Render the main application header."""
    st.markdown("""
    <div class="main-header">
        <h1>🎓 AI Study Buddy</h1>
        <p>Transform your PDF textbooks into interactive learning roadmaps — 
        completely offline, completely private.</p>
    </div>
    """, unsafe_allow_html=True)


# ============================================================
# PHASE 1: PDF UPLOAD & INGESTION
# ============================================================
def render_upload_tab():
    """Render the PDF upload and processing interface."""
    st.markdown("## 📤 Upload Your Document")
    st.markdown("Upload a PDF file to begin your study session. The document will be "
                "parsed, chunked, and indexed locally for fast retrieval.")

    uploaded_file = st.file_uploader(
        "Choose a PDF file",
        type=["pdf"],
        help="Upload any PDF textbook, research paper, or study material.",
        key="pdf_uploader"
    )

    if uploaded_file is not None and not st.session_state.document_loaded:
        if st.button("🚀 Process Document", type="primary", use_container_width=True):
            process_document(uploaded_file)

    if st.session_state.document_loaded:
        st.markdown("---")
        # ── Success Summary ──
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("""
            <div class="metric-card">
                <h2>{}</h2>
                <p>Pages Extracted</p>
            </div>
            """.format(st.session_state.num_pages), unsafe_allow_html=True)
        with col2:
            st.markdown("""
            <div class="metric-card">
                <h2>{}</h2>
                <p>Text Chunks Created</p>
            </div>
            """.format(len(st.session_state.document_chunks)), unsafe_allow_html=True)
        with col3:
            st.markdown("""
            <div class="metric-card">
                <h2>✅</h2>
                <p>Ready for Study</p>
            </div>
            """, unsafe_allow_html=True)

        st.success(f"✅ **{st.session_state.document_name}** has been processed and indexed. "
                   f"Navigate to the features above to start studying!")


def process_document(uploaded_file):
    """Process the uploaded PDF through Phase 1 & 2 pipeline."""
    start_time = time.time()
    progress_bar = st.progress(0, text="Starting document processing...")

    try:
        # ── Phase 1: Ingestion & Parsing ──
        progress_bar.progress(10, text="📖 Extracting text from PDF...")
        engine = st.session_state.ingestion_engine
        pdf_bytes = uploaded_file.read()

        progress_bar.progress(30, text="✂️ Chunking text into context blocks...")
        chunks = engine.process_pdf(pdf_bytes)

        if not chunks:
            st.error("❌ No text could be extracted from this PDF. "
                     "The document may be image-only or corrupted.")
            return

        # ── Count unique pages ──
        unique_pages = set(c["page_num"] for c in chunks)
        st.session_state.num_pages = len(unique_pages)

        # ── Phase 2: RAG Store Indexing ──
        progress_bar.progress(60, text="🔢 Computing vector embeddings...")
        rag = st.session_state.rag_store
        rag.clear()
        rag.add_documents(chunks)

        progress_bar.progress(85, text="💾 Saving index to disk cache...")
        rag.save_index(filename=uploaded_file.name.replace(".pdf", ""))

        # ── Update Session State ──
        st.session_state.document_loaded = True
        st.session_state.document_name = uploaded_file.name
        st.session_state.document_chunks = chunks

        # ── Phase 5: Telemetry Logging ──
        processing_time = (time.time() - start_time) * 1000
        doc_id = st.session_state.telemetry.log_document_upload(
            filename=uploaded_file.name,
            file_size_bytes=len(pdf_bytes),
            num_pages=st.session_state.num_pages,
            num_chunks=len(chunks),
            processing_time_ms=processing_time
        )
        st.session_state.document_id = doc_id

        progress_bar.progress(100, text="✅ Document processed successfully!")
        time.sleep(0.5)
        progress_bar.empty()

        logger.info(f"Document processed: {uploaded_file.name} → "
                    f"{len(chunks)} chunks in {processing_time:.0f}ms")
        st.rerun()

    except Exception as e:
        progress_bar.empty()
        st.error(f"❌ Error processing document: {str(e)}")
        logger.error(f"Document processing error: {e}", exc_info=True)


# ============================================================
# FEATURE 1: SUMMARY NOTES & FLOWCHARTS
# ============================================================
def render_summary_tab():
    """Render the Summary Notes & Flowchart generation interface."""
    if not st.session_state.document_loaded:
        st.warning("⚠️ Please upload a PDF document first.")
        return

    st.markdown("## 📝 Summary Notes & Flowcharts")
    st.markdown("Generate structured study notes and visual concept flowcharts from your document.")

    col_notes, col_flow = st.columns(2)

    with col_notes:
        st.markdown("### 📋 Summary Notes")
        if st.button("✨ Generate Summary Notes", type="primary",
                      use_container_width=True, key="btn_summary"):
            generate_summary_notes()

        if st.session_state.summary_notes:
            st.markdown("---")
            st.markdown(st.session_state.summary_notes)

    with col_flow:
        st.markdown("### 🔀 Concept Flowchart")
        if st.button("✨ Generate Flowchart", type="primary",
                      use_container_width=True, key="btn_flowchart"):
            generate_flowchart()

        if st.session_state.flowchart_image:
            st.markdown("---")
            st.markdown('<div class="flowchart-container">', unsafe_allow_html=True)
            st.image(st.session_state.flowchart_image, caption="Concept Mind Map",
                     use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

            # ── Download Button ──
            st.download_button(
                label="📥 Download Flowchart",
                data=st.session_state.flowchart_image,
                file_name="flowchart.png",
                mime="image/png",
                use_container_width=True
            )


def generate_summary_notes():
    """Generate summary notes using the LLM with RAG context."""
    start_time = time.time()

    with st.spinner("🤖 Generating summary notes with Llama 3.2..."):
        try:
            # ── Gather context from all chunks (first ~15 chunks for summary) ──
            context_chunks = st.session_state.document_chunks[:15]
            context = "\n\n".join([c["text"] for c in context_chunks])

            # ── Get prompt templates ──
            system_prompt, user_prompt = PromptTemplates.get_summary_prompt(context)

            # ── Generate via LLM ──
            llm = st.session_state.llm_engine
            response = llm.generate(prompt=user_prompt, system_prompt=system_prompt)

            st.session_state.summary_notes = response

            # ── Telemetry ──
            elapsed = (time.time() - start_time) * 1000
            st.session_state.telemetry.log_feature_usage(
                document_id=st.session_state.document_id,
                feature_name="summary_notes",
                response_time_ms=elapsed,
                success=True
            )
            st.rerun()

        except Exception as e:
            st.error(f"❌ Error generating summary: {str(e)}")
            st.session_state.telemetry.log_feature_usage(
                document_id=st.session_state.document_id,
                feature_name="summary_notes",
                response_time_ms=(time.time() - start_time) * 1000,
                success=False,
                error_message=str(e)
            )


def generate_flowchart():
    """Generate a Graphviz DOT flowchart and render it to PNG."""
    start_time = time.time()

    with st.spinner("🤖 Generating concept flowchart..."):
        try:
            # ── Gather context ──
            context_chunks = st.session_state.document_chunks[:10]
            context = "\n\n".join([c["text"] for c in context_chunks])

            # ── Get prompt templates ──
            system_prompt, user_prompt = PromptTemplates.get_flowchart_prompt(context)

            # ── Generate DOT via LLM ──
            llm = st.session_state.llm_engine
            response = llm.generate(prompt=user_prompt, system_prompt=system_prompt)

            # ── Extract and sanitize DOT code ──
            dot_code = llm._extract_dot_code(response)
            visualizer = st.session_state.visualizer
            dot_code = visualizer.sanitize_dot_source(dot_code)

            # ── Validate DOT syntax ──
            is_valid, error_msg = visualizer.validate_dot_syntax(dot_code)
            if not is_valid:
                logger.warning(f"Invalid DOT from LLM: {error_msg}. Using fallback.")
                dot_code = visualizer.create_default_flowchart(
                    title=st.session_state.document_name
                )

            # ── Render to PNG ──
            png_bytes = visualizer.render_dot_to_png(dot_code, filename="flowchart")
            if png_bytes:
                st.session_state.flowchart_dot = dot_code
                st.session_state.flowchart_image = png_bytes

            # ── Telemetry ──
            elapsed = (time.time() - start_time) * 1000
            st.session_state.telemetry.log_feature_usage(
                document_id=st.session_state.document_id,
                feature_name="flowchart",
                response_time_ms=elapsed,
                success=True
            )
            st.rerun()

        except Exception as e:
            st.error(f"❌ Error generating flowchart: {str(e)}")
            st.session_state.telemetry.log_feature_usage(
                document_id=st.session_state.document_id,
                feature_name="flowchart",
                response_time_ms=(time.time() - start_time) * 1000,
                success=False,
                error_message=str(e)
            )


# ============================================================
# FEATURE 2: CONTEXTUAL Q&A
# ============================================================
def render_qa_tab():
    """Render the Contextual Q&A interface with RAG retrieval."""
    if not st.session_state.document_loaded:
        st.warning("⚠️ Please upload a PDF document first.")
        return

    st.markdown("## 💬 Contextual Q&A")
    st.markdown("Ask questions about your document. Answers are generated using "
                "retrieval-augmented generation from your document's content.")

    # ── Question Input ──
    question = st.text_input(
        "Ask a question about your document:",
        placeholder="e.g., What are the main topics covered in this chapter?",
        key="qa_input"
    )

    if st.button("🔍 Get Answer", type="primary",
                  disabled=not question, key="btn_qa"):
        answer_question(question)

    # ── Chat History ──
    if st.session_state.qa_history:
        st.markdown("---")
        st.markdown("### 💬 Conversation History")
        for i, entry in enumerate(reversed(st.session_state.qa_history)):
            with st.expander(f"❓ {entry['question']}", expanded=(i == 0)):
                st.markdown(f"**📖 Retrieved Context (Top {len(entry['sources'])} chunks):**")
                for j, source in enumerate(entry["sources"]):
                    st.caption(f"Chunk {j+1} (Page {source['page_num']}): "
                              f"...{source['text'][:100]}...")
                st.markdown("---")
                st.markdown(f"**🤖 Answer:**")
                st.markdown(entry["answer"])


def answer_question(question: str):
    """Answer a question using RAG retrieval + LLM generation."""
    start_time = time.time()

    with st.spinner("🔍 Searching document and generating answer..."):
        try:
            # ── RAG Retrieval (Phase 2) ──
            rag = st.session_state.rag_store
            results = rag.search(query=question, top_k=5)

            if not results:
                st.warning("No relevant context found in the document for this question.")
                return

            # ── Build context from retrieved chunks ──
            context = "\n\n".join([
                f"[Page {r['page_num']}]: {r['text']}" for r in results
            ])

            # ── Get prompt templates ──
            system_prompt, user_prompt = PromptTemplates.get_qa_prompt(question, context)

            # ── Generate answer via LLM (Phase 3) ──
            llm = st.session_state.llm_engine
            answer = llm.generate(prompt=user_prompt, system_prompt=system_prompt)

            # ── Store in history ──
            st.session_state.qa_history.append({
                "question": question,
                "answer": answer,
                "sources": results
            })

            # ── Telemetry ──
            elapsed = (time.time() - start_time) * 1000
            st.session_state.telemetry.log_feature_usage(
                document_id=st.session_state.document_id,
                feature_name="qa",
                response_time_ms=elapsed,
                success=True
            )
            st.session_state.telemetry.log_qa_session(
                document_id=st.session_state.document_id,
                question=question,
                answer_length=len(answer)
            )
            st.rerun()

        except Exception as e:
            st.error(f"❌ Error generating answer: {str(e)}")
            logger.error(f"Q&A error: {e}", exc_info=True)


# ============================================================
# FEATURE 3: REVISION QUIZ & FEEDBACK
# ============================================================
def render_quiz_tab():
    """Render the Revision Quiz & Feedback interface."""
    if not st.session_state.document_loaded:
        st.warning("⚠️ Please upload a PDF document first.")
        return

    st.markdown("## 📝 Revision Quiz & Feedback")
    st.markdown("Test your understanding with auto-generated quiz questions. "
                "Get targeted feedback on your weak areas.")

    # ── Quiz Generation ──
    if not st.session_state.quiz_questions:
        col1, col2 = st.columns([3, 1])
        with col1:
            num_questions = st.slider("Number of questions", 3, 10, 5, key="quiz_num")
        with col2:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🎯 Generate Quiz", type="primary",
                          use_container_width=True, key="btn_quiz"):
                generate_quiz(num_questions)
    else:
        # ── Display Quiz ──
        st.markdown("---")
        st.markdown('<div class="quiz-container">', unsafe_allow_html=True)
        st.markdown("### 📋 Your Quiz")
        st.markdown(st.session_state.quiz_questions)
        st.markdown('</div>', unsafe_allow_html=True)

        # ── Answer Submission ──
        if not st.session_state.quiz_submitted:
            st.markdown("### ✍️ Your Answers")
            answers = st.text_area(
                "Type your answers below (number each answer to match the questions):",
                height=200,
                placeholder="1. Answer to question 1\n2. Answer to question 2\n...",
                key="quiz_answers"
            )

            col1, col2 = st.columns(2)
            with col1:
                if st.button("📤 Submit Answers", type="primary",
                              use_container_width=True, key="btn_submit_quiz"):
                    if answers.strip():
                        grade_quiz(answers)
                    else:
                        st.warning("Please enter your answers before submitting.")
            with col2:
                if st.button("🔄 New Quiz", use_container_width=True, key="btn_new_quiz"):
                    st.session_state.quiz_questions = ""
                    st.session_state.quiz_submitted = False
                    st.session_state.quiz_feedback = ""
                    st.rerun()

        # ── Display Feedback ──
        if st.session_state.quiz_submitted and st.session_state.quiz_feedback:
            st.markdown("---")
            st.markdown("### 📊 Your Results & Feedback")
            st.markdown(st.session_state.quiz_feedback)

            if st.button("🔄 Take Another Quiz", type="primary",
                          use_container_width=True, key="btn_retake"):
                st.session_state.quiz_questions = ""
                st.session_state.quiz_submitted = False
                st.session_state.quiz_feedback = ""
                st.rerun()


def generate_quiz(num_questions: int):
    """Generate quiz questions from document content."""
    start_time = time.time()

    with st.spinner("🤖 Generating quiz questions..."):
        try:
            # ── Gather context ──
            context_chunks = st.session_state.document_chunks[:12]
            context = "\n\n".join([c["text"] for c in context_chunks])

            # ── Get prompt templates ──
            system_prompt, user_prompt = PromptTemplates.get_quiz_prompt(
                context, num_questions
            )

            # ── Generate via LLM ──
            llm = st.session_state.llm_engine
            quiz = llm.generate(prompt=user_prompt, system_prompt=system_prompt)

            st.session_state.quiz_questions = quiz

            # ── Telemetry ──
            elapsed = (time.time() - start_time) * 1000
            st.session_state.telemetry.log_feature_usage(
                document_id=st.session_state.document_id,
                feature_name="quiz_generation",
                response_time_ms=elapsed,
                success=True
            )
            st.rerun()

        except Exception as e:
            st.error(f"❌ Error generating quiz: {str(e)}")


def grade_quiz(answers: str):
    """Grade quiz answers and provide feedback."""
    start_time = time.time()

    with st.spinner("🤖 Grading your answers..."):
        try:
            # ── Gather context ──
            context_chunks = st.session_state.document_chunks[:12]
            context = "\n\n".join([c["text"] for c in context_chunks])

            # ── Get prompt templates ──
            system_prompt, user_prompt = PromptTemplates.get_grading_prompt(
                questions=st.session_state.quiz_questions,
                answers=answers,
                context=context
            )

            # ── Generate via LLM ──
            llm = st.session_state.llm_engine
            feedback = llm.generate(prompt=user_prompt, system_prompt=system_prompt)

            st.session_state.quiz_feedback = feedback
            st.session_state.quiz_submitted = True

            # ── Telemetry ──
            elapsed = (time.time() - start_time) * 1000
            st.session_state.telemetry.log_feature_usage(
                document_id=st.session_state.document_id,
                feature_name="quiz_grading",
                response_time_ms=elapsed,
                success=True
            )

            # ── Try to extract a score for telemetry ──
            try:
                import re
                score_match = re.search(r'(\d+)%', feedback)
                if score_match:
                    score = float(score_match.group(1))
                    st.session_state.telemetry.log_quiz_result(
                        document_id=st.session_state.document_id,
                        num_questions=5,
                        score_percent=score,
                        weak_areas=""
                    )
            except Exception:
                pass

            st.rerun()

        except Exception as e:
            st.error(f"❌ Error grading quiz: {str(e)}")


# ============================================================
# MAIN APPLICATION LAYOUT
# ============================================================
def main():
    """Main application entry point."""
    # ── Initialize ──
    init_session_state()
    initialize_components()

    # ── Render Layout ──
    render_sidebar()
    render_header()

    # ── Feature Pipeline Indicator ──
    if st.session_state.document_loaded:
        st.markdown("---")
        cols = st.columns(4)
        steps = [
            ("✅ PDF Uploaded", True),
            ("📝 Summary & Flowchart", bool(st.session_state.summary_notes)),
            ("💬 Q&A Ready", bool(st.session_state.qa_history)),
            ("📝 Quiz Complete", st.session_state.quiz_submitted),
        ]
        for col, (label, done) in zip(cols, steps):
            with col:
                if done:
                    st.success(label)
                else:
                    st.info(label)

    # ── Main Tabs ──
    tab_upload, tab_summary, tab_qa, tab_quiz = st.tabs([
        "📤 Upload PDF",
        "📝 Summary & Flowchart",
        "💬 Contextual Q&A",
        "📝 Revision Quiz"
    ])

    with tab_upload:
        render_upload_tab()

    with tab_summary:
        render_summary_tab()

    with tab_qa:
        render_qa_tab()

    with tab_quiz:
        render_quiz_tab()


# ============================================================
# RUN APPLICATION
# ============================================================
if __name__ == "__main__":
    main()
