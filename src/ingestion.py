import json
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from config import settings
from parser import recursive_json_to_text  # <-- Import the isolated parser

class KnowledgeBaseBuilder:
    def __init__(self):
        self.data_path = settings.data_file_path
        self.persist_dir = settings.chroma_persist_dir
        self.embeddings = OpenAIEmbeddings(
            model=settings.embedding_model,
            api_key=settings.openai_api_key
        )

    def build(self):
        print("Loading dynamic JSON structure...")
        with open(self.data_path, "r", encoding="utf-8") as f:
            raw_data = json.load(f)

        documents = []

        if isinstance(raw_data, dict):
            for category, content in raw_data.items():
                print(f"Parsing generic category: {category}...")

                if isinstance(content, list):
                    for item in content:
                        # Use the imported pure function
                        flat_text = recursive_json_to_text(item)
                        doc_title = item.get("PolicyType", item.get("question", "General Info"))
                        documents.append(Document(
                            page_content=flat_text,
                            metadata={"category": category, "title": doc_title}
                        ))
                else:
                    # Use the imported pure function
                    flat_text = recursive_json_to_text(content)
                    documents.append(Document(
                        page_content=flat_text,
                        metadata={"category": category}
                    ))

        print(f"Constructed {len(documents)} dynamic documents. Persisting to ChromaDB...")

        Chroma.from_documents(
            documents=documents,
            embedding=self.embeddings,
            persist_directory=self.persist_dir
        )
        print("Success: Future-proof knowledge base ingested!")

if __name__ == "__main__":
    builder = KnowledgeBaseBuilder()
    builder.build()