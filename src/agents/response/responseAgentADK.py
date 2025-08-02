from google.adk.agents import LlmAgent

from router.agentRouter import AgentRouter

from response.sub_agents.contentAgent import ContentAgent
from response.sub_agents.visionAgent import VisionAgent
from response.sub_agents.voiceAgent import VoiceAgent
import logging
class ResponseAgentADK(LlmAgent):
    def __init__(self, model="gemini-2.0-flash"):
        # Compose description and instruction dynamically
        desc = "Routes queries dynamically to expert sub-agents for content, vision or voice."
        instr = (
            "On receiving a query, transfer control to one of the sub-agents: "
            "'ContentAgent', 'VisionAgent' and 'VoiceAgent'."
        )

        # Compose sub-agent instances including the nested ResponseSubRouter
        response_subrouter = AgentRouter(
            name="ResponseSubRouter",
            description="Routes response queries to Content, Vision, or Voice agents",
            instruction=(
                "Transfer queries to 'ContentAgent' for text, 'VisionAgent' for images, or 'VoiceAgent' for audio."
            ),
            sub_agents=[
                ContentAgent(),
                VisionAgent(),
                VoiceAgent()
            ]
        )

        logging.info(f"response_subrouter ---> {response_subrouter}")

        # Initialize the parent router agent with main sub-agents including the response sub-router
        super().__init__(
            name="ResponseAgentADK",
            model=model,
            description=desc,
            instruction=instr,
            sub_agents=[
                response_subrouter
            ]
        )
