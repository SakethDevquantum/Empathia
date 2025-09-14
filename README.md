# 🤗 Empathia — Your Empathy Assistant

Empathia is an **AI-powered empathetic counseling assistant** built with:
- **Streamlit** for the frontend UI
- **FastAPI** for the backend
- **LangChain** (with Ollama) for model orchestration
- **Chroma** for storing system prompts and enabling prompt retrieval

It is designed to provide **compassionate, empathetic responses** while still being able to answer general queries (math, factual questions, etc.).  
When answering non-empathy topics, it always reminds the user that it is specifically trained to **help people through sadness, grief, and loneliness**.

---

## ✨ Features
- **Empathetic Conversations**: Responds in a supportive, counselor-like tone (e.g., *"I’m sorry to hear that, you’ve come this far, you deserve peace"*).
- **Safe Handling of Crisis Queries**: For suicidal or violent thoughts, it:
  - Never says *“I can’t help with that.”*
  - Provides comforting words
  - Encourages seeking help
  - Suggests reaching out to **counselors, doctors, or the nearest police station**
- **General Queries Supported**: Can still answer math, coding, or factual questions, but always ends with a gentle reminder of its true role (*"I am Empathia, trained to guide those in grief"*).
- **Session-Based Chat**: Each user gets a unique session so their chat history is maintained during the conversation.
- **Persistent Knowledge Base**: System prompts are stored in Chroma DB and retrieved contextually based on user queries.

---

## 🛠️ Tech Stack
- **Frontend**: [Streamlit](https://streamlit.io/)  
- **Backend**: [FastAPI](https://fastapi.tiangolo.com/)  
- **Database**: [ChromaDB](https://www.trychroma.com/) for storing system prompts  
- **LLM Integration**: [Ollama](https://ollama.ai/) with LangChain (`ChatOllama`, `OllamaEmbeddings`) 

---

Note: This model was made to run locally using ollama for quick prototyping and testing, in order for you to test out this model, u can download ollama and a desired model from it and then be sure to change that name of your model in api_empathia.py file replacing it with 'llama3.1' . You can also proceed to use langchain_openai, langchain_anthropic, glog apis, langchain_huggingface or anyother api service and use their respective api keys to test out this model
