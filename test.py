from qdrant_client import QdrantClient
from config.settings import settings

client = QdrantClient(
    url=settings.qdrant_url,
    api_key=settings.qdrant_api_key,
    timeout=30,
    # check_compatibility=False,
)

print("URL:", settings.qdrant_url)
print("API key:", bool(settings.qdrant_api_key))

result = client.get_collections()

print(result)