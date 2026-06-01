"""
PDF Export Module
Generates professional PDF reports with citations and evidence tracking.
"""

from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
import json


class PDFReportGenerator:
    """Generate professional PDF reports from research summaries"""
    
    def __init__(self, output_dir: Path = Path("data/reports")):
        """Initialize report generator"""
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_report_markdown(
        self,
        title: str,
        query: str,
        answer: str,
        citations: List[Dict],
        paper_sources: List[str] = None,
        report_type: str = "single_question"
    ) -> str:
        """
        Generate markdown content for PDF report.
        
        Args:
            title: Report title
            query: The research question
            answer: The generated answer
            citations: List of citation metadata
            paper_sources: Source papers
            report_type: Type of report (single_question, comparison, meta_analysis)
        
        Returns:
            Markdown formatted report
        """
        lines = [
            f"# {title}\n",
            f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n",
            f"**Report Type:** {report_type.replace('_', ' ').title()}\n",
            "---\n",
        ]
        
        # Executive Summary
        lines.extend([
            "## Executive Summary\n",
            f"**Research Question:** {query}\n",
            "---\n",
        ])
        
        # Main Answer
        lines.extend([
            "## Answer\n",
            f"{answer}\n",
            "---\n",
        ])
        
        # Evidence & Citations
        lines.extend([
            "## Evidence & Citations\n",
            "*The following sources support the above findings:*\n",
        ])
        
        for i, citation in enumerate(citations, 1):
            source = citation.get('source', 'Unknown source')
            section = citation.get('section', 'unknown').title()
            text = citation.get('text', '')
            
            # Truncate long citations
            if len(text) > 300:
                text = text[:300] + "..."
            
            lines.extend([
                f"### [{i}] {source}\n",
                f"**Section:** {section}  \n",
                f"**Evidence:**\n",
                f"> {text}\n",
            ])
        
        # Source Papers
        if paper_sources:
            lines.extend([
                "---\n",
                "## Source Papers\n",
            ])
            for i, source in enumerate(paper_sources, 1):
                lines.append(f"{i}. {source}")
        
        # Disclaimer
        lines.extend([
            "\n---\n",
            "## Important Note\n",
            "*This report is generated using AI-assisted summarization of medical research. "
            "The information provided is for educational purposes only and should not be "
            "considered medical advice. Always consult with qualified healthcare professionals "
            "for medical decisions.*\n",
        ])
        
        return "\n".join(lines)
    
    def generate_comparison_report_markdown(
        self,
        title: str,
        query: str,
        findings_by_paper: Dict[str, str],
        consensus: List[str],
        contradictions: List[tuple],
        unique_findings: Dict[str, str]
    ) -> str:
        """Generate markdown for multi-paper comparison report"""
        lines = [
            f"# {title}\n",
            f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n",
            "**Report Type:** Multi-Paper Comparison\n",
            "---\n",
        ]
        
        lines.extend([
            "## Research Question\n",
            f"{query}\n",
            "---\n",
        ])
        
        # Individual Findings
        lines.extend([
            "## Findings by Paper\n",
        ])
        
        for paper_id, finding in findings_by_paper.items():
            lines.extend([
                f"### {paper_id}\n",
                f"{finding}\n",
            ])
        
        # Consensus
        lines.extend([
            "## Common Themes (Consensus)\n",
        ])
        for theme in consensus:
            lines.append(f"- **{theme}**")
        
        # Contradictions
        if contradictions:
            lines.extend([
                "\n## ⚠️ Potential Contradictions\n",
                "*The following papers appear to report conflicting findings:*\n",
            ])
            for p1, p2 in contradictions:
                lines.append(f"- **{p1}** vs **{p2}**")
        
        # Unique Findings
        if unique_findings:
            lines.extend([
                "\n## Paper-Specific Findings\n",
            ])
            for paper_id, finding in unique_findings.items():
                lines.extend([
                    f"### {paper_id}\n",
                    f"{finding}\n",
                ])
        
        lines.extend([
            "---\n",
            "## Disclaimer\n",
            "*This comparison is AI-generated. Review original papers for complete context.*\n",
        ])
        
        return "\n".join(lines)
    
    def generate_meta_analysis_report_markdown(
        self,
        title: str,
        metrics_table: str,
        summary_stats: str,
        analysis_notes: str = ""
    ) -> str:
        """Generate markdown for meta-analysis report"""
        lines = [
            f"# {title}\n",
            f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n",
            "**Report Type:** Meta-Analysis\n",
            "---\n",
        ]
        
        lines.extend([
            "## Overview\n",
            "This report presents extracted metrics from multiple medical studies.\n",
            "---\n",
        ])
        
        lines.extend([
            "## Study Metrics\n",
            metrics_table,
            "\n---\n",
        ])
        
        lines.extend([
            "## Summary Statistics\n",
            summary_stats,
            "\n",
        ])
        
        if analysis_notes:
            lines.extend([
                "## Analysis Notes\n",
                analysis_notes,
                "\n",
            ])
        
        lines.extend([
            "---\n",
            "## Limitations\n",
            "- Metrics are extracted using automated processes and may miss nuanced findings\n",
            "- Manual review of original papers is recommended for accuracy\n",
            "- This analysis does not replace formal meta-analysis review\n",
        ])
        
        return "\n".join(lines)
    
    def save_markdown_report(self, content: str, filename: str) -> Path:
        """Save markdown report to file"""
        filepath = self.output_dir / filename
        filepath.write_text(content, encoding="utf-8")
        return filepath
    
    def export_to_markdown(
        self,
        title: str,
        query: str,
        answer: str,
        citations: List[Dict],
        paper_sources: List[str] = None,
        filename: str = None
    ) -> Path:
        """
        Export report to markdown file (can be converted to PDF).
        
        Args:
            title: Report title
            query: Research question
            answer: Generated answer
            citations: Citation list
            paper_sources: Source papers
            filename: Output filename (auto-generated if None)
        
        Returns:
            Path to saved markdown file
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"report_{timestamp}.md"
        
        content = self.generate_report_markdown(
            title=title,
            query=query,
            answer=answer,
            citations=citations,
            paper_sources=paper_sources
        )
        
        return self.save_markdown_report(content, filename)
    
    def export_comparison_report(
        self,
        title: str,
        query: str,
        findings_by_paper: Dict[str, str],
        consensus: List[str],
        contradictions: List[tuple],
        unique_findings: Dict[str, str],
        filename: str = None
    ) -> Path:
        """Export comparison report to markdown"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"comparison_{timestamp}.md"
        
        content = self.generate_comparison_report_markdown(
            title=title,
            query=query,
            findings_by_paper=findings_by_paper,
            consensus=consensus,
            contradictions=contradictions,
            unique_findings=unique_findings
        )
        
        return self.save_markdown_report(content, filename)
    
    def export_meta_analysis_report(
        self,
        title: str,
        metrics_table: str,
        summary_stats: str,
        analysis_notes: str = "",
        filename: str = None
    ) -> Path:
        """Export meta-analysis report to markdown"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"meta_analysis_{timestamp}.md"
        
        content = self.generate_meta_analysis_report_markdown(
            title=title,
            metrics_table=metrics_table,
            summary_stats=summary_stats,
            analysis_notes=analysis_notes
        )
        
        return self.save_markdown_report(content, filename)
    
    def export_bibtex(
        self,
        citations: List[Dict],
        filename: str = "references.bib"
    ) -> Path:
        """
        Export citations in BibTeX format.
        
        Args:
            citations: List of citation metadata
            filename: Output filename
        
        Returns:
            Path to saved BibTeX file
        """
        lines = []
        for i, citation in enumerate(citations, 1):
            # Simple BibTeX entry
            entry = f"""@article{{ref{i},
  author = {{{citation.get('author', 'Unknown')}}},
  title = {{{citation.get('source', 'Unknown')}}},
  section = {{{citation.get('section', 'Unknown')}}},
  year = {{{datetime.now().year}}}
}}
"""
            lines.append(entry)
        
        filepath = self.output_dir / filename
        filepath.write_text("\n".join(lines), encoding="utf-8")
        return filepath
    
    def export_json_report(
        self,
        title: str,
        query: str,
        answer: str,
        citations: List[Dict],
        metadata: Dict = None,
        filename: str = None
    ) -> Path:
        """
        Export report as structured JSON.
        
        Args:
            title: Report title
            query: Research question
            answer: Generated answer
            citations: Citation list
            metadata: Additional metadata
            filename: Output filename
        
        Returns:
            Path to saved JSON file
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"report_{timestamp}.json"
        
        report = {
            "title": title,
            "query": query,
            "answer": answer,
            "citations": citations,
            "generated_at": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        
        filepath = self.output_dir / filename
        filepath.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
        return filepath


if __name__ == "__main__":
    # Example usage
    exporter = PDFReportGenerator()
    
    # Example report
    result = exporter.export_to_markdown(
        title="Medical Research Summary",
        query="What are the treatment options for condition X?",
        answer="Treatment options include...",
        citations=[
            {
                "source": "paper1.pdf",
                "section": "Results",
                "text": "The study found that treatment A was effective..."
            }
        ],
        paper_sources=["paper1.pdf", "paper2.pdf"]
    )
    
    print(f"Report saved to: {result}")
