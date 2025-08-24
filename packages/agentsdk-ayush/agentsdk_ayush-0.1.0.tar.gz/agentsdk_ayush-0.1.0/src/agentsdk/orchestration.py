from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Callable

import concurrent.futures

from agentsdk.agent import Agent
from agentsdk.state import SessionManager
from agentsdk.tool_subsystem import ToolRegistry

try:
    import frontmatter  # type: ignore
except Exception:  # pragma: no cover
    frontmatter = None  # type: ignore
from pathlib import Path
try:
    import yaml  # type: ignore
except Exception:  # pragma: no cover
    yaml = None  # type: ignore


@dataclass
class SubAgentConfig:
    name: str
    description: str
    tools: Optional[List[str]] = None
    system_prompt: Optional[str] = None


class OrchestratorAgent:
    """Orchestrates task decomposition and parallel sub-agent execution."""

    def __init__(
        self,
        planner: Agent,
        sub_agents: Dict[str, Agent],
        sessions: SessionManager,
        max_parallel: int = 4,
        on_subagent_start: Optional[Callable[[str, str], None]] = None,
        on_subagent_end: Optional[Callable[[str, str, str], None]] = None,
    ) -> None:
        self.planner = planner
        self.sub_agents = sub_agents
        self.sessions = sessions
        self.max_parallel = max_parallel
        self.on_subagent_start = on_subagent_start
        self.on_subagent_end = on_subagent_end

    def decompose(self, session_id: str, query: str) -> List[Dict[str, Any]]:
        # Build a planning prompt that enumerates available sub-agents
        agent_list = []
        for k, a in self.sub_agents.items():
            if k == "default":
                continue
            agent_list.append({"name": k, "tools": a.allowed_tools or []})
        plan_prompt = (
            "You are the orchestrator. Given the user query, produce a STRICT JSON array of tasks.\n"
            "Each item keys: task_id (string), description (string), agent (string from available agents), inputs (string).\n"
            f"Available agents: {agent_list}"
        )
        system = (self.planner.system_prompt or "") + "\n\n" + plan_prompt
        planner = Agent(
            name=self.planner.name,
            bedrock=self.planner.bedrock,
            registry=self.planner.registry,
            sessions=self.sessions,
            system_prompt=system,
            max_turns=3,
        )
        text = planner.chat(session_id=session_id + ":plan", user_input=query)
        try:
            import json

            plan = json.loads(text)
            if isinstance(plan, list):
                return plan
        except Exception:
            pass
        # Fallback to single task
        return [
            {"task_id": "t1", "description": query, "agent": "default", "inputs": query}
        ]

    def run(self, session_id: str, query: str, plan: Optional[List[Dict[str, Any]]] = None, *, synthesize: bool = True) -> str:
        plan = plan or self.decompose(session_id, query)

        results: Dict[str, str] = {}
        futures: List[concurrent.futures.Future[str]] = []
        future_to_info: Dict[concurrent.futures.Future[str], Dict[str, str]] = {}
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_parallel) as executor:
            for item in plan:
                agent_key = item.get("agent") or "default"
                agent = self.sub_agents.get(agent_key) or self.sub_agents.get("default")
                if agent is None:
                    continue
                task_input = item.get("inputs") or item.get("description") or query
                if self.on_subagent_start:
                    try:
                        self.on_subagent_start(agent_key, str(item.get("task_id", "t")))
                    except Exception:
                        pass
                # If explicit tool is provided, run the tool directly
                tool_name = item.get("tool")
                tool_args = item.get("args") or {}
                if tool_name:
                    # Use the agent's registry
                    registry: ToolRegistry = agent.registry
                    fut = executor.submit(lambda: registry.run_tool(tool_name, **tool_args))
                else:
                    fut = executor.submit(
                        agent.chat,
                        session_id=f"{session_id}:{item.get('task_id','t')}\n",
                        user_input=str(task_input),
                    )
                futures.append(fut)
                future_to_info[fut] = {"agent": agent_key, "task_id": str(item.get("task_id", "t"))}

            for idx, fut in enumerate(concurrent.futures.as_completed(futures), start=1):
                try:
                    out = fut.result()
                    results[str(idx)] = out
                except Exception as exc:  # noqa: BLE001
                    out = f"ERROR: {exc}"
                    results[str(idx)] = out
                if self.on_subagent_end:
                    try:
                        info = future_to_info.get(fut, {"agent": "unknown", "task_id": str(idx)})
                        self.on_subagent_end(info["agent"], info["task_id"], out)
                    except Exception:
                        pass

        if not synthesize:
            return "\n\n".join(v for _, v in sorted(results.items(), key=lambda kv: kv[0]))

        # Synthesis step: LLM consolidation using the planner
        synthesis_prompt = (
            "You are a synthesis agent. Combine the following task results into a concise, actionable answer.\n"
            "Ensure correctness, remove duplication, and provide clear next steps if relevant.\n\n"
        )
        parts = []
        for key, value in sorted(results.items(), key=lambda kv: kv[0]):
            parts.append(f"Task {key}:\n{value}")
        synthesis_input = synthesis_prompt + "\n\n" + "\n\n".join(parts)

        final_text = self.planner.chat(session_id=f"{session_id}:synthesis", user_input=synthesis_input)
        return final_text or "\n\n".join(v for _, v in sorted(results.items(), key=lambda kv: kv[0]))


def load_sub_agents_from_dir(
    directory: str | Path,
    base_agent: Agent,
) -> Dict[str, Agent]:
    """Load sub-agent configs from Markdown (YAML frontmatter) and YAML files."""
    agents: Dict[str, Agent] = {"default": base_agent}
    dir_path = Path(directory)
    if not dir_path.exists() or not dir_path.is_dir():
        return agents
    # Load Markdown configs
    if frontmatter is not None:
        for md_file in dir_path.glob("*.md"):
            try:
                post = frontmatter.load(md_file)
                meta = post.metadata or {}
                name = str(meta.get("name") or md_file.stem)
                tools = meta.get("tools")
                if tools is not None and not isinstance(tools, list):
                    tools = None
                system_prompt = str(post.content or "")
                sub_agent = Agent(
                    name=name,
                    bedrock=base_agent.bedrock,
                    registry=base_agent.registry,
                    sessions=base_agent.sessions,
                    system_prompt=system_prompt,
                    max_turns=base_agent.max_turns,
                    allowed_tools=tools,
                    on_thought=base_agent.on_thought,
                )
                agents[name] = sub_agent
            except Exception:
                continue
    # Load YAML configs
    if yaml is not None:
        for yml in list(dir_path.glob("*.yml")) + list(dir_path.glob("*.yaml")):
            try:
                data = yaml.safe_load(yml.read_text(encoding="utf-8")) or {}
                name = str(data.get("name") or yml.stem)
                system_prompt = str(data.get("system") or data.get("instructions") or "")
                tools = data.get("tools")
                if tools is not None and not isinstance(tools, list):
                    tools = None
                sub_agent = Agent(
                    name=name,
                    bedrock=base_agent.bedrock,
                    registry=base_agent.registry,
                    sessions=base_agent.sessions,
                    system_prompt=system_prompt,
                    max_turns=base_agent.max_turns,
                    allowed_tools=tools,
                    on_thought=base_agent.on_thought,
                )
                agents[name] = sub_agent
            except Exception:
                continue
    return agents


def scaffold_sub_agent_yaml(
    target_dir: str | Path,
    name: str,
    instructions: str,
    tools: Optional[List[str]] = None,
) -> Path:
    """Create a YAML sub-agent config file with the provided parameters."""
    path = Path(target_dir)
    path.mkdir(parents=True, exist_ok=True)
    filename = path / f"{name}.yaml"
    data = {
        "name": name,
        "instructions": instructions,
        "tools": tools or ["file_system"],
    }
    if yaml is None:
        # Minimal manual YAML
        content = (
            f"name: {name}\n"
            f"instructions: |\n  " + instructions.replace("\n", "\n  ") + "\n"
            f"tools: {data['tools']}\n"
        )
        filename.write_text(content, encoding="utf-8")
    else:
        filename.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
    return filename


