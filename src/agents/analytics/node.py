import pocketflow as pf
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils import call_llm,check_code
import json
from typing import Dict

class QueryforDB(pf.Node):
    def prep(self,shared):
        query=shared.get('analytics_agent_query')
        context=shared.get('analytics_agent_context',"No previous Context")
        database_schema=shared.get('database_schema')
        return query, context, database_schema
    def exec(self,prep_res):
        query, context, database_schema = prep_res
        # Get database query using query and context
        prompt=f'''
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

        response_text=call_llm(prompt)
        try:
            response_dict = json.loads(response_text)
        except json.JSONDecodeError:
            print("Error: LLM did not return a valid JSON object.")
                   # Handle the error, maybe by returning a specific error structure
            return {"query": query, "code": "Error: Invalid JSON response from LLM"}

        # Return the Python dictionary
        return response_dict
    def post(self,shared:Dict,prep_res,exec_res:Dict):
        code=exec_res['code']
        exec_res['tool-call']=check_code('code')
        shared['context'].append(exec_res)
        return check_code(code)



class AnalyticsAgentBase(pf.Node):
    def prep(self,shared):
        query=shared.get('analytics_agent_query')
        context=shared.get('analytics_agent_context',"No previous Context")
        return query,context

    def exec(self,prep_res):
        query, context = prep_res

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

        response_text=call_llm(prompt)
        try:
            response_dict = json.loads(response_text)
        except json.JSONDecodeError:
            print("Error: LLM did not return a valid JSON object.")
                   # Handle the error, maybe by returning a specific error structure
            return {"action": " ", "resoning": "Error: Invalid JSON response from LLM"}

        # Return the Python dictionary
        return response_dict

    def post(self, shared, prep_res, exec_res):
        action= exec_res["action"]
        query,context=prep_res
        exec_res["query"]=query
        context.append(exec_res)
        shared['context']=context
        return action
