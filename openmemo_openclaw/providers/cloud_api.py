"""
Cloud API provider — HTTP calls to OpenMemo Cloud API.
Default endpoint: https://api.openmemo.ai
"""

from typing import List

import requests


class CloudAPIProvider:
    def __init__(self, base_url: str = "https://api.openmemo.ai",
                 api_key: str = None, timeout: int = 30):
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._session = requests.Session()
        self._session.headers["Content-Type"] = "application/json"
        if api_key:
            self._session.headers["Authorization"] = f"Bearer {api_key}"

    def write_memory(self, content: str, scene: str = "",
                     memory_type: str = "observation",
                     agent_id: str = "",
                     confidence: float = 0.8,
                     metadata: dict = None) -> str:
        data = {
            "content": content,
            "scene": scene,
            "type": memory_type,
            "confidence": confidence,
            "agent_id": agent_id,
        }
        if metadata:
            data["metadata"] = metadata

        resp = self._session.post(
            f"{self._base_url}/memory/write",
            json=data,
            timeout=self._timeout,
        )
        resp.raise_for_status()
        return resp.json().get("memory_id", "")

    def recall_context(self, query: str, scene: str = "",
                       agent_id: str = "",
                       limit: int = 5) -> List[str]:
        data = {
            "query": query,
            "limit": limit,
            "agent_id": agent_id,
        }
        if scene:
            data["scene"] = scene

        resp = self._session.post(
            f"{self._base_url}/agent/context",
            json=data,
            timeout=self._timeout,
        )
        resp.raise_for_status()
        return resp.json().get("memory_context", [])

    def search_memory(self, query: str, scene: str = "",
                      agent_id: str = "",
                      limit: int = 10) -> List[dict]:
        data = {
            "query": query,
            "limit": limit,
            "agent_id": agent_id,
        }
        if scene:
            data["scene"] = scene

        resp = self._session.post(
            f"{self._base_url}/memory/search",
            json=data,
            timeout=self._timeout,
        )
        resp.raise_for_status()
        return resp.json().get("results", [])

    def list_scenes(self, agent_id: str = "") -> List[str]:
        params = {}
        if agent_id:
            params["agent_id"] = agent_id

        resp = self._session.get(
            f"{self._base_url}/memory/scenes",
            params=params,
            timeout=self._timeout,
        )
        resp.raise_for_status()
        return resp.json().get("scenes", [])

    def close(self):
        self._session.close()
