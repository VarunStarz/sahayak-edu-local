from google.adk.agents import LlmAgent

class ContentAgent(LlmAgent):
    def __init__(self):
        super().__init__(
            name="ContentAgent",
            model="gemini-2.0-flash",
            description="Handles responses for text-only content queries.",
            instruction="Respond to general text-based content queries. Implement logic here or call external content APIs."
        )

    # Optionally override methods or add custom logic
    # Example:
    # def custom_logic(self, ...):
    #     pass
