import pytest
import json
from pathlib import Path
from unittest.mock import AsyncMock, patch, MagicMock

# Import the modules we need to test
from knowledge.ingestion.validate_sources import validate_source
from knowledge.ingestion.parsers import check_domain_allowlist, parse_punjab_thresholds, parse_dpp_fao_data
from knowledge.retrieval.pgvector_client import PgVectorClient

# --- Schema Registry Tests ---

def test_validate_source_valid(tmp_path):
    valid_source = {
        "source_id": "test_src",
        "name": "Test Source",
        "type": "GOVERNMENT",
        "url": "https://example.gov.pk",
        "jurisdiction": "Punjab, Pakistan",
        "effective_date": "2024-01-01",
        "retrieval_date": "2026-08-16",
        "checksum": "sha256:abcd",
        "description": "Test description",
        "license": "Public Domain"
    }
    file_path = tmp_path / "valid.json"
    with open(file_path, "w") as f:
        json.dump(valid_source, f)
        
    is_valid, msg = validate_source(file_path)
    assert is_valid is True
    assert msg == "Valid"

def test_validate_source_missing_keys(tmp_path):
    invalid_source = {
        "source_id": "test_src",
        "name": "Test Source"
    }
    file_path = tmp_path / "invalid.json"
    with open(file_path, "w") as f:
        json.dump(invalid_source, f)
        
    is_valid, msg = validate_source(file_path)
    assert is_valid is False
    assert "Missing required keys" in msg

def test_validate_source_invalid_type(tmp_path):
    invalid_type = {
        "source_id": "test_src",
        "name": "Test Source",
        "type": "INVALID_TYPE",
        "url": "https://example.gov.pk",
        "jurisdiction": "Punjab, Pakistan",
        "effective_date": "2024-01-01",
        "retrieval_date": "2026-08-16",
        "checksum": "sha256:abcd",
        "description": "Test description",
        "license": "Public Domain"
    }
    file_path = tmp_path / "invalid_type.json"
    with open(file_path, "w") as f:
        json.dump(invalid_type, f)
        
    is_valid, msg = validate_source(file_path)
    assert is_valid is False
    assert "Invalid source type" in msg

# --- Domain Allowlist Tests ---

def test_domain_allowlist():
    allowed_domains = ["agripunjab.gov.pk", "fao.org"]
    
    assert check_domain_allowlist("https://agripunjab.gov.pk/pests", allowed_domains) is True
    assert check_domain_allowlist("http://www.fao.org/ipm", allowed_domains) is True
    assert check_domain_allowlist("https://malicious.com/agripunjab.gov.pk", allowed_domains) is False
    assert check_domain_allowlist("https://agripunjab.gov.pk.malicious.com", allowed_domains) is False

# --- Threshold Parsing (Punjab Gold Sets) Tests ---

def test_parse_punjab_thresholds():
    raw_text = """
    Pest: Whitefly, Threshold: 5 per leaf
    Some other text.
    Pest: Jassid, Threshold: 1 per leaf
    """
    results = parse_punjab_thresholds(raw_text)
    assert len(results) == 2
    
    assert results[0]["pest"] == "Whitefly"
    assert results[0]["threshold_value"] == 5
    assert results[0]["unit"] == "per leaf"
    
    assert results[1]["pest"] == "Jassid"
    assert results[1]["threshold_value"] == 1
    assert results[1]["unit"] == "per leaf"

# --- DPP/FAO Parsing Tests ---

def test_parse_dpp_fao_data():
    raw_json = {
        "items": [
            {
                "chemical": "Neonicotinoid",
                "guideline": "Use sparingly",
                "source": "FAO"
            },
            {
                "chemical": "Pyrethroid",
                "guideline": "Avoid near water"
            },
            {
                "unrelated": "data"
            }
        ]
    }
    results = parse_dpp_fao_data(raw_json)
    assert len(results) == 2
    
    assert results[0]["chemical"] == "Neonicotinoid"
    assert results[0]["guideline"] == "Use sparingly"
    assert results[0]["source"] == "FAO"
    
    assert results[1]["chemical"] == "Pyrethroid"
    assert results[1]["source"] == "UNKNOWN"

# --- Hybrid Retrieval Logic Tests ---

@pytest.mark.asyncio
async def test_hybrid_retrieval_logic():
    # Mocking asyncpg pool and connection
    with patch("knowledge.retrieval.pgvector_client.asyncpg.create_pool", new_callable=AsyncMock) as mock_create_pool:
        # Create a fake pool that yields a fake connection
        mock_pool = AsyncMock()
        mock_create_pool.return_value = mock_pool
        
        mock_conn = AsyncMock()
        # Mock fetch to return a list of fake rows
        mock_conn.fetch.return_value = [
            {
                "id": "uuid-1",
                "text_content": "Test content 1",
                "metadata": '{"source": "doc1"}',
                "vector_score": 0.8,
                "fts_score": 0.5,
                "hybrid_score": 0.65
            }
        ]
        
        # When pool.acquire() is called in an async with block
        mock_acquire_context = AsyncMock()
        mock_acquire_context.__aenter__.return_value = mock_conn
        mock_pool.acquire = MagicMock(return_value=mock_acquire_context)
        
        client = PgVectorClient("postgresql://fake")
        await client.connect()
        
        # Perform hybrid search
        results = await client.hybrid_cosine_similarity_search(
            query_text="pest", 
            query_embedding=[0.1] * 1536,
            limit=1
        )
        
        assert len(results) == 1
        assert results[0]["id"] == "uuid-1"
        assert results[0]["metadata"]["source"] == "doc1"
        assert results[0]["hybrid_score"] == 0.65
        
        # Verify that fetch was called
        mock_conn.fetch.assert_called_once()
        
        # We can also check if the SQL generated contains our expected RRF logic
        called_query = mock_conn.fetch.call_args[0][0]
        assert "hybrid_score" in called_query
        assert "vector_score" in called_query
        assert "fts_score" in called_query
