from google.adk.agents import LlmAgent

class AnalyticsAgent(LlmAgent):
    def __init__(self):
        super().__init__(
            name="AnalyticsAgent",
            model="gemini-2.0-flash",
            description="Handles the analytics part.",
            instruction="Handles the analytics part."
        )

    # Optionally add custom vision logic
    # def process_image(self, ...):
    #     pass
