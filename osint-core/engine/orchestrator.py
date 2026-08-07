import json
import asyncio
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field


@dataclass
class Task:
    id: str
    description: str
    tool_name: str
    params: Dict[str, Any]
    depends_on: List[str] = field(default_factory=list)
    status: str = "pending"
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


@dataclass
class InvestigationPlan:
    goal: str
    tasks: List[Task]
    parallel_groups: List[List[str]] = field(default_factory=list)


class OpenClawOrchestratorBridge:
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.max_steps = self.config.get("max_steps", 10)
        self.max_concurrency = self.config.get("max_concurrency", 5)
        self.gateway_url = self.config.get("gateway_url", "http://127.0.0.1:8080")
        self._task_queue: List[Task] = []
        self._results: Dict[str, Dict[str, Any]] = {}

    async def plan_investigation(self, goal: str, available_tools: List[str]) -> InvestigationPlan:
        from osint_core.tools import get_tool, get_all_tools

        all_tools = get_all_tools()
        plan = InvestigationPlan(goal=goal, tasks=[])

        task_id = 0
        for tool_name, tool_instance in all_tools.items():
            if tool_name not in available_tools and available_tools:
                continue
            task_id += 1
            task = Task(
                id=f"task-{task_id:04d}",
                description=f"Run {tool_name} for investigation: {goal}",
                tool_name=tool_name,
                params={"query": goal},
            )
            plan.tasks.append(task)

        return plan

    async def execute_plan(self, plan: InvestigationPlan, progress_callback=None) -> Dict[str, Any]:
        from osint_core.tools import get_tool

        results = {}
        pending = [t for t in plan.tasks if t.status == "pending"]

        while pending:
            batch = pending[: self.max_concurrency]
            pending = pending[self.max_concurrency :]

            tasks_coroutine = []
            for task in batch:
                tasks_coroutine.append(self._execute_task(task))

            task_results = await asyncio.gather(*tasks_coroutine, return_exceptions=True)

            for task, result in zip(batch, task_results):
                if isinstance(result, Exception):
                    task.status = "failed"
                    task.error = str(result)
                    results[task.id] = {"status": "failed", "error": str(result)}
                else:
                    task.status = result.status.value
                    task.result = result.to_dict()
                    results[task.id] = result.to_dict()
                    self._results[task.id] = result.to_dict()

                if progress_callback:
                    await progress_callback(task)

        return {
            "goal": plan.goal,
            "total_tasks": len(plan.tasks),
            "completed": sum(1 for t in plan.tasks if t.status == "success"),
            "failed": sum(1 for t in plan.tasks if t.status == "failed"),
            "results": results,
        }

    async def _execute_task(self, task: Task):
        from osint_core.tools import get_tool

        tool = get_tool(task.tool_name)
        if not tool:
            raise ValueError(f"Tool not found: {task.tool_name}")

        return tool.execute(task.params)

    async def run_adaptive_loop(self, goal: str, available_tools: List[str] = None) -> Dict[str, Any]:
        plan = await self.plan_investigation(goal, available_tools or [])
        return await self.execute_plan(plan)