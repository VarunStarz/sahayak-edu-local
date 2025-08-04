from google.adk.agents import LlmAgent

from router.agentRouter import AgentRouter

from response.sub_agents.contentAgent import ContentAgent
from response.sub_agents.visionAgent import VisionAgent
from response.sub_agents.voiceAgent import VoiceAgent
from curriculum.sub_agents.pacingAndSequenceAgent import PacingAndSequenceAgent
import logging

class HistoryAgentADK(LlmAgent):
    def __init__(self, model="gemini-2.0-flash"):
        # Compose description and instruction dynamically
        desc = "Checks the history for related queries."
        instr = (
            "On receiving a query, checks if the query or a similar one is already asked before by checking the vector database." \
            "If it is present in the vector database, it returns the answer from the db, else, it transfers the task to the dedicated agent."
        )

        ### --------------- QUERY VECTOR DB OPERATION ---------------------------

        present_in_vector_db = False

        # Compose sub-agent instances including the nested HistorySubRouter

        if present_in_vector_db == False:
            history_subrouter = AgentRouter(
            name="HistorySubRouter",
            description="Routes response queries to PacingAndSequence or Content or Vision or Voice agents",
            instruction=(
                "Transfer queries to 'PacingAndSequenceAgent' for generating/helping with the course curriculum, 'ContentAgent' for text, 'VisionAgent' for images, or 'VoiceAgent' for audio."
            ),
            sub_agents=[
                PacingAndSequenceAgent(),
                ContentAgent(),
                VisionAgent(),
                VoiceAgent()
                ]
            )

            logging.info(f"history_subrouter ---> {history_subrouter}")

        else:
            ### --------------- GENERATE A PROPER RESPONSE FROM THE ANSWER TAKEN FROM THE VECTOR DB ---------------------------
            pass

        # Initialize the parent router agent with main sub-agents including the response sub-router
        super().__init__(
            name="HistoryAgentADK",
            model=model,
            description=desc,
            instruction=instr,
            sub_agents=[
                history_subrouter
            ]
        )
