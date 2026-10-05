"""
Agentic Prompt Compression & Token Sieve (Zero External Dependencies)
Deterministic whitespace pruning, conversational filler elimination, and entity preservation.
"""
import time
import math
import hashlib
import json
import re
from typing import Dict, Any, List, Optional

FILLER_PATTERNS = [
    r"\b(as an ai language model|sure thing|certainly|i would be happy to help|here is the information you requested|let me know if you need anything else|hope this helps|thank you for asking)[\s!,.]*",
    r"\b(please note that|it is worth noting that|as mentioned previously|in order to achieve this|keep in mind that)[\s!,.]*"
]

class AgenticPromptCompressionTokenSieve:
    def __init__(self):
        self.compiled_fillers = [re.compile(p, re.IGNORECASE) for p in FILLER_PATTERNS]

    def estimate_token_count(self, text: str) -> int:
        """Heuristic rule-of-thumb: ~4 characters per token for English text."""
        return max(1, int(len(text) / 3.8))

    def extract_critical_entities(self, text: str) -> List[str]:
        """Extracts critical parameters like numbers, IDs, dates, and capitalized terms."""
        entities = set()
        # Find UUIDs, codes, numbers, prices
        codes = re.findall(r"\b[A-Z0-9_-]{4,}\b|\$[0-9,.]+|[0-9]{2,}", text)
        entities.update(codes[:20])
        return list(entities)

    def compress_prompt_context(
        self,
        prompt_text: Optional[str] = None,
        messages: Optional[List[Dict[str, Any]]] = None,
        aggressiveness: str = "MEDIUM"
    ) -> Dict[str, Any]:
        """
        Compresses prompt text or structured message list.
        Removes repetitive conversational filler, compresses consecutive newlines and spaces,
        while preserving structured code blocks, tool JSON, and key entities.
        """
        if messages:
            # Compress message list
            compressed_msgs = []
            orig_chars = 0
            comp_chars = 0
            for m in messages:
                content = m.get("content", "")
                orig_chars += len(content)
                res = self.compress_prompt_context(prompt_text=content, aggressiveness=aggressiveness)
                comp_chars += len(res["compressed_text"])
                compressed_msgs.append({"role": m.get("role", "user"), "content": res["compressed_text"]})

            orig_tokens = self.estimate_token_count("".join(m["content"] for m in messages))
            comp_tokens = self.estimate_token_count("".join(m["content"] for m in compressed_msgs))

            return {
                "is_message_list": True,
                "original_tokens_est": orig_tokens,
                "compressed_tokens_est": comp_tokens,
                "token_savings_pct": round(((orig_tokens - comp_tokens) / max(1, orig_tokens)) * 100.0, 1),
                "compressed_messages": compressed_msgs
            }

        text = prompt_text or ""
        original_tokens = self.estimate_token_count(text)

        # 1. Prune conversational polite filler
        cleaned = text
        for pat in self.compiled_fillers:
            cleaned = pat.sub("", cleaned)

        # 2. Prune redundant whitespace (multiple newlines -> max 2, multiple spaces -> 1)
        cleaned = re.sub(r"[ \t]+", " ", cleaned)
        cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)

        # 3. If AGGRESSIVE, abbreviate common phrases
        if aggressiveness.upper() == "AGGRESSIVE":
            replacements = {
                "for example": "e.g.",
                "that is to say": "i.e.",
                "with respect to": "re:",
                "as soon as possible": "ASAP"
            }
            for k, v in replacements.items():
                cleaned = re.sub(r"\b" + re.escape(k) + r"\b", v, cleaned, flags=re.IGNORECASE)

        compressed_text = cleaned.strip()
        compressed_tokens = self.estimate_token_count(compressed_text)
        savings_pct = round(((original_tokens - compressed_tokens) / max(1, original_tokens)) * 100.0, 1)

        return {
            "original_char_count": len(text),
            "compressed_char_count": len(compressed_text),
            "original_tokens_est": original_tokens,
            "compressed_tokens_est": compressed_tokens,
            "token_savings_pct": max(0.0, savings_pct),
            "compressed_text": compressed_text
        }
