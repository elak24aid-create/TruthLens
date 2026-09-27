import os
import json
import uuid
from pathlib import Path
from typing import List, Optional
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, status, Header
from app.schemas.history import HistoryItemCreate, HistoryItemResponse
from app.config import BASE_DIR

router = APIRouter(prefix="/history", tags=["History"])

HISTORY_FILE = BASE_DIR / "data" / "history.json"
USERS_FILE = BASE_DIR / "data" / "users.json"

def _get_current_user(authorization: str) -> Optional[str]:
    if not authorization or not authorization.startswith("Bearer "):
        return None
    token = authorization.split(" ")[1]
    if not os.path.exists(USERS_FILE):
        return None
    try:
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            users = json.load(f)
            for email, data in users.items():
                if data.get("token") == token:
                    return email
    except:
        pass
    return None

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
def get_history(authorization: Optional[str] = Header(None)):
    """
    Retrieves the list of previous checks sorted by newest first.
    """
    user_id = _get_current_user(authorization) if authorization else None
    
    items = _load_history()
    # Filter by user if logged in, else only show anonymous items
    if user_id:
        items = [i for i in items if i.get("user_id") == user_id]
    else:
        items = [i for i in items if not i.get("user_id")]
        
    # Sort descending by timestamp
    return sorted(items, key=lambda x: x.get("timestamp", ""), reverse=True)

@router.post("", response_model=HistoryItemResponse, status_code=status.HTTP_201_CREATED)
def add_history_entry(entry: HistoryItemCreate, authorization: Optional[str] = Header(None)):
    """
    Saves an analysis check to local history.
    """
    user_id = _get_current_user(authorization) if authorization else None
    
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
        "user_id": user_id
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
