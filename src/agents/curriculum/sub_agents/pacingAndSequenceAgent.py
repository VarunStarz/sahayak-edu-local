from google.adk.agents import LlmAgent

class PacingAndSequenceAgent(LlmAgent):
    def __init__(self):
        super().__init__(
            name="PacingAndSequenceAgent",
            model="gemini-2.0-flash",
            description="Handles generation/help with course curriculum.",
            instruction="Help the teacher with generating a proper course curriculum or topics necessry to teach a class here."
        )

    # Optionally add custom vision logic
    # def process_image(self, ...):
    #     pass
