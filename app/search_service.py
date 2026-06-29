from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchIndex, SimpleField, SearchableField,
    SearchField, SearchFieldDataType, VectorSearch,
    HnswAlgorithmConfiguration, VectorSearchProfile
)
from azure.search.documents.models import VectorizedQuery
from azure.core.credentials import AzureKeyCredential
from openai import OpenAI
import os, uuid

def get_embedding_client():
    return OpenAI(
        base_url=os.getenv("AZURE_OPENAI_EMBEDDING_ENDPOINT"),
        api_key=os.getenv("AZURE_OPENAI_EMBEDDING_KEY")
    )

def get_search_client():
    return SearchClient(
        os.getenv("AZURE_SEARCH_ENDPOINT"),
        os.getenv("AZURE_SEARCH_INDEX"),
        AzureKeyCredential(os.getenv("AZURE_SEARCH_KEY"))
    )

def get_index_client():
    return SearchIndexClient(
        os.getenv("AZURE_SEARCH_ENDPOINT"),
        AzureKeyCredential(os.getenv("AZURE_SEARCH_KEY"))
    )

def create_index():
    idx_client = get_index_client()
    fields = [
        SimpleField(name="id", type=SearchFieldDataType.String, key=True),
        SearchableField(name="content", type=SearchFieldDataType.String),
        SimpleField(name="filename", type=SearchFieldDataType.String, filterable=True),
        SearchField(name="embedding", type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
                    searchable=True, vector_search_dimensions=3072, vector_search_profile_name="myProfile"),
    ]
    vector_search = VectorSearch(
        algorithms=[HnswAlgorithmConfiguration(name="myHnsw")],
        profiles=[VectorSearchProfile(name="myProfile", algorithm_configuration_name="myHnsw")]
    )
    idx_client.create_or_update_index(SearchIndex(name=os.getenv("AZURE_SEARCH_INDEX"), fields=fields, vector_search=vector_search))

def get_embedding(text: str) -> list[float]:
    client = get_embedding_client()
    response = client.embeddings.create(input=text, model=os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT"))
    return response.data[0].embedding

def index_chunks(chunks: list[str], filename: str):
    search_client = get_search_client()
    docs = [{"id": str(uuid.uuid4()), "content": chunk, "filename": filename, "embedding": get_embedding(chunk)} for chunk in chunks]
    search_client.upload_documents(docs)

def hybrid_search(query: str, top_k: int = 5) -> list[str]:
    search_client = get_search_client()
    q_embedding = get_embedding(query)
    results = search_client.search(
        search_text=query,
        vector_queries=[VectorizedQuery(vector=q_embedding, k_nearest_neighbors=top_k, fields="embedding")],
        top=top_k
    )
    return [r["content"] for r in results]