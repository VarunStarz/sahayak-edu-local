import pocketflow as pf
from ....utils import call_llm
import json

class BetterPrompt(pf.Node):
    def prep(self,shared):
        query=shared['response_agent_query']
        context=shared['response_agent_context']
        return query,context

    def exec(self,prep_res):
        query,context=prep_res

        prompt=f'''
        ### ROLE ###
        You are an expert system specializing in information retrieval, semantic search, and search engine query optimization.

        ### OBJECTIVE ###
        Your task is to take a user's natural language question and transform it into several optimized formats suitable for different search systems. You must analyze the user's core intent and generate multiple phrasings to maximize the chances of finding a relevant match in a knowledge base or on the web.

        ### ORIGINAL USER QUESTION ###

        {query}

        ### CONTEXT ###
        {context}


    ### INSTRUCTIONS ###
    1.  **Analyze Intent:** First, analyze the original question to identify the core user intent, the key entities (e.g., products, places, concepts), and the specific information being sought.
    2.  **Generate for Vector Search:** Based on the intent, formulate two types of queries for a semantic search system:
            * **Hypothetical Answer:** Create a concise, ideal answer to the question. This paragraph should be rich with the keywords, technical terms, and concepts likely to be found in a perfect source document.
            * **Alternative Phrasings:** Create a list of alternative questions that use synonyms and rephrase the core intent.
    3.  **Generate for Web Search:** Formulate a list of concise, keyword-focused queries an expert would type into a search engine like Google. Remove all conversational filler words.

    ### OUTPUT FORMAT & JSON SCHEMA ###
    Your final output must be **only** a single, valid JSON object. Do not include any text, explanation, or markdown formatting before or after the JSON block.

    Your response must conform to the following JSON schema:

    ```json
    {{
    "vectorSearch": {{
        "hypotheticalAnswer": "string",
        "alternativePhrasings": [
        "string"
        ]
    }},
    "webSearch": {{
        "queries": [
        "string"
        ]
    }}
    }}
    ```
    **Schema Description:**

    * **`vectorSearch` (object):** Contains queries optimized for semantic search.
        * **`hypotheticalAnswer` (string):** The generated paragraph that represents the ideal answer.
        * **`alternativePhrasings` (array of strings):** A list of different ways to ask the original question.
    * **`webSearch` (object):** Contains queries optimized for keyword search engines.
        * **`queries` (array of strings):** A list of concise, keyword-focused search terms.
    '''

        response_text=call_llm(prompt)
        try:
            response_dict = json.loads(response_text)
        except json.JSONDecodeError:
            print("Error: LLM did not return a valid JSON object.")
                   # Handle the error, maybe by returning a specific error structure
            return {"query": query, "code": "Error: Invalid JSON response from LLM"}
        return response_dict

    def post(self,shared,prep_res,exec_res):
        query,context=prep_res
        vector_q,web_q=exec_res['vectorSearch']['alternativePhrasing']
        shared["vector_search_queries"]=vector_q
        shared["web_search_queries"]=web_q
        shared["context"].append({"query":query,"tool_call":{"name":"better_prompt","tool_output":exec_res}})
        return "Refining the Prompt DONE"


class ContentAgent(pf.Node):
    def prep(self, shared):
        """Get the question and context for answering."""
        return shared["response_agent_query"], shared.get("query_context", "")

    def exec(self, prep_res):
        """Call the LLM to generate a final answer."""
        question, context = prep_res

        print(f"✍️ Crafting final answer...")

        # Create a prompt for the LLM to answer the question
        prompt = f"""
### CONTEXT
Based on the following information, answer the question.
Question: {question}
Research: {context}

## YOUR ANSWER:
Provide a comprehensive answer using the research results.
"""
        # Call the LLM to generate an answer
        answer = call_llm(prompt)
        return answer

    def post(self, shared, prep_res, exec_res):
        """Save the final answer and complete the flow."""
        # Save the answer in the shared store
        shared["answer"] = exec_res

        print(f"✅ Answer generated successfully")

        # We're done - no need to continue the flow
        return "done"

class VoiceAgent(pf.Node):
    def prep(self, shared):
        """Get the question and context for answering."""
        return shared["response_agent_query"],shared.get("voice_setting",),shared.get("query_context", "")

    def exec(self, prep_res):
        """Call the LLM to generate a final answer."""
        question,settings,context = prep_res

        print(f"✍️ Crafting final answer...")

        # Create a prompt for the LLM to answer the question
        prompt = f"""
### CONTEXT
Based on the following information, answer the question.
Question: {question}
Research: {context}

## YOUR ANSWER:
Provide a comprehensive answer using the research results.
"""
        # Call the LLM to generate an answer
        text_answer = call_llm(prompt)
        final_answer = TTS(text_answer,settings)
        return final_answer

    def post(self, shared, prep_res, exec_res):
        """Save the final answer and complete the flow."""
        # Save the answer in the shared store
        shared["answer"] = {"output":exec_res,"format":"voice"}

        print(f"✅ Answer generated successfully")

        # We're done - no need to continue the flow
        return "done"
