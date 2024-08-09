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
    client.create_collection(collection_name=collection_name, schema=schema)
    
    # Create an index on the vector field
    index_params = {
        "metric_type": "L2",
        "index_type": "IVF_FLAT",
        "params": {"nlist": 1024}
    }
    client.create_index(collection_name, "vector", index_params)

def insert_data(collection_name, data):
    return client.insert(collection_name, data)

def search_vectors(collection_name, query_vectors, limit=5, output_fields=None):
    search_params = {
        "metric_type": "L2",
        "params": {"nprobe": 10},
    }
    return client.search(
        collection_name=collection_name,
        data=query_vectors,
        limit=limit,
        output_fields=output_fields,
        search_params=search_params
    )

# Create the collection when this module is imported
create_collection()