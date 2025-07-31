import pocketflow as pf
from ....utils import call_llm
import json

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
    def post(self,shared,prep_res,exec_res):
        query,code= exec_res['query'],exec_res['code']
        try:
            ast.parse(code)
            print('Code Return is valid Python Syntax')
        except  SyntaxError:
            print('Code Return is not valid Python Syntax')



class AnalyticsAgent(pf.AsyncNode):
    async def prep_async(self, shared):
        query = shared.get('query')
