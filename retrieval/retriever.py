import os
from langchain.document_loaders import TextLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain_ibm import WatsonxEmbeddings
from ibm_watsonx_ai.metanames import EmbedTextParamsMetaNames as EmbedParams
from ibm_watsonx_ai.foundation_models.utils.enums import EmbeddingTypes

def setup_retriever(directory_path, credentials, project_id):
    # Initialize an empty list to store all text chunks
    all_texts = []

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

    return docsearch.as_retriever()
