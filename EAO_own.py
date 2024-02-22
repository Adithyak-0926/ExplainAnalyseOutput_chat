import streamlit as st
from langchain_community.chat_message_histories import StreamlitChatMessageHistory

import json
import time

from langchain_community.document_loaders import PyPDFLoader
from langchain_community.document_loaders import JSONLoader
from langchain_community.document_loaders import DirectoryLoader

from langchain.chains import LLMChain
from langchain.prompts import (
    PromptTemplate
)
from langchain.memory import ConversationBufferWindowMemory

from langchain_openai import ChatOpenAI
from langchain_openai import OpenAI
from langchain_community.callbacks import get_openai_callback


import os

OPENAI_ACCESS_TOKEN = os.environ.get('OPENAI_ACCESS_KEY')

st.set_page_config(page_title="EAO_Chat", page_icon=":tiger:")
st.title(":tiger: EAO_chat")

# Check if the user has entered the JSON path
if 'json_path' not in st.session_state:
    st.session_state['json_path'] = ''

# Step 1: Ask the user to enter the JSON path
if not st.session_state['json_path']:
    st.session_state['json_path'] = st.text_input('Enter the path to folder containing JSON file:')

if 'langchain_messages' not in st.session_state:
    st.session_state['langchain_messages'] = []
   
def extract_metrics(question,document):
    # Define the prompt template for metric extraction
    metric_extractor_template = """You are a metric extractor and can extract the necessary metrics from the user question based on the context provided which is a documentation containing definitions of all metrics.
             context : {document} \n
             question : {question} \n
             Instructions : 
             1) You need to just return the list of names of metrics whose values will be needed to answer the question.
             2) Always return ‘queryID’ and ‘Operator’ into the list regardless of the need. 
             Note: only return the list of operators and do not write a single token extra apart from names
           
             """
    new_prompt_template = PromptTemplate.from_template(template=metric_extractor_template)

    # Create the LLMChain for metric extraction
    metric_extractor = LLMChain(llm=llm, prompt=new_prompt_template, verbose=False)

    # Extract metrics using the LLMChain
    with get_openai_callback() as ab:
        res = metric_extractor({'question': question, 'document': document})
        metrics_list = res['text'].split('\n')  # Split the text into a list of metrics
        print(f"Total Tokens for extraction: {ab.total_tokens}")
        print(f"Prompt Tokens for extraction: {ab.prompt_tokens}")
        print(f"Completion Tokens for extraction: {ab.completion_tokens}")
        print(f"Total Cost (USD) for extraction: ${ab.total_cost}")

    # Remove any empty strings or unnecessary whitespace
    metrics_list = [metric.strip() for metric in metrics_list if metric.strip()]
    print(metrics_list)
    return metrics_list

def clean_json(json_data, metric_list):
    if isinstance(json_data, dict):
        keys_to_delete = []
        # for key, value in json_data.items():
        for key in list(json_data.keys()):
            value = json_data[key]
            if isinstance(value, list):
                 if all(isinstance(item, (int, float)) for item in value) and key.lower() not in [metric.lower() for metric in metric_list]:
                     keys_to_delete.append(key)
                 clean_json(value, metric_list)
            else:
                if key.lower() not in [metric.lower() for metric in metric_list]:
                        keys_to_delete.append(key)
        for key in keys_to_delete:
            del json_data[key]
    elif isinstance(json_data, list):
        for item in json_data:
                clean_json(item, metric_list)
    # print(json_data)
    return json_data

def process_json_files(input_folder, output_folder,question, document):
    # perform extraction
    metrics_list = extract_metrics(question, document)
    # Iterate over each JSON file in the provided folder
    for filename in os.listdir(input_folder):
        if filename.endswith(".json"):
            input_path = os.path.join(input_folder, filename)
            output_path = os.path.join(output_folder, filename)

            # Load the JSON data
            with open(input_path, 'r') as f:
                json_data = json.load(f)

            # Perform cleanup process 
            modified_json_data = clean_json(json_data, metrics_list)

                # Save the modified JSON data to a separate file
            output_file = os.path.splitext(output_path)[0] + f"_{question.replace(' ', '_')}.json"
            with open(output_file, 'w') as f:
                json.dump(modified_json_data, f, indent=4)


def clean_output_folder(output_folder):
    # Iterate over each file in the output folder
    for filename in os.listdir(output_folder):
        file_path = os.path.join(output_folder, filename)
        # Check if the file is a regular file (not a directory)
        if os.path.isfile(file_path):
            # Remove the file
            os.remove(file_path)

# Set up memory
msgs = StreamlitChatMessageHistory(key="langchain_messages")
if len(msgs.messages) == 0:
     msgs.add_ai_message("How can I help you?")

llm = ChatOpenAI(
          temperature=0,
          api_key=OPENAI_ACCESS_TOKEN,
          model="gpt-4-1106-preview",
         )

#specifying the doc that contains all definitions of E0A metrics
with open('Documentantion.md', 'r') as f:
    documentation = f.read()

input_folder = st.session_state['json_path']
output_folder = 'Temp_Json_Folder'

JSON_Analyser_template = """You are now a JSON Analyzer! You will be provided with data from one or multiple JSON files, which contain query execution statistics. Each JSON is associated with a specific query, identified by a QueryID. 
                        JSON Data:
                        —
                        {data}
                        —

                        \n{document}\n as a reference, please respond to the {question}. Keep the following points in mind:
                        If the question relates to performance, include relevant snippets or sections from the provided JSON data.
                        When analyzing data from two or more JSON files, reference each document/JSON by its QueryID.
                        Examples to guide your analysis:
                        Question: How many join operators are there?
                            Thought Process: Examine the JSON data to count the number of JOIN operators by looking at the ‘operator’ metric. Apply this process for all queries associated with unique QueryIDs.
                        Question: What are the most expensive operators?
                            Thought Process: Focus on the ‘cost_percent’ and ‘cost_percent_str’ metrics in the JSON data. Calculate the total sum of ‘cost_percent’ for all operators to see if it exceeds 50%. If not, consider other metrics such as ‘thread_duration’ for evaluating costs, and explain the rationale behind your metric selection.

             """

# new_prompt_template = PromptTemplate(input_variables=['question','data','document'], template="You are Json Analyser now! You will be given data of a single json or multiple jsons which consists of query execution stats for a query which one refers to with QueryID for every json.Looking at the json/s: \n{data}\n and keeping the document :\n{document}\n as reference, answer to the {question}!Keep the points in mind 1)If the question is related to performance, consider showing some snippet or some part of the json which was provided earlier.2)In case of two or more jsons data, refer a document/json with queryID of it(as a query). Keep your explanation to maximum 100 tokens")
new_prompt_template = PromptTemplate.from_template(template=JSON_Analyser_template)
memory = ConversationBufferWindowMemory(input_key='question',k=10)
QnA_teller = LLMChain(llm=llm,prompt= new_prompt_template,verbose= False,memory=memory)

# button for clearing previous chat
if st.button('Clear Chat'):
               msgs.clear()
# Render current messages from StreamlitChatMessageHistory
for msg in msgs.messages:
            st.chat_message(msg.type).write(msg.content)

view_messages = st.expander("your chat history in this session")
if prompt := st.chat_input():
           start_time = time.time()
           msgs.add_user_message(prompt)
           process_json_files(input_folder,output_folder,prompt,documentation)
           loader = DirectoryLoader(output_folder, glob="**/*.json", show_progress=True, loader_cls=JSONLoader, loader_kwargs={'jq_schema': '.', 'text_content': False})
           modified_data = loader.load()
           with get_openai_callback() as cb:
              response = QnA_teller({'question': prompt, 'document': documentation, 'data': modified_data})
              # Print token usage details
              print(f"Total Tokens: {cb.total_tokens}")
              print(f"Prompt Tokens: {cb.prompt_tokens}")
              print(f"Completion Tokens: {cb.completion_tokens}")
              print(f"Total Cost (USD): ${cb.total_cost}")
           print(f"time taken for the question: {prompt} is {time.time()-start_time}")   
           msgs.add_ai_message(response['text'])
           st.chat_message("ai").write(response['text']) 
           clean_output_folder(output_folder)
           
with view_messages:
            view_messages.json(st.session_state.langchain_messages)

    