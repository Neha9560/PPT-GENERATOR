# Step 1: Load Modules
import os
import time
import langchain
from langchain.agents import create_agent
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
import pytesseract as pyt
from tavily import TavilyClient
from langchain.messages import SystemMessage, HumanMessage
import numpy as np
import streamlit as st

#==============step 2: Streamlit front-end=============
# To show web-app: complete page layout
st.set_page_config(layout='wide')

st.title("AI PPT GENERATOR")
st.divider()
st.sidebar.title("Enter API-KEYS")

#================step2 load API -keys==============
GOOGLE_API_KEY = st.sidebar.text_input("Google-API", type = "password")
TAVILY_API_KEY = st.sidebar.text_input("TAVILY-API", type = "password")

#==============API VALIDATIONS ==============
ALL_API =[GOOGLE_API_KEY, TAVILY_API_KEY]

if not all(ALL_API):
  st.sidebar.error("Must PASS APP API-KEYS")

elif all(ALL_API):
  st.sidebar.success("API-KEYS LOADED SUCCESSFULLY")
  # MODEL LOAD
  MODEL = ChatGoogleGenerativeAI(
    google_api_key = GOOGLE_API_KEY,
    model = st.sidebar.selectbox("Gemini-Model-Name",
                                 options = ["gemini-2.5-flash",
                                           "gemini-2.5-flash-lite",
                                           "gemini-3.5-flash",
                                           "gemini-2.5-flash-lite"])
  )
else:
  st.sidebar.info("CHECK-API-KEYS")

# ========setp 5 backend code=============
def Search_latest_info(query):
  """This funcation helps to give
  latest search using tavily
  based on given user query related research or
  contents"""


  client =TavilyClient(api_key = TAVILY_API_KEY)
  response = client.search(query)
  return response

#================STEP 6 USER INPUT=============
st.header("Write prompt to Generate PPT or Image or Fetch Latest Nwes")

user_input = st.text_area("Write Here:")

# tool2 Generate image using free api

def generate_image(img_prompt, slide_no = 1):
  """This funcation helps user to generate
  image using free api, with given
  img_prompt"""

  url = f"https://image.pollinations.ai/{img_prompt}"

  import requests as r
  content = r.get(url).content
  with open(f"ai_image_{slide_no}.jpeg", 'wb') as f:
    f.write(content)
    


  from PIL import Image
  img = Image.open(f"ai_image_{slide_no}.jpeg")
  return url

def agent_prompt(query):
  """This help to promptity the given user
  query, suppose user needs PPT based on given
  query by user, it give detailed professional
  prompt to return the output"""


  prompt = f"""Give detailed highly professional
  prompt for below given prompt.

  you are a professional ppt designer,
  based on user given query, your task is to professional
  HTML output prompt with no markdowns.
  User Query: {query}"""

  response = model.invoke(prompt)
  final_prompt = response.content[-1]['text']

  with open("PPT_PROMPT.txt", 'w') as f:
    f.write(final_prompt)

  return final_prompt

def run_agent(leader_agent, query):

  prompt = f"""Based on Below given Query,
  your tasks in to call specific tool, first to
  promptify user prompt, than call image tool, or
  latest search if required.give slide dynamic,ui,ux
  with creative design, keep help of funcation to generate image
  based on given topic,
  with no of slide asked
  and imbed that in same html ppt
  and using file handling embed this output html, use java script funcation
  to generate image useing async func and threading and give output in HTML
  user query given below:

  """
  prompt = prompt+query

  prompt = agent_prompt(prompt)


  response = leader_agent.invoke({'messages':[{'role':'user',
                                               'content':prompt}]})

  code = response['messages'][-1].content[-1]['text']
  return code



#==============STEP 7 AGENT CALL===============

if all (ALL_API):
  leader_agent = create_agent(
    model = model,
    tools =[ Search_latest_info,
            # generate_image
              ])
else:
  st.error("must pass api key")


#================= STEP 8  NAVBAR STREAMKIT==================
tab1,tab2,tab3 = st.tabs(["Generate Image",
                          "Fetch Latest Nwes",
                          "Generate PPT"])

if (user_input) and (leader_agent):
  # Tab 1 code
  with tab1:
    if st.button("Generate Image", key = "Gen-Image"):
      with st.spinner("Running Agent"):
        try:
          img = generate_image(user_input)
          st.image(img)
        except:
              url = f"https://image.pollinations.ai/{user_input}"
              time.sleep(4)
              st.image(url)

# TAB 1 code:
    with tab2:
      if st.button("Fetch News", key = "Fetch-News"):
        with st.spinner("Running Agent"):
          try:
            prompt = "Give Multiple news in HTML card Fromat for topics" + user_input
            response = leader_agent.invoke({'messages':[{'role':'user',
                                                         'content':prompt}]})
            code = response['messages'][-1].content[-1]['text']
            st.html(code, width="stretch",
                    unsafe_allows_javascript=True)
          except Exception as err:
            st.error(err)

# TAB 3 Code:
    with tab3:
      if st.button("Generate ppt", key = "Gen-ppt"):
        with st.spinner("Running Agent"):
          try:
            code = run_agent(leader_agent,user)
            st.html(code, width="stretch",
                    unsafe_allow_javascript=True)
            # File save
            with open("ppt.html", 'w') as f:
               f.write(code)

            st.download_button(label = "DOWNLOAD PPT",
                            data = code,
                            file_name = 'ppt.html',
                            mime = 'text/html')
          except Exception as err:
            st.error(err)


