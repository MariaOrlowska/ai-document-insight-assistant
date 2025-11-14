from config import AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT, AZURE_DOCUMENT_INTELLIGENCE_KEY
import os
import mimetypes
import binascii
import logging
import traceback
from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.core.exceptions import HttpResponseError
# local docx fallback
from docx import Document as DocxDocument

logging.basicConfig(level=logging.INFO)

def extract_text_from_doc(file_path: str) -> str:
    logging.info("extract_text_from_doc called with: %s", file_path)

    if not os.path.exists(file_path):
        raise ValueError(f"File not found: {file_path}")
    size = os.path.getsize(file_path)
    if size == 0:
        raise ValueError(f"File is empty: {file_path}")

    ext = os.path.splitext(file_path)[1].lower()
    mime_type, _ = mimetypes.guess_type(file_path)
    logging.info("File diagnostics - size: %d bytes, ext: %s, mime: %s", size, ext, mime_type)

    # read bytes for Azure call
    with open(file_path, "rb") as f:
        data = f.read(10 * 1024 * 1024)  # safeguard: read up to 10MB

    # normalize mime if unknown
    if not mime_type:
        if ext == ".pdf":
            mime_type = "application/pdf"
        elif ext == ".docx":
            mime_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        elif ext in (".png", ".jpg", ".jpeg", ".tiff", ".bmp"):
            mime_map = {".png":"image/png", ".jpg":"image/jpeg", ".jpeg":"image/jpeg", ".tiff":"image/tiff", ".bmp":"image/bmp"}
            mime_type = mime_map.get(ext)

    client = DocumentIntelligenceClient(endpoint=AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT, credential=AzureKeyCredential(AZURE_DOCUMENT_INTELLIGENCE_KEY))

    candidate_models = ["prebuilt-document", "prebuilt-layout", "prebuilt-read"]
    last_error = None
    for model_id in candidate_models:
        try:
            logging.info("Trying Azure model '%s' with content_type=%s", model_id, mime_type)
            poller = client.begin_analyze_document(model_id, body=data, content_type=mime_type)
            result = poller.result()

            # prefer top-level content
            top_content = getattr(result, "content", None)
            if top_content and top_content.strip():
                return top_content

            # aggregate pages/lines
            pages = getattr(result, "pages", None) or []
            collected = []
            for p in pages:
                # try common attributes
                for attr in ("content", "text"):
                    v = getattr(p, attr, None)
                    if v:
                        collected.append(v)
                        break
                else:
                    lines = getattr(p, "lines", None) or []
                    line_texts = []
                    for line in lines:
                        ln = getattr(line, "content", None) or getattr(line, "text", None)
                        if ln:
                            line_texts.append(ln)
                    if line_texts:
                        collected.append("\n".join(line_texts))
            if collected:
                return "\n\n".join(collected)

            last_error = RuntimeError("No textual content found in Azure analysis result.")
        except HttpResponseError as hre:
            logging.warning("Azure HttpResponseError for model %s: %s", model_id, getattr(hre, "message", str(hre)))
            last_error = hre
        except Exception as e:
            logging.error("Azure analysis unexpected error: %s\n%s", e, traceback.format_exc())
            last_error = e

    # FALLBACK for .docx using python-docx
    if ext == ".docx":
        try:
            logging.info("Azure failed — falling back to python-docx for .docx")
            doc = DocxDocument(file_path)
            paragraphs = [p.text.strip() for p in doc.paragraphs if p.text and p.text.strip()]
            if paragraphs:
                return "\n\n".join(paragraphs)
            logging.warning("python-docx found no paragraphs.")
        except Exception as e:
            logging.error("python-docx fallback error: %s", e)

    # final error
    msg = (
        "Document analysis failed. Possible causes:\n"
        "- file corrupted/unsupported (try a small PDF),\n"
        "- AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT is not a Document Intelligence resource,\n"
        "- or no prebuilt model available in this region/resource.\n"
    )
    if last_error:
        raise RuntimeError(msg + f" Last error: {type(last_error).__name__}: {last_error}") from last_error
    raise RuntimeError(msg)

