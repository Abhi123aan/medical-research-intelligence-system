# 🧠 Medical Research Summarizer & Intelligence System

A **local, offline GPT-like assistant** that summarizes and answers questions from uploaded **medical research papers** — built entirely with open-source Hugging Face models, no paid APIs or GPU required.

---

## ⚙️ Overview

This project demonstrates how to build a lightweight **Retrieval-Augmented Generation (RAG)** pipeline on CPU using open-source models.

Users can:
- ✅ Upload research PDFs  
- ✅ Ask domain-specific questions (e.g., *"What treatment is recommended?"*)  
- ✅ Receive concise, citation-linked answers generated locally  
- ✅ **Compare findings across multiple papers** (v2.0+)
- ✅ **Extract key study metrics** (v2.0+)
- ✅ **Export professional PDF reports with citations** (v2.0+)

All processing — PDF parsing, retrieval, embedding, and summarization — happens fully on your machine.

---

## 🧩 Architecture

```
apps/
├── api/
│   ├── core/
│   │   └── config.py        ← Loads global .env and paths
│   ├── nlp/
│   │   └── parse_pdf.py     ← Converts PDFs → JSON (sections & sentences)
│   ├── rag/
│   │   ├── embed.py         ← Sentence embeddings via MiniLM
│   │   ├── retrieve.py      ← Hybrid BM25 + semantic retriever
│   │   └── generate.py      ← Summarization / answer generation
│   └── features/            ← NEW v2.0: Advanced features
│       ├── multi_doc_comparison.py  ← Compare multiple papers
│       ├── meta_analysis.py         ← Extract study metrics
│       └── pdf_exporter.py          ← Generate PDF reports
└── web/
    └── app.py               ← Streamlit web interface (UPDATED v2.0)

.env / global.env            ← API keys or model names (never commit)
requirements.txt             ← Dependencies
examples_usage.py            ← Example scripts for all features (NEW v2.0)
README.md                    ← This file
```

---

## 🧠 How It Works

### 🔵 CORE (Original - Still Essential)

#### 1️⃣ PDF Parsing (`parse_pdf.py`)
- Extracts text with **PyMuPDF** and regex cleaning
- Splits content into structured sections

```json
{
  "paper_id": "breast-cancer-meta-analysis",
  "sections": [
    {"name": "Abstract", "text": "..."},
    {"name": "Results",  "text": "..."},
    {"name": "Conclusion","text": "..."}
  ]
}
```

Parsed outputs live in `data/parsed/`.

---

#### 2️⃣ Embedding & Retrieval (`embed.py`, `retrieve.py`)
- Uses **Sentence-Transformers MiniLM-L6-v2** for semantic vectors.  
- **BM25** ranks lexical overlap; **MMR** ensures diverse top-k evidence.
- Combines lexical + semantic + section weighting for better context selection.

---

#### 3️⃣ Summarization (`generate.py`)
- Abstractive summarization via **DistilBART-CNN** (default).
- Chunked batching for long texts to stay within CPU limits.
- Cleans citations and formats readable paragraphs.
- Falls back to extractive summaries if abstractive fails.

---

#### 4️⃣ Frontend (`app.py`)
A **Streamlit** dashboard providing:
- Paper upload & parsing  
- Question box  
- Instant answer + cited evidence view  
- Audience switch (*Expert / Patient*)  

Everything executes locally — no network calls.

---

### 🟢 NEW FEATURES (v2.0+)

#### 5️⃣ Multi-Document Comparison (`multi_doc_comparison.py`) 📊
Compare findings across multiple papers at once:
- Side-by-side evidence analysis
- Identify **consensus** (common themes across papers)
- Detect **contradictions** (conflicting findings)
- Extract **unique findings** per paper
- Generate comparison tables

#### 6️⃣ Meta-Analysis Extraction (`meta_analysis.py`) 📈
Automatically extract and compare key metrics:
- **Sample sizes** across studies
- **Treatment protocols** and interventions
- **Efficacy rates** and outcomes
- **Side effects** frequency
- **Statistical significance** (p-values)
- **Follow-up durations**
- Auto-generated meta-analysis tables

#### 7️⃣ PDF Report Export (`pdf_exporter.py`) 📄
Export answers as professional reports with full citations:
- **Markdown reports** with citations and evidence
- **JSON export** for structured data
- **BibTeX format** for reference managers
- **Multiple report types**: Single answer, Comparison, Meta-analysis
- Professional formatting with disclaimers

---

## 🏗️ Core Concepts

| Concept | Explanation |
|----------|--------------|
| **RAG (Retrieval-Augmented Generation)** | Combines search + generation for grounded answers. |
| **BM25** | Classical keyword ranking (term-frequency / inverse-doc-freq). |
| **Sentence Transformer** | Embeds sentences into dense semantic vectors. |
| **MMR** | *Maximal Marginal Relevance* to keep retrieved evidence diverse. |
| **DistilBART** | Lightweight summarization transformer ideal for CPUs. |
| **Multi-Document Comparison** | Analyzes findings across multiple papers to identify consensus & contradictions. |
| **Meta-Analysis** | Extracts and compares key study metrics (N, efficacy, p-values). |

---

## 💡 Design Philosophy

- **Educational →** transparent end-to-end RAG example  
- **Local-first →** no API keys or GPU dependency  
- **Extensible →** swap models or add new features easily  
- **Transparent →** inspect every intermediate step  
- **Production-ready →** professional report generation with citations (v2.0+)

---

## 📁 Workflow Examples

### Basic Workflow (Core Feature)

1️⃣ Parse your PDF  
```bash
python -m apps.api.nlp.parse_pdf "data/raw/Immunotherapy_Cancer_Treatment.pdf"
```
Produces `data/parsed/immunotherapy_cancer_treatment.json`.

2️⃣ Run the app  
```bash
streamlit run apps/web/app.py
```

3️⃣ Use the web UI  
- Upload & parse PDFs
- Ask questions like *"What are the main findings?"*  
- View summarized answers + source snippets  

---

### Advanced Workflows (v2.0+ Features)

#### Multi-Document Comparison
```python
from pathlib import Path
from apps.api.features.multi_doc_comparison import MultiDocComparator

parsed_dir = Path("data/parsed")
comparator = MultiDocComparator(parsed_dir)

result = comparator.compare_papers(
    query="What are the treatment outcomes?",
    paper_ids=["cancer_study_1", "cancer_study_2", "cancer_study_3"],
    top_k=5
)

print(comparator.generate_comparison_table(result))
```

#### Meta-Analysis Extraction
```python
from pathlib import Path
from apps.api.features.meta_analysis import MetaAnalysisExtractor

parsed_dir = Path("data/parsed")
extractor = MetaAnalysisExtractor(parsed_dir)

metrics = extractor.extract_study_metrics()
print(extractor.generate_meta_analysis_table(metrics))
print(extractor.generate_summary_stats(metrics))
```

#### Q&A with PDF Report Export
```python
from pathlib import Path
from apps.api.rag.retrieve import SimpleStore
from apps.api.rag.generate import summarize_paper
from apps.api.features.pdf_exporter import PDFReportGenerator

parsed_dir = Path("data/parsed")
exporter = PDFReportGenerator()

store = SimpleStore(parsed_dir)
contexts = store.search("What is the treatment protocol?", top_k=6)
context_text = " ".join([c['text'] for c in contexts])
answer = summarize_paper(context_text, question="What is the treatment protocol?")

report_path = exporter.export_to_markdown(
    title="Treatment Protocol Analysis",
    query="What is the treatment protocol?",
    answer=answer,
    citations=[{"source": c['meta']['source'], "section": c['meta']['section'], "text": c['text']} for c in contexts]
)
```

#### Run All Examples
```bash
python examples_usage.py

# Select:
# 1. Basic Q&A (single paper)
# 2. Multi-document comparison
# 3. Meta-analysis extraction
# 4. Q&A with PDF export
# 5. End-to-end workflow
# 6. Run all examples
```

---

## ⚡ Performance Notes

| Metric | Approx Value |
|--------:|--------------|
| CPU latency (single query) | 5 – 15 s |
| CPU latency (multi-doc comparison) | 10 – 25 s |
| CPU latency (meta-analysis extraction) | 3 – 10 s |
| RAM usage | < 1 GB |
| Disk cache | ~500 MB (HF models + embeddings) |

### Tips to speed up
- Reduce `top_k` in retriever (e.g. 6 → 4)  
- Lower `max_words` chunk size in `generate.py`  
- Switch to `sshleifer/distilbart-cnn-12-6` (smaller model)  
- Run on GPU if available → set `device=0`
- Cache retrieval results for repeated queries

---

## 🧰 Extending the App

| Goal | File to edit | Hint |
|------|---------------|------|
| Use another summarizer | `generate.py` | Change model in `pipeline()` |
| Tune section weights | `retrieve.py` | Adjust `SECTION_WEIGHTS` |
| Add new prompt style | `generate.py` | Edit `summarize_paper()` |
| Enable GPU | `generate.py` | Set `device=0` in pipeline init |
| Cache retrieval results | `retrieve.py` | Decorate `search()` with `lru_cache` |
| Add new metric extraction | `meta_analysis.py` | Add regex pattern in `_extract_*()` methods |
| Custom contradiction detection | `multi_doc_comparison.py` | Modify `_find_contradictions()` |
| Support additional export formats | `pdf_exporter.py` | Add new `export_*()` method |

---

## 🧠 Learning Outcomes

By studying this repo you'll grasp:
- How RAG pipelines combine retrieval + generation  
- Integrating Hugging Face pipelines for CPU inference  
- Designing transparent, educational AI tools  
- Structuring research summarization apps end-to-end  
- **Multi-document analysis and comparison** (v2.0+)
- **Automated metric extraction from research papers** (v2.0+)
- **Professional report generation with citations** (v2.0+)

---

## 🎯 Web UI Features (Streamlit)

The Streamlit app now includes:

### Section 1: Upload & Parse
- Drag-and-drop PDF upload
- Automatic parsing to JSON
- Paper library view

### Section 2: Single Paper Q&A ⭐ (Core)
- Ask questions about papers
- Adjustable evidence chunks
- Citation tracking
- One-click report export

### Section 3: Paper Summarization ⭐ (Core)
- Summarize full papers
- Choose audience (expert/patient)
- Generate executive summaries

### Section 4: Multi-Document Comparison (v2.0+)
- Compare 2+ papers side-by-side
- View consensus & contradictions
- Export comparison reports

### Section 5: Meta-Analysis Extraction (v2.0+)
- Auto-extract study metrics
- Sample sizes, efficacy rates, p-values
- Summary statistics tables
- Detailed metrics view

### Section 6: Reports & Export (v2.0+)
- View all generated reports
- Download Markdown/JSON/BibTeX
- Convert to PDF with pandoc

---

## 📖 Convert Markdown Reports to PDF

```bash
# Install pandoc (one-time)
# Windows: choco install pandoc
# Mac: brew install pandoc
# Linux: sudo apt install pandoc

# Convert any generated report
pandoc report.md -o report.pdf

# With custom styling
pandoc report.md -o report.pdf --css=style.css -V colorlinks
```

---

## 🙌 Authors & Credits

**Original Development:** Suha Roy  
**Enhanced by (v2.0):** Multi-document comparison, Meta-analysis extraction, PDF export features

Models from [Hugging Face Hub](https://huggingface.co/)  
Example papers from *Indian Journal of Medical Research (IJMR)*.  

Educational project showcasing open-source RAG for medical literature.

---

## 🚀 Quick Start

```bash
# Clone
git clone https://github.com/Abhi123aan/medical-research-intelligence-system
cd medical-research-intelligence-system

# Create venv
python -m venv .venv
.\.venv\Scripts\activate      # on Windows
# or
source .venv/bin/activate     # on Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Parse your PDFs
python -m apps.api.nlp.parse_pdf "data/raw/<your_paper>.pdf"

# Run the local web app
streamlit run apps/web/app.py
```

Once launched, open [http://localhost:8501](http://localhost:8501) in your browser.

### Try Example Scripts

```bash
# Run example workflows
python examples_usage.py
```

---

## 📦 Dependencies

```
fastapi
uvicorn[standard]
pydantic
pydantic-settings
python-multipart
PyMuPDF          # PDF parsing
numpy
requests
httpx
streamlit        # Web interface
torch
transformers     # HF models
sentence-transformers  # Embeddings
python-dotenv
rank-bm25        # BM25 retrieval
scispaCy         # Scientific NLP
reportlab        # PDF generation
```

---

## ⚖️ Disclaimer

This system is for **educational and research purposes only**. The AI-generated summaries and comparisons should not be used as primary medical advice. Always:
- ✅ Consult original research papers
- ✅ Verify findings with domain experts
- ✅ Follow institutional review protocols
- ✅ Respect patient privacy and data protection

---

## 📝 License

MIT License - See LICENSE file for details

---

## 🎯 Roadmap

- [x] Core RAG system ✅ **DONE**
- [x] Streamlit web UI ✅ **DONE**
- [x] Multi-document comparison ✅ **DONE (v2.0)**
- [x] Meta-analysis extraction ✅ **DONE (v2.0)**
- [x] PDF report export ✅ **DONE (v2.0)**
- [x] Example scripts ✅ **DONE (v2.0)**
- [ ] Direct PDF export button (integrate pandoc)
- [ ] Database for caching embeddings
- [ ] API endpoint for external integration
- [ ] Fine-tuned summarizer for medical text
- [ ] Support for tables & figures extraction
- [ ] Clinical trial tracker feature
- [ ] Multi-language support
- [ ] Docker containerization

---

**Questions or Issues?** Open an issue on GitHub!
