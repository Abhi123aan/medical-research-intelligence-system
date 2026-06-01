"""
Multi-Document Comparison Module
Compares findings across multiple papers and highlights agreements/contradictions.
"""

from pathlib import Path
import json
from typing import List, Dict, Tuple
from dataclasses import dataclass
import numpy as np
from apps.api.rag.retrieve import SimpleStore
from apps.api.rag.generate import summarize_paper


@dataclass
class ComparisonResult:
    """Result of comparing multiple papers on a topic"""
    question: str
    papers_analyzed: int
    findings: Dict[str, List[str]]  # {paper_id: [findings]}
    consensus: List[str]
    contradictions: List[Tuple[str, str]]  # [(paper1, paper2), ...]
    unique_findings: Dict[str, str]  # {paper_id: unique_finding}


class MultiDocComparator:
    """Compare findings across multiple research papers"""
    
    def __init__(self, parsed_dir: Path):
        """Initialize with parsed papers directory"""
        self.parsed_dir = parsed_dir
        self.store = SimpleStore(parsed_dir)
        self.papers = self._load_all_papers()
    
    def _load_all_papers(self) -> Dict[str, Dict]:
        """Load all parsed papers"""
        papers = {}
        for jf in self.parsed_dir.glob("*.json"):
            j = json.loads(jf.read_text(encoding="utf-8"))
            papers[j.get("paper_id", jf.stem)] = j
        return papers
    
    def compare_papers(
        self, 
        query: str, 
        paper_ids: List[str] = None,
        top_k: int = 5
    ) -> ComparisonResult:
        """
        Compare findings across multiple papers for a specific query.
        
        Args:
            query: The research question to compare across papers
            paper_ids: List of paper IDs to compare (None = all papers)
            top_k: Number of evidence chunks per paper
        
        Returns:
            ComparisonResult with findings, consensus, and contradictions
        """
        if paper_ids is None:
            paper_ids = list(self.papers.keys())
        
        # Get findings for each paper
        findings_per_paper = {}
        contexts_per_paper = {}
        
        for pid in paper_ids:
            if pid not in self.papers:
                continue
            
            # Get context from this specific paper
            contexts = self.store.search(query, top_k=top_k)
            
            # Filter to only this paper
            paper_contexts = [
                c for c in contexts 
                if c['meta']['paper_id'] == pid
            ]
            
            if paper_contexts:
                contexts_per_paper[pid] = paper_contexts
                # Generate summary for this paper's findings
                combined_text = " ".join([c['text'] for c in paper_contexts])
                finding = summarize_paper(combined_text, question=query)
                findings_per_paper[pid] = finding
        
        # Analyze consensus and contradictions
        consensus = self._extract_consensus(findings_per_paper)
        contradictions = self._find_contradictions(findings_per_paper)
        unique = self._find_unique_findings(findings_per_paper, consensus)
        
        return ComparisonResult(
            question=query,
            papers_analyzed=len(findings_per_paper),
            findings=findings_per_paper,
            consensus=consensus,
            contradictions=contradictions,
            unique_findings=unique
        )
    
    def _extract_consensus(self, findings: Dict[str, str]) -> List[str]:
        """Extract common themes across papers"""
        if not findings:
            return []
        
        # Simple keyword overlap detection
        common_keywords = self._get_common_keywords(list(findings.values()))
        return common_keywords[:5]  # Top 5 common themes
    
    def _get_common_keywords(self, texts: List[str], n_common: int = 5) -> List[str]:
        """Extract common keywords from multiple texts"""
        if not texts:
            return []
        
        # Tokenize and count word frequencies
        all_words = {}
        for text in texts:
            words = set(text.lower().split())
            words = {w for w in words if len(w) > 4 and not w.startswith("the")}
            
            for word in words:
                all_words[word] = all_words.get(word, 0) + 1
        
        # Find words appearing in multiple texts
        common = [w for w, count in all_words.items() if count >= 2]
        return sorted(common, key=lambda w: all_words[w], reverse=True)[:n_common]
    
    def _find_contradictions(self, findings: Dict[str, str]) -> List[Tuple[str, str]]:
        """Detect potential contradictions between papers"""
        contradictions = []
        paper_ids = list(findings.keys())
        
        contradiction_keywords = [
            ("no effect", "significant effect"),
            ("contraindicated", "recommended"),
            ("ineffective", "effective"),
            ("harmful", "beneficial"),
            ("not recommended", "recommended"),
        ]
        
        for i, p1 in enumerate(paper_ids):
            for p2 in paper_ids[i+1:]:
                finding1 = findings[p1].lower()
                finding2 = findings[p2].lower()
                
                for neg, pos in contradiction_keywords:
                    if neg in finding1 and pos in finding2:
                        contradictions.append((p1, p2))
                        break
        
        return contradictions
    
    def _find_unique_findings(
        self, 
        findings: Dict[str, str], 
        consensus: List[str]
    ) -> Dict[str, str]:
        """Find findings unique to each paper"""
        unique = {}
        
        for pid, finding in findings.items():
            # Remove consensus keywords
            unique_finding = finding
            for keyword in consensus:
                unique_finding = unique_finding.replace(keyword, "")
            
            if unique_finding.strip():
                unique[pid] = unique_finding.strip()
        
        return unique
    
    def generate_comparison_table(self, result: ComparisonResult) -> str:
        """Generate a markdown table comparing findings"""
        lines = [
            f"# Comparison: {result.question}\n",
            f"**Papers analyzed:** {result.papers_analyzed}\n",
            "---\n",
            "## Findings by Paper\n",
            "| Paper ID | Finding |",
            "| --- | --- |",
        ]
        
        for pid, finding in result.findings.items():
            finding_short = finding[:100] + "..." if len(finding) > 100 else finding
            lines.append(f"| {pid} | {finding_short} |")
        
        lines.extend([
            "\n## Consensus (Common themes)\n",
        ])
        
        for theme in result.consensus:
            lines.append(f"- {theme}")
        
        if result.contradictions:
            lines.extend([
                "\n## ⚠️ Potential Contradictions\n",
            ])
            for p1, p2 in result.contradictions:
                lines.append(f"- **{p1}** vs **{p2}**")
        
        if result.unique_findings:
            lines.extend([
                "\n## Unique Findings\n",
            ])
            for pid, finding in result.unique_findings.items():
                lines.append(f"**{pid}:** {finding[:150]}...\n")
        
        return "\n".join(lines)


if __name__ == "__main__":
    from pathlib import Path
    parsed_dir = Path("data/parsed")
    
    comparator = MultiDocComparator(parsed_dir)
    result = comparator.compare_papers(
        query="What are the treatment options?",
        top_k=3
    )
    
    print(comparator.generate_comparison_table(result))
