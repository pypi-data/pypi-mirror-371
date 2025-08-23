# imports
import os
from dotenv import load_dotenv
import streamlit as st

# Load environment variables
load_dotenv()

# Check if .env file exists
if not os.path.exists('.env'):
    st.error("❌ .env file not found!")
    st.info("Please create a .env file with your GROQ_API_KEY")
    st.stop()

# Set env vars (optional if you're passing keys directly)
langchain_api_key = os.getenv("LANGCHAIN_API_KEY") or os.getenv("LANGSMITH_API_KEY")
if langchain_api_key:
    os.environ["LANGCHAIN_API_KEY"] = langchain_api_key
    os.environ["LANGCHAIN_TRACKING_V2"] = "true"

# LangChain & Groq imports
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_groq import ChatGroq  # ✅ Replaced Google with Groq

# LLM Setup with Groq
groq_api_key = os.getenv("GROQ_API_KEY")
if not groq_api_key:
    st.error("❌ GROQ_API_KEY not found in environment variables!")
    st.info("Please add GROQ_API_KEY to your .env file")
    st.stop()

llm = ChatGroq(
    groq_api_key=groq_api_key,
    model_name="gemma2-9b-it",         # You can also use llama3-8b, llama3-70b, gemma-7b
    temperature=0.2
)

# Prompt Template
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant."),
    ("user", "Question: {Question}"),
])

# Streamlit UI
st.title("LangChain + Groq Demo ⚡")

input_text = st.text_input("Ask a question about any topic of your interest:")

output_parser = StrOutputParser()

# Chain: Prompt → LLM → Output Parser
chain = prompt | llm | output_parser

if input_text:
    response = chain.invoke({"Question": input_text})
    st.write(response)
