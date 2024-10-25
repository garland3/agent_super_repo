# A1 Simple Test - Code Explanation

This Python script demonstrates the implementation of a RAG (Retrieval Augmented Generation) system using LangChain to answer questions about the US Open Tennis Championship. Here's a detailed breakdown of how the code works:

## 1. Library Imports and Setup
The script begins by importing necessary libraries:
- Environment management: `os`, `dotenv`
- LangChain components for:
  - Language models and embeddings (OpenAI, Anthropic)
  - Vector storage (Chroma)
  - Document loading and processing
  - Prompts and agents
  - Memory management

## 2. Environment and Model Initialization
- Loads environment variables from a .env file
- Initializes the Anthropic Claude 3 model (claude-3-sonnet-20240229) as the main LLM
- Sets up OpenAI embeddings for vector storage
- Defines URLs containing information about IBM's involvement in the US Open

## 3. Document Processing
- Loads content from the specified URLs using WebBaseLoader
- Splits documents into smaller chunks using RecursiveCharacterTextSplitter
  - Chunk size: 250 tokens
  - No overlap between chunks
- Creates a Chroma vector store with the document chunks
  - Chroma is a vector database that can run both in-memory and with persistence
  - In this implementation, it's running in-memory by default since no persist_directory is specified
  - This means the vector store will be recreated each time the script runs
- Sets up a retriever interface for the vector store

## 4. RAG Tool Definition
- Defines a custom tool `get_US_Open_context` using the @tool decorator
- This tool retrieves relevant context about IBM's involvement in the 2024 US Open
- Uses the vector store retriever to find relevant information based on the input question

## 5. Prompt Engineering
- Defines a system prompt that:
  - Explains available tools
  - Specifies the JSON format for tool usage
  - Provides a structured format for the agent's thought process
- Creates a human prompt template that includes:
  - The user's input
  - Agent's scratchpad (working memory)
- Sets up conversation memory using ConversationBufferMemory

## 6. Agent Setup
- Creates a chain that:
  - Processes input and maintains conversation history
  - Formats the prompt
  - Sends it to the LLM
  - Parses the JSON output
- Initializes an AgentExecutor with:
  - The defined chain
  - Available tools
  - Error handling
  - Verbose output
  - Conversation memory

## 7. Example Usage
The script includes a test section that:
- Defines sample queries about the US Open and a control question
- Runs each query through the agent
- Prints the responses and adds separators for clarity

## Key Features
- **RAG Implementation**: Combines retrieval from documents with LLM generation
- **Memory Management**: Maintains conversation history
- **Structured Output**: Uses JSON format for clear action specification
- **Error Handling**: Includes parsing error management
- **Modular Design**: Separates document processing, tool definition, and agent setup

This implementation allows for intelligent question-answering about the US Open Tennis Championship, with the ability to retrieve and synthesize information from multiple sources while maintaining conversation context.
