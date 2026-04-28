# Life Insurance Support Assistant (AI Agent)

A production-ready, conversational AI agent designed to assist users with life insurance inquiries. This project implements a Retrieval-Augmented Generation (RAG) architecture using LangGraph and FastAPI, featuring a highly responsive streaming command-line interface.

## 🚀 Features
* **Complex Agent Workflow:** Utilizes `LangGraph` to dynamically route user queries, deciding when to trigger the retrieval tool and when to rely on conversational context.
* **Conversational Memory:** Maintains context across multi-turn interactions using LangGraph's `MemorySaver` checkpointer.
* **Configurable Knowledge Base:** Implements a local `ChromaDB` vector store populated with industry-standard ACORD terminology for life insurance policies, claims, and riders.
* **Blazing Fast UX:** Features a native async FastAPI backend with Server-Sent Events (SSE) token streaming to the CLI, virtually eliminating time-to-first-token latency.
* **SOLID Architecture:** Decoupled data ingestion, rigorous `Pydantic` schema validation, and centralized configuration via `pydantic-settings`.

## 🛠️ Tech Stack
* **Language:** Python 3.10+
* **Orchestration:** LangGraph & LangChain
* **LLM:** OpenAI API (`gpt-4o-mini`, `text-embedding-3-small`)
* **Backend:** FastAPI & Uvicorn
* **Vector Database:** ChromaDB

## 📦 Setup & Installation

**1. Clone the repository**
\`\`\`bash
git clone git@github.com:sazzadhsakib/life-insurance-ai-agent.git
cd life-insurance-agent
\`\`\`

**2. Create a virtual environment**
\`\`\`bash
python -m venv venv
source venv/bin/activate
\`\`\`

**3. Install dependencies**
\`\`\`bash
pip install -r requirements.txt
\`\`\`

**4. Environment Variables**
Create a `.env` file in the root directory and add your OpenAI API key:
\`\`\`env
OPENAI_API_KEY=sk-your-actual-api-key
\`\`\`

## ⚙️ Usage

**1. Build the Knowledge Base**
Before starting the server, initialize the vector database by ingesting the provided JSON data.
\`\`\`bash
cd src
python ingestion.py
\`\`\`

**2. Start the FastAPI Backend**
Start the async server (this handles the LangGraph execution and token streaming).
\`\`\`bash
cd src
uvicorn app:app --reload
\`\`\`

**3. Launch the Interactive CLI**
Open a new terminal window, ensure your virtual environment is active, and run the client:
\`\`\`bash
cd src
python cli.py
\`\`\`

## 🧪 Testing Scenarios
Try the following prompts in the CLI to test the system's capabilities:
1. **Standard Retrieval:** "What is term life insurance?"
2. **Contextual Memory:** "Does that policy type require a medical exam?" *(Follow-up to previous)*
3. **Complex Process:** "How do I file a claim, and what is an accelerated death benefit rider?"
4. **Out-of-Bounds Rejection:** "Can you write a Python script for me?"