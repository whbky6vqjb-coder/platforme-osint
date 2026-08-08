import os
import sys
import json
import time

def setup_hf_dataset():
    hf_token = os.environ.get("HF_TOKEN")
    if not hf_token:
        print("ERROR: HF_TOKEN environment variable not set")
        print("Set it with: $env:HF_TOKEN = 'your_hf_token'")
        sys.exit(1)

    try:
        from huggingface_hub import HfApi, create_repo
        api = HfApi(token=hf_token)

        repo_id = "platforme-osint/state"
        repo_type = "dataset"

        try:
            api.repo_info(repo_id=repo_id, repo_type=repo_type, token=hf_token)
            print(f"Dataset {repo_id} already exists")
        except Exception:
            print(f"Creating dataset {repo_id}...")
            create_repo(repo_id=repo_id, repo_type=repo_type, token=hf_token, exist_ok=True)
            print(f"Dataset {repo_id} created successfully")

        state_file = "state.json"
        initial_state = {
            "status": "idle",
            "machine_id": "",
            "session_start": 0,
            "session_expires": 0,
            "handoff_ready": False,
            "next_leader": "",
            "last_save": time.time(),
            "heartbeat": time.time(),
            "investigation_id": "",
            "sliding_window": {"turns": [], "summaries": [], "total_tokens": 0},
            "failed_attempts": [],
            "trust_scores": {},
            "report_draft": "",
            "prompt_cache": {},
            "token_estimator_cache": {},
        }

        local_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "persistence", state_file)
        os.makedirs(os.path.dirname(local_path), exist_ok=True)

        with open(local_path, "w") as f:
            json.dump(initial_state, f, indent=2)
        print(f"Initial state file written to {local_path}")

        try:
            api.upload_file(
                path_or_fileobj=local_path,
                path_in_repo=state_file,
                repo_id=repo_id,
                repo_type=repo_type,
                token=hf_token,
            )
            print(f"State file uploaded to {repo_id}/{state_file}")
        except Exception as e:
            print(f"Warning: Could not upload to HF Dataset: {e}")
            print("State file saved locally for manual upload")

        print("HF Dataset setup complete")

    except ImportError:
        print("ERROR: huggingface_hub not installed")
        print("Install with: pip install huggingface_hub")
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)

if __name__ == "__main__":
    setup_hf_dataset()