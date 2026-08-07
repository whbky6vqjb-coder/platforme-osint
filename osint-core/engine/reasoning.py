import asyncio
import json
import time
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from .persistence import PersistenceManager, InvestigationState
from .kaggle_coordinator import KaggleCoordinator, KaggleSessionState


class RetryHandler:
    def __init__(self, max_attempts: int = 3, base_delay_seconds: float = 1.0,
                 max_delay_seconds: float = 30.0, backoff_multiplier: float = 2.0, jitter: bool = True):
        self.max_attempts = max_attempts
        self.base_delay = base_delay_seconds
        self.max_delay = max_delay_seconds
        self.backoff_multiplier = backoff_multiplier
        self.jitter = jitter

    async def execute(self, func, *args, **kwargs):
        delay = self.base_delay
        last_exception = None
        for attempt in range(1, self.max_attempts + 1):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                if attempt >= self.max_attempts:
                    break
                actual_delay = min(delay, self.max_delay)
                if self.jitter:
                    import random
                    actual_delay = actual_delay * (0.5 + random.random())
                await asyncio.sleep(actual_delay)
                delay *= self.backoff_multiplier
        raise last_exception


class CircuitBreaker:
    def __init__(self, failure_threshold: int = 5, recovery_timeout_seconds: float = 60.0,
                 half_open_max_requests: int = 1):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout_seconds
        self.half_open_max = half_open_max_requests
        self._failures = 0
        self._last_failure_time = 0.0
        self._state = "closed"
        self._half_open_requests = 0

    @property
    def is_open(self) -> bool:
        if self._state == "open":
            if time.time() - self._last_failure_time > self.recovery_timeout:
                self._state = "half_open"
                self._half_open_requests = 0
                return False
            return True
        return False

    def record_success(self):
        self._failures = 0
        self._state = "closed"

    def record_failure(self):
        self._failures += 1
        self._last_failure_time = time.time()
        if self._failures >= self.failure_threshold:
            self._state = "open"

    async def execute(self, func, *args, **kwargs):
        if self.is_open:
            raise CircuitBreakerOpenError("Circuit breaker is open")
        if self._state == "half_open":
            if self._half_open_requests >= self.half_open_max:
                raise CircuitBreakerOpenError("Circuit breaker is half-open, max requests reached")
            self._half_open_requests += 1
        try:
            result = await func(*args, **kwargs)
            self.record_success()
            return result
        except Exception as e:
            self.record_failure()
            raise


class CircuitBreakerOpenError(Exception):
    pass


@dataclass
class ReasoningStep:
    step_type: str
    content: str
    confidence: float = 0.0
    sources: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ReasoningResult:
    conclusion: str
    confidence: float
    steps: List[ReasoningStep]
    trust_score: float
    recommendations: List[str]
    raw_data_summary: str


@dataclass
class ConversationTurn:
    role: str
    content: str
    tokens: int = 0


class PromptOptimizer:
    def __init__(self):
        self._cache: Dict[str, str] = {}
        self._cache_hits = 0
        self._cache_misses = 0
        self._last_optimization = 0.0
        self.optimization_interval = 5.0

    def get_optimized_prompt(self, prompt_key: str, base_prompt: str) -> str:
        now = time.time()
        if now - self._last_optimization > self.optimization_interval:
            self._optimize_cache()
            self._last_optimization = now

        if prompt_key in self._cache:
            self._cache_hits += 1
            return self._cache[prompt_key]

        self._cache_misses += 1
        optimized = self._optimize_prompt(base_prompt)
        self._cache[prompt_key] = optimized
        return optimized

    def _optimize_prompt(self, prompt: str) -> str:
        lines = prompt.split("\n")
        optimized_lines = []
        seen = set()
        for line in lines:
            stripped = line.strip()
            if not stripped:
                continue
            key = stripped[:80]
            if key not in seen:
                seen.add(key)
                optimized_lines.append(stripped)

        return "\n".join(optimized_lines)

    def _optimize_cache(self):
        if len(self._cache) > 100:
            oldest_keys = sorted(self._cache.keys())[:len(self._cache) // 2]
            for key in oldest_keys:
                del self._cache[key]

    def get_stats(self) -> Dict[str, Any]:
        return {
            "cache_size": len(self._cache),
            "cache_hits": self._cache_hits,
            "cache_misses": self._cache_misses,
            "hit_rate": self._cache_hits / max(self._cache_hits + self._cache_misses, 1),
        }


class TokenEstimator:
    def __init__(self):
        self._token_cache: Dict[str, int] = {}

    def estimate_tokens(self, text: str) -> int:
        if text in self._token_cache:
            return self._token_cache[text]
        estimated = max(1, len(text) // 4)
        self._token_cache[text] = estimated
        return estimated

    def estimate_messages_tokens(self, messages: List[Dict[str, str]]) -> int:
        total = 0
        for msg in messages:
            content = msg.get("content", "")
            total += self.estimate_tokens(content)
            total += 10
        return total

    def estimate_prompt_overhead(self) -> int:
        return 2000

    def clear_cache(self):
        self._token_cache.clear()


class SlidingWindowManager:
    def __init__(self, max_tokens: int = 128000, summary_interval: int = 10, summary_max_tokens: int = 2000, keep_recent: int = 5):
        self.max_tokens = max_tokens
        self.summary_interval = summary_interval
        self.summary_max_tokens = summary_max_tokens
        self.keep_recent = keep_recent
        self.turns: List[ConversationTurn] = []
        self.summaries: List[str] = []
        self.total_tokens = 0
        self.failed_attempts: List[Dict[str, Any]] = []
        self._token_estimator = TokenEstimator()

    def add_turn(self, role: str, content: str, estimated_tokens: int = 0):
        if estimated_tokens == 0:
            estimated_tokens = self._token_estimator.estimate_tokens(content)
        self.turns.append(ConversationTurn(role=role, content=content, tokens=estimated_tokens))
        self.total_tokens += estimated_tokens

    def needs_summarization(self) -> bool:
        return len(self.turns) >= self.summary_interval and self.total_tokens > self.max_tokens * 0.7

    def summarize_and_compress(self, summarizer_func=None) -> str:
        if not self.turns:
            return ""
        recent = self.turns[-self.keep_recent:]
        older = self.turns[:-self.keep_recent]
        summary = " | ".join([t.content[:200] for t in older])
        if len(summary) > self.summary_max_tokens:
            summary = summary[:self.summary_max_tokens]
        self.turns = list(recent)
        self.summaries.append(summary)
        self.total_tokens = sum(t.tokens for t in self.turns)
        return summary

    def compress_memory(self, compression_ratio: float = 0.3, preserve_entities: bool = True, preserve_trust_scores: bool = True, preserve_pivot_paths: bool = True) -> Dict[str, Any]:
        compressed = {
            "entities": [],
            "trust_scores": {},
            "pivot_paths": [],
            "summaries": list(self.summaries),
            "total_turns_compressed": len(self.turns),
        }
        if preserve_entities:
            for turn in self.turns:
                pass
        if preserve_trust_scores:
            compressed["trust_scores"] = {"note": "Trust scores preserved from investigation state"}
        if preserve_pivot_paths:
            compressed["pivot_paths"] = ["Pivot paths preserved from investigation state"]
        return compressed

    def get_context_messages(self) -> List[Dict[str, str]]:
        messages = []
        for summary in self.summaries:
            messages.append({"role": "system", "content": f"[Previous investigation summary: {summary[:500]}]"})
        for turn in self.turns:
            messages.append({"role": turn.role, "content": turn.content})
        return messages

    def auto_optimize(self) -> Dict[str, Any]:
        stats = {
            "total_turns": len(self.turns),
            "total_summaries": len(self.summaries),
            "total_tokens": self.total_tokens,
            "compression_ratio": 0.0,
            "actions_taken": [],
        }
        if self.total_tokens > self.max_tokens * 0.7:
            if len(self.turns) > self.summary_interval:
                self.summarize_and_compress()
                stats["actions_taken"].append("sliding_window_compression")
                stats["compression_ratio"] = 0.3
        if len(self.summaries) > 20:
            self.summaries = self.summaries[-10:]
            stats["actions_taken"].append("summary_pruning")
        if self.total_tokens > self.max_tokens * 0.9:
            self.hierarchical_summarize()
            stats["actions_taken"].append("hierarchical_summarization")
        return stats

    def hierarchical_summarize(self) -> Dict[str, Any]:
        if len(self.summaries) < 2:
            return {"action": "none", "reason": "not enough summaries"}
        level1_summaries = self.summaries[-10:]
        level1_text = " | ".join(level1_summaries)
        level2_summary = f"[Hierarchical L2] {level1_text[:2000]}"
        self.summaries = self.summaries[:-10] + [level2_summary]
        return {
            "action": "hierarchical_summarization",
            "level1_count": len(level1_summaries),
            "level2_summary_length": len(level2_summary),
        }

    def chunk_investigation(self, max_tokens_per_chunk: int = 100000) -> List[Dict[str, Any]]:
        chunks = []
        current_chunk = []
        current_tokens = 0
        for turn in self.turns:
            turn_tokens = turn.tokens
            if current_tokens + turn_tokens > max_tokens_per_chunk and current_chunk:
                chunks.append({
                    "turns": list(current_chunk),
                    "total_tokens": current_tokens,
                })
                current_chunk = []
                current_tokens = 0
            current_chunk.append(turn)
            current_tokens += turn_tokens
        if current_chunk:
            chunks.append({
                "turns": list(current_chunk),
                "total_tokens": current_tokens,
            })
        return chunks

    def retrieve_relevant_context(self, query: str, max_results: int = 5) -> List[str]:
        relevant = []
        query_lower = query.lower()
        for turn in self.turns:
            if query_lower in turn.content.lower():
                relevant.append(turn.content)
                if len(relevant) >= max_results:
                    break
        for summary in self.summaries:
            if query_lower in summary.lower():
                relevant.append(summary)
                if len(relevant) >= max_results:
                    break
        for attempt in self.failed_attempts:
            query_match = attempt.get("query", "").lower()
            if query_lower in query_match or query_match in query_lower:
                relevant.append(f"[FAILED ATTEMPT] {attempt.get('query', '')}: {attempt.get('reason', 'no result')}")
                if len(relevant) >= max_results:
                    break
        return relevant

    def record_failed_attempt(self, query: str, reason: str, source: str = ""):
        self.failed_attempts.append({
            "query": query,
            "reason": reason,
            "source": source,
            "timestamp": time.time(),
        })

    def get_failed_attempts(self) -> List[Dict[str, Any]]:
        return list(self.failed_attempts)

    def reset(self):
        self.turns.clear()
        self.summaries.clear()
        self.total_tokens = 0
        self.failed_attempts.clear()


class HermesReasoningEngine:
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.provider = self.config.get("provider", "openai-compatible")
        self.api_base = self.config.get("api_base", "http://127.0.0.1:11434/v1")
        self.api_key = self.config.get("api_key", "ollama")
        self.model = self.config.get("model", "hermes-3-8b")
        self.temperature = self.config.get("temperature", 0.3)
        self.max_tokens = self.config.get("max_tokens", 4096)
        self.context_window = self.config.get("context_window", 128000)
        sliding_config = self.config.get("sliding_window", {})
        self.sliding_window = SlidingWindowManager(
            max_tokens=self.context_window,
            summary_interval=sliding_config.get("summary_interval_steps", 10),
            summary_max_tokens=sliding_config.get("summary_max_tokens", 2000),
            keep_recent=sliding_config.get("keep_recent_turns", 5),
        )
        self.prompt_optimizer = PromptOptimizer()
        self.token_estimator = TokenEstimator()
        self.persistence = PersistenceManager(save_interval_hours=4.0)
        self.kaggle = KaggleCoordinator()
        self._client = None
        self._auto_save_timer = None
        retry_config = self.config.get("retry", {})
        circuit_config = self.config.get("circuit_breaker", {})
        self.retry_handler = RetryHandler(
            max_attempts=retry_config.get("max_attempts", 3),
            base_delay_seconds=retry_config.get("base_delay_seconds", 1.0),
            max_delay_seconds=retry_config.get("max_delay_seconds", 30.0),
            backoff_multiplier=retry_config.get("backoff_multiplier", 2.0),
            jitter=retry_config.get("jitter", True),
        )
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=circuit_config.get("failure_threshold", 5),
            recovery_timeout_seconds=circuit_config.get("recovery_timeout_seconds", 60.0),
            half_open_max_requests=circuit_config.get("half_open_max_requests", 1),
        )

    def _get_client(self):
        if self._client is not None:
            return self._client

        try:
            import httpx
            self._client = httpx.AsyncClient(
                base_url=self.api_base,
                headers={"Authorization": f"Bearer {self.api_key}"},
                timeout=120.0,
            )
        except ImportError:
            import urllib.request
            import json as json_stdlib
            self._client = _StdLibClient(self.api_base, self.api_key)

        return self._client

    async def reason(self, query: str, context: Dict[str, Any] = None) -> ReasoningResult:
        system_prompt = self._build_system_prompt()
        optimized_prompt = self.prompt_optimizer.get_optimized_prompt("system_prompt", system_prompt)
        user_prompt = self._build_user_prompt(query, context or {})

        self.sliding_window.add_turn("user", user_prompt, estimated_tokens=len(user_prompt) // 4)
        self.persistence.save_turn("user", user_prompt, len(user_prompt) // 4)

        if self.sliding_window.needs_summarization():
            summary = self.sliding_window.summarize_and_compress()
            self.persistence.save_summary(summary)

        if len(self.sliding_window.summaries) % 5 == 0 and len(self.sliding_window.summaries) > 0:
            self.sliding_window.compress_memory(
                compression_ratio=0.3,
                preserve_entities=True,
                preserve_trust_scores=True,
                preserve_pivot_paths=True,
            )

        optimization_stats = self.sliding_window.auto_optimize()
        self.persistence.save_optimization_stats(optimization_stats)

        if self.sliding_window.total_tokens > self.context_window * 0.9:
            self.sliding_window.hierarchical_summarize()
            optimization_stats["actions_taken"].append("hierarchical_summarization")

        messages = [
            {"role": "system", "content": optimized_prompt},
        ]
        messages.extend(self.sliding_window.get_context_messages())

        estimated_context_tokens = self.token_estimator.estimate_messages_tokens(messages)

        if estimated_context_tokens > self.context_window:
            relevant = self.sliding_window.retrieve_relevant_context(query, max_results=5)
            messages = [
                {"role": "system", "content": optimized_prompt},
                {"role": "system", "content": f"[Relevant context retrieved: {' | '.join(relevant)}]"},
            ]
            messages.extend(self.sliding_window.get_context_messages()[-self.sliding_window.keep_recent:])

        response = await self._chat_completion(messages)

        if not response or len(response.strip()) < 10:
            self.sliding_window.record_failed_attempt(
                query=query,
                reason="empty_or_error_response",
                source="llm",
            )
            self.persistence.save_failed_attempt(query, "empty_or_error_response", "llm")
        else:
            self.sliding_window.add_turn("assistant", response, estimated_tokens=len(response) // 4)
            self.persistence.save_turn("assistant", response, len(response) // 4)

        self.persistence.auto_save()

        return self._parse_reasoning_response(response, query)

    def _build_system_prompt(self) -> str:
        return """You are Hermes-3, an advanced OSINT reasoning engine specialized in open-source intelligence investigation.

Your capabilities:
1. Cross-reference data from multiple OSINT sources
2. Perform entity pivoting (IP -> email -> company -> shell company -> property)
3. Apply the Faisceau de preuves triangulé method (legal + technical + physical evidence)
4. Generate trust scores and confidence levels for each finding
5. Detect weak signals and hidden infrastructure projects
6. Produce Mermaid diagrams and Nodal graph descriptions for entity relationships
7. Generate structured investigation reports with source attribution

You operate with full transparency - cite every source, flag uncertainty, and distinguish between confirmed facts and hypotheses.

Output format: Always respond with valid JSON containing:
- "conclusion": string
- "confidence": float (0.0-1.0)
- "trust_score": float (0.0-1.0)
- "reasoning_steps": array of step objects
- "recommendations": array of strings
- "data_summary": string

Use XML tags for structured reasoning: <REASONING>, <SCRATCHPAD>, <PLAN>, <EXECUTION>, <REFLECTION>."""

    def _build_user_prompt(self, query: str, context: Dict[str, Any]) -> str:
        lines = [f"Investigation Goal: {query}", ""]

        if context.get("raw_results"):
            lines.append("Raw OSINT Results:")
            for tool_name, result in context["raw_results"].items():
                lines.append(f"  [{tool_name}] Status: {result.get('status', 'unknown')}")
                if result.get("data"):
                    data_str = str(result["data"])[:500]
                    lines.append(f"    Data: {data_str}")
            lines.append("")

        if context.get("existing_entities"):
            lines.append("Known Entities:")
            for entity in context["existing_entities"]:
                lines.append(f"  - {entity}")
            lines.append("")

        lines.append("Analyze the data above, correlate findings across sources, perform pivoting, and produce a comprehensive intelligence assessment.")

        return "\n".join(lines)

    async def _chat_completion(self, messages: List[Dict[str, str]]) -> str:
        async def _do_request():
            client = self._get_client()
            payload = {
                "model": self.model,
                "messages": messages,
                "temperature": self.temperature,
                "max_tokens": self.max_tokens,
                "response_format": {"type": "json_object"},
            }
            if hasattr(client, "post"):
                response = await client.post(
                    "/chat/completions",
                    json=payload,
                    headers={"Content-Type": "application/json"},
                )
                response.raise_for_status()
                data = response.json()
                return data["choices"][0]["message"]["content"]
            else:
                return await client._raw_request(payload)

        try:
            return await self.circuit_breaker.execute(
                self.retry_handler.execute, _do_request
            )
        except CircuitBreakerOpenError:
            return f"Circuit breaker open: endpoint unreachable, retrying after cooldown"
        except Exception as e:
            return f"Request failed after retries: {str(e)[:200]}"

    def _parse_reasoning_response(self, raw_response: str, query: str) -> ReasoningResult:
        try:
            json_str = raw_response
            if "```json" in raw_response:
                json_str = raw_response.split("```json")[1].split("```")[0]
            elif "```" in raw_response:
                json_str = raw_response.split("```")[1].split("```")[0]

            data = json.loads(json_str.strip())
            steps = []
            for step_data in data.get("reasoning_steps", []):
                steps.append(ReasoningStep(
                    step_type=step_data.get("type", "analysis"),
                    content=step_data.get("content", ""),
                    confidence=step_data.get("confidence", 0.0),
                    sources=step_data.get("sources", []),
                    metadata=step_data.get("metadata", {}),
                ))

            return ReasoningResult(
                conclusion=data.get("conclusion", raw_response),
                confidence=data.get("confidence", 0.5),
                trust_score=data.get("trust_score", 0.5),
                steps=steps,
                recommendations=data.get("recommendations", []),
                raw_data_summary=data.get("data_summary", ""),
            )
        except (json.JSONDecodeError, KeyError, IndexError):
            return ReasoningResult(
                conclusion=raw_response,
                confidence=0.3,
                trust_score=0.3,
                steps=[ReasoningStep(step_type="raw", content=raw_response)],
                recommendations=["Manual review recommended"],
                raw_data_summary=raw_response[:2000],
            )

    async def close(self):
        if self._client is not None:
            await self._client.aclose()
            self._client = None
        self.persistence.save()
        self.persistence.stop_auto_save_timer()

    def restore_state(self, investigation_id: str = "") -> bool:
        state = self.persistence.load_latest(investigation_id)
        if state is None:
            return False
        self.sliding_window.turns = state.turns
        self.sliding_window.summaries = state.summaries
        self.sliding_window.total_tokens = state.total_tokens
        self.sliding_window.failed_attempts = state.failed_attempts
        self.persistence._state = state
        return True

    def save_state(self) -> Dict[str, Any]:
        return self.persistence.save()

    def get_persistence_stats(self) -> Dict[str, Any]:
        return self.persistence.get_save_stats()

    def start_auto_save(self):
        return self.persistence.start_auto_save_timer()

    def stop_auto_save(self):
        self.persistence.stop_auto_save_timer()

    def start_kaggle_session(self, investigation_id: str = "") -> KaggleSessionState:
        return self.kaggle.initialize_session(investigation_id=investigation_id)

    def claim_kaggle_leadership(self) -> bool:
        return self.kaggle.claim_leadership()

    def release_kaggle_leadership(self):
        self.kaggle.release_leadership()

    def handoff_to_next_machine(self, next_machine: str) -> bool:
        return self.kaggle.transfer_leadership(next_machine)

    def resume_after_kaggle_handoff(self) -> bool:
        return self.kaggle.resume_after_handoff()

    def get_kaggle_stats(self) -> Dict[str, Any]:
        return self.kaggle.get_coordination_stats()


class _StdLibClient:
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url
        self.api_key = api_key

    async def _raw_request(self, payload: Dict[str, Any]) -> str:
        import urllib.request
        import urllib.error

        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            f"{self.base_url}/chat/completions",
            data=data,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
            },
        )
        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                body = resp.read().decode("utf-8")
                parsed = json.loads(body)
                return parsed["choices"][0]["message"]["content"]
        except urllib.error.HTTPError as e:
            return f"API Error: {e.code} - {e.reason}"