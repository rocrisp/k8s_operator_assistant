import os
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

# Step-by-step tabs
level1 = "Level 1 Operator"
level2 = "Level 2 Operator"
level3 = "Level 3 Operator"
level4 = "Level 4 Operator"
level5 = "Level 5 Operator"

levels = [level1, level2, level3, level4, level5]

one, two, three, four, five = st.tabs(levels)

# level 1: Ask a question and unlock level 2
with one:
    query = st.text_input("Ask a question about Kubernetes operators:", "What is Rose? Where do Rose and Chen work? Can Rose work?")
    query_submitted = st.button("Get Answer")
    st.session_state["one"] = True
    
    if query_submitted and query:
        with st.spinner('Processing...'):
            response = qa.invoke(query)
            st.session_state['response'] = response['result']
            st.write("### Answer")
            st.write(st.session_state['response'])

# level 2: 
with two:
    st.write("level 2 operator")

# level 3: 
with three:
    st.write("level 3 operator")
    
# level 4: 
with four:
    st.write("level 4 operator")
    
# level 5: 
with five:
    st.write("level 5 operator")