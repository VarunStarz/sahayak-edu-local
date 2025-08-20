from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool

from router.agentRouter import AgentRouter

from response.sub_agents.contentAgent import ContentAgent
from response.sub_agents.visionAgent import VisionAgent
from response.sub_agents.voiceAgent import VoiceAgent
from curriculum.sub_agents.pacingAndSequenceAgent import PacingAndSequenceAgent
import logging

from .RAG import EnhancedRAG
def rag_query(query:str, model="gemma3n:e2b-it-q4_k_m"):
    ragAgent = EnhancedRAG(model=model)
    ragAgent.setup_retrieval_chain()
    print(f"\n**Question:** {query}")
    response = ragAgent.query(query)
    if "error" in response:
        return {"present_in_vector_db": "False","error":f"Error: {response['error']}","Sources":"0"}
    else:
        return{"present_in_vector_db" : "True","answer":response['answer'],"**Sources:**":f"{len(response.get('context', []))} documents used"}

history_rag_tool = FunctionTool(func=rag_query)


class HistoryAgentADK(LlmAgent):
    def __init__(self,model,tool=history_rag_tool):
        # Compose description and instruction dynamically
        desc = "Checks the history for related queries."
        instr = (
            "On receiving a query, use the rag_query tool to check if a similar query has been answered before. "
            "The tool returns a JSON response with a 'present_in_vector_db' field: "
            "- If 'present_in_vector_db' is 'True', the query was found and you should return the 'answer' field from the response along with source information. "
            "- If 'present_in_vector_db' is 'False' or there's an 'error' field, the query was not found in the database, so transfer the task to the appropriate sub-agent via the HistorySubRouter. "
            "Always check the 'present_in_vector_db' field first to determine the appropriate action."
        )

        ### --------------- QUERY VECTOR DB OPERATION ---------------------------


        # Compose sub-agent instances including the nested HistorySubRouter
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

        # Initialize the parent router agent with main sub-agents including the response sub-router
        super().__init__(
            name="HistoryAgentADK",
            model=model,
            description=desc,
            instruction=instr,
            tools=[tool],
            sub_agents=[
                history_subrouter
            ]
        )
