# %% 
# Import required libraries
import os
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_anthropic import ChatAnthropic
from langchain.vectorstores import Chroma
from langchain_community.document_loaders import WebBaseLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.prompts import PromptTemplate
from langchain.tools import tool
from langchain.tools.render import render_text_description_and_args
from langchain.agents.output_parsers import JSONAgentOutputParser
from langchain.agents.format_scratchpad import format_log_to_str
from langchain.agents import AgentExecutor
from langchain.memory import ConversationBufferMemory
from langchain_core.runnables import RunnablePassthrough


# %% 
# Load environment variables
load_dotenv(os.getcwd()+"/.env", override=True)

# Initialize LLM and Embeddings
llm = ChatAnthropic(
    anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
    model="claude-3-sonnet-20240229",
    max_tokens=1000,
    temperature=0
)

embeddings = OpenAIEmbeddings(
    openai_api_key=os.getenv("OPENAI_API_KEY")
)

# Define URLs for knowledge base
urls = [
    'https://www.ibm.com/case-studies/us-open',
    'https://www.ibm.com/sports/usopen',
    'https://newsroom.ibm.com/US-Open-AI-Tennis-Fan-Engagement',
    'https://newsroom.ibm.com/2024-08-15-ibm-and-the-usta-serve-up-new-and-enhanced-generative-ai-features-for-2024-us-open-digital-platforms'
]
# %%
# Load and process documents
docs = [WebBaseLoader(url).load() for url in urls]
docs_list = [item for sublist in docs for item in sublist]

# Split documents
text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(chunk_size=250, chunk_overlap=0)
doc_splits = text_splitter.split_documents(docs_list)

# Create vector store and retriever
vectorstore = Chroma.from_documents(
    documents=doc_splits,
    collection_name="agentic-rag-chroma",
    embedding=embeddings,
)
retriever = vectorstore.as_retriever()

# %%
# Define RAG tool
@tool
def get_US_Open_context(question: str):
    """Get context about IBM's involvement in the 2024 US Open Tennis Championship."""
    context = retriever.invoke(question)
    return context

tools = [get_US_Open_context]

# Set up prompts
system_prompt = """Respond to the human as helpfully and accurately as possible. You have access to the following tools: {tools}

Use a json blob to specify a tool by providing an action key (tool name) and an action_input key (tool input).

Valid "action" values: "Final Answer" or {tool_names}

Provide only ONE action per $JSON_BLOB, as shown:"

```
{{
"action": $TOOL_NAME,
"action_input": $INPUT
}}
```

Follow this format:

Question: input question to answer
Thought: consider previous and subsequent steps
Action:
```
$JSON_BLOB
```
Observation: action result
... (repeat Thought/Action/Observation N times)
Thought: I know what to respond
Action:
```
{{
"action": "Final Answer",
"action_input": "Final response to human"
}}
```
Begin! Reminder to ALWAYS respond with a valid json blob of a single action.
Respond directly if appropriate. Format is Action:```$JSON_BLOB```then Observation"""

human_prompt = """{input}

{agent_scratchpad}

(reminder to always respond in a JSON blob)"""

# Create prompt template
prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    MessagesPlaceholder("chat_history", optional=True),
    ("human", human_prompt),
])

# Finalize prompt template
prompt = prompt.partial(
    tools=render_text_description_and_args(list(tools)),
    tool_names=", ".join([t.name for t in tools]),
)

# Set up memory and chain
memory = ConversationBufferMemory()

chain = (
    RunnablePassthrough.assign(
        agent_scratchpad=lambda x: format_log_to_str(x["intermediate_steps"]),
        chat_history=lambda x: memory.chat_memory.messages,
    )
    | prompt 
    | llm 
    | JSONAgentOutputParser()
)

# Create agent executor
agent_executor = AgentExecutor(
    agent=chain, 
    tools=tools, 
    handle_parsing_errors=True, 
    verbose=True, 
    memory=memory
)

# Example usage
if __name__ == "__main__":
    # Test queries
    queries = [
        "Where was the 2024 US Open Tennis Championship?",
        "How did IBM use watsonx at the 2024 US Open Tennis Championship?",
        "What is the capital of France?"
    ]
    
    for query in queries:
        print(f"\nQuery: {query}")
        response = agent_executor.invoke({"input": query})
        print(f"Response: {response['output']}\n")
        print("-" * 50)