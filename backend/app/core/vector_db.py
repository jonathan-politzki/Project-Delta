# vector_db.py

from pymilvus import MilvusClient, DataType, FieldSchema, CollectionSchema

client = MilvusClient("milvus_demo.db")

def create_collection(collection_name="demo_collection", dimension=1536):
    if client.has_collection(collection_name):
        client.drop_collection(collection_name)
    
    fields = [
        FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
        FieldSchema(name="vector", dtype=DataType.FLOAT_VECTOR, dim=dimension),
        FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=65535),
        FieldSchema(name="subject", dtype=DataType.VARCHAR, max_length=255)
    ]
    
    schema = CollectionSchema(fields, description="Demo collection for vector search")
    client.create_collection(collection_name, schema)

def insert_data(collection_name, data):
    return client.insert(collection_name, data)

def search_vectors(collection_name, query_vectors, limit=5, output_fields=None):
    return client.search(
        collection_name=collection_name,
        data=query_vectors,
        limit=limit,
        output_fields=output_fields
    )

# Create the collection when this module is imported
create_collection()