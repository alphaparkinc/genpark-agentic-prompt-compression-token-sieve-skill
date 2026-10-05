"""Example usage for AgenticPromptCompressionTokenSieve."""
import sys
import json
from client import AgenticPromptCompressionTokenSieve

sys.stdout.reconfigure(encoding='utf-8')

def main():
    print("=== Dynamic Prompt Compression & Token Sieve Demo ===")
    sieve = AgenticPromptCompressionTokenSieve()

    verbose_agent_dialogue = """
    Certainly! As an AI language model, I would be happy to help you with that calculation.
    
    
    Please note that according to database record ACC-9912, the gross revenue reached $1,450,000 for Q3.
    
    In order to achieve this, the team deployed 14 autonomous agents.
    Hope this helps! Let me know if you need anything else!
    """

    print("\n--- Compressing Multi-Turn Agent Dialogue ---")
    comp = sieve.compress_prompt_context(verbose_agent_dialogue, aggressiveness="AGGRESSIVE")
    print(f"Original Est Tokens: {comp['original_tokens_est']} -> Compressed: {comp['compressed_tokens_est']}")
    print(f"Savings: {comp['token_savings_pct']}%\n")
    print("Compressed Text Output:")
    print(comp["compressed_text"])

if __name__ == "__main__":
    main()
