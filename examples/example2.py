from langchain.chains import LLMChain
from langchain_core.prompts import PromptTemplate
from langchain_community.llms import Ollama

# Define a prompt template
prompt_template = PromptTemplate.from_template(
    """
    ### INSTRUCTION
    {mood}
    {actor}
    {instruction}
    ```
    {input_1}
    ```

    {objective_instruction}
    ```
    {input_2}
    ```

    {output_instruction}
    ```
    {template}
    ```

    {language_target} {actor}
    ### RESPONSE
    """
)

# Initialize the language model
llm = Ollama(
    model="mistral:7b-instruct-v0.3-q4_0",
    base_url="http://10.13.129.49:11434",
    num_ctx=25000,
    temperature=0.7,
)

# Create an LLMChain with the prompt template and language model
llm_chain = LLMChain(prompt=prompt_template, llm=llm)

# Define the input variables for the chain
inputs = {
    "mood": "You are happy",
    "actor": "Act like Spiderman",
    "instruction": "In response to the following email:",
    "input_1": "Hello, I need help with my account.",
    "objective_instruction": "Use the following as notes on what needs to be expressed as if it was Spiderman:",
    "input_2": "Resolve the account issue.",
    "output_instruction": "Use the following as the objective of the act:",
    "template": "Provide a friendly and helpful response.",
    "language_target": "Respond in English"
}

# Run the chain with the input variables
response = llm_chain.run(**inputs)

# Output the response
print(response)

