from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils import call_llm, check_code
from typing import Dict, Any

def generate_db_query(query: str, context: str = "No previous Context", database_schema: str = "") -> Dict[str, Any]:
    """
    Converts natural language query into ObjectBox database query code.

    Args:
        query: Natural language query from user
        context: Previous conversation context
        database_schema: Database schema information

    Returns:
        Dictionary containing the generated query code and metadata
    """
    prompt = f'''
    You are an expert API that exclusively translates natural language requests into ObjectBox queries for the Python SDK.

    Given the database schema, convert the user's request into a valid ObjectBox query.
    Your output MUST be a single JSON object and nothing else. Do not add explanations or markdown formatting.

    Input:
    NATURAL LANGUAGE QUERY: {query}
    CONTEXT: {context}
    DATABASE SCHEMA: {database_schema}

    TASK:
    Translate the natural language request into an ObjectBox query for the Python SDK. The query should assume a Box instance is available as `box`.

    OUTPUT FORMAT (JSON only):
    {{
        "query": "{query}",
        "context": "{context}",
        "database_used": "ObjectBox",
        "code": "[Generated ObjectBox Python SDK query code here]"
    }}'''

    response_text = call_llm(prompt)
    try:
        response_dict = json.loads(response_text)
        # Validate and execute the code
        code = response_dict.get('code', '')
        response_dict['tool_call_result'] = check_code(code)
        return response_dict
    except json.JSONDecodeError:
        return {
            "query": query,
            "context": context,
            "database_used": "ObjectBox",
            "code": "Error: Invalid JSON response from LLM",
            "error": "JSON decode error"
        }

def determine_analytics_action(query: str, context: str = "No previous Context") -> Dict[str, str]:
    """
    Analyzes user query to determine the appropriate analytics action.

    Args:
        query: User's natural language query
        context: Previous conversation context

    Returns:
        Dictionary with action type and reasoning
    """
    prompt = f"""
    You are an Analytics Agent designed to provide data analytics capabilities through natural language processing. Your primary function is to interpret user queries and determine the most appropriate action to fulfill their analytical needs.

    **Available Actions:**
    1. "db" - Query and display database information based on the user's question
    2. "graph" - Generate and display visualizations/graphs based on the user's analytical request
    3. "upload" - Upload data into existing databases or create new databases as needed (primarily for teachers)

    **Your Task:**
    Analyze the user's natural language query and select exactly ONE of the three actions above that best addresses their request. Consider the following guidelines:

    - Choose "db" when users need to see raw data, search for specific records, or want tabular information
    - Choose "graph" when users request visualizations, trends, comparisons, or want to see data represented visually
    - Choose "upload" when users need to add new data, create databases, or manage data storage (especially for educational contexts)

    **Context:** {context}

    **User Query:** {query}

    **Output Format:**
    You must respond with a JSON object in the following format:
    {{
      "action": "db|graph|upload",
      "reasoning": "Brief explanation of why this action was chosen"
    }}

    **Instructions:**
    1. Read the user's query carefully
    2. Consider the provided context
    3. Select the most appropriate action from: "db", "graph", or "upload"
    4. Provide a concise reasoning for your choice
    5. Format your response as valid JSON only

    Context: This agent serves educational environments where teachers may need to manage data while students and staff require various forms of data analysis and visualization.
    """

    response_text = call_llm(prompt)
    try:
        response_dict = json.loads(response_text)
        return response_dict
    except json.JSONDecodeError:
        return {
            "action": "db",
            "reasoning": "Error: Invalid JSON response from LLM, defaulting to database query"
        }

# Create function tools
db_query_tool = FunctionTool(func=generate_db_query)
action_determination_tool = FunctionTool(func=determine_analytics_action)

class DatabaseAgent(LlmAgent):
    def __init__(self):
        super().__init__(
            name="DatabaseAgent",
            model="gemini-2.0-flash",
            description="Handles database queries and data retrieval operations.",
            instruction=(
                "You handle database-related queries. When you receive a query, use the generate_db_query tool "
                "to convert natural language into ObjectBox database query code. "
                "The tool returns a JSON object with the generated code and metadata. "
                "Execute the code if it's valid and return the results to the user. "
                "If there are errors in code generation, report them clearly."
            ),
            tools=[db_query_tool]
        )

class GraphAgent(LlmAgent):
    def __init__(self):
        super().__init__(
            name="GraphAgent",
            model="gemini-2.0-flash",
            description="Handles data visualization and graph generation.",
            instruction=(
                "You handle requests for data visualization and graph generation. "
                "When users request charts, graphs, plots, or any visual representation of data, "
                "you should create appropriate visualizations using available plotting libraries. "
                "Consider the data type and user's specific visualization needs when creating graphs."
            )
        )

class UploadAgent(LlmAgent):
    def __init__(self):
        super().__init__(
            name="UploadAgent",
            model="gemini-2.0-flash",
            description="Handles data upload and database management operations.",
            instruction=(
                "You handle data upload operations and database management. "
                "This includes uploading new data to existing databases, creating new databases, "
                "and managing data storage operations. You primarily serve educational contexts "
                "where teachers need to manage student data and course information."
            )
        )

class AnalyticsAgent(LlmAgent):
    def __init__(self):
        # Create sub-agents for different analytics operations
        database_agent = DatabaseAgent()
        graph_agent = GraphAgent()
        upload_agent = UploadAgent()

        super().__init__(
            name="AnalyticsAgent",
            model="gemini-2.0-flash",
            description="Provides comprehensive data analytics capabilities through natural language processing.",
            instruction=(
                "You are the main Analytics Agent that handles all data analytics requests. "
                "When you receive a query, first use the determine_analytics_action tool to understand "
                "what type of action is needed. The tool returns a JSON object with 'action' field that can be: "
                "'db' for database queries, 'graph' for visualizations, or 'upload' for data management. "
                "Based on the action returned: "
                "- Route 'db' requests to DatabaseAgent for data retrieval and querying "
                "- Route 'graph' requests to GraphAgent for creating visualizations "
                "- Route 'upload' requests to UploadAgent for data upload and management "
                "Always explain your reasoning for the chosen action to the user."
            ),
            tools=[action_determination_tool],
            sub_agents=[database_agent, graph_agent, upload_agent]
        )
