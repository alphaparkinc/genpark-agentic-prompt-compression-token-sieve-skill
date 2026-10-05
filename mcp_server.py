"""MCP Server for Agentic Prompt Compression Token Sieve."""
import sys
import json
import time
from client import AgenticPromptCompressionTokenSieve

sieve = AgenticPromptCompressionTokenSieve()

def handle_call_tool(params):
    name = params.get("name")
    args = params.get("arguments", {})
    if name != "compress_agent_prompt_context":
        raise ValueError(f"Unknown tool: {name}")

    action = args.get("action", "compress_prompt_context")
    if action == "compress_prompt_context":
        return sieve.compress_prompt_context(
            prompt_text=args.get("prompt_text"),
            messages=args.get("messages"),
            aggressiveness=args.get("aggressiveness", "MEDIUM")
        )
    elif action == "estimate_token_count":
        cnt = sieve.estimate_token_count(args.get("prompt_text", ""))
        return {"estimated_tokens": cnt}
    elif action == "extract_critical_entities":
        ents = sieve.extract_critical_entities(args.get("prompt_text", ""))
        return {"entities": ents}
    else:
        raise ValueError(f"Invalid action: {action}")

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        print("Running self-test...")
        sample = "Certainly! I would be happy to help with that.   \n\n\nHere is the information you requested for order #ORD-4491."
        res = sieve.compress_prompt_context(prompt_text=sample)
        assert "Certainly!" not in res["compressed_text"]
        assert "ORD-4491" in res["compressed_text"]
        assert res["token_savings_pct"] > 0
        print("Self-test PASSED!")
        sys.exit(0)

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
            msg_id = req.get("id")
            method = req.get("method")
            if method == "initialize":
                resp = {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "serverInfo": {"name": "AgenticPromptCompressionTokenSieve", "version": "1.0.0"},
                        "capabilities": {"tools": {}}
                    }
                }
            elif method == "tools/list":
                resp = {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "result": {
                        "tools": [{
                            "name": "compress_agent_prompt_context",
                            "description": "Compress multi-turn LLM agent prompts: remove whitespace, filter polite filler tokens, preserve tool call schemas and key entities, and compute compression savings.",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "action": {"type": "string", "enum": ["compress_prompt_context", "estimate_token_count", "extract_critical_entities"]},
                                    "prompt_text": {"type": "string"},
                                    "messages": {"type": "array"},
                                    "aggressiveness": {"type": "string"}
                                },
                                "required": ["action"]
                            }
                        }]
                    }
                }
            elif method == "tools/call":
                res = handle_call_tool(req.get("params", {}))
                resp = {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "result": {"content": [{"type": "text", "text": json.dumps(res, indent=2)}]}
                }
            else:
                resp = {"jsonrpc": "2.0", "id": msg_id, "result": {}}
            print(json.dumps(resp), flush=True)
        except Exception as e:
            err_resp = {"jsonrpc": "2.0", "id": None, "error": {"code": -32000, "message": str(e)}}
            print(json.dumps(err_resp), flush=True)

if __name__ == "__main__":
    main()
