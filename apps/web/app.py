import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[2]))
import streamlit as st
import json
from apps.api.nlp.parse_pdf import parse_pdf_to_sections
from apps.api.rag.retrieve import SimpleStore
from apps.api.rag.generate import summarize_paper
from apps.api.core.config import settings
from apps.api.features.multi_doc_comparison import MultiDocComparator
from apps.api.features.meta_analysis import MetaAnalysisExtractor
from apps.api.features.pdf_exporter import PDFReportGenerator

st.set_page_config(page_title="Medical Research Intelligence System", page_icon="🧪", layout="wide")
st.title("🧪 Medical Research Intelligence System v2.0")
st.caption("Upload PDFs → Parse → Ask questions → Compare → Export Reports")

with st.sidebar:
    st.header("⚙️ Settings")
    st.write("Embed model:", settings.HF_EMBED_MODEL)
    st.write("Summarizer model:", settings.HF_SUMMARIZER_MODEL)
    st.write("Storage:", settings.STORAGE_DIR)
    st.divider()
    st.info("✨ New Features:\n- Multi-doc comparison\n- Meta-analysis extraction\n- PDF report export")

# ============== SECTION 1: Upload & Parse ==============
st.subheader("📤 Section 1: Upload & Parse PDFs")
col1, col2 = st.columns(2)

with col1:
    files = st.file_uploader("Drag & drop PDFs", type=["pdf"], accept_multiple_files=True)
    if files:
        out_dir = Path(settings.STORAGE_DIR) / "pdfs"
        out_dir.mkdir(parents=True, exist_ok=True)
        for f in files:
            (out_dir / f.name).write_bytes(f.read())
        st.success(f"✅ Uploaded {len(files)} file(s).")

with col2:
    if st.button("🔄 Parse PDFs Now", type="primary", use_container_width=True):
        pdf_dir = Path(settings.STORAGE_DIR) / "pdfs"
        out_dir = Path(settings.STORAGE_DIR) / "parsed"
        out_dir.mkdir(parents=True, exist_ok=True)
        n = 0
        progress_bar = st.progress(0)
        for i, pdf in enumerate(list(pdf_dir.glob("*.pdf"))):
            parsed = parse_pdf_to_sections(pdf)
            (out_dir / f"{pdf.stem}.json").write_text(json.dumps(parsed, ensure_ascii=False), encoding="utf-8")
            n += 1
            progress_bar.progress((i + 1) / len(list(pdf_dir.glob("*.pdf"))))
        st.success(f"✅ Ingested {n} file(s).")

parsed_dir = Path(settings.STORAGE_DIR) / "parsed"
papers = sorted(parsed_dir.glob("*.json"))

with st.expander("📚 Paper Library", expanded=True):
    if not papers:
        st.info("No parsed papers yet. Upload and parse PDFs first.")
    else:
        for p in papers:
            j = json.loads(p.read_text(encoding="utf-8"))
            st.markdown(f"- **{j.get('title', p.stem)}** — `{j.get('paper_id', p.stem)}` — {len(j.get('sections', []))} sections")

st.divider()

# ============== SECTION 2: Single Paper Q&A ==============
st.subheader("❓ Section 2: Ask a Question (Single Paper)")
col1, col2 = st.columns([3, 1])

with col1:
    q = st.text_input("Your question", placeholder="What is the main conclusion?")

with col2:
    k = st.slider("Evidence chunks", 2, 10, 6, label_visibility="collapsed")

if st.button("🔍 Get Answer", type="primary", use_container_width=True) and q:
    with st.status("⏳ Generating answer...", expanded=True):
        store = SimpleStore(parsed_dir)
        ctxs = store.search(q, top_k=k)
        
        if not ctxs:
            st.error("❌ No relevant evidence found.")
        else:
            # Prepare context for summarization
            context_text = " ".join([c['text'] for c in ctxs])
            ans = summarize_paper(context_text, question=q)
            
            st.markdown("### 📝 Answer")
            st.write(ans)
            
            with st.expander("📖 Evidence & Citations"):
                for i, c in enumerate(ctxs, 1):
                    st.markdown(f"**[{i}]** `{c['meta']['source']}` — *{c['meta']['section']}*")
                    st.caption(c['text'][:600] + ('...' if len(c['text']) > 600 else ''))
            
            # Export single answer as report
            if st.button("💾 Export as Report"):
                exporter = PDFReportGenerator()
                report_path = exporter.export_to_markdown(
                    title=f"Research Summary: {q[:50]}",
                    query=q,
                    answer=ans,
                    citations=[{"source": c['meta']['source'], "section": c['meta']['section'], "text": c['text']} for c in ctxs],
                    paper_sources=[c['meta']['source'] for c in ctxs]
                )
                st.success(f"✅ Report saved to: `{report_path}`")
                st.info("💡 Tip: Convert markdown to PDF using: `pandoc report.md -o report.pdf`")

st.divider()

# ============== SECTION 3: Single Paper Summarization ==============
st.subheader("📄 Section 3: Summarize a Paper")
ids = [p.stem for p in papers]

if ids:
    col1, col2 = st.columns([2, 1])
    with col1:
        chosen = st.selectbox("Choose paper", ids, index=0)
    with col2:
        mode = st.radio("Audience", ["expert", "patient"], horizontal=True, label_visibility="collapsed")
    
    if st.button("📋 Generate Summary", type="primary", use_container_width=True):
        j = json.loads((parsed_dir / f"{chosen}.json").read_text(encoding="utf-8"))
        ctxs = [{"text": s["text"], "meta": {"source": f"{chosen}.json", "section": s["name"]}} for s in j.get("sections", [])]
        prompt = f"Summarize this paper for a {'researcher' if mode == 'expert' else 'patient'}."
        summ = summarize_paper(" ".join([c['text'] for c in ctxs]), question=prompt)
        
        st.markdown("### 📌 Summary")
        st.write(summ)
        
        # Export summary as report
        if st.button("💾 Export Summary as Report"):
            exporter = PDFReportGenerator()
            report_path = exporter.export_to_markdown(
                title=f"Paper Summary: {chosen}",
                query=prompt,
                answer=summ,
                citations=[c['meta'] for c in ctxs],
                paper_sources=[chosen]
            )
            st.success(f"✅ Report saved to: `{report_path}`")
else:
    st.info("No papers to summarize yet.")

st.divider()

# ============== SECTION 4: Multi-Document Comparison ==============
st.subheader("🔀 Section 4: Compare Multiple Papers")

if len(papers) >= 2:
    col1, col2 = st.columns([2, 1])
    
    with col1:
        comparison_query = st.text_input(
            "Comparison question",
            placeholder="What are the treatment outcomes across papers?",
            key="comparison_query"
        )
    
    with col2:
        selected_papers = st.multiselect(
            "Select papers to compare",
            options=[p.stem for p in papers],
            default=[p.stem for p in papers[:min(3, len(papers))]]
        )
    
    if st.button("⚖️ Compare Papers", type="primary", use_container_width=True) and comparison_query and selected_papers:
        with st.status("⏳ Analyzing papers...", expanded=True):
            comparator = MultiDocComparator(parsed_dir)
            result = comparator.compare_papers(
                query=comparison_query,
                paper_ids=selected_papers,
                top_k=5
            )
            
            st.markdown("### 📊 Comparison Results")
            
            # Findings by paper
            with st.expander("📖 Findings by Paper"):
                for pid, finding in result.findings.items():
                    st.markdown(f"**{pid}**")
                    st.write(finding)
            
            # Consensus
            if result.consensus:
                with st.expander("✅ Consensus (Common Themes)"):
                    for theme in result.consensus:
                        st.markdown(f"- {theme}")
            
            # Contradictions
            if result.contradictions:
                with st.expander("⚠️ Potential Contradictions"):
                    st.warning("The following papers appear to have conflicting findings:")
                    for p1, p2 in result.contradictions:
                        st.markdown(f"- **{p1}** vs **{p2}**")
            
            # Unique findings
            if result.unique_findings:
                with st.expander("🔍 Unique Findings"):
                    for pid, finding in result.unique_findings.items():
                        st.markdown(f"**{pid}**: {finding[:200]}...")
            
            # Export comparison report
            if st.button("💾 Export Comparison Report"):
                exporter = PDFReportGenerator()
                report_path = exporter.export_comparison_report(
                    title=f"Paper Comparison: {comparison_query[:50]}",
                    query=comparison_query,
                    findings_by_paper=result.findings,
                    consensus=result.consensus,
                    contradictions=result.contradictions,
                    unique_findings=result.unique_findings
                )
                st.success(f"✅ Report saved to: `{report_path}`")
            
            # Display comparison table
            st.markdown("### 📋 Comparison Table")
            st.markdown(comparator.generate_comparison_table(result))

else:
    st.info(f"Need at least 2 papers to compare. Currently have {len(papers)}.")

st.divider()

# ============== SECTION 5: Meta-Analysis Extraction ==============
st.subheader("📊 Section 5: Meta-Analysis Extraction")

if papers:
    if st.button("🔬 Extract Study Metrics", type="primary", use_container_width=True):
        with st.status("⏳ Extracting metrics from all papers...", expanded=True):
            extractor = MetaAnalysisExtractor(parsed_dir)
            metrics = extractor.extract_study_metrics()
            
            st.markdown("### 📈 Extracted Study Metrics")
            
            # Metrics table
            with st.expander("📋 Study Metrics Table"):
                st.markdown(extractor.generate_meta_analysis_table(metrics))
            
            # Summary statistics
            with st.expander("📊 Summary Statistics"):
                st.markdown(extractor.generate_summary_stats(metrics))
            
            # Export meta-analysis report
            if st.button("💾 Export Meta-Analysis Report"):
                exporter = PDFReportGenerator()
                report_path = exporter.export_meta_analysis_report(
                    title="Meta-Analysis of Study Metrics",
                    metrics_table=extractor.generate_meta_analysis_table(metrics),
                    summary_stats=extractor.generate_summary_stats(metrics),
                    analysis_notes="Metrics extracted using automated pattern matching. Manual review recommended."
                )
                st.success(f"✅ Report saved to: `{report_path}`")
            
            # Detailed metrics view
            with st.expander("🔍 Detailed Metrics by Paper"):
                for m in metrics:
                    with st.expander(f"📄 {m.paper_id}"):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.metric("Sample Size", m.sample_size or "N/A")
                            st.metric("Study Type", m.study_type or "N/A")
                            st.metric("Treatment", (m.treatment[:30] + "...") if m.treatment and len(m.treatment) > 30 else (m.treatment or "N/A"))
                        with col2:
                            st.metric("Efficacy Rate", f"{m.efficacy_rate}%" if m.efficacy_rate else "N/A")
                            st.metric("P-Value", m.statistical_significance or "N/A")
                            st.metric("Follow-up", m.follow_up_duration or "N/A")
                        
                        if m.side_effects:
                            st.markdown("**Side Effects:**")
                            for effect in m.side_effects:
                                st.write(f"- {effect}")

else:
    st.info("No papers available. Upload and parse PDFs first.")

st.divider()

# ============== SECTION 6: Reports & Export ==============
st.subheader("📁 Section 6: Saved Reports")

reports_dir = Path(settings.STORAGE_DIR) / ".." / "reports"
if reports_dir.exists():
    reports = list(reports_dir.glob("*.md")) + list(reports_dir.glob("*.json"))
    if reports:
        st.success(f"Found {len(reports)} saved reports")
        for report in sorted(reports, reverse=True)[:10]:
            col1, col2 = st.columns([4, 1])
            with col1:
                st.markdown(f"📄 `{report.name}`")
            with col2:
                with open(report, 'r') as f:
                    st.download_button(
                        "⬇️",
                        f.read(),
                        file_name=report.name,
                        mime="text/markdown" if report.suffix == ".md" else "application/json"
                    )
    else:
        st.info("No reports generated yet. Use the sections above to generate reports.")
else:
    st.info("Reports directory not found. Generate your first report to create it.")

st.divider()

# Footer
st.markdown("---")
st.markdown("""
### 🚀 Features
- ✅ **Single Paper Q&A** - Ask questions about individual papers
- ✅ **Multi-Document Comparison** - Compare findings across papers
- ✅ **Meta-Analysis Extraction** - Extract and compare study metrics
- ✅ **PDF Report Export** - Export findings as professional reports

### 📖 Convert Markdown to PDF
```bash
pip install pandoc
pandoc report.md -o report.pdf
```

### 💡 Tips
- Use the sidebar to adjust embedding and summarization models
- Multi-doc comparison works best with 2-5 papers
- Meta-analysis extraction uses regex patterns; review results manually
""")
