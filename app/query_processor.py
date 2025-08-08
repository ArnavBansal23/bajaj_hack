import logging
import os
from dotenv import load_dotenv  # Add this import
load_dotenv()  # Add this line right here

import google.generativeai as genai
from typing import List, Dict

from .models import DocumentChunk
from .in_memory_vector_store import InMemoryVectorStore

logger = logging.getLogger(__name__)

# Configure the API key from environment variables
api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

class QueryProcessor:
    def __init__(self, embedding_service, vector_store):
        self.embedding_service = embedding_service
        self.vector_store = vector_store or InMemoryVectorStore()
        self.model_name = "gemini-2.0-flash"

    async def process_batch_queries(self, queries: List[str], document_chunks: List[DocumentChunk]) -> List[str]:
        """Process multiple questions against the same document context"""
        try:
            logger.info(f"🔄 Processing {len(queries)} queries against {len(document_chunks)} document chunks")

            # Store chunks in memory vector store
            if isinstance(self.vector_store, InMemoryVectorStore):
                self.vector_store.add_documents(document_chunks)

            answers = []

            for i, query in enumerate(queries):
                logger.info(f"🔍 Processing query {i+1}/{len(queries)}: {query}")

                try:
                    # Generate query embedding
                    query_embedding = await self.embedding_service.generate_query_embedding(query)

                    # Search for relevant documents
                    relevant_docs = self.vector_store.search_similar(query_embedding, top_k=10)

                    # Filter by similarity threshold
                    filtered_docs = [doc for doc in relevant_docs if doc.get('similarity', 0) > 0.3]

                    if not filtered_docs:
                        logger.warning(f"⚠️ No relevant documents found for query {i+1}")
                        filtered_docs = relevant_docs[:5]  # Use top 5 anyway

                    # Generate answer using LLM
                    result = await self._generate_single_answer(query, filtered_docs)
                    answers.append(result)

                except Exception as e:
                    logger.error(f"❌ Failed to process query {i+1}: {str(e)}")
                    answers.append("Unable to process this question due to an error.")

            logger.info(f"✅ Completed processing {len(answers)} queries")
            return answers

        except Exception as e:
            logger.error(f"❌ Batch query processing failed: {str(e)}")
            return ["Processing error occurred."] * len(queries)

    async def _generate_single_answer(self, query: str, relevant_docs: List[Dict]) -> str:
        """Generate a single answer for a query"""
        try:
            if not api_key:
                return "API key not configured for processing"

            # Prepare context from relevant documents
            context = self._prepare_context(relevant_docs)

            # Create focused prompt for single question
            prompt = f"""Answer this specific question using the provided policy documents. Give a clear, concise answer with relevant context.

QUESTION: {query}

POLICY DOCUMENTS:
{context}

Provide a direct answer that includes the main facts and any important conditions or limitations. Keep the response informative but concise - aim for 1 sentences for simple questions, or a short paragraph for complex ones.

Answer:"""

            # Generate response
            model = genai.GenerativeModel(self.model_name)
            response = model.generate_content(prompt)

            # Clean and return the response
            answer = response.text.strip()

            # Remove any "Answer:" prefix if present
            if answer.lower().startswith("answer:"):
                answer = answer[7:].strip()

            logger.debug(f"✅ Generated answer: {answer[:100]}...")
            return answer

        except Exception as e:
            logger.error(f"❌ Failed to generate answer: {str(e)}")
            return f"Unable to generate answer: {str(e)}"

    def _prepare_context(self, relevant_docs: List[Dict]) -> str:
        """
        A helper method to combine the text from relevant documents into a single string.
        This is a placeholder implementation.
        """
        context_parts = [doc['text'] for doc in relevant_docs if 'text' in doc]
        return "\n\n---\n\n".join(context_parts)