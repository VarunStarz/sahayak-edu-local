from google.adk.agents import LlmAgent

class VisionAgent(LlmAgent):
    def __init__(self):
        super().__init__(
            name="VisionAgent",
            model="gemini-2.0-flash",
            description="Handles queries requiring image or visual content processing.",
            instruction="Analyze, create, or interpret visual content. Integrate vision APIs or custom model calls here."
        )

    # Optionally add custom vision logic
    # def process_image(self, ...):
    #     pass
