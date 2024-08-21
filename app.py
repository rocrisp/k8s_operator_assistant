import os
import getpass
import streamlit as st
from ibm_watsonx_ai import Credentials
from dotenv import load_dotenv
from langchain_ibm import WatsonxLLM
from langchain.chains import RetrievalQA
from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as GenParams
from ibm_watsonx_ai.foundation_models.utils.enums import DecodingMethods, ModelTypes
from retrieval.retriever import setup_retriever

# Load environment variables from the .env file
load_dotenv()

# Check if the API key is set as an environment variable
api_key = os.getenv('WATSONX_APIKEY')

# If the API key is not found in the environment, exit
if not api_key:
    exit("Please set the WATSONX_APIKEY environment variable")

credentials = Credentials(
    url="https://us-south.ml.cloud.ibm.com",
    api_key=api_key,
)

# Check if the project_id is set as an environment variable
project_id = os.getenv('WATSONX_PROJECTKEY')

# If the project_id is not found in the environment, exit
if not project_id:
    exit("Please set the WATSONX_PROJECTKEY environment variable")

# Setup the retriever
retriever = setup_retriever('/Users/rosecrisp/k8s_operator_assistant/docs/', credentials, project_id)

model_id = ModelTypes.GRANITE_13B_CHAT_V2

parameters = {
    GenParams.DECODING_METHOD: DecodingMethods.GREEDY,
    GenParams.MIN_NEW_TOKENS: 1,
    GenParams.MAX_NEW_TOKENS: 100,
    GenParams.STOP_SEQUENCES: ["sequence1", "sequence2", "sequence3", "sequence4"]
}

watsonx_granite = WatsonxLLM(
    model_id=model_id.value,
    url=credentials.get("url"),
    apikey=credentials.get("apikey"),
    project_id=project_id,
    params=parameters
)

qa = RetrievalQA.from_chain_type(llm=watsonx_granite, chain_type="stuff", retriever=retriever)

st.title("Kubernetes Operator Assistant")

query = st.text_input("Ask a question about Kubernetes operators:", "What is Rose? Where do Rose and Chen work? Can Rose work?")

if st.button("Get Answer"):
    with st.spinner('Processing...'):
        response = qa.invoke(query)
        st.write("### Answer")
        st.write(response['result'])  # Ensure that 'result' is the correct key for your output
