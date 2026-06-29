from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import AnalyzeDocumentRequest
from azure.core.credentials import AzureKeyCredential
import os

def extract_text(blob_url: str) -> list[str]:
    client = DocumentIntelligenceClient(
        endpoint=os.getenv("AZURE_DOC_INTEL_ENDPOINT"),
        credential=AzureKeyCredential(os.getenv("AZURE_DOC_INTEL_KEY"))
    )
    poller = client.begin_analyze_document(
        "prebuilt-layout",
        AnalyzeDocumentRequest(url_source=blob_url)
    )
    result = poller.result()
    chunks = []
    for page in result.pages:
        text = " ".join([
            line.content for line in (page.lines or [])
        ])
        if text.strip():
            chunks.append(text)
    return chunks