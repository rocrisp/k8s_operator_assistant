import streamlit as st
from agents.operator_agent import OperatorAgent
from retrieval.retriever import Retriever
from langchain.llms import Ollama
from langchain.prompts import ChatPromptTemplate
from langchain.schema.runnable import RunnablePassthrough
from langchain.schema.output_parser import StrOutputParser

# Initialize the agent
operator_agent = OperatorAgent()

# List of URLs to load documents from
urls = [
    "https://www.redhat.com/rhdc/managed-files/cl-oreilly-kubernetes-operators-ebook-f21452-202001-en_2.pdf",
    "https://examples.openshift.pub/operators/",
    "https://www.redhat.com/rhdc/managed-files/cm-oreilly-kubernetes-patterns-ebook-f19824-201910-en_0.pdf",
    "https://github.com/PacktPublishing/The-Kubernetes-Operator-Framework-Book",
    "https://github.com/fabric8io/kubernetes-client/blob/main/doc/CHEATSHEET.md",
    "https://gist.github.com/rafaeltuelho/111850b0db31106a4d12a186e1fbc53e",
    "https://docs.redhat.com/en/documentation/openshift_container_platform/4.3/pdf/operators/OpenShift_Container_Platform-4.3-Operators-en-US.pdf",
    "https://sdk.operatorframework.io/docs/building-operators/golang/quickstart/",
]

# Initialize retriever
retriever = Retriever(urls)

# Setup RAG chain
ollama = Ollama(base_url="http://localhost:11434", model="autopilot")

template = """Answer the question only from the following context:
{context}

Question: {question}
"""
prompt = ChatPromptTemplate.from_template(template)

rag_chain = (
    {"context": retriever.retrieve, "question": RunnablePassthrough()}
    | prompt
    | ollama
    | StrOutputParser()
)

st.title("Kubernetes Operator Assistant")

if 'step' not in st.session_state:
    st.session_state.step = 1

if st.session_state.step == 1:
    kind = st.text_input("Enter the kind of operator (e.g., Memcache):")
    if st.button("Next", key='next1'):
        st.session_state.kind = kind
        st.session_state.step = 2

if st.session_state.step == 2:
    services = st.text_area("Enter the resources (e.g., secrets, deployment, configmap):")
    if st.button("Next", key='next2'):
        st.session_state.services = [service.strip() for service in services.split(',')]
        st.session_state.step = 3

# if st.session_state.step == 3:
#     application = st.text_input("Enter the application the reconciler should deploy:")
#     if st.button("Generate Operator Code", key='generate'):
#         st.session_state.application = application
#         operator_code = operator_agent.generate_operator(st.session_state.kind, st.session_state.services, st.session_state.application)
#         st.code(operator_code, language='go')

if st.session_state.step == 3:
    application = st.text_input("Enter the application the reconciler should deploy:")
    if st.button("Generate Operator Code", key='generate'):
        st.session_state.application = application
        question = f"Generate operator code for kind={st.session_state.kind}, services={st.session_state.services}, application={st.session_state.application}"
        context = retriever.retrieve(question)
        response = rag_chain({"context": context, "question": question})
        st.code(response, language='go')

    question = st.text_input("Ask a question about the Kubernetes operator:")
    if question:
        context = retriever.retrieve(question)
        response = rag_chain({"context": context, "question": question})
        st.write(response)
        
# if st.session_state.step == 3:
#     query = f"Generate a Kubernetes operator for {st.session_state.kind} that manages {', '.join(st.session_state.services)}"
#     response = rag_chain.invoke(query)
#     st.code(response, language='go')
#     if st.button("Start Over", key='start_over'):
#         st.session_state.step = 1
#         st.session_state.kind = None
#         st.session_state.services = None
#         st.session_state.application