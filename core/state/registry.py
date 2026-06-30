# core/state/registry.py
from typing import Dict, Any

active_jobs: Dict[str, Any] = {}
live_progress: Dict[str, Any] = {}
active_processes: Dict[str, Any] = {}
