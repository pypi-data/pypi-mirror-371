"""LangchainNotion toolkit for grouping Notion tools for agent use."""

from typing import List, Dict
from langchain_core.tools import BaseTool, BaseToolkit
from langchain_notion.notion_wrapper import NotionWrapper
from langchain_notion.tools import SearchQuery, PageId, LangchainNotionTool, CreatePage, UpdatePage


class LangchainNotionToolkit(BaseToolkit):
    """
    Toolkit for grouping Notion tools (search, get, create, update) for use with LangChain agents.
    Requires NOTION_API_KEY to be set in the environment or passed to NotionWrapper.
    """

    tools: List[BaseTool] = []

    @classmethod
    def from_notion_wrapper(cls, api: NotionWrapper) -> "LangchainNotionToolkit":
        """
        Instantiate the toolkit with all Notion tools using a NotionWrapper instance.
        Args:
            api (NotionWrapper): An authenticated NotionWrapper instance.
        Returns:
            LangchainNotionToolkit: Toolkit with all Notion tools registered.
        """
        # Define the supported Notion operations for the toolkit
        ops: List[Dict] = [
            {
                "mode": "search_pages",
                "name": "Search Pages",
                "description": "Search Notion Pages by keywords",
                "args_schema": SearchQuery,
            },
            {
                "mode": "get_page",
                "name": "Get Page",
                "description": "Retrieve a page's title, url, and properties.",
                "args_schema": PageId,
            },
            {
                "mode": "create_page",
                "name": "Create Page",
                "description": "Create a new page in Notion.",
                "args_schema": CreatePage,
            },
            {
                "mode": "update_page",
                "name": "Update Page",
                "description": "Update an existing page in Notion.",
                "args_schema": UpdatePage,
            },
        ]

        # Instantiate each tool with the provided NotionWrapper
        tools = [
            LangchainNotionTool(
                mode=op["mode"],
                name=op["name"],
                description=op["description"],
                args_schema=op["args_schema"],
                api=api,
            )
            for op in ops
        ]

        return cls(tools=tools)

    def get_tools(self) -> List[BaseTool]:
        """
        Return the list of Notion tools in this toolkit.
        """
        return self.tools