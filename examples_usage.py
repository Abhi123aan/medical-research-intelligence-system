"""
Example Usage Scripts for Medical Research Intelligence System v2.0
"""

from pathlib import Path
from apps.api.nlp.parse_pdf import parse_pdf_to_sections
from apps.api.rag.retrieve import SimpleStore
from apps.api.rag.generate import summarize_paper
from apps.api.features.multi_doc_comparison import MultiDocComparator
from apps.api.features.meta_analysis import MetaAnalysisExtractor
from apps.api.features.pdf_exporter import PDFReportGenerator


def example_1_basic_qa():
    """Example 1: Basic Q&A on a single paper"""
    print("\n" + "="*60)
    print("EXAMPLE 1: Basic Q&A on Single Paper")
    print("="*60)
    
    parsed_dir = Path("data/parsed")
    
    # Initialize retriever
    store = SimpleStore(parsed_dir)
    
    # Ask a question
    query = "What are the main treatment options?"
    contexts = store.search(query, top_k=6)
    
    if contexts:
        # Generate answer
        context_text = " ".join([c['text'] for c in contexts])
        answer = summarize_paper(context_text, question=query)
        
        print(f"\n❓ Question: {query}")
        print(f"\n📝 Answer: {answer}")
        print(f"\n📖 Evidence from {len(contexts)} sources")
        for i, ctx in enumerate(contexts, 1):
            print(f"   [{i}] {ctx['meta']['source']} ({ctx['meta']['section']})")


def example_2_multi_document_comparison():
    """Example 2: Compare findings across multiple papers"""
    print("\n" + "="*60)
    print("EXAMPLE 2: Multi-Document Comparison")
    print("="*60)
    
    parsed_dir = Path("data/parsed")
    
    # Initialize comparator
    comparator = MultiDocComparator(parsed_dir)
    
    # Get all available papers
    all_papers = list(comparator.papers.keys())
    print(f"\n📚 Available papers: {all_papers}")
    
    if len(all_papers) >= 2:
        # Compare papers
        query = "What are the treatment outcomes?"
        print(f"\n🔀 Comparing papers on: {query}")
        
        result = comparator.compare_papers(
            query=query,
            paper_ids=all_papers[:3],  # Compare first 3 papers
            top_k=5
        )
        
        print(f"\n✅ Papers analyzed: {result.papers_analyzed}")
        
        # Show findings
        print("\n📖 Findings by Paper:")
        for pid, finding in result.findings.items():
            print(f"  {pid}: {finding[:100]}...")
        
        # Show consensus
        if result.consensus:
            print(f"\n✅ Consensus themes: {', '.join(result.consensus[:3])}")
        
        # Show contradictions
        if result.contradictions:
            print(f"\n⚠️ Potential contradictions: {len(result.contradictions)}")
            for p1, p2 in result.contradictions:
                print(f"   {p1} vs {p2}")
        
        # Generate table
        print("\n📋 Comparison Table:")
        print(comparator.generate_comparison_table(result))
        
        # Export report
        exporter = PDFReportGenerator()
        report_path = exporter.export_comparison_report(
            title="Treatment Outcomes Comparison",
            query=query,
            findings_by_paper=result.findings,
            consensus=result.consensus,
            contradictions=result.contradictions,
            unique_findings=result.unique_findings
        )
        print(f"\n💾 Report saved: {report_path}")
    else:
        print("\n⚠️ Need at least 2 papers to compare")


def example_3_meta_analysis():
    """Example 3: Extract and compare study metrics"""
    print("\n" + "="*60)
    print("EXAMPLE 3: Meta-Analysis Extraction")
    print("="*60)
    
    parsed_dir = Path("data/parsed")
    
    # Initialize extractor
    extractor = MetaAnalysisExtractor(parsed_dir)
    
    # Extract metrics from all papers
    print("\n🔬 Extracting study metrics...")
    metrics = extractor.extract_study_metrics()
    
    print(f"✅ Extracted metrics from {len(metrics)} papers\n")
    
    # Display metrics table
    print("📈 Study Metrics Table:")
    print(extractor.generate_meta_analysis_table(metrics))
    
    # Display summary statistics
    print("\n📊 Summary Statistics:")
    print(extractor.generate_summary_stats(metrics))
    
    # Export report
    exporter = PDFReportGenerator()
    report_path = exporter.export_meta_analysis_report(
        title="Meta-Analysis of Study Metrics",
        metrics_table=extractor.generate_meta_analysis_table(metrics),
        summary_stats=extractor.generate_summary_stats(metrics),
        analysis_notes="Metrics extracted using automated pattern matching. Manual review of original papers recommended."
    )
    print(f"\n💾 Report saved: {report_path}")


def example_4_single_paper_export():
    """Example 4: Ask question and export as PDF report"""
    print("\n" + "="*60)
    print("EXAMPLE 4: Q&A with PDF Report Export")
    print("="*60)
    
    parsed_dir = Path("data/parsed")
    
    # Get answer from RAG
    store = SimpleStore(parsed_dir)
    query = "What are the efficacy rates and side effects?"
    contexts = store.search(query, top_k=6)
    
    if contexts:
        context_text = " ".join([c['text'] for c in contexts])
        answer = summarize_paper(context_text, question=query)
        
        print(f"\n❓ Question: {query}")
        print(f"\n📝 Answer: {answer}")
        
        # Export as PDF report
        exporter = PDFReportGenerator()
        
        # Export as Markdown
        report_path = exporter.export_to_markdown(
            title="Efficacy and Safety Analysis",
            query=query,
            answer=answer,
            citations=[{
                "source": c['meta']['source'],
                "section": c['meta']['section'],
                "text": c['text']
            } for c in contexts],
            paper_sources=list(set([c['meta']['source'] for c in contexts]))
        )
        
        print(f"\n💾 Markdown report saved: {report_path}")
        print("\n📖 Convert to PDF with:")
        print(f"   pandoc {report_path} -o report.pdf")
        
        # Export as JSON
        json_path = exporter.export_json_report(
            title="Efficacy and Safety Analysis",
            query=query,
            answer=answer,
            citations=[{
                "source": c['meta']['source'],
                "section": c['meta']['section'],
                "text": c['text']
            } for c in contexts]
        )
        print(f"\n💾 JSON report saved: {json_path}")
        
        # Export as BibTeX
        bibtex_path = exporter.export_bibtex(
            citations=[{
                "source": c['meta']['source'],
                "section": c['meta']['section']
            } for c in contexts]
        )
        print(f"\n💾 BibTeX file saved: {bibtex_path}")


def example_5_end_to_end_workflow():
    """Example 5: Complete end-to-end workflow"""
    print("\n" + "="*60)
    print("EXAMPLE 5: End-to-End Workflow")
    print("="*60)
    
    pdf_path = Path("data/raw/example_paper.pdf")
    parsed_dir = Path("data/parsed")
    
    # Step 1: Parse PDF
    if pdf_path.exists():
        print(f"\n📄 Step 1: Parsing {pdf_path.name}...")
        parsed = parse_pdf_to_sections(pdf_path)
        print(f"   ✅ Found {len(parsed['sections'])} sections")
        
        # Save parsed data
        (parsed_dir / f"{parsed['paper_id']}.json").write_text(
            __import__('json').dumps(parsed, ensure_ascii=False),
            encoding="utf-8"
        )
        print(f"   ✅ Saved as {parsed['paper_id']}.json")
    
    # Step 2: Ask question
    print(f"\n❓ Step 2: Asking question...")
    store = SimpleStore(parsed_dir)
    query = "What is the main finding?"
    contexts = store.search(query, top_k=5)
    
    if contexts:
        context_text = " ".join([c['text'] for c in contexts])
        answer = summarize_paper(context_text, question=query)
        print(f"   ✅ Got answer: {answer[:100]}...")
        
        # Step 3: Export report
        print(f"\n📋 Step 3: Exporting report...")
        exporter = PDFReportGenerator()
        report_path = exporter.export_to_markdown(
            title=f"Analysis: {query}",
            query=query,
            answer=answer,
            citations=[{"source": c['meta']['source'], "section": c['meta']['section'], "text": c['text']} for c in contexts]
        )
        print(f"   ✅ Report saved: {report_path}")
        
        # Step 4: Compare with other papers (if available)
        parsed_papers = list(parsed_dir.glob("*.json"))
        if len(parsed_papers) >= 2:
            print(f"\n🔀 Step 4: Comparing {len(parsed_papers)} papers...")
            comparator = MultiDocComparator(parsed_dir)
            paper_ids = [p.stem for p in parsed_papers[:3]]
            result = comparator.compare_papers(query=query, paper_ids=paper_ids)
            print(f"   ✅ Found {len(result.consensus)} consensus themes")
            
            comp_report = exporter.export_comparison_report(
                title=f"Comparison: {query}",
                query=query,
                findings_by_paper=result.findings,
                consensus=result.consensus,
                contradictions=result.contradictions,
                unique_findings=result.unique_findings
            )
            print(f"   ✅ Comparison report saved: {comp_report}")
        
        # Step 5: Meta-analysis
        if len(parsed_papers) >= 1:
            print(f"\n📊 Step 5: Meta-analysis extraction...")
            extractor = MetaAnalysisExtractor(parsed_dir)
            metrics = extractor.extract_study_metrics()
            print(f"   ✅ Extracted metrics from {len(metrics)} papers")
            
            meta_report = exporter.export_meta_analysis_report(
                title="Meta-Analysis Results",
                metrics_table=extractor.generate_meta_analysis_table(metrics),
                summary_stats=extractor.generate_summary_stats(metrics)
            )
            print(f"   ✅ Meta-analysis report saved: {meta_report}")
        
        print(f"\n✨ Workflow complete!")


if __name__ == "__main__":
    import sys
    
    print("\n" + "="*60)
    print("Medical Research Intelligence System v2.0")
    print("Example Usage Scripts")
    print("="*60)
    
    print("\nAvailable examples:")
    print("1. Basic Q&A (single paper)")
    print("2. Multi-document comparison")
    print("3. Meta-analysis extraction")
    print("4. Q&A with PDF export")
    print("5. End-to-end workflow")
    print("6. Run all examples")
    
    choice = input("\nSelect example (1-6): ").strip()
    
    try:
        if choice == "1":
            example_1_basic_qa()
        elif choice == "2":
            example_2_multi_document_comparison()
        elif choice == "3":
            example_3_meta_analysis()
        elif choice == "4":
            example_4_single_paper_export()
        elif choice == "5":
            example_5_end_to_end_workflow()
        elif choice == "6":
            example_1_basic_qa()
            example_2_multi_document_comparison()
            example_3_meta_analysis()
            example_4_single_paper_export()
        else:
            print("Invalid choice")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\n💡 Make sure you have:")
        print("   - Parsed papers in data/parsed/")
        print("   - Installed all dependencies (pip install -r requirements.txt)")
