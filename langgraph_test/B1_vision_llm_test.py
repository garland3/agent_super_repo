from typing import Any
import os
# from unstructured.partition.pdf import partition_pdf
# import pytesseract
# import uuid

# from langchain.embeddings import OpenAIEmbeddings
# from langchain.retrievers.multi_vector import MultiVectorRetriever
# from langchain.schema.document import Document
# from langchain.storage import InMemoryStore
# from langchain.vectorstores import Chroma

import base64
# from langchain.chat_models import ChatOpenAI
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema.messages import HumanMessage, AIMessage
# from dotenv import load_dotenv

# from langchain.schema.runnable import RunnablePassthrough
# from langchain.prompts import ChatPromptTemplate
# from langchain.schema.output_parser import StrOutputParser
from langchain_together import ChatTogether


# llm= ChatOpenAI(model="gpt-4o-mini", max_tokens=1024)
llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro")
llm = ChatTogether(
    model="meta-llama/Llama-3.2-11B-Vision-Instruct-Turbo",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
    # api_key="...",
    # other params...
)


# Function to encode images
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


# Function for image summaries
def summarize_image(encoded_image):
    prompt = [
        AIMessage(content="You are a bot that is good at analyzing images."),
        HumanMessage(content=[
            {"type": "text", "text": "Describe the contents of this image."},
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{encoded_image}"
                },
            },
        ])
    ]
    
    response = llm.invoke(prompt)
    return response.content


file = "/home/garlan/git/agents/agent_super_repo/langgraph_test/imgs/R8_sd3.5L_00001_.png"
encoding = encode_image(file)
summary = summarize_image(encoding)
print(summary)