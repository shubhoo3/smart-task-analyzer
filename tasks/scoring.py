from __future__ import annotations

from datetime import date
from typing import Any, Dict, List


def compute_task_score(task: Dict[str, Any]) -> Dict[str, Any]:
    """Compute a priority score for a single task.

    The function is defensive: it tolerates missing or malformed data
    and attaches an explanation string describing the reasoning.
    """
    today = date.today()
    title = task.get("title") or "Untitled Task"

    # Parse due_date
    raw_due = task.get("due_date")
    due_date = None
    due_explanation = ""
    urgency_score = 0.0

    if isinstance(raw_due, date):
        due_date = raw_due
    elif isinstance(raw_due, str):
        try:
            # Expecting ISO format YYYY-MM-DD
            year, month, day = [int(x) for x in raw_due.split("-")]
            due_date = date(year, month, day)
        except Exception:
            due_explanation = "Invalid due_date format; treated as no deadline. "
    else:
        if raw_due is not None:
            due_explanation = "Unrecognized due_date; treated as no deadline. "

    days_until_due = None
    if due_date is not None:
        delta = (due_date - today).days
        days_until_due = delta
        if delta < 0:
            urgency_score = 1.5  # Past due: highest urgency boost
            due_explanation += "Task is past due; strong urgency boost. "
        elif delta == 0:
            urgency_score = 1.3  # Due today
            due_explanation += "Task is due today; high urgency boost. "
        elif delta <= 3:
            urgency_score = 1.1  # Due soon
            due_explanation += "Task is due soon (<= 3 days); moderate urgency boost. "
        elif delta <= 7:
            urgency_score = 1.0
            due_explanation += "Task is due within a week; neutral urgency. "
        else:
            urgency_score = 0.8
            due_explanation += "Task is far in the future; slightly reduced urgency. "
    else:
        urgency_score = 0.9
        due_explanation += "No valid due date; mild penalty to urgency. "

    # Importance (1–10, default 5)
    raw_importance = task.get("importance", 5)
    try:
        importance = int(raw_importance)
    except Exception:
        importance = 5
    importance = max(1, min(importance, 10))

    # Estimated hours (effort). Lower effort is slightly favored.
    raw_effort = task.get("estimated_hours", 1)
    try:
        estimated_hours = float(raw_effort)
        if estimated_hours <= 0:
            estimated_hours = 1.0
    except Exception:
        estimated_hours = 1.0

    # Dependencies: assume a list of identifiers; penalize if non-empty.
    raw_deps = task.get("dependencies")
    if isinstance(raw_deps, list):
        dependencies: List[Any] = raw_deps
    elif raw_deps in (None, "", {}):
        dependencies = []
    else:
        # Attempt to treat single value as one dependency
        dependencies = [raw_deps]

    dep_penalty = 0.0
    dep_explanation = ""
    if dependencies:
        dep_penalty = 0.2 + 0.05 * len(dependencies)
        dep_explanation = (
            f"Task has {len(dependencies)} dependencies; small penalty applied. "
        )
    else:
        dep_explanation = "No dependencies; no penalty. "

    # Core scoring heuristic:
    #   base = importance (1–10)
    #   urgency multiplier: 0.8–1.5
    #   effort factor: smaller tasks get a small bonus (divide by log-like factor)
    #   dependencies subtract a small amount
    import math

    effort_factor = 1.0 / (1.0 + math.log10(estimated_hours + 1.0))

    base = float(importance)
    raw_score = base * urgency_score * effort_factor

    # Apply dependency penalty
    final_score = max(0.0, raw_score - dep_penalty)

    explanation = (
        f"Title: {title}. "
        f"Importance={importance}, Estimated hours={estimated_hours:.1f}, "
        f"Urgency multiplier={urgency_score:.2f}, Effort factor={effort_factor:.2f}. "
        f"Base score={raw_score:.2f}, Dependency penalty={dep_penalty:.2f}. "
        f"Final score={final_score:.2f}. "
        + due_explanation
        + dep_explanation
    )

    enriched = dict(task)
    enriched["_score"] = round(final_score, 4)
    enriched["_explanation"] = explanation
    enriched["_days_until_due"] = days_until_due
    return enriched
