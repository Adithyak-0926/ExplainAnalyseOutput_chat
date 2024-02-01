import streamlit as st
from langchain_community.chat_message_histories import StreamlitChatMessageHistory

import random

import json
from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader
from langchain_community.document_loaders import JSONLoader
from langchain_community.document_loaders import DirectoryLoader

from langchain.chains import LLMChain
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

OPENAI_ACCESS_TOKEN = "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"

st.set_page_config(page_title="EAO_Chat", page_icon=":tiger:")
st.title(":tiger: EAO_chat")

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
documentloader = PyPDFLoader("/home/kanamarlapudi/Downloads/ExplainAnalyseOutput-2.pdf")
document = documentloader.load()
loader = JSONLoader("/home/kanamarlapudi/Downloads/jsonStat_test/query_Q87053-80-20231009.094002.554.json",
                        jq_schema='.',
    text_content=False)
data = loader.load()

path = '/home/kanamarlapudi/Downloads/jsonStat_test'
loader = DirectoryLoader(path, glob="**/*.json",show_progress=True, loader_cls=JSONLoader, loader_kwargs = {'jq_schema':'.','text_content':False})
jsons = loader.load()



new_prompt_template = PromptTemplate(input_variables=['question'], template="You are a json stat interpretor now! Looking at the json: \n{data}\n and keeping the document :\n{document}\n as reference, answer to the {question}! If the question is related to performance, consider showing some snippet or some part of the json which was provided earlier.Keep your explanation to maximum 100 tokens")
# memory = ConversationBufferWindowMemory(k=10)
QnA_teller = LLMChain(llm=llm,prompt= new_prompt_template,verbose= False)

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
with view_messages:
      view_messages.json(st.session_state.langchain_messages)    