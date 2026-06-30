from typing import Any

import httpx
from app.config import settings


class SmartsheetClient:
    BASE_URL = "https://api.smartsheet.com/2.0"

    def __init__(self, token: str | None = None):
        self.token = token or settings.SMARTSHEET_API_TOKEN
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }

    async def _get(
        self, path: str, params: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.BASE_URL}{path}",
                headers=self.headers,
                params=params,
                timeout=60.0,
            )
            response.raise_for_status()
            return response.json()

    async def list_sheets(self, include_all: bool = True) -> list[dict[str, Any]]:
        data = await self._get("/sheets", params={"includeAll": "true"})
        return data.get("data", [])

    async def get_sheet(
        self, sheet_id: int, modified_since: str | None = None
    ) -> dict[str, Any]:
        params: dict[str, Any] = {}
        if modified_since:
            params["modifiedSince"] = modified_since
        return await self._get(f"/sheets/{sheet_id}", params=params)

    async def get_sheet_columns(self, sheet_id: int) -> list[dict[str, Any]]:
        sheet = await self.get_sheet(sheet_id)
        return sheet.get("columns", [])


smartsheet_client = SmartsheetClient()
