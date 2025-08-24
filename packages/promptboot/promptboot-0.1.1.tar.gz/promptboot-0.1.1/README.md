# PromptBoot
Vibe coding results.
A micro framework for bootstrapping AI applications with prompt engineering, inspired by SpringBoot.

## Features

- Configuration-driven (based on `config.yaml`)
- System/User Prompt + Schema
- Direct `list[dict]` messages support (fully compatible with OpenAI's `messages`)
- Logging & local record
- Pydantic validation + automatic retry
- Reusable with `pip install -e .` (SpringBoot-style startup)
- Both synchronous and asynchronous clients

## Installation

First install the required dependencies:

```bash
pip install openai tenacity pydantic pyyaml
```

Then install the package in development mode:

```bash
git clone <your-repo>
cd promptboot
pip install -e .
```

## Configuration

Create a `config.yaml` file in your project root:

```yaml
model_client:
  base_url: "https://api.openai.com/v1"
  api_key: "YOUR_API_KEY"
  model: "gpt-4o-mini"
  temperature: 0.3
  max_retries: 3
  retry_wait: 2

logging:
  dir: "./logs"
  level: "INFO"
```

## Usage

Basic usage with synchronous client:

```python
from promptboot import PromptClient

client = PromptClient()
result = client.call(system_prompt="...", user_prompt="...")
print(result)
```

With schema validation:

```python
from pydantic import BaseModel
from typing import List
from promptboot import PromptClient

class FruitsResponse(BaseModel):
    fruits: List[str]

client = PromptClient()
result = client.call(
    system_prompt="You are a helpful assistant.",
    user_prompt="Give me 3 fruits as JSON in format {\"fruits\": [..]}",
    schema=FruitsResponse
)
print(result)  # Returns validated Pydantic model
```

Asynchronous usage:

```python
import asyncio
from pydantic import BaseModel
from typing import List
from promptboot import AsyncPromptClient


class FruitsResponse(BaseModel):
    fruits: List[str]


async def main():
    prompt_client = AsyncPromptClient()

    result = await prompt_client.call(
        system_prompt="You are a helpful assistant.",
        user_prompt="Give me 3 fruits as JSON in format {\"fruits\": [..]}",
        schema=FruitsResponse,
    )

    print("Validated Result:", result)


if __name__ == "__main__":
    asyncio.run(main())
```

## Project Structure

```
promptboot/
├── promptboot/
│   ├── __init__.py
│   ├── client.py
│   ├── async_client.py
│   ├── config.py
│   └── logs/
│       ├── __init__.py
│       ├── logger.py
│       └── log_manager.py
├── config.yaml
├── setup.py
├── pyproject.toml
└── examples/
    └── demo.py
```