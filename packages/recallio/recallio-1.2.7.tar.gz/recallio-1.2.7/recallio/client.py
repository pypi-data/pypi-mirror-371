"""HTTP client for the Recallio API."""
from __future__ import annotations

import json
import os
import requests

from .models import (
    MemoryWriteRequest,
    MemoryRecallRequest,
    MemoryDeleteRequest,
    RecallSummaryRequest,
    MemoryExportRequest,
    DocumentIngestRequest,
    RecallTopicsRequest,
    MemoryDto,
    MemoryWithScoreDto,
    SummarizedMemoriesDto,
    TopicsDto,
    TopicItemDto,
    SubTopicItemDto,
    GraphAddRequest,
    GraphSearchRequest,
    GraphSearchResult,
    GraphEntity,
    GraphRelationship,
    GraphAddResponse,
)
from .errors import RecallioAPIError


class RecallioClient:
    """Client for interacting with the Recallio API."""

    def __init__(self, api_key: str, base_url: str = "https://app.recallio.ai") -> None:
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            }
        )

    def _request(
        self,
        method: str,
        path: str,
        json: dict | None = None,
        params: dict | None = None,
        data: dict | list | None = None,
        files: dict | None = None,
    ) -> dict | str:
        url = f"{self.base_url}{path}"
        headers = self.session.headers.copy()
        if files:
            headers.pop("Content-Type", None)
        response = self.session.request(
            method, url, json=json, params=params, data=data, files=files, headers=headers
        )
        if response.status_code >= 200 and response.status_code < 300:
            if response.content:
                try:
                    return response.json()
                except ValueError:
                    return response.text
            return {}
        try:
            data = response.json()
            message = data.get("error", response.text)
        except ValueError:
            message = response.text
        raise RecallioAPIError(message, status_code=response.status_code)

    def _normalize_content_messages(self, content: object) -> str:
        """Validate and serialize message content to a JSON string.

        Accepts either a single dict with keys `role` and `content`,
        or a list of such dicts, and returns a JSON string.
        """
        # Single message dict
        if isinstance(content, dict):
            if "role" in content and "content" in content:
                return json.dumps([content], ensure_ascii=False)
            raise ValueError(
                "content dict must include 'role' and 'content' keys"
            )

        # List of message dicts
        if isinstance(content, list):
            if all(isinstance(item, dict) and "role" in item and "content" in item for item in content):
                return json.dumps(content, ensure_ascii=False)
            raise ValueError(
                "content list must contain dict items with 'role' and 'content' keys"
            )

        raise ValueError(
            "content must be a string, a dict with 'role' and 'content', or a list of such dicts"
        )

    def write_memory(self, request: MemoryWriteRequest) -> None:
        """Store a memory asynchronously."""
        payload = request.to_dict()
        content_value = payload.get("content")
        # If content is provided as a dict or list (message objects), validate and serialize
        if content_value is not None and not isinstance(content_value, str):
            payload["content"] = self._normalize_content_messages(content_value)
        self._request("POST", "/api/Memory/write", json=payload)
        return None

    def ingest_document(self, request: DocumentIngestRequest) -> None:
        """Upload a PDF document and ingest its content."""
        data = [
            ("UserId", request.userId),
            ("ProjectId", request.projectId),
        ]
        if request.consentFlag is not None:
            data.append(("ConsentFlag", str(request.consentFlag).lower()))
        if request.tags:
            for tag in request.tags:
                data.append(("Tags", tag))
        with open(request.file_path, "rb") as file_obj:
            files = {"File": (os.path.basename(request.file_path), file_obj)}
            self._request(
                "POST", "/api/Memory/ingest-document", data=data, files=files
            )
        return None

    def recall_memory(self, request: MemoryRecallRequest) -> list[MemoryWithScoreDto]:
        data = self._request(
            "POST",
            "/api/Memory/recall",
            json=request.to_body(),
            params=request.to_params(),
        )
        if isinstance(data, list):
            return [MemoryWithScoreDto(**item) for item in data]
        return [MemoryWithScoreDto(**data)]

    def recall_summary(self, request: RecallSummaryRequest) -> SummarizedMemoriesDto:
        data = self._request("POST", "/api/Memory/recall-summary", json=request.to_dict())
        if isinstance(data, dict):
            return SummarizedMemoriesDto(**data)
        return SummarizedMemoriesDto()

    def recall_topics(self, request: RecallTopicsRequest) -> TopicsDto:
        data = self._request("POST", "/api/Memory/recall-topics", json=request.to_dict())
        if isinstance(data, dict):
            topics = []
            for item in data.get("topics", []) or []:
                sub_topics = (
                    [SubTopicItemDto(**st) for st in item.get("subTopics", [])]
                    if item.get("subTopics")
                    else None
                )
                topics.append(
                    TopicItemDto(name=item.get("name"), subTopics=sub_topics)
                )
            return TopicsDto(topics=topics or None, users=data.get("users"))
        return TopicsDto()

    def delete_memory(self, request: MemoryDeleteRequest) -> None:
        self._request("DELETE", "/api/Memory/delete", json=request.to_dict())
        return None

    def export_memory(self, request: MemoryExportRequest) -> str:
        data = self._request("GET", "/api/Memory/export", params=request.to_params())
        if isinstance(data, str):
            return data
        return ""

    def add_graph_memory(self, request: GraphAddRequest) -> GraphAddResponse:
        data = self._request("POST", "/api/GraphMemory/add", json=request.to_dict())
        if isinstance(data, dict):
            return GraphAddResponse(
                deleted_entities=[GraphEntity(**e) for e in data.get("deleted_entities", [])] if data.get("deleted_entities") else None,
                added_entities=[GraphEntity(**e) for e in data.get("added_entities", [])] if data.get("added_entities") else None,
                relationships=[GraphRelationship(**r) for r in data.get("relationships", [])] if data.get("relationships") else None,
            )
        return GraphAddResponse()

    def search_graph_memory(self, request: GraphSearchRequest) -> list[GraphSearchResult]:
        data = self._request("POST", "/api/GraphMemory/search", json=request.to_dict())
        if isinstance(data, list):
            return [GraphSearchResult(**item) for item in data]
        return [GraphSearchResult(**data)]

    def get_graph_relationships(
        self,
        user_id: str | None = None,
        project_id: str | None = None,
        limit: int | None = None,
    ) -> list[GraphSearchResult]:
        params = {}
        if user_id is not None:
            params["userId"] = user_id
        if project_id is not None:
            params["projectId"] = project_id
        if limit is not None:
            params["limit"] = limit
        data = self._request("GET", "/api/GraphMemory/relationships", params=params)
        if isinstance(data, list):
            return [GraphSearchResult(**item) for item in data]
        return [GraphSearchResult(**data)]

    def delete_all_graph_memory(
        self,
        user_id: str | None = None,
        project_id: str | None = None,
    ) -> None:
        params = {}
        if user_id is not None:
            params["userId"] = user_id
        if project_id is not None:
            params["projectId"] = project_id
        self._request("DELETE", "/api/GraphMemory/delete-all", params=params)
        return None
