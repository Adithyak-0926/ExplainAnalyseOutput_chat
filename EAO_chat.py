import streamlit as st
from langchain_community.chat_message_histories import StreamlitChatMessageHistory

import json
from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader
from langchain_community.document_loaders import JSONLoader
from langchain_community.document_loaders import DirectoryLoader

from langchain.chains import LLMChain
from langchain.chains import AnalyzeDocumentChain
from langchain.prompts import (
    ChatPromptTemplate,
    MessagesPlaceholder,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    PromptTemplate
)
from langchain.memory import ConversationBufferWindowMemory

from langchain_openai import ChatOpenAI
from langchain_openai import OpenAI

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
# else:
#     # Step 2: Show a loading spinner while processing the user's input
#     with st.spinner('Loading...'):
if 'langchain_messages' not in st.session_state:
    st.session_state['langchain_messages'] = []

# Set up memory
msgs = StreamlitChatMessageHistory(key="langchain_messages")
if len(msgs.messages) == 0:
     msgs.add_ai_message("How can I help you?")

llm = ChatOpenAI(
          temperature=0,
          api_key=OPENAI_ACCESS_TOKEN,
          model="gpt-4-1106-preview"
           # model="gpt-3.5-turbo"
         )
#specifying the doc that contains all definitions of E0A metrics
documentloader = PyPDFLoader('explainAnalizeOutput _documentation.pdf')
document = documentloader.load()

#loads all the jsons data from the folder provided by the user
loader = DirectoryLoader(st.session_state['json_path'], glob="**/*.json",show_progress=True, loader_cls=JSONLoader, loader_kwargs = {'jq_schema':'.','text_content':False})
jsons = loader.load()

new_prompt_template = PromptTemplate(input_variables=['question','data','document'], template="You are Json Analyser now! You will be given data of a single json or multiple jsons which consists of query execution stats for a query which one refers to with QueryID for every json.Looking at the json/s: \n{data}\n and keeping the document :\n{document}\n as reference, answer to the {question}!Keep the points in mind 1)If the question is related to performance, consider showing some snippet or some part of the json which was provided earlier.2)In case of two or more jsons data, refer a document/json with queryID of it(as a query). Keep your explanation to maximum 100 tokens")
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
           msgs.add_user_message(prompt)
           response = QnA_teller({'question': prompt, 'document': document, 'data': jsons})
           msgs.add_ai_message(response['text'])
           st.chat_message("ai").write(response['text']) 
           print(memory.load_memory_variables({}))
with view_messages:
            view_messages.json(st.session_state.langchain_messages)

    