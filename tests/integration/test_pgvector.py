from unittest.mock import AsyncMock, patch

import pytest

from knowledge.retrieval.pgvector_client import PgVectorClient


@pytest.fixture
def pg_client():
    client = PgVectorClient("postgresql://fake_user:fake_pass@localhost:5432/fake_db")
    return client

@pytest.mark.asyncio
async def test_connect_close(pg_client):
    with patch("knowledge.retrieval.pgvector_client.asyncpg.create_pool", new_callable=AsyncMock) as mock_pool:
        mock_pool.return_value = AsyncMock()
        await pg_client.connect()
        mock_pool.assert_called_once_with(pg_client.dsn)
        assert pg_client.pool is not None
        
        await pg_client.close()
        assert pg_client.pool is None

@pytest.mark.asyncio
async def test_ensure_table(pg_client):
    with patch("knowledge.retrieval.pgvector_client.asyncpg.create_pool", new_callable=AsyncMock) as mock_pool:
        pool_mock = AsyncMock()
        mock_pool.return_value = pool_mock
        await pg_client.connect()
        
        # Mock connection context manager
        conn_mock = AsyncMock()
        pool_mock.acquire.return_value.__aenter__.return_value = conn_mock
        
        await pg_client.ensure_table()
        
        # Verify executed queries
        assert conn_mock.execute.call_count == 4

@pytest.mark.asyncio
async def test_ingest_chunks(pg_client):
    with patch("knowledge.retrieval.pgvector_client.asyncpg.create_pool", new_callable=AsyncMock) as mock_pool:
        pool_mock = AsyncMock()
        mock_pool.return_value = pool_mock
        await pg_client.connect()
        
        conn_mock = AsyncMock()
        pool_mock.acquire.return_value.__aenter__.return_value = conn_mock
        
        chunks = [
            {
                "text": "test chunk",
                "embedding": [0.1, 0.2, 0.3],
                "metadata": {"source": "test"}
            }
        ]
        
        await pg_client.ingest_chunks(chunks)
        conn_mock.executemany.assert_called_once()

@pytest.mark.asyncio
async def test_hybrid_cosine_similarity_search(pg_client):
    with patch("knowledge.retrieval.pgvector_client.asyncpg.create_pool", new_callable=AsyncMock) as mock_pool:
        pool_mock = AsyncMock()
        mock_pool.return_value = pool_mock
        await pg_client.connect()
        
        conn_mock = AsyncMock()
        pool_mock.acquire.return_value.__aenter__.return_value = conn_mock
        
        # Mock fetched rows
        conn_mock.fetch.return_value = [
            {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "text_content": "dummy text",
                "metadata": '{"source": "test"}',
                "vector_score": 0.8,
                "fts_score": 0.5,
                "hybrid_score": 0.65
            }
        ]
        
        results = await pg_client.hybrid_cosine_similarity_search(
            query_text="dummy text",
            query_embedding=[0.1, 0.2, 0.3],
            limit=1
        )
        
        assert len(results) == 1
        assert results[0]["id"] == "123e4567-e89b-12d3-a456-426614174000"
        assert results[0]["hybrid_score"] == 0.65
        assert results[0]["metadata"]["source"] == "test"
