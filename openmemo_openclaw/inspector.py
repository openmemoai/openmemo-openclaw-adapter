"""
Memory Inspector Server — built-in dashboard for openmemo-openclaw.

Provides a lightweight HTTP server (stdlib only, zero extra dependencies) that
serves the Inspector Dashboard UI and all required API endpoints.

Auto-starts when features["inspector"] is True in AdapterConfig.
Default port: 8780 → http://localhost:8780/inspector
"""

import json
import logging
import threading
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

from openmemo_openclaw.inspector_html import INSPECTOR_HTML
from openmemo_openclaw.version_check import get_local_versions

logger = logging.getLogger("openmemo_openclaw")


class InspectorServer:
    def __init__(self, adapter, port: int = 8780):
        self._adapter = adapter
        self._port = port
        self._server = None
        self._thread = None
        self._running = False

    def start(self):
        if self._running:
            return
        handler_class = _make_handler(self._adapter)
        try:
            self._server = HTTPServer(("127.0.0.1", self._port), handler_class)
            self._thread = threading.Thread(
                target=self._server.serve_forever,
                daemon=True,
                name="openmemo-inspector",
            )
            self._thread.start()
            self._running = True
            logger.info(
                "[openmemo] Memory Inspector started → http://localhost:%d/inspector",
                self._port,
            )
        except OSError as e:
            logger.warning("[openmemo] Inspector failed to start on port %d: %s", self._port, e)

    def stop(self):
        if self._server and self._running:
            self._server.shutdown()
            self._server.server_close()
            if self._thread:
                self._thread.join(timeout=5)
            self._running = False
            logger.info("[openmemo] Inspector stopped")

    @property
    def url(self) -> str:
        return f"http://localhost:{self._port}/inspector"

    @property
    def running(self) -> bool:
        return self._running


def _make_handler(adapter):
    class InspectorHandler(BaseHTTPRequestHandler):
        def log_message(self, format, *args):
            pass

        def _send_json(self, data, status=200):
            body = json.dumps(data).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def _send_html(self, html):
            body = html.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_OPTIONS(self):
            self.send_response(204)
            self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
            self.send_header("Access-Control-Allow-Headers", "Content-Type")
            self.end_headers()

        def do_GET(self):
            parsed = urlparse(self.path)
            path = parsed.path.rstrip("/")
            qs = parse_qs(parsed.query)

            if path == "/inspector" or path == "":
                self._serve_inspector()
            elif path == "/api/inspector/checklist":
                self._serve_checklist()
            elif path == "/api/inspector/memory-summary":
                self._serve_memory_summary()
            elif path == "/api/inspector/health":
                self._serve_health()
            elif path == "/api/inspector/recent":
                self._serve_recent()
            elif path == "/api/inspector/search":
                q = qs.get("q", [""])[0]
                self._serve_search(q)
            elif path == "/api/inspector/rules":
                self._serve_rules()
            elif path == "/version":
                self._serve_version()
            else:
                self.send_response(404)
                self.end_headers()

        def do_POST(self):
            parsed = urlparse(self.path)
            path = parsed.path.rstrip("/")

            if path == "/session/scene_override":
                self._handle_scene_override()
            else:
                self.send_response(404)
                self.end_headers()

        def _serve_inspector(self):
            self._send_html(INSPECTOR_HTML)

        def _serve_checklist(self):
            checks = []

            try:
                adapter._client.list_scenes()
                checks.append({"name": "Backend Connected", "status": "ok"})
            except Exception:
                checks.append({"name": "Backend Connected", "status": "fail"})

            worker = adapter._async_worker or adapter._sync_worker
            if worker:
                checks.append({"name": "Pipeline Active", "status": "ok"})
                stats = worker.stats if hasattr(worker, "stats") else {}
                if stats.get("failed", 0) == 0:
                    checks.append({"name": "Write Healthy", "status": "ok"})
                else:
                    checks.append({"name": "Write Healthy", "status": "warning"})
            else:
                checks.append({"name": "Pipeline Active", "status": "fail"})
                checks.append({"name": "Write Healthy", "status": "fail"})

            try:
                adapter._client.search_memory(query="health_check_probe", limit=1)
                checks.append({"name": "Recall Working", "status": "ok"})
            except Exception:
                checks.append({"name": "Recall Working", "status": "fail"})

            feat = adapter._config.features
            checks.append({
                "name": "Task Dedup Active",
                "status": "ok" if feat.get("task_precheck", True) else "warning",
            })
            checks.append({
                "name": "Conflict Suppression",
                "status": "ok" if feat.get("suppression", True) else "warning",
            })

            mr = adapter.memory_rules if hasattr(adapter, "memory_rules") else None
            checks.append({
                "name": "Memory Rules",
                "status": "ok" if mr and mr.enabled else "warning",
            })

            overall = "ok"
            if any(c["status"] == "fail" for c in checks):
                overall = "fail"
            elif any(c["status"] == "warning" for c in checks):
                overall = "warning"

            self._send_json({"status": overall, "checks": checks})

        def _serve_memory_summary(self):
            try:
                scenes = adapter._client.list_scenes()
            except Exception:
                scenes = []

            memories = []
            try:
                memories = adapter._client.search_memory(query="", limit=200)
            except Exception:
                try:
                    memories = adapter._client.search_memory(query="*", limit=200)
                except Exception:
                    pass

            type_dist = {}
            scene_dist = {}
            for m in memories:
                mt = m.get("memory_type") or m.get("cell_type") or m.get("type") or "unknown"
                sc = m.get("scene") or "general"
                type_dist[mt] = type_dist.get(mt, 0) + 1
                scene_dist[sc] = scene_dist.get(sc, 0) + 1

            if not scene_dist and scenes:
                for s in scenes:
                    scene_dist[s] = scene_dist.get(s, 0)

            self._send_json({
                "total_memories": len(memories),
                "total_cells": len(memories),
                "total_scenes": len(scenes) or len(scene_dist),
                "type_distribution": type_dist,
                "scene_distribution": scene_dist,
            })

        def _serve_health(self):
            status = "ok"
            try:
                adapter._client.list_scenes()
            except Exception:
                status = "fail"

            worker = adapter._async_worker or adapter._sync_worker
            if worker and hasattr(worker, "stats"):
                wstats = worker.stats
                if wstats.get("failed", 0) > 0:
                    status = "warning" if status == "ok" else status

            total_memories = 0
            total_scenes = 0
            try:
                scenes = adapter._client.list_scenes()
                total_scenes = len(scenes)
                results = adapter._client.search_memory(query="", limit=1)
                total_memories = len(results)
            except Exception:
                if status == "ok":
                    status = "cold_start"

            from openmemo_openclaw import __version__ as adapter_version

            self._send_json({
                "status": status,
                "backend": adapter._config.backend,
                "api_version": "0.6.0",
                "engine_version": f"openmemo-openclaw {adapter_version}",
                "total_memories": total_memories,
                "total_scenes": total_scenes,
            })

        def _serve_recent(self):
            try:
                results = adapter._client.search_memory(query="", limit=20)
                if not results:
                    results = adapter._client.search_memory(query="*", limit=20)
            except Exception:
                results = []

            try:
                from openmemo_openclaw.ranker import rank_memories
                conflict = adapter._config.conflict_policy
                if not adapter._config.features.get("suppression", True):
                    conflict = "none"
                ranked = rank_memories(
                    results,
                    current_scene=adapter._current_scene,
                    conflict_policy=conflict,
                )
                results = ranked
            except Exception:
                pass

            self._send_json({"recent": results})

        def _serve_search(self, query):
            if not query or len(query) < 2:
                self._send_json({"results": []})
                return
            try:
                results = adapter._client.search_memory(query=query, limit=20)
            except Exception:
                results = []

            try:
                from openmemo_openclaw.ranker import rank_memories
                conflict = adapter._config.conflict_policy
                if not adapter._config.features.get("suppression", True):
                    conflict = "none"
                results = rank_memories(
                    results,
                    current_scene=adapter._current_scene,
                    conflict_policy=conflict,
                )
            except Exception:
                pass

            self._send_json({"results": results})

        def _serve_rules(self):
            rules = adapter.memory_rules if hasattr(adapter, "memory_rules") else None
            if rules:
                status = rules.status
                self._send_json({
                    "enabled": status["enabled"],
                    "version": status["version"],
                    "mode": adapter._config.memory_rules_mode,
                    "rule_count": status["rule_count"],
                    "custom_rules": status["custom_rules"],
                    "rules_text": rules.rules_text if status["enabled"] else "",
                })
            else:
                self._send_json({
                    "enabled": False,
                    "version": "0",
                    "mode": "disabled",
                    "rule_count": 0,
                    "custom_rules": 0,
                    "rules_text": "",
                })

        def _serve_version(self):
            versions = get_local_versions()
            self._send_json({
                "latest_core": versions.get("core") or "0.6.0",
                "latest_adapter": versions.get("adapter") or "2.2.0",
                "schema_version": 2,
            })

        def _handle_scene_override(self):
            try:
                length = int(self.headers.get("Content-Length", 0))
                body = json.loads(self.rfile.read(length)) if length > 0 else {}
                scene = body.get("scene", "")
                if not scene:
                    self._send_json({"error": "scene required"}, 400)
                    return
                adapter.scene_override(scene)
                self._send_json({"ok": True, "scene": scene})
            except Exception as e:
                self._send_json({"error": str(e)}, 500)

    return InspectorHandler
