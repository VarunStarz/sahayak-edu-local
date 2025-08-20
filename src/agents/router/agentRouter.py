from typing import List
from google.adk.agents import LlmAgent
from google.adk.agents.llm_agent import ToolUnion

class AgentRouter(LlmAgent):
    def __init__(self,
                 name: str = "AgentRouter",
                 model: str = "gemini-2.0-flash",
                 description: str | None = None,
                 instruction: str | None = None,
                 sub_agents: list | None = None,
                 tool: List[ToolUnion] | None = None):
        """
        Dynamic Agent Router to delegate queries to sub-agents.

        Args:
            name (str): Name of the agent router.
            model (str): Model identifier.
            description (str): High-level description of the router agent.
            instruction (str): Instructions guiding the LLM for delegation.
            sub_agents (list): List of sub-agent instances (LlmAgent objects).
        """
        super().__init__(
            name=name,
            model=model,
            description=description or "Dynamic router agent that delegates requests to sub-agents.",
            instruction=instruction or (
                "You are the central router. Analyze each query and transfer to the best sub-agent."
            ),
            tools=tool or [],
            sub_agents=sub_agents or []
        )
