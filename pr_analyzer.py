# pr_analyzer.py

import os
import json
from dotenv import load_dotenv
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_nvidia_ai_endpoints import ChatNVIDIA
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain.docstore.document import Document

class PRAnalyzer:
    """
    An AI-powered pull request analyzer using a RAG pipeline with NVIDIA NeMo.
    """
    # ======================================================
    #                 CONFIGURATION
    # ======================================================
    NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")
    CODEBASE_PATH = "Jaypatil588_nvidia-hackathon_dump.txt"
    EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
    LLM_MODEL = "nvidia/llama-3.3-nemotron-super-49b-v1"
    FAISS_INDEX_PATH = "faiss_index"

    def __init__(self):
        """
        Initializes the analyzer by building the full RAG pipeline.
        This is a one-time setup cost.
        """
        print("Initializing PRAnalyzer...")
        if not self.NVIDIA_API_KEY or "your_default" in self.NVIDIA_API_KEY:
             raise ValueError("NVIDIA_API_KEY not found. Please set it in your environment.")
        
        self._setup_rag_pipeline()
        print("PRAnalyzer initialized successfully.")

    def _load_codebase(self) -> list[Document]:
        """Loads and splits the codebase from a text file."""
        print(f"\nLoading codebase from '{self.CODEBASE_PATH}'...")
        with open(self.CODEBASE_PATH, "r", encoding="utf-8") as f:
            codebase = f.read()

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=2000, chunk_overlap=200, separators=["\n\n", "\n", ".", " ", ""]
        )
        documents = text_splitter.create_documents([codebase])
        print(f"Split codebase into {len(documents)} documents.")
        return documents

    def _get_vectorstore(self, documents: list[Document]) -> FAISS:
        """Creates or loads a FAISS vector store."""
        embeddings = HuggingFaceEmbeddings(model_name=self.EMBEDDING_MODEL)
        if os.path.exists(self.FAISS_INDEX_PATH):
            print("Loading existing FAISS index...")
            vector_store = FAISS.load_local(
                self.FAISS_INDEX_PATH, 
                embeddings, 
                allow_dangerous_deserialization=True
            )
        else:
            print("Creating new FAISS vector store...")
            vector_store = FAISS.from_documents(documents, embeddings)
            vector_store.save_local(self.FAISS_INDEX_PATH)
            print(f"FAISS index saved to '{self.FAISS_INDEX_PATH}'.")
        return vector_store

    def _setup_rag_pipeline(self):
        """Builds the full RAG pipeline."""
        code_docs = self._load_codebase()
        vector_store = self._get_vectorstore(code_docs)
        
        print("Initializing NVIDIA LLM and RAG chain...")
        llm = ChatNVIDIA(
            model=self.LLM_MODEL, nvidia_api_key=self.NVIDIA_API_KEY,
            temperature=0.1, max_tokens=2048
        )

        prompt_template = """
        You are an AI-powered code review assistant acting as a Senior Staff Engineer. Your primary goal is to maintain a high-quality, secure, and readable codebase by identifying issues in pull requests.
        Carefully analyze the provided "PULL REQUEST DIFF" in conjunction with the "CONTEXT FROM EXISTING CODEBASE".
        
        Your analysis MUST produce a single, clean JSON object. Do not include any other text or markdown outside of the JSON structure.

        JSON Output Structure:
        {{
          "overall_assessment": "A brief, one-sentence summary of the PR's quality.",
          "concerns": [
            {{
              "file_path": "The full path to the file with the issue.",
              "line_number_start": "The starting line number of the code block in question.",
              "line_number_end": "The ending line number of the code block in question.",
              "severity": "CRITICAL|HIGH|MEDIUM|LOW",
              "type": "Security|Bug|Readability|Best Practice",
              "description": "A detailed and clear explanation of the issue.",
              "suggestion": "A concrete, actionable code suggestion to resolve the issue."
            }}
          ],
          "approve": boolean
        }}

        CONTEXT FROM EXISTING CODEBASE:
        {context}

        PULL REQUEST DIFF:
        {question}

        RESPONSE (JSON only):
        """
        
        prompt_template2 =""" 
            You are an AI-powered code review assistant acting as a Senior Staff Engineer. Your primary goal is to maintain a high-quality, secure, and readable codebase by identifying issues in pull requests.
            Carefully analyze the provided "PULL REQUEST DIFF" in conjunction with the "CONTEXT FROM EXISTING CODEBASE".

            Your analysis MUST produce a single, clean JSON object. Do not include any other text or markdown outside of the JSON structure.

            JSON Output Structure:
            JSON

            {{
            "overall_assessment": "A brief, one-sentence summary of the PR's quality.",
            "concerns": [
                {{
                "file_path": "The full path to the file with the issue.",
                "line_number_start": "The starting line number of the code block in question.",
                "line_number_end": "The ending line number of the code block in question.",
                "severity": "CRITICAL|HIGH|MEDIUM|LOW",
                "type": "Security|Bug|Readability|Best Practice|Performance|Scalability|Maintainability",
                "vulnerability_type": "Injection|Broken Authentication|Sensitive Data Exposure|XML External Entities (XXE)|Broken Access Control|Security Misconfiguration|Cross-Site Scripting (XSS)|Insecure Deserialization|Using Components with Known Vulnerabilities|Insufficient Logging & Monitoring|Server-Side Request Forgery (SSRF)|Improper Error Handling|Denial-of-Service (DoS)|Memory Leak|Race Condition|Insecure Direct Object References (IDOR)|Path Traversal|Unvalidated Redirects and Forwards|Code Quality|Other",
                "description": "A detailed and clear explanation of the issue.",
                "suggestion": "A concrete, actionable code suggestion to resolve the issue."
                }}
            ],
            "approve": boolean
            }}

            CONTEXT FROM EXISTING CODEBASE:
            {context}

            PULL REQUEST DIFF:
            {question}

            RESPONSE (JSON only):
            """
        
        
        PROMPT = PromptTemplate(template=prompt_template, input_variables=["context", "question"])
        PROMPT2 = PromptTemplate(template=prompt_template2, input_variables=["context", "question"])


        self.rag_chain = RetrievalQA.from_chain_type(
            llm=llm, chain_type="stuff",
            retriever=vector_store.as_retriever(search_kwargs={'k': 4}),
            chain_type_kwargs={"prompt": PROMPT}
        )

        self.rag_chain2 = RetrievalQA.from_chain_type(
            llm=llm, chain_type="stuff",
            retriever=vector_store.as_retriever(search_kwargs={'k': 4}),
            chain_type_kwargs={"prompt": PROMPT2}
        )
        print("RAG pipeline created successfully.")

    def analyze(self, pr_diff: str, mode) -> dict:
        """
        Analyzes a given PR diff and returns a structured review as a dictionary.
        """

        if mode == "pr_review":
            print("\n--- Analyzing New Pull Request Diff ---")
            if not pr_diff:
                return {"error": "PR diff content is empty."}
                
            result = self.rag_chain.invoke({"query": pr_diff})
            response_text = result.get("result", "{}")
            
            print("\n--- Raw LLM Response ---")
            print(response_text)
            
            try:
                # Clean the response to ensure it's valid JSON
                if "```json" in response_text:
                    response_text = response_text.split("```json\n")[1].split("\n```")[0]
                
                return json.loads(response_text)
            except (json.JSONDecodeError, IndexError):
                print("Error: Failed to decode JSON from LLM response.")
                return {
                    "overall_assessment": "Failed to parse the AI model's response.",
                    "concerns": [{"description": response_text, "severity": "CRITICAL", "type": "Parsing Error"}],
                    "approve": False
                }
        elif mode == "vulneribility_check":
            print("\n--- Analyzing vulneribility_check---")
            if not pr_diff:
                return {"error": " content is empty."}
                
            result = self.rag_chain2.invoke({"query": pr_diff})
            response_text = result.get("result", "{}")
            
            print("\n--- Raw LLM Response ---")
            print(response_text)
            
            try:
                # Clean the response to ensure it's valid JSON
                if "```json" in response_text:
                    response_text = response_text.split("```json\n")[1].split("\n```")[0]
                
                return json.loads(response_text)
            except (json.JSONDecodeError, IndexError):
                print("Error: Failed to decode JSON from LLM response.")
                return {
                    "overall_assessment": "Failed to parse the AI model's response.",
                    "concerns": [{"description": response_text, "severity": "CRITICAL", "type": "Parsing Error"}],
                    "approve": False
                }
        