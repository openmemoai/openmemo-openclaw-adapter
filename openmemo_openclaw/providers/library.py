"""
Library provider — direct OpenMemo SDK calls (no server needed).
"""

from typing import List


class LibraryProvider:
    def __init__(self, db_path: str = "openmemo.db"):
        from openmemo import OpenMemo
        self._memory = OpenMemo(db_path=db_path)

    def write_memory(self, content: str, scene: str = "",
                     memory_type: str = "observation",
                     agent_id: str = "",
                     confidence: float = 0.8,
                     metadata: dict = None) -> str:
        return self._memory.write_memory(
            content=content,
            scene=scene,
            memory_type=memory_type,
            agent_id=agent_id,
            confidence=confidence,
            metadata=metadata,
        )

    def recall_context(self, query: str, scene: str = "",
                       agent_id: str = "",
                       limit: int = 5) -> List[str]:
        result = self._memory.recall_context(
            query=query,
            scene=scene,
            agent_id=agent_id,
            limit=limit,
            mode="kv",
        )
        return result.get("context", [])

    def search_memory(self, query: str, scene: str = "",
                      agent_id: str = "",
                      limit: int = 10) -> List[dict]:
        return self._memory.search_memory(
            query=query,
            scene=scene,
            agent_id=agent_id,
            limit=limit,
        )

    def list_scenes(self, agent_id: str = "") -> List[str]:
        return self._memory.list_scenes(agent_id=agent_id)

    def close(self):
        self._memory.close()
