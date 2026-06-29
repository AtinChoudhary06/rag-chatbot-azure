from azure.cosmos import CosmosClient, PartitionKey
import os, time

def get_container():
    client = CosmosClient(os.getenv("AZURE_COSMOS_URI"), os.getenv("AZURE_COSMOS_KEY"))
    db = client.create_database_if_not_exists(id=os.getenv("COSMOS_DB"))
    container = db.create_container_if_not_exists(
        id=os.getenv("COSMOS_CONTAINER"),
        partition_key=PartitionKey(path="/session_id")
    )
    return container

def save_message(session_id: str, role: str, content: str):
    container = get_container()
    container.upsert_item({
        "id": f"{session_id}-{int(time.time()*1000)}",
        "session_id": session_id,
        "role": role,
        "content": content,
        "timestamp": time.time()
    })

def get_history(session_id: str) -> list[dict]:
    container = get_container()
    items = list(container.query_items(
        query="SELECT * FROM c WHERE c.session_id=@sid ORDER BY c.timestamp",
        parameters=[{"name": "@sid", "value": session_id}],
        enable_cross_partition_query=True
    ))
    return [{"role": i["role"], "content": i["content"]} for i in items]