from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils import call_llm, check_code
from typing import Dict, Any


def check_generated_code(code: str) -> Dict[str, Any]:
    """
    Validates if the generated ObjectBox query code is syntactically correct.

    Args:
        code: Generated ObjectBox query code to validate

    Returns:
        Dictionary with validation results
    """
    try:
        # Use the existing check_code function from utils
        validation_result = check_code(code)

        # Determine if code is valid based on the check_code result
        is_valid = validation_result.get('success', False) if isinstance(validation_result, dict) else bool(validation_result)

        return {
            "code": code,
            "is_valid": is_valid,
            "validation_result": validation_result,
            "message": "Code validation completed" if is_valid else "Code validation failed"
        }
    except Exception as e:
        return {
            "code": code,
            "is_valid": False,
            "validation_result": None,
            "message": f"Error during code validation: {str(e)}"
        }

def execute_database_query(code: str, database_context: str = "") -> Dict[str, Any]:
    """
    Executes the validated ObjectBox query code and retrieves data.

    Args:
        code: Validated ObjectBox query code to execute
        database_context: Additional context about the database

    Returns:
        Dictionary containing query results or error information
    """
    try:

        result = {
            "code_executed": code,
            "execution_status": "success",
            "data": "Placeholder: In real implementation, this would contain actual query results",
            "row_count": 0,
            "message": "Query executed successfully (simulated)"
        }

        return result

    except Exception as e:
        return {
            "code_executed": code,
            "execution_status": "error",
            "data": None,
            "row_count": 0,
            "message": f"Error executing query: {str(e)}"
        }

# Create function tools
code_checker_tool = FunctionTool(func=check_generated_code)
db_execution_tool = FunctionTool(func=execute_database_query)

class DatabaseAgent(LlmAgent):
    def __init__(self):
        super().__init__(
            name="DatabaseAgent",
            model="gemini-2.0-flash",
            description="Handles database queries and data retrieval operations.",
            instruction=(
                "You handle database-related queries following this workflow: "
                "1. First, convert natural language query into ObjectBox database query code "
                "2. Then, use the check_generated_code tool to validate if the generated code is correct "
                "3. If the code checker tool returns 'is_valid': True, proceed to use the execute_database_query tool to run the query and get actual data "
                "4. If the code checker tool returns 'is_valid': False, inform the user about the code validation error and do not execute "
                "5. Return the final results or error messages to the user "
                "Always follow this sequence: generate -> check -> execute (only if valid). "
                "The check_generated_code tool output contains an 'is_valid' field that determines whether to proceed with execution."
            ),
            tools=[code_checker_tool, db_execution_tool]
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
                "When you receive a query, first use the query and context to understand "
                "what type of action is needed. action will be of type db, graph and upload "
                "Based on the action returned: "
                "- Route 'db' requests to DatabaseAgent for data retrieval and querying "
                "- Route 'graph' requests to GraphAgent for creating visualizations "
                "- Route 'upload' requests to UploadAgent for data upload and management "
                "Always explain your reasoning for the chosen action to the user."
            ),
            sub_agents=[database_agent, graph_agent, upload_agent]
        )
