from __future__ import annotations

import json
from datetime import date
from typing import Any, Dict, List

from django.http import HttpRequest, JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .scoring import compute_task_score


def _parse_request_body(request: HttpRequest) -> Dict[str, Any]:
    try:
        body_unicode = request.body.decode("utf-8")
        if not body_unicode.strip():
            return {}
        return json.loads(body_unicode)
    except Exception:
        return {}


@csrf_exempt
def analyze_tasks(request: HttpRequest) -> JsonResponse:
    if request.method != "POST":
        return JsonResponse({"detail": "Only POST is allowed."}, status=405)

    payload = _parse_request_body(request)
    raw_tasks = payload.get("tasks")

    if not isinstance(raw_tasks, list):
        return JsonResponse(
            {"detail": "Request body must contain a 'tasks' list."}, status=400
        )

    strategy = payload.get("strategy") or "default"

    scored: List[Dict[str, Any]] = []
    for item in raw_tasks:
        if not isinstance(item, dict):
            continue
        enriched = compute_task_score(item)
        scored.append(enriched)

    # Default sorting: by descending score, then earliest due date
    def sort_key(t: Dict[str, Any]):
        score = t.get("_score") or 0.0
        days = t.get("_days_until_due")
        return (-float(score), days if days is not None else 10 ** 6)

    scored.sort(key=sort_key)

    return JsonResponse({"tasks": scored, "strategy": strategy}, status=200)


@csrf_exempt
def suggest_tasks(request: HttpRequest) -> JsonResponse:
    if request.method not in ("GET", "POST"):
        return JsonResponse({"detail": "Only GET or POST is allowed."}, status=405)

    # Allow both GET (no body) and POST (same payload as analyze)
    raw_tasks: List[Dict[str, Any]] = []
    if request.method == "POST":
        payload = _parse_request_body(request)
        maybe_tasks = payload.get("tasks")
        if isinstance(maybe_tasks, list):
            raw_tasks = [t for t in maybe_tasks if isinstance(t, dict)]

    scored: List[Dict[str, Any]] = [compute_task_score(t) for t in raw_tasks]

    def sort_key(t: Dict[str, Any]):
        score = t.get("_score") or 0.0
        days = t.get("_days_until_due")
        return (-float(score), days if days is not None else 10 ** 6)

    scored.sort(key=sort_key)
    top = scored[:3]

    today = date.today().isoformat()
    explanations = [t.get("_explanation", "") for t in top]
    summary = (
        f"Top {len(top)} suggestions for {today}: "
        + " | ".join(explanations) if top else "No tasks provided to suggest from."
    )

    return JsonResponse({"tasks": top, "summary": summary}, status=200)
