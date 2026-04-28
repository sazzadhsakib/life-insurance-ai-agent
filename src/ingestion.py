import json
import os
from dotenv import load_dotenv
from typing import List
from pydantic import ValidationError
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from schema import PolicyRecord
from config import settings


load_dotenv()

class KnowledgeBaseBuilder:
    def __init__(self):
        # Everything is pulled cleanly from the settings object
        self.data_path = settings.data_file_path
        self.persist_dir = settings.chroma_persist_dir
        self.embeddings = OpenAIEmbeddings(
            model=settings.embedding_model,
            api_key=settings.openai_api_key
        )

    def _load_and_validate_data(self) -> List[PolicyRecord]:
        """Loads JSON and strictly validates it against the Pydantic schema."""
        with open(self.data_path, "r", encoding="utf-8") as f:
            raw_data = json.load(f)

        valid_records = []
        for item in raw_data:
            try:
                record = PolicyRecord(**item)
                valid_records.append(record)
            except ValidationError as e:
                print(f"Skipping invalid record. Error: {e}")
        return valid_records

    def _create_documents(self, records: List[PolicyRecord]) -> List[Document]:
        """Maps validated records into LangChain Document objects with rich metadata."""
        documents = []
        for record in records:
            doc = Document(
                page_content=record.Content,
                metadata={
                    "topic": record.Topic,
                    "policy_type": record.PolicyType,
                    "acord_code": record.AcordCode
                }
            )
            documents.append(doc)
        return documents

    def build(self):
        """Orchestrates the ingestion pipeline."""
        print("Validating source data...")
        records = self._load_and_validate_data()

        print("Constructing document representations...")
        documents = self._create_documents(records)

        print(f"Persisting vector store to {self.persist_dir}...")
        Chroma.from_documents(
            documents=documents,
            embedding=self.embeddings,
            persist_directory=self.persist_dir
        )
        print(f"Success: {len(documents)} records ingested.")

if __name__ == "__main__":
    builder = KnowledgeBaseBuilder()
    builder.build()