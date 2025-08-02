"""
Main entry point for the Multi-Agent Educational Platform
"""
import asyncio
import logging
import logging.config
from pathlib import Path

from config import get_config, ensure_directories

from flask import Flask, request, jsonify
app = Flask(__name__)

from src.agents.history.historyAgent import HistoryAgent
from src.agents.router.agentRouter import AgentRouter

from src.agents.analytics.node import AnalyticsAgentBase
from src.agents.response.responseAgentADK import ResponseAgentADK

def setup_logging():
    """Setup logging configuration"""
    config = get_config()
    logging.config.dictConfig(config["logging"])
    return logging.getLogger(__name__)


async def main():
    """Main application entry point"""
    # Ensure required directories exist
    ensure_directories()
    
    # Setup logging
    logger = setup_logging()
    logger.info("Starting Multi-Agent Educational Platform")
    
    try:
        # TODO: Initialize ObjectBox database
        # TODO: Initialize PocketFlow components
        # TODO: Setup MCP client connections
        # TODO: Start the main application flow

        @app.route('/entryPoint', methods=['POST'])
        def pgvectordemo():
            logger.info('Entering into entryPoint')
            data = request.get_json()
            query = data['query']

            #rag = HistoryAgent()
            #response = rag.query(query)

            router = AgentRouter(
                name="MainRouter",
                description="Routes response queries to Analytics, Curriculum, Planning or Response agents",
                instruction=(
                    "Transfer queries to 'AnalyticsAgent' for analytics, 'CurriculumAgent' for curriculum help, "
                    "'PlanningAgent' for planning help or 'ResponseAgentADK' for text, image or audio output."
                ),
                sub_agents=[
                    AnalyticsAgentBase(),
                    ResponseAgentADK()
                ]
            )
            logger.info(f"router ---> {router}")
            logger.info('Returning from entryPoint')

            return jsonify({'response': 'Hi'})
        
        logger.info("Platform initialization complete")
        
        # Keep the application running
        while True:
            await asyncio.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("Shutting down platform...")
    except Exception as e:
        logger.error(f"Platform error: {e}")
        raise
    finally:
        logger.info("Platform shutdown complete")


if __name__ == "__main__":
    asyncio.run(main())