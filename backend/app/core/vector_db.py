from pymilvus import MilvusClient

# Initialize the client
client = MilvusClient("milvus_demo.db")

def create_collection(collection_name="demo_collection", dimension=1536):
    """Create a collection if it doesn't exist"""
    if client.has_collection(collection_name):
        client.drop_collection(collection_name)
    
    client.create_collection(
        collection_name=collection_name,
        dimension=dimension,
    )

def insert_data(collection_name, data):
    """Insert data into the collection"""
    return client.insert(collection_name, data)

def search_vectors(collection_name, query_vectors, limit=5, output_fields=None):
    """Search for similar vectors"""
    return client.search(
        collection_name=collection_name,
        data=query_vectors,
        limit=limit,
        output_fields=output_fields
    )

def delete_entities(collection_name, ids=None, filter=None):
    """Delete entities by id or filter"""
    return client.delete(collection_name, ids=ids, filter=filter)

# Create the collection when this module is imported
create_collection()