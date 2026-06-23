# 🎓 AI Study Buddy

Transform PDF textbooks into interactive learning journeys — completely offline and privacy-preserving.

## Theme

**AI-Powered Education**

---

## Team Name

AI Study Buddy Team

## Team Members

| Name | TECH ID |
|--------|----------|
| Yash Kumar | 256309 |
| Tasviraj Chauhan | A96EB0 |
| Shubham | C15DF1 |
| Yash Purohit | C15DDC |

---

## Features

- 📄 PDF Upload and Processing
- 📝 AI-Generated Summary Notes
- 🔀 Concept Flowchart Generation
- 💬 Context-Aware Question Answering
- 🧠 Active Recall Quiz Generation
- 📊 Smart Feedback System
- 🔒 Fully Local and Privacy-Preserving

---

## Tech Stack

### Frontend
- Streamlit

### Backend
- Python

### AI Models
- Ollama
- Llama 3.2 1B

### Vector Store
- FAISS

### PDF Processing
- PyPDF
- PDFPlumber

### Visualization
- Graphviz
- PyVis

### Embedding Model
- all-MiniLM-L6-v2

---

## Project Structure

```text
AI-Study-Buddy/
│
├── app.py
├── core/
├── prompts/
├── telemetry/
├── cache/
├── README.md
├── PRD.md
├── Contribution.md
├── requirements.txt
└── .gitignore
```

---

## Setup Instructions

### 1. Clone the Repository

```bash
git clone <repository-url>
cd AI-Study-Buddy
```

### 2. Create a Virtual Environment

#### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

#### Linux / MacOS

```bash
python -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Install Ollama

Download and install Ollama.

Start Ollama:

```bash
ollama serve
```

Pull the model:

```bash
ollama pull llama3.2:1b
```

### 5. Run the Application

```bash
streamlit run app.py
```

---

## Workflow

1. Upload a PDF.
2. Generate summary notes and flowcharts.
3. Ask questions related to the document.
4. Attempt active recall quizzes.
5. Receive AI-generated feedback.

---

## Future Scope

- Multi-document support
- ChromaDB integration
- Vision-enabled models
- Model quantization for faster inference

---

## License

Developed for **TechPreneur 2026**.