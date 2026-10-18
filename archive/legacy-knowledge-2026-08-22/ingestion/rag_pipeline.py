import asyncio

try:
    import asyncpg
except ImportError:
    asyncpg = None

# Real pgvector extension setup and ingestion
async def init_db(dsn: str):
    if asyncpg is None:
        print("asyncpg not installed, skipping real RAG DB init")
        return None
    conn = await asyncpg.connect(dsn)
    await conn.execute("CREATE EXTENSION IF NOT EXISTS vector;")
    await conn.execute('''
        CREATE TABLE IF NOT EXISTS agronomy_knowledge (
            id SERIAL PRIMARY KEY,
            authority VARCHAR(255),
            crop VARCHAR(100),
            problem VARCHAR(100),
            content TEXT,
            embedding vector(384) -- Using all-MiniLM-L6-v2 size
        );
    ''')
    return conn

async def ingest_knowledge(conn, authority: str, crop: str, problem: str, text: str, embedding: list):
    if conn is None: return
    await conn.execute('''
        INSERT INTO agronomy_knowledge (authority, crop, problem, content, embedding)
        VALUES ($1, $2, $3, $4, $5)
    ''', authority, crop, problem, text, str(embedding))

async def retrieve_knowledge(conn, query_embedding: list, limit: int = 3):
    if conn is None: return []
    # Cosine distance retrieval using pgvector
    rows = await conn.fetch('''
        SELECT id, authority, crop, problem, content, 1 - (embedding <=> $1::vector) AS similarity
        FROM agronomy_knowledge
        ORDER BY embedding <=> $1::vector
        LIMIT $2
    ''', str(query_embedding), limit)
    return rows

async def test_rag():
    # Dummy local pg credentials for standard tests
    dsn = "postgresql://postgres:postgres@localhost:5432/sids_rag"
    try:
        conn = await init_db(dsn)
        if conn:
            # Example fake embedding for "cotton whitefly control"
            dummy_embed = [0.01] * 384
            await ingest_knowledge(conn, "Punjab Agriculture", "Cotton", "Whitefly", "Use neonicotinoids if threshold exceeds 5 per leaf.", dummy_embed)
            res = await retrieve_knowledge(conn, dummy_embed)
            print("RAG Retrieval success:", res)
            await conn.close()
    except Exception as e:
        print(f"RAG DB not available: {e}")

if __name__ == "__main__":
    asyncio.run(test_rag())
