import os
from dotenv import load_dotenv
from pymilvus import connections, Collection, FieldSchema, CollectionSchema, DataType, utility

# Load environment variables
load_dotenv()

def connect_to_milvus():
    """Establish connection to Milvus"""
    host = os.getenv("MILVUS_HOST", "localhost")
    port = os.getenv("MILVUS_PORT", "19530")
    connections.connect("default", host=host, port=port)

def create_collection():
    """Create or get the text_embeddings collection"""
    collection_name = "text_embeddings"
    
    if utility.has_collection(collection_name):
        return Collection(collection_name)
    
    fields = [
        FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
        FieldSchema(name="url", dtype=DataType.VARCHAR, max_length=500),
        FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=1536)
    ]
    schema = CollectionSchema(fields, description="Text embeddings for writer analysis")
    collection = Collection(collection_name, schema)
    
    index_params = {
        "metric_type": "L2",
        "index_type": "IVF_FLAT",
        "params": {"nlist": 1024}
    }
    collection.create_index("embedding", index_params)
    return collection

connect_to_milvus()
collection = create_collection()

async def store_embedding(url: str, embedding: list[float]):
    """Store a single embedding in the collection"""
    data = [
        [url],
        [embedding]
    ]
    collection.insert(data)
    await collection.flush()

def search_similar_embeddings(query_embedding: list[float], top_k: int = 5):
    """Search for similar embeddings"""
    search_params = {"metric_type": "L2", "params": {"nprobe": 10}}
    results = collection.search(
        data=[query_embedding],
        anns_field="embedding",
        param=search_params,
        limit=top_k,
        output_fields=["url"]
    )
    return results[0]  # Return the first (and only) query result