"""LangchainNotion tools for interacting with Notion via LangChain."""

from typing import Optional, Type, Any
from langchain_core.callbacks import CallbackManagerForToolRun
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field
from langchain_notion.notion_wrapper import NotionWrapper


class SearchQuery(BaseModel):
    """Input schema for searching Notion pages by keyword(s)."""

    query: str = Field(..., description="Keyword(s) to search for pages.")


class PageId(BaseModel):
    """Input schema for retrieving a Notion page by ID."""

    page_id: str = Field(..., description="The Notion Page ID.")


class CreatePage(BaseModel):
    """Input schema for creating a new Notion page."""

    parent: Optional[Any] = Field(
        None, description="Parent database ID or page ID to create the page under."
    )
    properties: dict = Field(
        ..., description="Properties of the page to be created."
    )


class UpdatePage(BaseModel):
    """Input schema for updating an existing Notion page."""

    page_id: str = Field(..., description="The Notion Page ID to update.")
    properties: dict = Field(
        ..., description="Properties of the page to be updated."
    )


class LangchainNotionTool(BaseTool):  # type: ignore[override]
    """
    Tool for interacting with Notion via the NotionWrapper.
    Supports searching, retrieving, creating, and updating Notion pages.
    Requires the NOTION_API_KEY environment variable to be set.
    """

    mode: str
    name: str = ""
    description: str = ""
    api: NotionWrapper = Field(default_factory=NotionWrapper)
    args_schema: Optional[Type[BaseModel]] = None

    def _run(
        self,
        instructions: Optional[str] = "",
        run_manager: Optional[CallbackManagerForToolRun] = None,
        **kwargs: Any
    ) -> str:
        """
        Run the tool with the provided arguments.
        Dispatches to the appropriate NotionWrapper method based on args_schema.
        """
        if self.args_schema is SearchQuery:
            return self.api.search_pages(kwargs["query"])
        if self.args_schema is PageId:
            return self.api.get_page(kwargs["page_id"])
        if self.args_schema is CreatePage:
            return self.api.create_page(kwargs["parent"], kwargs["properties"])
        if self.args_schema is UpdatePage:
            return self.api.update_page(kwargs["page_id"], kwargs["properties"])

        return "Unsupported arguments for this tool."
