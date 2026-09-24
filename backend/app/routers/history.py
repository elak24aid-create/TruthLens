import os
import json
import uuid
from pathlib import Path
from typing import List
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, status
from backend.app.schemas.history import HistoryItemCreate, HistoryItemResponse
from backend.app.config import BASE_DIR

router = APIRouter(prefix="/history", tags=["History"])

HISTORY_FILE = BASE_DIR / "data" / "history.json"


def _load_history() -> List[dict]:
    if not os.path.exists(HISTORY_FILE):
        return []
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def _save_history(items: List[dict]):
    HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(items, f, indent=2)


@router.get("", response_model=List[HistoryItemResponse])
def get_history():
    """
    Retrieves the list of previous checks sorted by newest first.
    """
    items = _load_history()
    # Sort descending by timestamp
    return sorted(items, key=lambda x: x.get("timestamp", ""), reverse=True)


@router.post("", response_model=HistoryItemResponse, status_code=status.HTTP_201_CREATED)
def add_history_entry(entry: HistoryItemCreate):
    """
    Saves an analysis check to local history.
    """
    items = _load_history()
    new_item = {
        "id": str(uuid.uuid4()),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "text_snippet": entry.text_snippet[:200],
        "verdict": entry.verdict.value,
        "confidence": entry.confidence,
        "summary": entry.summary,
        "input_type": entry.input_type,
        "url": entry.url,
        "analysis_result": entry.analysis_result,
        "research_result": entry.research_result,
    }
    items.insert(0, new_item)
    _save_history(items)
    return new_item


@router.delete("/{item_id}")
def delete_history_entry(item_id: str):
    """
    Deletes a specific history check by its ID.
    """
    items = _load_history()
    filtered = [item for item in items if item.get("id") != item_id]
    if len(filtered) == len(items):
        raise HTTPException(status_code=404, detail="History entry not found")
    _save_history(filtered)
    return {"status": "success", "message": f"History entry {item_id} deleted."}


@router.delete("")
def clear_all_history():
    """
    Clears all saved history entries.
    """
    _save_history([])
    return {"status": "success", "message": "All history records cleared."}
