import json
import os
import time
import threading
from typing import Any, Dict, List, Optional, Set
from datetime import datetime, timedelta


class KaggleSessionState:
    def __init__(self):
        self.session_id: str = ""
        self.machine_id: str = ""
        self.investigation_id: str = ""
        self.status: str = "idle"
        self.model_loaded: bool = False
        self.llama_server_port: int = 8080
        self.sliding_window_state: Dict[str, Any] = {}
        self.failed_attempts: List[Dict[str, Any]] = []
        self.trust_scores: Dict[str, Any] = {}
        self.report_draft: str = ""
        self.prompt_cache: Dict[str, str] = {}
        self.token_estimator_cache: Dict[str, int] = {}
        self.investigation_phase: str = "initial"
        self.current_query: str = ""
        self.entities_found: List[Dict[str, Any]] = []
        self.pivots_done: List[Dict[str, Any]] = []
        self.handoff_ready: bool = False
        self.next_leader: str = ""
        self.last_save: float = 0.0
        self.session_start: float = 0.0
        self.session_expires: float = 0.0
        self.heartbeat: float = 0.0
        self.total_sessions_run: int = 0
        self.total_hours_investigated: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "machine_id": self.machine_id,
            "investigation_id": self.investigation_id,
            "status": self.status,
            "model_loaded": self.model_loaded,
            "llama_server_port": self.llama_server_port,
            "sliding_window_state": self.sliding_window_state,
            "failed_attempts": self.failed_attempts,
            "trust_scores": self.trust_scores,
            "report_draft": self.report_draft,
            "prompt_cache": self.prompt_cache,
            "token_estimator_cache": self.token_estimator_cache,
            "investigation_phase": self.investigation_phase,
            "current_query": self.current_query,
            "entities_found": self.entities_found,
            "pivots_done": self.pivots_done,
            "handoff_ready": self.handoff_ready,
            "next_leader": self.next_leader,
            "last_save": self.last_save,
            "session_start": self.session_start,
            "session_expires": self.session_expires,
            "heartbeat": self.heartbeat,
            "total_sessions_run": self.total_sessions_run,
            "total_hours_investigated": self.total_hours_investigated,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "KaggleSessionState":
        state = cls()
        for key, value in data.items():
            if hasattr(state, key):
                setattr(state, key, value)
        return state


class KaggleCoordinator:
    def __init__(
        self,
        machine_id: str = "",
        hf_dataset_name: str = "platforme-osint/state",
        hf_token: str = "",
        state_file: str = "state.json",
        model_path: str = "",
        session_duration_hours: float = 11.5,
        handoff_warning_minutes: float = 30,
        save_interval_minutes: float = 15,
        heartbeat_interval_seconds: float = 60,
    ):
        self.machine_id = machine_id or os.environ.get("KAGGLE_SESSION_ID", "unknown")
        self.hf_dataset_name = hf_dataset_name
        self.hf_token = hf_token or os.environ.get("HF_TOKEN", "")
        self.state_file = state_file
        self.model_path = model_path or os.environ.get("MODEL_PATH", "")
        self.session_duration_hours = session_duration_hours
        self.handoff_warning_minutes = handoff_warning_minutes
        self.save_interval_minutes = save_interval_minutes
        self.heartbeat_interval_seconds = heartbeat_interval_seconds
        self._state: Optional[KaggleSessionState] = None
        self._hf_client = None
        self._auto_save_timer: Optional[threading.Timer] = None
        self._heartbeat_timer: Optional[threading.Timer] = None
        self._is_leader: bool = False
        self._session_start: float = 0.0
        self._last_save: float = 0.0
        self._last_heartbeat: float = 0.0
        self._last_handoff_check: float = 0.0
        self._shutdown_requested: bool = False

    def _get_hf_client(self):
        if self._hf_client is not None:
            return self._hf_client
        try:
            from huggingface_hub import HfApi
            self._hf_client = HfApi(token=self.hf_token)
        except ImportError:
            self._hf_client = None
        return self._hf_client

    def _read_state_from_hf(self) -> Optional[Dict[str, Any]]:
        client = self._get_hf_client()
        if client is None:
            return None
        try:
            files = client.list_repo_files(self.hf_dataset_name, repo_type="dataset")
            if self.state_file not in files:
                return None
            import huggingface_hub
            path = huggingface_hub.hf_hub_download(
                repo_id=self.hf_dataset_name,
                filename=self.state_file,
                repo_type="dataset",
                token=self.hf_token,
            )
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return None

    def _write_state_to_hf(self, state: Dict[str, Any]) -> bool:
        client = self._get_hf_client()
        if client is None:
            return False
        try:
            import tempfile
            with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
                json.dump(state, f, ensure_ascii=False, indent=2)
                temp_path = f.name
            client.upload_file(
                path_or_fileobj=temp_path,
                path_in_repo=self.state_file,
                repo_id=self.hf_dataset_name,
                repo_type="dataset",
                token=self.hf_token,
            )
            os.unlink(temp_path)
            return True
        except Exception:
            return False

    def initialize_session(self, investigation_id: str = "", model_path: str = "") -> KaggleSessionState:
        state = KaggleSessionState()
        state.session_id = f"{self.machine_id}_{int(time.time())}"
        state.machine_id = self.machine_id
        state.investigation_id = investigation_id or self._get_or_create_investigation_id()
        state.model_path = model_path or self.model_path
        state.session_start = time.time()
        state.session_expires = state.session_start + self.session_duration_hours * 3600
        state.last_save = state.session_start
        state.heartbeat = state.session_start
        state.total_sessions_run += 1
        self._state = state
        self._session_start = state.session_start
        return state

    def _get_or_create_investigation_id(self) -> str:
        existing = self._read_state_from_hf()
        if existing and "investigation_id" in existing:
            return existing["investigation_id"]
        return f"investigation_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"

    def claim_leadership(self) -> bool:
        state = self._read_state_from_hf()
        if state is None:
            state = {}
        if state.get("status") == "running" and state.get("machine_id") != self.machine_id:
            time_since_heartbeat = time.time() - state.get("heartbeat", 0)
            if time_since_heartbeat < self.session_duration_hours * 3600:
                return False
        state["status"] = "running"
        state["machine_id"] = self.machine_id
        state["session_start"] = time.time()
        state["session_expires"] = state["session_start"] + self.session_duration_hours * 3600
        state["handoff_ready"] = False
        state["next_leader"] = ""
        self._write_state_to_hf(state)
        self._is_leader = True
        return True

    def release_leadership(self):
        state = self._read_state_from_hf()
        if state and state.get("machine_id") == self.machine_id:
            state["status"] = "idle"
            state["machine_id"] = ""
            state["handoff_ready"] = True
            self._write_state_to_hf(state)
        self._is_leader = False

    def save_state(self) -> Dict[str, Any]:
        if self._state is None:
            return {}
        state_dict = self._state.to_dict()
        state_dict["last_save"] = time.time()
        state_dict["heartbeat"] = time.time()
        state_dict["status"] = "running" if self._is_leader else "idle"
        self._write_state_to_hf(state_dict)
        self._last_save = time.time()
        return state_dict

    def load_state(self) -> Optional[KaggleSessionState]:
        state_dict = self._read_state_from_hf()
        if state_dict is None:
            return None
        state = KaggleSessionState.from_dict(state_dict)
        self._state = state
        return state

    def should_handoff(self) -> bool:
        if self._state is None:
            return False
        remaining = self._state.session_expires - time.time()
        return remaining < self.handoff_warning_minutes * 60

    def should_save(self) -> bool:
        return time.time() - self._last_save > self.save_interval_minutes * 60

    def should_heartbeat(self) -> bool:
        return time.time() - self._last_heartbeat > self.heartbeat_interval_seconds

    def get_time_remaining(self) -> float:
        if self._state is None:
            return 0
        return max(0, self._state.session_expires - time.time())

    def get_session_duration_elapsed(self) -> float:
        if self._state is None:
            return 0
        return time.time() - self._state.session_start

    def transfer_leadership(self, next_machine: str) -> bool:
        state = self._state.to_dict() if self._state else {}
        state["handoff_ready"] = True
        state["next_leader"] = next_machine
        state["status"] = "handoff"
        state["machine_id"] = ""
        state["last_save"] = time.time()
        success = self._write_state_to_hf(state)
        if success:
            self._is_leader = False
        return success

    def resume_after_handoff(self) -> bool:
        state_dict = self._read_state_from_hf()
        if state_dict is None or not state_dict.get("handoff_ready"):
            return False
        state = KaggleSessionState.from_dict(state_dict)
        state.session_id = f"{self.machine_id}_{int(time.time())}"
        state.machine_id = self.machine_id
        state.status = "running"
        state.session_start = time.time()
        state.session_expires = state.session_start + self.session_duration_hours * 3600
        state.handoff_ready = False
        state.next_leader = ""
        state.total_sessions_run += 1
        state.total_hours_investigated += self.get_session_duration_elapsed()
        self._state = state
        self._session_start = state.session_start
        self._is_leader = True
        self._write_state_to_hf(state.to_dict())
        return True

    def start_auto_save_loop(self):
        def _auto_save_loop():
            while not self._shutdown_requested:
                time.sleep(60)
                if self.should_save():
                    self.save_state()
                if self.should_handoff():
                    self._on_handoff_warning()

        self._auto_save_timer = threading.Thread(target=_auto_save_loop, daemon=True)
        self._auto_save_timer.start()
        return self._auto_save_timer

    def start_heartbeat_loop(self):
        def _heartbeat_loop():
            while not self._shutdown_requested:
                time.sleep(self.heartbeat_interval_seconds)
                if self._is_leader:
                    self.save_state()

        self._heartbeat_timer = threading.Thread(target=_heartbeat_loop, daemon=True)
        self._heartbeat_timer.start()
        return self._heartbeat_timer

    def _on_handoff_warning(self):
        remaining_minutes = self.get_time_remaining() / 60
        print(f"[KAGGLE COORDINATOR] WARNING: {remaining_minutes:.0f} minutes remaining. Preparing handoff.")

    def shutdown(self):
        self._shutdown_requested = True
        self.save_state()
        self.release_leadership()
        if self._auto_save_timer:
            self._auto_save_timer.cancel()
        if self._heartbeat_timer:
            self._heartbeat_timer.cancel()

    def get_coordination_stats(self) -> Dict[str, Any]:
        return {
            "machine_id": self.machine_id,
            "is_leader": self._is_leader,
            "session_id": self._state.session_id if self._state else "",
            "investigation_id": self._state.investigation_id if self._state else "",
            "time_remaining_seconds": self.get_time_remaining(),
            "time_remaining_minutes": self.get_time_remaining() / 60,
            "session_elapsed_seconds": self.get_session_duration_elapsed(),
            "session_elapsed_hours": self.get_session_duration_elapsed() / 3600,
            "total_sessions_run": self._state.total_sessions_run if self._state else 0,
            "total_hours_investigated": self._state.total_hours_investigated if self._state else 0,
            "last_save": self._last_save,
            "handoff_ready": self._state.handoff_ready if self._state else False,
            "next_leader": self._state.next_leader if self._state else "",
            "shutdown_requested": self._shutdown_requested,
        }


class KaggleMachineManager:
    def __init__(self, machines: List[str], hf_dataset_name: str = "platforme-osint/state"):
        self.machines = machines
        self.hf_dataset_name = hf_dataset_name
        self.current_index = 0

    def get_next_machine(self) -> str:
        machine = self.machines[self.current_index % len(self.machines)]
        self.current_index += 1
        return machine

    def get_current_leader(self) -> Optional[str]:
        pass

    def rotate_machines(self) -> List[str]:
        return self.machines[self.current_index:] + self.machines[:self.current_index]