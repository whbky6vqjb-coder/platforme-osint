import json
import os
import time
import threading
from typing import Any, Dict, List, Optional
from datetime import datetime


class HFStateStore:
    def __init__(self, dataset_name: str = "platforme-osint/state", token: str = ""):
        self.dataset_name = dataset_name
        self.token = token or os.environ.get("HF_TOKEN", "")
        self._client = None

    def _get_client(self):
        if self._client is not None:
            return self._client
        try:
            from huggingface_hub import HfApi
            self._client = HfApi(token=self.token)
        except ImportError:
            self._client = None
        return self._client

    def read(self, filename: str = "state.json") -> Optional[Dict[str, Any]]:
        client = self._get_client()
        if client is None:
            return None
        try:
            import huggingface_hub
            path = huggingface_hub.hf_hub_download(
                repo_id=self.dataset_name,
                filename=filename,
                repo_type="dataset",
                token=self.token,
            )
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return None

    def write(self, data: Dict[str, Any], filename: str = "state.json") -> bool:
        client = self._get_client()
        if client is None:
            return False
        try:
            import tempfile
            with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                temp_path = f.name
            client.upload_file(
                path_or_fileobj=temp_path,
                path_in_repo=filename,
                repo_id=self.dataset_name,
                repo_type="dataset",
                token=self.token,
            )
            os.unlink(temp_path)
            return True
        except Exception:
            return False

    def list_files(self) -> List[str]:
        client = self._get_client()
        if client is None:
            return []
        try:
            return client.list_repo_files(self.dataset_name, repo_type="dataset")
        except Exception:
            return []


class InvestigationState:
    def __init__(self):
        self.turns: List[Dict[str, Any]] = []
        self.summaries: List[str] = []
        self.failed_attempts: List[Dict[str, Any]] = []
        self.total_tokens: int = 0
        self.investigation_id: str = ""
        self.start_time: float = 0.0
        self.last_save_time: float = 0.0
        self.optimization_stats: Dict[str, Any] = {}
        self.model_used: str = ""
        self.context_window: int = 0
        self.compression_ratio: float = 0.0
        self.session_id: str = ""
        self.machine_id: str = ""
        self.session_start: float = 0.0
        self.session_expires: float = 0.0
        self.handoff_ready: bool = False
        self.next_leader: str = ""
        self.total_sessions_run: int = 0
        self.total_hours_investigated: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "turns": [
                {"role": t.role, "content": t.content, "tokens": t.tokens}
                for t in self.turns
            ],
            "summaries": list(self.summaries),
            "failed_attempts": list(self.failed_attempts),
            "total_tokens": self.total_tokens,
            "investigation_id": self.investigation_id,
            "start_time": self.start_time,
            "last_save_time": self.last_save_time,
            "optimization_stats": self.optimization_stats,
            "model_used": self.model_used,
            "context_window": self.context_window,
            "compression_ratio": self.compression_ratio,
            "session_id": self.session_id,
            "machine_id": self.machine_id,
            "session_start": self.session_start,
            "session_expires": self.session_expires,
            "handoff_ready": self.handoff_ready,
            "next_leader": self.next_leader,
            "total_sessions_run": self.total_sessions_run,
            "total_hours_investigated": self.total_hours_investigated,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "InvestigationState":
        state = cls()
        state.turns = [
            type("ConversationTurn", (), t) for t in data.get("turns", [])
        ]
        state.summaries = list(data.get("summaries", []))
        state.failed_attempts = list(data.get("failed_attempts", []))
        state.total_tokens = data.get("total_tokens", 0)
        state.investigation_id = data.get("investigation_id", "")
        state.start_time = data.get("start_time", 0.0)
        state.last_save_time = data.get("last_save_time", 0.0)
        state.optimization_stats = data.get("optimization_stats", {})
        state.model_used = data.get("model_used", "")
        state.context_window = data.get("context_window", 0)
        state.compression_ratio = data.get("compression_ratio", 0.0)
        state.session_id = data.get("session_id", "")
        state.machine_id = data.get("machine_id", "")
        state.session_start = data.get("session_start", 0.0)
        state.session_expires = data.get("session_expires", 0.0)
        state.handoff_ready = data.get("handoff_ready", False)
        state.next_leader = data.get("next_leader", "")
        state.total_sessions_run = data.get("total_sessions_run", 0)
        state.total_hours_investigated = data.get("total_hours_investigated", 0.0)
        return state

    def to_dict(self) -> Dict[str, Any]:
        return {
            "turns": [
                {"role": t.role, "content": t.content, "tokens": t.tokens}
                for t in self.turns
            ],
            "summaries": list(self.summaries),
            "failed_attempts": list(self.failed_attempts),
            "total_tokens": self.total_tokens,
            "investigation_id": self.investigation_id,
            "start_time": self.start_time,
            "last_save_time": self.last_save_time,
            "optimization_stats": self.optimization_stats,
            "model_used": self.model_used,
            "context_window": self.context_window,
            "compression_ratio": self.compression_ratio,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "InvestigationState":
        state = cls()
        state.turns = [
            type("ConversationTurn", (), t) for t in data.get("turns", [])
        ]
        state.summaries = list(data.get("summaries", []))
        state.failed_attempts = list(data.get("failed_attempts", []))
        state.total_tokens = data.get("total_tokens", 0)
        state.investigation_id = data.get("investigation_id", "")
        state.start_time = data.get("start_time", 0.0)
        state.last_save_time = data.get("last_save_time", 0.0)
        state.optimization_stats = data.get("optimization_stats", {})
        state.model_used = data.get("model_used", "")
        state.context_window = data.get("context_window", 0)
        state.compression_ratio = data.get("compression_ratio", 0.0)
        return state


class PersistenceManager:
    def __init__(self, save_dir: str = None, save_interval_hours: float = 4.0, hf_dataset: str = "", hf_token: str = ""):
        self.save_dir = save_dir or os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "..", "..", "data", "persistence"
        )
        self.save_interval = save_interval_hours * 3600
        self._state: Optional[InvestigationState] = None
        self._timer: Optional[threading.Timer] = None
        self._last_save: float = 0.0
        self._save_count: int = 0
        self.hf_store = HFStateStore(dataset_name=hf_dataset, token=hf_token)
        os.makedirs(self.save_dir, exist_ok=True)

    def initialize_state(
        self,
        investigation_id: str = "",
        model_used: str = "",
        context_window: int = 0,
        compression_ratio: float = 0.0,
        session_id: str = "",
        machine_id: str = "",
        session_start: float = 0.0,
        session_expires: float = 0.0,
    ) -> InvestigationState:
        self._state = InvestigationState()
        self._state.investigation_id = investigation_id
        self._state.start_time = time.time()
        self._state.last_save_time = self._state.start_time
        self._state.model_used = model_used
        self._state.context_window = context_window
        self._state.compression_ratio = compression_ratio
        self._state.session_id = session_id
        self._state.machine_id = machine_id
        self._state.session_start = session_start
        self._state.session_expires = session_expires
        return self._state

    def get_state(self) -> InvestigationState:
        if self._state is None:
            self._state = InvestigationState()
        return self._state

    def save_turn(self, role: str, content: str, tokens: int):
        if self._state is None:
            return
        self._state.turns.append(
            type("ConversationTurn", (), {"role": role, "content": content, "tokens": tokens})
        )
        self._state.total_tokens += tokens

    def save_summary(self, summary: str):
        if self._state is None:
            return
        self._state.summaries.append(summary)

    def save_failed_attempt(self, query: str, reason: str, source: str = ""):
        if self._state is None:
            return
        self._state.failed_attempts.append(
            {
                "query": query,
                "reason": reason,
                "source": source,
                "timestamp": time.time(),
            }
        )

    def save_optimization_stats(self, stats: Dict[str, Any]):
        if self._state is None:
            return
        self._state.optimization_stats = stats

    def set_session_info(self, session_id: str, machine_id: str, session_start: float, session_expires: float):
        if self._state is None:
            return
        self._state.session_id = session_id
        self._state.machine_id = machine_id
        self._state.session_start = session_start
        self._state.session_expires = session_expires

    def set_handoff_info(self, handoff_ready: bool, next_leader: str):
        if self._state is None:
            return
        self._state.handoff_ready = handoff_ready
        self._state.next_leader = next_leader

    def auto_save(self) -> Dict[str, Any]:
        if self._state is None:
            return {"status": "no_state", "saved": False}

        now = time.time()
        if now - self._last_save < self.save_interval:
            return {"status": "not_due", "saved": False, "seconds_until_next": self.save_interval - (now - self._last_save)}

        result = self.save()
        self._last_save = time.time()
        return result

    def save(self) -> Dict[str, Any]:
        if self._state is None:
            return {"status": "no_state", "saved": False}

        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"investigation_{self._state.investigation_id or 'unknown'}_{timestamp}.json"
        filepath = os.path.join(self.save_dir, filename)

        data = self._state.to_dict()
        data["save_timestamp"] = time.time()
        data["save_count"] = self._save_count + 1

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        self._save_count += 1
        self._state.last_save_time = time.time()

        self.hf_store.write(data, filename="state.json")

        return {
            "status": "saved",
            "saved": True,
            "filepath": filepath,
            "filename": filename,
            "turns_saved": len(self._state.turns),
            "summaries_saved": len(self._state.summaries),
            "failed_attempts_saved": len(self._state.failed_attempts),
            "total_tokens_saved": self._state.total_tokens,
            "hf_synced": True,
        }

    def load_latest(self, investigation_id: str = "") -> Optional[InvestigationState]:
        hf_state = self.hf_store.read("state.json")
        if hf_state:
            state = InvestigationState.from_dict(hf_state)
            state.last_save_time = hf_state.get("save_timestamp", 0.0)
            self._state = state
            self._save_count = hf_state.get("save_count", 0)
            self._last_save = time.time()
            return state

        files = sorted(
            [f for f in os.listdir(self.save_dir) if f.endswith(".json")],
            reverse=True,
        )

        for filename in files:
            filepath = os.path.join(self.save_dir, filename)
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)

                if investigation_id and investigation_id not in filename:
                    continue

                state = InvestigationState.from_dict(data)
                state.last_save_time = data.get("save_timestamp", 0.0)
                self._state = state
                self._save_count = data.get("save_count", 0)
                self._last_save = time.time()

                return state
            except (json.JSONDecodeError, KeyError, TypeError):
                continue

        return None

    def load_all_for_investigation(self, investigation_id: str) -> List[InvestigationState]:
        states = []
        for filename in sorted(os.listdir(self.save_dir)):
            if not filename.endswith(".json"):
                continue
            if investigation_id not in filename:
                continue
            filepath = os.path.join(self.save_dir, filename)
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                state = InvestigationState.from_dict(data)
                state.last_save_time = data.get("save_timestamp", 0.0)
                states.append(state)
            except (json.JSONDecodeError, KeyError, TypeError):
                continue
        return states

    def get_save_stats(self) -> Dict[str, Any]:
        files = [f for f in os.listdir(self.save_dir) if f.endswith(".json")]
        total_saved = len(files)
        total_size = sum(
            os.path.getsize(os.path.join(self.save_dir, f)) for f in files
        )
        return {
            "save_dir": self.save_dir,
            "total_saves": total_saved,
            "total_size_bytes": total_size,
            "save_interval_hours": self.save_interval / 3600,
            "last_save_time": self._last_save,
            "save_count": self._save_count,
            "hf_dataset": self.hf_store.dataset_name,
            "hf_synced": True,
        }

    def start_auto_save_timer(self):
        def _auto_save_loop():
            while True:
                time.sleep(self.save_interval)
                self.auto_save()

        self._timer = threading.Thread(target=_auto_save_loop, daemon=True)
        self._timer.start()
        return self._timer

    def stop_auto_save_timer(self):
        if self._timer is not None:
            self._timer.cancel()
            self._timer = None

    def force_save(self) -> Dict[str, Any]:
        self._last_save = 0.0
        return self.save()

    def cleanup_old_saves(self, max_age_hours: float = 168.0):
        now = time.time()
        max_age_seconds = max_age_hours * 3600
        deleted = 0
        for filename in os.listdir(self.save_dir):
            if not filename.endswith(".json"):
                continue
            filepath = os.path.join(self.save_dir, filename)
            try:
                if now - os.path.getmtime(filepath) > max_age_seconds:
                    os.remove(filepath)
                    deleted += 1
            except OSError:
                continue
        return {"deleted": deleted, "max_age_hours": max_age_hours}

    def merge_states(self, states: List[InvestigationState]) -> InvestigationState:
        if not states:
            return InvestigationState()

        merged = InvestigationState()
        merged.investigation_id = states[0].investigation_id
        merged.model_used = states[0].model_used
        merged.context_window = states[0].context_window
        merged.compression_ratio = states[0].compression_ratio
        merged.start_time = min(s.start_time for s in states)
        merged.session_id = states[-1].session_id
        merged.machine_id = states[-1].machine_id
        merged.total_sessions_run = len(states)

        all_turns = []
        all_summaries = []
        all_failed = []
        total_tokens = 0

        for state in states:
            all_turns.extend(state.turns)
            all_summaries.extend(state.summaries)
            all_failed.extend(state.failed_attempts)
            total_tokens += state.total_tokens

        merged.turns = all_turns
        merged.summaries = all_summaries
        merged.failed_attempts = all_failed
        merged.total_tokens = total_tokens

        return merged