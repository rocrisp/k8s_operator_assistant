import streamlit as st
from streamlit_quill import st_quill
from langchain.callbacks.base import BaseCallbackHandler
import re

from langchain_community.llms import Ollama
from langchain_ibm import WatsonxLLM

from langchain.chains import LLMChain
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain_core.prompts import PromptTemplate
import os

import debugpy
import streamlit as st
from langchain.callbacks import StreamlitCallbackHandler

debug =0
if debug:
    # pylint: disable=invalid-name
    markdown = st.markdown(
    """
    ## Ready to attach the VS Code Debugger!
    ![Python: Remote Attach](https://awesome-streamlit.readthedocs.io/en/latest/_images/vscode_python_remote_attach.png)
    for more info see the [VS Code section at awesome-streamlit.readthedocs.io]
    (https://awesome-streamlit.readthedocs.io/en/latest/vscode.html#integrated-debugging)
    """
    )

    if not debugpy.is_client_connected():
        debugpy.listen(5679)
        debugpy.wait_for_client()

    markdown.empty()



class StreamDisplayHandler(BaseCallbackHandler):
    def __init__(self, container, initial_text="", display_method='markdown'):
        self.container = container
        self.text = initial_text
        self.display_method = display_method
        self.new_sentence = ""

    def on_llm_new_token(self, token: str, **kwargs) -> None:
        self.text += token
        self.new_sentence += token

        display_function = getattr(self.container, self.display_method, None)
        if display_function is not None:
            display_function(self.text)
        else:
            raise ValueError(f"Invalid display_method: {self.display_method}")

    def on_llm_end(self, response, **kwargs) -> None:
        self.text=""

mood="{mood}"
actor="{actor}"
instruction="{instruction}"
input_1="{input_1}"

objective_instruction="{objective_instruction}"
input_2="{input_2}"

output_instruction="{output_instruction}"
template="{template}"

language_target="{language_target}"

if 'response' not in st.session_state:
    st.session_state['response'] = ""

if 'revisions' not in st.session_state:
    st.session_state.revisions = []

# Example TEMPLATES
TEMPLATES = {
    "Language Model": {
        "Prompt Template":f"""
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
    },
    "First Touch": {
        "Email": """Thank you for contacting Red Hat about the issue you're experiencing with your [system/service/etc.]. My name is Chen and I'm here to help you resolve this issue as quickly as possible.
I understand that [issue the customer is experiencing] can be frustrating and I'm committed to assisting you in any way I can. As a first step, you might try [suggested action plan to resolve the issue]. If that doesn't work, please let me know and we can explore other options together.
Please let me know if you have any further questions or if there's anything else I can do to help. Thank you for choosing Red Hat for your support needs. We value your business and strive to provide the best service possible.
Best Regards,""",
        "Instruction": "Write a client facing email in response to this email:",
        "Objective": "The email needs to convey the following objective:",
        "Input_Context": "Case Description",
        "Input_Objective": "Response Objective",
        "Output_Format": "Using this as a template:",
        "Execution Code": f"instruction=Instruction,objective_instruction=Objective,output_instruction=Output_Format,input_1=input_1,input_2=input_2,template=Email,language_target=language_target,mood=mood,actor=actor"
    },
    "Case Continuation": {
        "Email": """Thank you for getting back to us,
[EMAIL_BODY]
Please let me know if you have any further questions or if there's anything else I can do to help. Thank you for choosing Red Hat for your support needs. We value your business and strive to provide the best service possible.
Best Regards,""",
        "Instruction": "Write a client facing email in response to this email:",
        "Objective": "The email needs to convey the following objective:",
        "Input_Context": "Case Description",
        "Input_Objective": "Response Objective",
        "Output_Format": "Using this as a template:",
        "Execution Code": f"instruction=Instruction,objective_instruction=Objective,output_instruction=Output_Format,input_1=input_1,input_2=input_2,template=Email,language_target=language_target,mood=mood,actor=actor"
   
    },
    "Assisting Colleague": {
        "Email": """My name is Chen and I will also be helping you resolve this issue along with my colleagues.
[EMAIL_BODY]
Please let me know if you have any further questions or if there's anything else I can do to help. Thank you for choosing Red Hat for your support needs. We value your business and strive to provide the best service possible.
Best Regards,""",
        "Instruction": "Write a client facing email in response to this email:",
        "Objective": "The email needs to convey the following objective:",
        "Input_Context": "Case Description",
        "Input_Objective": "Response Objective",
        "Output_Format": "Using this as a template:",
        "Execution Code": f"instruction=Instruction,objective_instruction=Objective,output_instruction=Output_Format,input_1=input_1,input_2=input_2,template=Email,language_target=language_target,mood=mood,actor=actor"
   
    },
}

# Function to handle template selection and content retrieval
def get_template_content(set_name, template_name):
    return TEMPLATES[set_name][template_name]


def prompt_template_maker(template,data):
    prompt=get_template_content("Language Model","Prompt Template")
    assignments = data.split(',')
    variables = {}
    for assignment in assignments:
        print(assignment)
        key, value = assignment.split('=')
        if value.strip() in TEMPLATES[template]:
            globals()[key.strip()] = get_template_content(template, value.strip())
            variables[key] = get_template_content(template, value)
        else:
            globals()[key.strip()] =globals()[value.strip()]
            variables[key] = globals()[value.strip()]

            
    prompt_template = PromptTemplate.from_template(prompt)
    prompt_template.partial(**variables)
    return prompt_template

def prompt_run_maker(template,data):
    prompt_template=get_template_content("Language Model","Prompt Template")
    assignments = data.split(',')
    variables = {}
    for assignment in assignments:
        print(assignment)
        key, value = assignment.split('=')
        if value.strip() in TEMPLATES[template]:
            globals()[key.strip()] = get_template_content(template, value.strip())
            variables[key] = get_template_content(template, value)
        else:
            globals()[key.strip()] =globals()[value.strip()]
            variables[key] = globals()[value.strip()]
    if actor_sel !="Normal":
        print ("Parmaters Overwritten")
        for param_override in actor_params:
            variables[param_override] = actor_params[param_override]

    return variables


# Title of the Application
st.warning("This app is for demo purposes only and not for commercial use or productional use AT THIS TIME")


# Title of the Application
st.title("RedHat Email AI Tool")

# Creating a collapsible card for each template
with st.expander("Expand to modify AI Output Settings"):
    st.header("Settings")
    options = ["English", "Spanish"]
    language_target = st.radio("Lanaguage:", options,key = "language")
    language_target = "\n\n Respond in " + language_target
    
    # Create columns for layout
    colx1, colx2 = st.columns(2)
    with colx1:
        options = ["Normal","Spiderman", "Batman", "Superman", "Custom"]
        actor_sel = st.radio("Actor:", options,key = "actor")
    with colx2:
        if actor_sel=="Normal":
            actor=""
        if actor_sel == "Custom":
            actor_sel = st.text_area("Enter your Actor here:",key="custom_actor", value="Dead Pool" ,  height=100)
        actor_params={}
        actor_params["actor"] = "Act like " + actor_sel + " reponding to a case"
        actor_params["instruction"]="In response to the following email:"
        actor_params["objective_instruction"]="Use the following as a notes what needs to be expressed in as if it was "+ actor_sel + ":"
        actor_params["output_instruction"]= "Use the following as a objective of the act:"

    # Create columns for layout
    colx1, colx2 = st.columns(2)
    with colx1:
        options = ["Normal", "Angry", "Happy", "Funny", "Custom" ]
        mood = st.radio("Mood:", options,key = "mood")
        if mood != "Normal":
            mood= " You are " + mood 
        else: 
            mood=""
    with colx2:
        if mood == "Custom":
            mood = st.text_area("Enter your Mood here:",key="custom_mood" ,  height=100)


# Creating a collapsible card for each template
with st.expander("Expand to modify AI Settings"):
   

    st.header("Backend Engine")
    # Replace with your own options
    choices = ["IBM-WatsonX","Ollama"]
    backend_selection = st.selectbox("Select a choice:", choices)

    if backend_selection == "Ollama":
        base_url=st.text_input("Base_URL", "http://10.13.129.49:11434")
        temperature_value = st.slider("Select Creativity/Temperature:", min_value=0.0, max_value=1.0, value=0.7, step=0.1)
        num_ctx = st.slider("Select Context Value", min_value=5000, max_value=45000, value=25000, step=3000)

        choices = ["mistral:7b-instruct-v0.3-q4_0"]
        model_selection = st.selectbox("Select a Model:", choices)
        if st.button("Try Connection"):
            llm = Ollama(
                model=model_selection,
                base_url=base_url,
                num_ctx=num_ctx,
                temperature=temperature_value,
            )


    if backend_selection == "IBM-WatsonX":
        #api_key=st.text_input("API_KEY", "")
        api_key = os.environ["WATSONX_APIKEY"]
        choices = ["mistralai/mixtral-8x7b-instruct-v01"]
        model_selection = st.selectbox("Select a Model:", choices)

        decoding_method = st.selectbox(
            "Decoding Method",
            ["sample", "greedy", "beam"]
        )

        max_new_tokens = st.number_input(
            "Max New Tokens",
            min_value=1,
            max_value=10000,
            value=8000
        )

        min_new_tokens = st.number_input(
            "Min New Tokens",
            min_value=1,
            max_value=10000,
            value=1
        )

        temperature = st.slider(
            "Temperature",
            min_value=0.0,
            max_value=1.0,
            value=0.7
        )

        top_k = st.slider(
            "Top K",
            min_value=1,
            max_value=100,
            value=50
        )

        top_p = st.slider(
            "Top P",
            min_value=0.0,
            max_value=1.0,
            value=1.0
        )

        parameters = {
            "decoding_method": decoding_method,
            "max_new_tokens": max_new_tokens,
            "min_new_tokens": min_new_tokens,
            "temperature": temperature,
            "top_k": top_k,
            "top_p": top_p,
        }
        api_key = os.environ["WATSONX_APIKEY"]
        if st.button("Try Connection"):

            llm = WatsonxLLM(
                model_id=model_selection,
                url="https://us-south.ml.cloud.ibm.com",
                project_id="aa445498-edd9-487a-b5b0-6a28b485897e",
                params=parameters,
                streaming=True
            )



# Creating a collapsible card for each template
with st.expander("Expand to modify Email Templates"):
    st.header("Template Configuration")
    TEMPLATE_SET_LIST = list(TEMPLATES.keys())
    Template_Set = st.selectbox("Select a Template Set:", TEMPLATE_SET_LIST)

    TEMPLATE_VAL_LIST = list(TEMPLATES[Template_Set].keys())
    Email_Selection = st.selectbox("Select a Template:", TEMPLATE_VAL_LIST)

    # Generate a unique key for the editor

    editor_key = f"{Template_Set}_{Email_Selection}_edit_box"





    # Initialize the session state for the editor content if it doesn't exist
    if editor_key not in st.session_state:
        st.session_state[editor_key] = get_template_content(Template_Set, Email_Selection)


    # First Touch Template
    st.title(f"{Template_Set} - {Email_Selection}")

    # Display the editor with the content from session state
    edited_content = st.text_area(value=st.session_state[editor_key], key=editor_key,label=editor_key)

    # Save the edited content back to the TEMPLATES dictionary
    if st.button(f"Save {Template_Set} - {Email_Selection}"):
        TEMPLATES[Template_Set][Email_Selection] = edited_content
        del st.session_state[editor_key]
        st.session_state[editor_key] = edited_content
        st.success("Template updated successfully!")


#result = llm_chain.run(**execution_params)
st.header("Template Selection")
# Replace with your own options
TEMPLATE_SET_LIST_FILTERED=TEMPLATE_SET_LIST
TEMPLATE_SET_LIST_FILTERED.remove("Language Model")
Template_choice =st.selectbox("Select a Template Set:", TEMPLATE_SET_LIST_FILTERED, key="Template")


st.header(get_template_content(Template_choice,"Input_Context"))
input_1 = st.text_area( key="input_1",label=get_template_content(Template_choice,"Input_Context"))

st.header(get_template_content(Template_choice,"Input_Objective"))
input_2 = st.text_area( key="input_2",label=get_template_content(Template_choice,"Input_Objective"))




if st.button("Generate Response"):
    if backend_selection == "Ollama":
        st_callback = StreamlitCallbackHandler(st.container())

        llm = Ollama(
            model=model_selection,
            base_url=base_url,
            num_ctx=num_ctx,
            temperature=temperature_value,
            callbacks=[st_callback]
        )

        llm_input=prompt_run_maker(Template_choice,get_template_content(Template_choice,"Execution Code"))
        prompt=prompt_template_maker(Template_choice,get_template_content(Template_choice,"Execution Code"))
        #st.write(get_template_content("Language Model","Prompt Template"))
        llm_chain = LLMChain(prompt=prompt, llm=llm,verbose=True)
        chat_box = llm_chain.run(**llm_input)

        chat_wrote= st.write(chat_box)

    elif backend_selection ==  "IBM-WatsonX":
        llm_input=prompt_run_maker(Template_choice,get_template_content(Template_choice,"Execution Code"))
        prompt=prompt_template_maker(Template_choice,get_template_content(Template_choice,"Execution Code"))
        st_callback = StreamlitCallbackHandler(st.container())
        llm = WatsonxLLM(
            model_id=model_selection,
            url="https://us-south.ml.cloud.ibm.com",
            project_id="aa445498-edd9-487a-b5b0-6a28b485897e",
            params=parameters,
            streaming=True,
            callbacks=[st_callback],
        )
        llm_chain = LLMChain(prompt=prompt, llm=llm,verbose=True)
       
        chat_box = llm_chain.run(**llm_input)
        st.session_state.response = chat_box
        st.write(st.session_state.response)



with st.expander("Expand to modify Generated Emaail"):
    st.title(f"Modify LLM Output")
    edit_output = st.text_area( label="Edit_Output",key="Edit_Output")
    # Define the prompt template for the second chain
    suggestion_prompt = PromptTemplate(
        input_variables=["previous_response", "new_input"],
        template="Based on the previous email that was generated by a LLM: {previous_response}, and the new input: {new_input}, generate a new improved message."
    )

    st_callback = StreamlitCallbackHandler(st.container())



    # Create the second LLMChain
    if backend_selection == "Ollama":
        llm = Ollama(
            model=model_selection,
            base_url=base_url,
            num_ctx=num_ctx,
            temperature=temperature_value,
            callbacks=[st_callback],
        )


    elif backend_selection ==  "IBM-WatsonX":

        llm = WatsonxLLM(
            model_id=model_selection,
            url="https://us-south.ml.cloud.ibm.com",
            project_id="aa445498-edd9-487a-b5b0-6a28b485897e",
            params=parameters,
            streaming=True,
            callbacks=[st_callback],
        )

    suggestion_llm_chain = LLMChain(prompt=suggestion_prompt, llm=llm,verbose=True)

    # Display the editor with the content from session state

    if st.button("Regenerate Response"):
        st.title(f"Old - LLM Response")
        st.write(st.session_state.response)
        # Run the second LLMChain using the output of the first LLMChain
        suggestion_input = {
            "previous_response":st.session_state.response,
            "new_input": edit_output
        }
        st.title(f"New - LLM Response")
        suggestions = suggestion_llm_chain.run(**suggestion_input)
        suggestions_wrote= st.write(suggestions)
        st.session_state.response=suggestions

