"""
Meta-Analysis Extraction Module
Automatically extracts and compares key metrics across studies.
"""

from pathlib import Path
import json
import re
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from apps.api.rag.retrieve import SimpleStore


@dataclass
class StudyMetrics:
    """Extracted metrics from a single study"""
    paper_id: str
    sample_size: Optional[int] = None
    study_type: Optional[str] = None
    treatment: Optional[str] = None
    outcome: Optional[str] = None
    efficacy_rate: Optional[float] = None
    side_effects: List[str] = None
    follow_up_duration: Optional[str] = None
    statistical_significance: Optional[str] = None
    
    def __post_init__(self):
        if self.side_effects is None:
            self.side_effects = []


class MetaAnalysisExtractor:
    """Extract and compare key metrics across medical studies"""
    
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
    
    def extract_study_metrics(
        self,
        paper_ids: List[str] = None,
        metric_type: str = "treatment"
    ) -> List[StudyMetrics]:
        """
        Extract key metrics from studies.
        
        Args:
            paper_ids: List of paper IDs to extract from (None = all)
            metric_type: Type of metrics to extract ('treatment', 'efficacy', 'safety')
        
        Returns:
            List of extracted metrics per study
        """
        if paper_ids is None:
            paper_ids = list(self.papers.keys())
        
        metrics_list = []
        
        for pid in paper_ids:
            if pid not in self.papers:
                continue
            
            paper = self.papers[pid]
            all_text = self._extract_paper_text(paper)
            
            metrics = StudyMetrics(paper_id=pid)
            
            # Extract various metrics
            metrics.sample_size = self._extract_sample_size(all_text)
            metrics.study_type = self._extract_study_type(all_text)
            metrics.treatment = self._extract_treatment(all_text)
            metrics.outcome = self._extract_outcome(all_text)
            metrics.efficacy_rate = self._extract_efficacy(all_text)
            metrics.side_effects = self._extract_side_effects(all_text)
            metrics.follow_up_duration = self._extract_follow_up(all_text)
            metrics.statistical_significance = self._extract_significance(all_text)
            
            metrics_list.append(metrics)
        
        return metrics_list
    
    def _extract_paper_text(self, paper: Dict) -> str:
        """Extract all text from paper"""
        sections = paper.get("sections", [])
        return " ".join([s.get("text", "") for s in sections])
    
    def _extract_sample_size(self, text: str) -> Optional[int]:
        """Extract sample size/number of participants"""
        patterns = [
            r"n\s*=\s*(\d+(?:,\d{3})*)",
            r"sample size.*?(\d+(?:,\d{3})*)",
            r"(\d+(?:,\d{3})*)\s*(?:patients|participants|subjects)",
            r"enrolled\s*(\d+(?:,\d{3})*)",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    return int(match.group(1).replace(",", ""))
                except:
                    pass
        return None
    
    def _extract_study_type(self, text: str) -> Optional[str]:
        """Extract type of study (RCT, observational, case study, etc.)"""
        study_types = [
            "randomized controlled trial",
            "rct",
            "meta-analysis",
            "systematic review",
            "cohort study",
            "case-control study",
            "observational study",
            "case study",
            "cross-sectional",
        ]
        
        text_lower = text.lower()
        for stype in study_types:
            if stype in text_lower:
                return stype
        return None
    
    def _extract_treatment(self, text: str) -> Optional[str]:
        """Extract primary treatment/intervention"""
        patterns = [
            r"treated with\s+([a-zA-Z\s]+?)(?:\.|,)",
            r"intervention:\s*([a-zA-Z\s]+?)(?:\.|,)",
            r"therapy:\s*([a-zA-Z\s]+?)(?:\.|,)",
            r"drug:\s*([a-zA-Z\s]+?)(?:\.|,)",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        return None
    
    def _extract_outcome(self, text: str) -> Optional[str]:
        """Extract primary outcome measure"""
        patterns = [
            r"primary outcome.*?:\s*([a-zA-Z\s]+?)(?:\.|,)",
            r"primary endpoint.*?:\s*([a-zA-Z\s]+?)(?:\.|,)",
            r"measured by\s+([a-zA-Z\s]+?)(?:\.|,)",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        return None
    
    def _extract_efficacy(self, text: str) -> Optional[float]:
        """Extract efficacy/success rate"""
        patterns = [
            r"(\d+(?:\.\d+)?)\s*%.*?(?:effective|success|response|improvement)",
            r"response rate.*?(\d+(?:\.\d+)?)\s*%",
            r"efficacy.*?(\d+(?:\.\d+)?)\s*%",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    return float(match.group(1))
                except:
                    pass
        return None
    
    def _extract_side_effects(self, text: str) -> List[str]:
        """Extract reported side effects"""
        side_effects = []
        common_adverse_events = [
            "headache",
            "nausea",
            "fatigue",
            "diarrhea",
            "vomiting",
            "infection",
            "fever",
            "rash",
            "allergic",
            "hypertension",
            "hypotension",
        ]
        
        text_lower = text.lower()
        for effect in common_adverse_events:
            if effect in text_lower:
                side_effects.append(effect)
        
        return side_effects
    
    def _extract_follow_up(self, text: str) -> Optional[str]:
        """Extract follow-up duration"""
        patterns = [
            r"follow.?up.*?(\d+\s*(?:weeks?|months?|years?))",
            r"followed.*?for.*?(\d+\s*(?:weeks?|months?|years?))",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)
        return None
    
    def _extract_significance(self, text: str) -> Optional[str]:
        """Extract statistical significance (p-value, etc.)"""
        patterns = [
            r"p\s*[<>=]\s*([\d.]+)",
            r"statistically significant.*?p\s*[<>=]\s*([\d.]+)",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return f"p {match.group(0)}"
        return None
    
    def generate_meta_analysis_table(self, metrics_list: List[StudyMetrics]) -> str:
        """Generate markdown table of extracted metrics"""
        lines = [
            "# Meta-Analysis: Extracted Study Metrics\n",
            "| Paper ID | Type | N | Treatment | Efficacy | P-Value | Side Effects |",
            "| --- | --- | --- | --- | --- | --- | --- |",
        ]
        
        for m in metrics_list:
            n = m.sample_size if m.sample_size else "-"
            stype = m.study_type if m.study_type else "-"
            treatment = m.treatment if m.treatment else "-"
            treatment = treatment[:30] + "..." if treatment and len(treatment) > 30 else treatment
            efficacy = f"{m.efficacy_rate}%" if m.efficacy_rate else "-"
            pval = m.statistical_significance if m.statistical_significance else "-"
            effects = ", ".join(m.side_effects[:2]) if m.side_effects else "-"
            
            lines.append(
                f"| {m.paper_id} | {stype} | {n} | {treatment} | {efficacy} | {pval} | {effects} |"
            )
        
        return "\n".join(lines)
    
    def generate_summary_stats(self, metrics_list: List[StudyMetrics]) -> str:
        """Generate summary statistics across studies"""
        lines = ["\n# Summary Statistics Across Studies\n"]
        
        # Sample size stats
        sample_sizes = [m.sample_size for m in metrics_list if m.sample_size]
        if sample_sizes:
            lines.append(f"**Sample Sizes:**")
            lines.append(f"- Mean: {sum(sample_sizes) / len(sample_sizes):.0f}")
            lines.append(f"- Median: {sorted(sample_sizes)[len(sample_sizes)//2]}")
            lines.append(f"- Range: {min(sample_sizes)} - {max(sample_sizes)}\n")
        
        # Efficacy stats
        efficacies = [m.efficacy_rate for m in metrics_list if m.efficacy_rate]
        if efficacies:
            lines.append(f"**Efficacy Rates:**")
            lines.append(f"- Mean: {sum(efficacies) / len(efficacies):.1f}%")
            lines.append(f"- Range: {min(efficacies):.1f}% - {max(efficacies):.1f}%\n")
        
        # Study type distribution
        types = {}
        for m in metrics_list:
            if m.study_type:
                types[m.study_type] = types.get(m.study_type, 0) + 1
        
        if types:
            lines.append(f"**Study Types:**")
            for stype, count in sorted(types.items()):
                lines.append(f"- {stype}: {count}")
        
        return "\n".join(lines)


if __name__ == "__main__":
    parsed_dir = Path("data/parsed")
    
    extractor = MetaAnalysisExtractor(parsed_dir)
    metrics = extractor.extract_study_metrics()
    
    print(extractor.generate_meta_analysis_table(metrics))
    print(extractor.generate_summary_stats(metrics))
