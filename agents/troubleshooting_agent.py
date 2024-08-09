# Import the Ollama class from the langchain_community package
from langchain_community.llms import Ollama

class TroubleshootingAgent:
    def __init__(self):
        self.llm = Ollama(base_url="http://localhost:11434", model="autopilot")

    def get_response(self, query):
        response = self.llm.invoke(query)
        return response
