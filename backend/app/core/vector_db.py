from pymilvus import connections, Collection, FieldSchema, CollectionSchema, DataType, utility

# Connect to Milvus
connections.connect("default", host="localhost", port="19530")

def create_collection():
    if utility.has_collection("text_embeddings"):
        return Collection("text_embeddings")
    
    fields = [
        FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
        FieldSchema(name="url", dtype=DataType.VARCHAR, max_length=500),
        FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=1536)  # Dimension for OpenAI's ada-002 model
    ]
    schema = CollectionSchema(fields, "Text embeddings for writer analysis")
    collection = Collection("text_embeddings", schema)
    
    # Create an IVF_FLAT index for the embedding field
    index_params = {
        "metric_type": "L2",
        "index_type": "IVF_FLAT",
        "params": {"nlist": 1024}
    }
    collection.create_index("embedding", index_params)
    return collection

collection = create_collection()

async def store_embedding(url: str, embedding: list[float]):
    collection.insert([
        [url],
        [embedding]
    ])
    await collection.flush()