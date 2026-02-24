# LLM Integration Guide

The Agentic Tree application includes optional LLM (Large Language Model) integration to power more intelligent chat responses. Currently, **OpenAI's GPT-3.5 Turbo** is supported.

## Quick Start

### 1. Install the OpenAI Package

```bash
cd backend
pip install openai
```

### 2. Set Environment Variables

Export your OpenAI API key:

```bash
export OPENAI_API_KEY="sk-..."
export USE_LLM_AGENT=1
```

Or add them to a `.env` file in the `backend/` directory:

```ini
OPENAI_API_KEY=sk-...
USE_LLM_AGENT=1
OPENAI_MODEL=gpt-3.5-turbo
```

### 3. Restart the Backend

```bash
cd backend
uvicorn venv.main:app --reload
```

### 4. Test the LLM Chat

```bash
curl -X POST http://localhost:8000/chat \
  -H "Authorization: Bearer <YOUR_ACCESS_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "tree_id": 1,
    "message": "What is the height of the tree?"
  }'
```

## How It Works

1. **User sends a message** via the `/chat` endpoint.
2. **Backend checks** if `USE_LLM_AGENT=1` and OpenAI API key is configured.
3. **If enabled**: The message and current tree state are sent to OpenAI's ChatGPT API.
4. **OpenAI responds** with:
   - `response`: Text answer to the user
   - `modified`: Whether the tree was changed
   - `tree`: Updated tree data (if `modified=true`)
5. **If the LLM is unavailable**, the system automatically falls back to rule-based responses.

## Architecture

- **[ai_agent.py](venv/ai_agent.py)**: Main chat orchestrator. Checks `USE_LLM_AGENT` and delegates to the LLM adapter or rule-based logic.
- **[ai_agent_adapter.py](venv/ai_agent_adapter.py)**: OpenAI API wrapper. Constructs prompts, calls ChatGPT, and parses JSON responses.

## Configuration Options

| Variable | Default | Description |
|----------|---------|-------------|
| `USE_LLM_AGENT` | `` | Set to `1` to enable LLM-driven chat |
| `OPENAI_API_KEY` | `` | Your OpenAI API key (required if using LLM) |
| `OPENAI_MODEL` | `gpt-3.5-turbo` | OpenAI model to use |

## Security Best Practices

- **Never commit API keys** to version control. Use `.gitignore` to exclude `.env` files.
- **Use environment variables** or a secrets manager (e.g., AWS Secrets Manager, HashiCorp Vault).
- **Rotate API keys** regularly.
- **Monitor usage** on the OpenAI dashboard to detect unexpected cost spikes.
- **Set rate limits** on your API keys to prevent abuse.

## Cost Estimation

- GPT-3.5 Turbo: ~$0.0005 per 1K input tokens, ~$0.0015 per 1K output tokens.
- A typical tree chat request = ~200-500 tokens.
- **Budget Example**: 1,000 requests = ~$0.50-$1.00 USD.

## Fallback Behavior

If the LLM is unavailable (no API key, network error, rate limit), the system **automatically** falls back to rule-based logic:

- Responds with facts about the tree (height, leaf count, etc.).
- Does not modify the tree.
- Provides consistent, predictable answers.

No errors are exposed to the user; they simply receive a rule-based response instead of an LLM-driven one.

## Example Prompts

Once enabled, try these user messages:

- "What is the height of the tree?"
- "How many leaf nodes are there?"
- "Insert node 15 as a left child of node 10"
- "Tell me the structure of this tree"
- "What are the leaves?"

## Troubleshooting

### "OPENAI_API_KEY environment variable not set"

Set the environment variable before starting the server:

```bash
export OPENAI_API_KEY="sk-..."
uvicorn venv.main:app --reload
```

### "openai package not installed"

Install it:

```bash
pip install openai
```

### "LLM provider error" (API errors)

Check:
- Your API key is valid and has sufficient credits
- OpenAI services are not experiencing outages
- Your network connection
- Rate limits (free trial has limits)

Errors are logged; check the server logs for details.

## Future Enhancements

- Support for **Google Gemini API**
- Support for **Anthropic Claude**
- **Vector embeddings** for semantic search over tree history
- **Conversation memory** to maintain context across multiple messages
- **Fine-tuned models** trained on tree operation domain
