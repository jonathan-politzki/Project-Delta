from pymilvus import MilvusClient, DataType, FieldSchema, CollectionSchema
import logging

logger = logging.getLogger(__name__)

USE_MILVUS = False  # Set this to False to disable Milvus

client = None
if USE_MILVUS:
    try:
        client = MilvusClient("milvus_demo.db")
    except Exception as e:
        logger.error(f"Failed to connect to Milvus: {str(e)}")

def create_collection(collection_name="demo_collection", dimension=1536):
    if USE_MILVUS:
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
            "field_name": "vector",
            "metric_type": "L2",
            "index_type": "IVF_FLAT",
            "params": {"nlist": 1024}
        }
        try:
            client.create_index(collection_name, index_params)
            logger.info(f"Successfully created index on collection: {collection_name}")
        except Exception as e:
            logger.error(f"Failed to create an index on collection: {collection_name}")
            logger.error(f"Error: {str(e)}")
    else:
        logger.info("Milvus operations are disabled.")

def insert_data(collection_name, data):
    if USE_MILVUS:
        # Your insert_data implementation here
        pass
    else:
        logger.info("Milvus operations are disabled.")

def search_vectors(collection_name, query_vectors, limit=5, output_fields=None):
    if USE_MILVUS:
        search_params = {
            "metric_type": "L2",
            "params": {"nprobe": 10},
        }
        try:
            return client.search(
                collection_name=collection_name,
                data=query_vectors,
                anns_field="vector",
                param=search_params,
                limit=limit,
                output_fields=output_fields
            )
        except Exception as e:
            logger.error(f"Error during vector search: {str(e)}")
    else:
        logger.info("Milvus operations are disabled.")
    return []

# Create the collection when this module is imported, commented out for now
# if USE_MILVUS and client is not None:
#     create_collection()