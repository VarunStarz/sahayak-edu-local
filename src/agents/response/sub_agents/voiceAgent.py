from google.adk.agents import LlmAgent

class VoiceAgent(LlmAgent):
    def __init__(self):
        super().__init__(
            name="VoiceAgent",
            model="gemini-2.0-flash",
            description="Handles queries involving voice input/output.",
            instruction="Transcribe, synthesize, or understand audio/voice content. Place voice-processing logic here."
        )

    # Optionally add voice functions
    # def handle_audio(self, ...):
    #     pass
