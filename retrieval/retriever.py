from langchain_community.document_loaders import WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.embeddings import SentenceTransformerEmbeddings
from langchain_community.vectorstores import Chroma

class Retriever:
    def __init__(self, urls):
        self.urls = urls
        self.documents = self._load_documents_from_urls(urls)
        self.splits = self._split_docs(self.documents)
        self.embeddings = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
        self.vectorstore = self._populate_vectorstore(self.splits)
        #self.retriever = self.vectorstore.as_retriever()

    def _load_documents_from_urls(self, urls):
        data = []
        for url in urls:
            loader = WebBaseLoader(url)
            page = loader.load()
            page[0].page_content = page[0].page_content.replace('\n', '')
            data.extend(page)
        return data

    def _split_docs(self, data):
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
        return text_splitter.split_documents(data)

    def _populate_vectorstore(self, splits):
        vectorstore = Chroma.from_documents(
            documents=splits,
            collection_name="rag-chroma",
            embedding=self.embeddings,
        )
        return vectorstore

    def retrieve(self, query, k=5):
        results = self.vectorstore.similarity_search(query, k=k)
        return "\n".join([result.page_content for result in results])
