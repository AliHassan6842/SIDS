import json
from typing import Any

import asyncpg


class PgVectorClient:
    def __init__(self, dsn: str):
        self.dsn = dsn
        self.pool = None

    async def connect(self):
        """Initializes the connection pool."""
        if not self.pool:
            self.pool = await asyncpg.create_pool(self.dsn)

    async def close(self):
        """Closes the connection pool."""
        if self.pool:
            await self.pool.close()
            self.pool = None

    async def ensure_table(self):
        """Ensures the pgvector extension and knowledge_chunks table exist."""
        if not self.pool:
            raise RuntimeError("Database pool not initialized. Call connect() first.")
            
        async with self.pool.acquire() as conn:
            await conn.execute("CREATE EXTENSION IF NOT EXISTS vector;")
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS knowledge_chunks (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    text_content TEXT NOT NULL,
                    embedding vector(1536), -- Assuming standard text embedding size
                    metadata JSONB,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                );
            ''')
            # Create an HNSW index for cosine distance
            await conn.execute('''
                CREATE INDEX IF NOT EXISTS knowledge_chunks_embedding_idx 
                ON knowledge_chunks 
                USING hnsw (embedding vector_cosine_ops);
            ''')
            # Create GIN index for full-text search (hybrid)
            await conn.execute('''
                CREATE INDEX IF NOT EXISTS knowledge_chunks_text_idx 
                ON knowledge_chunks 
                USING GIN (to_tsvector('english', text_content));
            ''')

    async def ingest_chunks(self, chunks: list[dict[str, Any]]):
        """
        Ingests a list of document chunks into the database.
        Expected chunk format:
        {
            "text": "The content...",
            "embedding": [0.1, 0.2, ...],
            "metadata": {"source": "doc1"}
        }
        """
        if not self.pool:
            raise RuntimeError("Database pool not initialized. Call connect() first.")
            
        if not chunks:
            return

        async with self.pool.acquire() as conn:
            # Prepare the query for fast insertion
            query = '''
                INSERT INTO knowledge_chunks (text_content, embedding, metadata)
                VALUES ($1, $2::vector, $3)
            '''
            
            # Format data for executemany
            values = []
            for chunk in chunks:
                # pgvector asyncpg support - pass list as string or register vector type.
                # Simplest way without registering custom types is passing list as string representation
                emb_str = f"[{','.join(map(str, chunk['embedding']))}]"
                meta_json = json.dumps(chunk.get("metadata", {}))
                values.append((chunk["text"], emb_str, meta_json))
                
            await conn.executemany(query, values)

    async def hybrid_cosine_similarity_search(
        self, 
        query_text: str, 
        query_embedding: list[float], 
        limit: int = 5, 
        alpha: float = 0.5,
        metadata_filter: dict[str, Any] | None = None
    ) -> list[dict[str, Any]]:
        """
        Executes a hybrid search using both vector cosine similarity and full-text search (FTS).
        alpha controls the weighting:
        1.0 = pure vector search
        0.0 = pure full-text search
        0.5 = equal weighting
        """
        if not self.pool:
            raise RuntimeError("Database pool not initialized. Call connect() first.")
            
        emb_str = f"[{','.join(map(str, query_embedding))}]"
        
        # Build metadata filter query string
        meta_sql = "TRUE"
        params = [query_text, emb_str, limit]
        
        if metadata_filter:
            param_idx = 4
            meta_conditions = []
            for k, v in metadata_filter.items():
                meta_conditions.append(f"metadata->>'{k}' = ${param_idx}")
                params.append(str(v))
                param_idx += 1
            if meta_conditions:
                meta_sql = " AND ".join(meta_conditions)
                
        # Use Reciprocal Rank Fusion (RRF) or a normalized score combination
        # For simplicity, we combine ts_rank and cosine distance via linear interpolation of ranks or scores
        # Note: vector_cosine_ops returns distance (0 is exact match, 2 is exact opposite).
        # Cosine similarity = 1 - distance.
        query = f'''
            WITH vector_search AS (
                SELECT 
                    id, 
                    text_content, 
                    metadata, 
                    (1 - (embedding <=> $2::vector)) AS vector_score
                FROM knowledge_chunks
                WHERE {meta_sql}
            ),
            fts_search AS (
                SELECT 
                    id, 
                    ts_rank(to_tsvector('english', text_content), plainto_tsquery('english', $1)) AS fts_score
                FROM knowledge_chunks
                WHERE {meta_sql} AND to_tsvector('english', text_content) @@ plainto_tsquery('english', $1)
            )
            SELECT 
                COALESCE(v.id, f.id) AS id,
                COALESCE(v.text_content, (SELECT text_content FROM knowledge_chunks WHERE id = COALESCE(v.id, f.id))) AS text_content,
                COALESCE(v.metadata, (SELECT metadata FROM knowledge_chunks WHERE id = COALESCE(v.id, f.id))) AS metadata,
                COALESCE(v.vector_score, 0.0) AS vector_score,
                COALESCE(f.fts_score, 0.0) AS fts_score,
                ({alpha} * COALESCE(v.vector_score, 0.0) + (1.0 - {alpha}) * COALESCE(f.fts_score, 0.0)) AS hybrid_score
            FROM vector_search v
            FULL OUTER JOIN fts_search f ON v.id = f.id
            ORDER BY hybrid_score DESC
            LIMIT $3;
        '''
        
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(query, *params)
            
            results = []
            for row in rows:
                meta = row["metadata"]
                if isinstance(meta, str):
                    meta = json.loads(meta)
                results.append({
                    "id": str(row["id"]),
                    "text_content": row["text_content"],
                    "metadata": meta,
                    "vector_score": float(row["vector_score"]),
                    "fts_score": float(row["fts_score"]),
                    "hybrid_score": float(row["hybrid_score"])
                })
                
            return results
