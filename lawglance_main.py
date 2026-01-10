import threading
import logging
from langchain.schema import HumanMessage, AIMessage
from chains import get_rag_chain
from prompts import SYSTEM_PROMPT, QA_PROMPT

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    handlers=[logging.StreamHandler()]
)

class Lawglance:
    """
    Lawglance is a conversational AI interface that leverages a retrieval-augmented generation (RAG) pipeline 
    to answer user queries based on vector search and LLM responses.

    Redis caching is DISABLED for local development.
    """

    store = {}
    store_lock = threading.Lock()

    def __init__(self, llm, embeddings, vector_store):
        self.llm = llm
        self.embeddings = embeddings
        self.vector_store = vector_store

    def get_session_history(self, session_id):
        with Lawglance.store_lock:
            if session_id not in Lawglance.store:
                Lawglance.store[session_id] = []
                logging.info(f"Created new chat history for session_id: {session_id}")
        return Lawglance.store[session_id]

    def conversational(self, query, session_id):
        logging.info("Generating new answer (Redis disabled)")

        rag_chain = get_rag_chain(
            self.llm,
            self.vector_store,
            SYSTEM_PROMPT,
            QA_PROMPT
        )

        messages = self.get_session_history(session_id)

        response = rag_chain.invoke(
            {"input": query, "chat_history": messages}
        )

        answer = response["answer"]

        # Update in-memory chat history
        messages.append(HumanMessage(content=query))
        messages.append(AIMessage(content=answer))

        return answer, messages
