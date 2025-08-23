import json
import os
from typing import Optional, List, Dict, Any
from notion_client import Client


class NotionWrapper:
    """
    Wrapper around the Notion SDK for basic page operations.
    Requires NOTION_API_KEY to be set in the environment or passed as an argument.
    """
    def __init__(self, api_key: Optional[str] = None, default_db_id: Optional[str] = None):
        self.api_key = api_key or os.environ.get("NOTION_API_KEY")
        if not self.api_key:
            raise ValueError("NOTION_API_KEY is required.")
        self.client = Client(auth=self.api_key)
        self.default_db_id = default_db_id or os.environ.get("NOTION_DATABASE_ID")

    def _get_title_of_page(self, page_obj: Dict[str, Any]) -> str:
        """Extracts the title from a Notion page object."""
        props = page_obj.get("properties", {})
        for prop in props.values():
            if prop.get("type") == "title":
                title = prop.get("title") or []
                if title and title[0].get("plain_text"):
                    return title[0]["plain_text"]
        return ""

    def search_pages(self, query: str, number_of_pages: int = 5) -> str:
        """
        Search for Notion pages matching the query string.
        Returns a JSON string of page IDs, titles, and URLs.
        """
        respon = self.client.search(query=query, page_size=number_of_pages, filter={"value": "page", "property": "object"})
        output: List[Dict[str, Any]] = []
        results = respon.get("results", [])
        if not results:
            return "0 results."
        for result in results:
            output.append({
                "id": result.get('id'),
                "title": self._get_title_of_page(result),
                "url": result.get('url')
            })
        return json.dumps(output)

    def get_page(self, page_id) -> str:
        """
        Retrieve a Notion page by its ID.
        Returns a JSON string with page details.
        """
        page = self.client.pages.retrieve(page_id=page_id)
        return json.dumps({
            "id": page.get("id"),
            "title": self._get_title_of_page(page),
            "url": page.get("url"),
            "properties": page.get("properties", {})
        })

    def create_page(self, parent: Optional[Any], properties: Dict[str, Any]) -> str:
        """
        Create a new Notion page under the given parent (database or page).
        Returns a JSON string with the new page's details.
        """
        if not parent:
            parent = {"database_id": self.default_db_id} if self.default_db_id else None
        if not parent:
            raise ValueError("Parent database ID is required to create a page.")
        page = self.client.pages.create(parent=parent, properties=properties)
        return json.dumps({
            "id": page.get("id"),
            "title": self._get_title_of_page(page),
            "url": page.get("url")
        })

    def update_page(self, page_id: str, properties: Dict[str, Any]) -> str:
        """
        Update properties of an existing Notion page.
        Returns a JSON string with the updated page's details.
        """
        if not page_id:
            raise ValueError("Page ID is required to update a page.")
        page = self.client.pages.update(page_id=page_id, properties=properties)
        return json.dumps({
            "id": page.get("id"),
            "title": self._get_title_of_page(page),
            "url": page.get("url")
        })
