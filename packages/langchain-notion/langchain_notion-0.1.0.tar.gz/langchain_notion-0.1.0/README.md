# langchain-notion

This package provides a LangChain integration for interacting with Notion via the LangchainNotion toolkit and tools. It enables you to access, search, create, and update Notion pages programmatically using LangChain interfaces.

## Installation

```bash
pip install -U langchain-notion
```

## Configuration

Set your Notion API key as an environment variable before using the toolkit:

```bash
export NOTION_API_KEY="your-notion-api-key"
```

## Usage: Notion Toolkit & Tools

The toolkit provides tools for interacting with Notion pages:

```python
import os
from langchain_notion.toolkits import LangchainNotionToolkit
from langchain_notion.notion_wrapper import NotionWrapper

key = os.environ.get("NOTION_API_KEY")
api = NotionWrapper(api_key=key)
toolkit = LangchainNotionToolkit.from_notion_wrapper(api)
tools = toolkit.get_tools()

# Example: Search for pages
tool = next(t for t in tools if t.name == "Search Pages")
print(tool.run({"query": "test"}))
```

## Project Structure & Maintenance

- All code is in the `langchain_notion/` directory.
- Tests are in `tests/unit_tests/`.
- The `.gitignore` is set up to ignore all build, cache, and notebook checkpoint files.
- Unused scripts and placeholder files have been removed for clarity and maintainability.
- `main_test.py` is kept for compatibility or future use, but is excluded from packaging.

## License

This project is licensed under the MIT License.
