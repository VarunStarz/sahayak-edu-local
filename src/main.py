"""
Main entry point for the Multi-Agent Educational Platform
"""
import logging
import logging.config
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import get_config, ensure_directories
from utils import call_agent_async
from flask import Flask, request, jsonify
import os
##from agents.history.historyAgent import HistoryAgent
from agents.router.agentRouter import AgentRouter
from agents.analytics.node import AnalyticsAgentBase
from agents.response.responseAgentADK import ResponseAgentADK
from agents.analytics.analyticsAgentADK import AnalyticsAgent
from agents.curriculum.curriculumAgent import CurriculumAgent
from agents.planning.planningAgentADK import PlanningAgent

from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner

app = Flask(__name__)

def setup_logging():
    """Setup logging configuration"""
    config = get_config()
    logging.config.dictConfig(config["logging"])
    return logging.getLogger(__name__)

# Initialize logging and directories at module level
ensure_directories()
logger = setup_logging()

@app.route('/entryPoint', methods=['POST'])
async def pgvectordemo():
    logger.info('Entering into entryPoint')
    data = request.get_json()
    query = data['query']

    router = AgentRouter(
        name="MainRouter",
        description="Routes response queries to Analytics, Curriculum, Planning or Response agents",
        instruction=(
            "Transfer queries to 'AnalyticsAgent' for analytics, 'CurriculumAgent' for curriculum help, "
            "'PlanningAgent' for planning help or 'ResponseAgentADK' for text, image or audio output."
        ),
        sub_agents=[
            AnalyticsAgent(),
            CurriculumAgent,
            PlanningAgent(),
            ResponseAgentADK()
        ]
    )
    #rag = HistoryAgent()
    #response = rag.query(query)
    session_service = InMemorySessionService()

    # Define constants for identifying the interaction context
    APP_NAME = "weather_tutorial_app"
    USER_ID = "user_1"
    SESSION_ID = "session_001" # Using a fixed ID for simplicity

    # Create the specific session where the conversation will happen
    session = await session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=SESSION_ID
    )
    print(f"Session created: App='{APP_NAME}', User='{USER_ID}', Session='{SESSION_ID}'")

    # --- Runner ---
    # Key Concept: Runner orchestrates the agent execution loop.
    runner = Runner(
        agent=router, # The agent we want to run
        app_name=APP_NAME,   # Associates runs with our app
        session_service=session_service # Uses our session manager
    )
    print(f"Runner created for agent '{runner.agent.name}'.")

    output=await call_agent_async(query,runner,USER_ID,SESSION_ID)

    logger.info(f"router ---> {router}")
    logger.info('Returning from entryPoint')


    return jsonify({'response': output})

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'service': 'Multi-Agent Educational Platform'})

def main():
    """Main application entry point"""
    logger.info("Starting Multi-Agent Educational Platform")
    os.environ["GOOGLE_API_KEY"] = "" # <--- REPLACE
    try:
        # TODO: Initialize ObjectBox database
        # TODO: Initialize PocketFlow components
        # TODO: Setup MCP client connections

        logger.info("Platform initialization complete")

        # Start Flask server
        app.run(host='0.0.0.0', port=8000, debug=True)

    except KeyboardInterrupt:
        logger.info("Shutting down platform...")
    except Exception as e:
        logger.error(f"Platform error: {e}")
        raise
    finally:
        logger.info("Platform shutdown complete")


if __name__ == "__main__":
    main()
