import logging
from pathlib import Path

from src.rag import INDEX_NAME, rag_pipeline
from src.utils import convert_document_to_md

logger = logging.getLogger(__name__)

docs_dir = r"C:\Users\andre\OneDrive\Рабочий стол\ДИО-Консалт\Внутренняя база знаний\Коммерческие предложения"


def main() -> None:
    for doc_path in Path(docs_dir).iterdir():
        logger.info("Start indexing document: `%s`", doc_path)
        doc_file = doc_path.read_bytes()
        md_text = convert_document_to_md(doc_file, file_extension=doc_path.suffix)
        rag_pipeline.indexing(
            text=md_text,
            metadata={"source": doc_path.name, "category": "Коммерческие предложения"}
        )


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
