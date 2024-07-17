import streamlit as st
from agents import FAQAgent, CodeSnippetAgent, ExplanationAgent, TroubleshootingAgent
from retrieval.retriever import Retriever
from config import OLLAMA_API_KEY

# Sample documents for retrieval (replace with actual documents)
documents = [
    "The Operator SDK helps you build Kubernetes applications.",
    "A Kubernetes operator is a method of packaging, deploying, and managing a Kubernetes application.",
    # Add more documents...
]

# Initialize retriever
retriever = Retriever(documents)

# Initialize agents with retriever
faq_agent = FAQAgent()
code_snippet_agent = CodeSnippetAgent()
explanation_agent = ExplanationAgent(api_key=OLLAMA_API_KEY)
troubleshooting_agent = TroubleshootingAgent()

# Streamlit UI
st.title("Kubernetes Operator Assistant")

query = st.text_input("Ask a question about Kubernetes Operators:")
if query:
    context = " ".join(retriever.retrieve(query))
    # Determine the agent to use based on the query
    if "faq" in query.lower():
        response = faq_agent.get_response(query, context)
    elif "code" in query.lower():
        response = code_snippet_agent.get_response(query)
    elif "explain" in query.lower():
        response = explanation_agent.get_response(query)
    elif "troubleshoot" in query.lower():
        response = troubleshooting_agent.get_response(query)
    else:
        response = "I'm not sure how to help with that."

    st.write(response)
