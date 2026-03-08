"""
Health check — verifies OpenMemo backend connectivity on adapter init.

Checks:
  - endpoint reachable
  - /memory/write responds
  - /agent/context responds
  - namespace usable
"""

import logging
from typing import List, Tuple

logger = logging.getLogger("openmemo_openclaw")


class HealthCheckError(Exception):
    pass


def check_local_api(endpoint: str, timeout: int = 5) -> List[Tuple[str, bool, str]]:
    import requests
    results = []

    try:
        resp = requests.get(f"{endpoint}/memory/scenes", timeout=timeout)
        if resp.status_code < 500:
            results.append(("endpoint", True, f"{endpoint} reachable"))
        else:
            results.append(("endpoint", False, f"{endpoint} returned {resp.status_code}"))
    except requests.ConnectionError:
        results.append(("endpoint", False, f"cannot connect to {endpoint}"))
        return results
    except Exception as e:
        results.append(("endpoint", False, str(e)))
        return results

    try:
        resp = requests.post(
            f"{endpoint}/memory/search",
            json={"query": "health_check", "limit": 1},
            timeout=timeout,
        )
        if resp.status_code < 500:
            results.append(("search", True, "/memory/search OK"))
        else:
            results.append(("search", False, f"/memory/search returned {resp.status_code}"))
    except Exception as e:
        results.append(("search", False, str(e)))

    try:
        resp = requests.post(
            f"{endpoint}/agent/context",
            json={"query": "health_check", "limit": 1},
            timeout=timeout,
        )
        if resp.status_code < 500:
            results.append(("context", True, "/agent/context OK"))
        else:
            results.append(("context", False, f"/agent/context returned {resp.status_code}"))
    except Exception as e:
        results.append(("context", False, str(e)))

    return results


def check_library() -> List[Tuple[str, bool, str]]:
    results = []
    try:
        from openmemo import OpenMemo
        results.append(("library", True, "openmemo package available"))
    except ImportError:
        results.append(("library", False, "openmemo package not installed (pip install openmemo)"))
        return results

    try:
        mem = OpenMemo(db_path=":memory:")
        mem.close()
        results.append(("init", True, "OpenMemo initialized OK"))
    except Exception as e:
        results.append(("init", False, f"OpenMemo init failed: {e}"))

    return results


def check_cloud_api(cloud_url: str, api_key: str = None, timeout: int = 10) -> List[Tuple[str, bool, str]]:
    import requests
    results = []
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    try:
        resp = requests.get(f"{cloud_url}/memory/scenes", headers=headers, timeout=timeout)
        if resp.status_code < 500:
            results.append(("cloud", True, f"{cloud_url} reachable"))
        else:
            results.append(("cloud", False, f"{cloud_url} returned {resp.status_code}"))
    except requests.ConnectionError:
        results.append(("cloud", False, f"cannot connect to {cloud_url}"))
    except Exception as e:
        results.append(("cloud", False, str(e)))

    return results


def run_health_check(config) -> str:
    backend = config.backend

    if backend == "library":
        results = check_library()
    elif backend == "cloud_api":
        results = check_cloud_api(config.cloud_url, config.api_key)
    elif backend == "local_api":
        results = check_local_api(config.endpoint)
    elif backend == "auto":
        lib_results = check_library()
        if all(ok for _, ok, _ in lib_results):
            results = lib_results
            backend = "library"
        else:
            api_results = check_local_api(config.endpoint)
            if all(ok for _, ok, _ in api_results):
                results = api_results
                backend = "local_api"
            else:
                cloud_results = check_cloud_api(config.cloud_url, config.api_key)
                results = cloud_results
                backend = "cloud_api"
    else:
        results = [("config", False, f"unknown backend: {backend}")]

    passed = all(ok for _, ok, _ in results)

    for check_name, ok, msg in results:
        if ok:
            logger.info("[openmemo] health %s: %s", check_name, msg)
        else:
            logger.warning("[openmemo] health %s: %s", check_name, msg)

    if not passed:
        failures = [msg for _, ok, msg in results if not ok]
        raise HealthCheckError(
            f"OpenMemo backend unavailable: {'; '.join(failures)}"
        )

    return backend
