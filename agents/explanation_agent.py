import openai

class ExplanationAgent:
    def __init__(self, api_key):
        openai.api_key = api_key

    def get_response(self, query):
        response = openai.Completion.create(
            engine="davinci",
            prompt=query,
            max_tokens=150
        )
        return response.choices[0].text.strip()
