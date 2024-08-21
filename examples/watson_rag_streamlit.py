import os
import getpass
import streamlit as st
from ibm_watsonx_ai import Credentials
from dotenv import load_dotenv
from langchain.document_loaders import TextLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import Chroma
from ibm_watsonx_ai.foundation_models.utils import get_embedding_model_specs
from langchain_ibm import WatsonxEmbeddings
from ibm_watsonx_ai.metanames import EmbedTextParamsMetaNames as EmbedParams
from ibm_watsonx_ai.foundation_models.utils.enums import EmbeddingTypes, ModelTypes
from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as GenParams
from ibm_watsonx_ai.foundation_models.utils.enums import DecodingMethods
from langchain_ibm import WatsonxLLM
from langchain.chains import RetrievalQA

# Load environment variables from the .env file
load_dotenv()

# Check if the API key is set as an environment variable
api_key = os.getenv('WATSONX_APIKEY')

# If the API key is not found in the environment, prompt the user to enter it
if not api_key:
    api_key = getpass.getpass("Please enter your WML API key (hit enter): ")

credentials = Credentials(
    url="https://us-south.ml.cloud.ibm.com",
    api_key=api_key,
)

try:
    project_id = os.environ["PROJECT_ID"]
except KeyError:
    project_id = st.text_input("Please enter your project_id (hit enter): ")
    if not project_id:
        st.stop()

# Initialize an empty list to store all text chunks
all_texts = []

# Directory containing your text files
directory_path = '/Users/rosecrisp/k8s_operator_assistant/docs/'

# Process each text file in the directory
for filename in os.listdir(directory_path):
    if filename.endswith(".txt"):
        # Load the text file
        filepath = os.path.join(directory_path, filename)
        loader = TextLoader(filepath)
        documents = loader.load()

        # Split the text into chunks
        text_splitter = CharacterTextSplitter(chunk_size=1300, chunk_overlap=0)
        texts = text_splitter.split_documents(documents)
    
        # Add the text chunks to the list
        all_texts.extend(texts)

# Get embedding model specs
get_embedding_model_specs(credentials.get('url'))

embed_params = {
    EmbedParams.TRUNCATE_INPUT_TOKENS: 128,
    EmbedParams.RETURN_OPTIONS: {
        'input_text': True
    }
}

embeddings = WatsonxEmbeddings(
    model_id=EmbeddingTypes.IBM_SLATE_30M_ENG.value,
    url=credentials["url"],
    params=embed_params,
    apikey=credentials["apikey"],
    project_id=project_id
)

# Create the Chroma vector store with the embeddings
docsearch = Chroma.from_documents(all_texts, embeddings)

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

qa = RetrievalQA.from_chain_type(llm=watsonx_granite, chain_type="stuff", retriever=docsearch.as_retriever())

st.title("Kubernetes Operator Assistant")

query = st.text_input("Ask a question about Kubernetes operators:", "What is Rose? Where do Rose and Chen work? Can Rose work?")

if st.button("Get Answer"):
    with st.spinner('Processing...'):
        response = qa.invoke(query)
        st.write("### Answer")
        st.write(response['result'])  # Ensure that 'result' is the correct key for your output
