"""
Embedding Service.
Generates text embeddings using Google Gemini API (google-genai) with prompt enrichment.
"""

import hashlib
import numpy as np
from typing import Optional
from google import genai

from app.config import settings

class EmbeddingService:
    EMBEDDING_DIM = 768

    def __init__(self):
        self._client = None

    def _get_client(self):
        if self._client is None:
            self._client = genai.Client(api_key=settings.GEMINI_API_KEY)
        return self._client

    def enrich_prompt(self, title: str, metadata: dict) -> str:
        date_str = metadata.get("date", "Unknown date")
        location = metadata.get("location", "Unknown")
        category = metadata.get("category", "unknown")
        sentiment_val = metadata.get("sentiment", 0.0)

        if sentiment_val > 0.5:
            sentiment_label = "hopeful / positive"
        elif sentiment_val > 0.0:
            sentiment_label = "cautiously optimistic"
        elif sentiment_val > -0.5:
            sentiment_label = "tense / uncertain"
        else:
            sentiment_label = "tragic / devastating"

        enriched = (
            f"[Vietnam War, {date_str}, {location}] "
            f"Context: {title}. "
            f"Sentiment: {sentiment_label}. "
            f"Category: {category.replace('_', ' ')}"
        )
        return enriched

    async def generate_embeddings(self, texts: list[str], metadata_list: list[dict]) -> np.ndarray:
        enriched_texts = [
            self.enrich_prompt(text, meta)
            for text, meta in zip(texts, metadata_list)
        ]

        if settings.USE_MOCK_EMBEDDINGS:
            return self._generate_mock_embeddings(enriched_texts)
        else:
            return await self._generate_real_embeddings(enriched_texts)

    def _generate_mock_embeddings(self, texts: list[str]) -> np.ndarray:
        embeddings = []
        for text in texts:
            text_hash = hashlib.sha256(text.encode()).hexdigest()
            seed = int(text_hash[:8], 16)
            rng = np.random.RandomState(seed)
            embedding = rng.randn(self.EMBEDDING_DIM).astype(np.float32)
            
            if "conflict" in text.lower() or "bombing" in text.lower() or "offensive" in text.lower():
                embedding[:50] += 2.0
            elif "peace" in text.lower() or "ceasefire" in text.lower() or "accord" in text.lower():
                embedding[:50] -= 2.0
                embedding[50:100] += 2.0
            
            norm = np.linalg.norm(embedding)
            if norm > 0:
                embedding = embedding / norm
            embeddings.append(embedding)

        return np.array(embeddings)

    async def _generate_real_embeddings(self, texts: list[str]) -> np.ndarray:
        client = self._get_client()
        all_embeddings = []
        batch_size = 100

        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            try:
                batch_embeddings = []
                for text in batch:
                    result = client.models.embed_content(
                        model="gemini-embedding-2",
                        contents=text,
                    )
                    batch_embeddings.append(result.embeddings[0].values)
                
                all_embeddings.extend(batch_embeddings)
            except Exception as e:
                print(f"[WARN] Gemini API error, falling back to mock: {e}")
                mock_embeddings = self._generate_mock_embeddings(batch)
                all_embeddings.extend(mock_embeddings.tolist())

        return np.array(all_embeddings)
