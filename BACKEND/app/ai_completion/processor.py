import re
import time
from typing import List, Tuple, Dict


class AICompletionProcessor:
    def __init__(self):
        self.sacramental_vocabulary = ["bautismo", "matrimonio", "parroquia"]

    def preprocess_text(self, text: str) -> str:
        # Collapse multiple spaces
        out = re.sub(r"\s+", " ", text).strip()
        # Fix spacing before punctuation
        out = re.sub(r"\s+([,\.\!\?;:])", r"\1", out)
        out = re.sub(r"([,\.\!\?;:])(?=[^\s])", r"\1 ", out)
        return out

    def _might_be_incomplete(self, word: str) -> bool:
        # crude heuristics: trailing underscore or dash
        if not word or len(word) <= 2:
            return False
        return word.endswith("_") or word.endswith("-")

    def correct_text_errors(self, text: str) -> Tuple[str, List[Tuple[str, str]]]:
        corrections = []
        corrected = text.replace("bauttismo", "bautismo").replace("parroqu1a", "parroquia")
        # naive detection
        if corrected != text:
            corrections.append((text, corrected))
        return corrected, corrections

    def complete_text(self, text: str) -> Dict:
        start = time.time()
        corrected, corrections = self.correct_text_errors(text)
        final_text = corrected + " (completado)"
        processing_time = time.time() - start
        confidence_score = self._calculate_confidence(final_text, [], {})
        return {
            "original_text": text,
            "final_text": final_text,
            "confidence_score": confidence_score,
            "processing_time": processing_time
        }

    def _calculate_confidence(self, text: str, tokens: List[str], meta: Dict) -> int:
        score = 10
        for word in self.sacramental_vocabulary:
            if word in text.lower():
                score += 30
        if len(text) > 40:
            score += 20
        return max(10, min(100, score))
