
```markdown
# API Reference

## Generate Text

```http
POST /api/generate
Content-Type: application/json

{
  "prompt": "Hello world",
  "provider": "openai",
  "model": "gpt-3.5-turbo",
  "max_tokens": 100,
  "temperature": 0.7
}


# Response:

{
  "text": "Hello! How can I help you today?",
  "model": "gpt-3.5-turbo",
  "provider": "openai",
  "tokens_used": 15,
  "processing_time": 0.85
}

# Stream Text

POST /api/stream
Content-Type: application/json

{
  "prompt": "Tell me a story",
  "provider": "anthropic",
  "stream": true
}
 -- The response is a Server-Sent Events stream.

# Model Comparison

POST /api/compare
Content-Type: application/json

{
  "prompt": "Explain AI",
  "models": [
    {"provider": "openai", "model": "gpt-3.5-turbo"},
    {"provider": "anthropic", "model": "claude-2"}
  ]
}