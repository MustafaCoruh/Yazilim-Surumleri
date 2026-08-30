from pathlib import Path
from zipfile import ZipFile

from dokumanlar.docx_olustur import create_docx


def test_word_documents_can_be_generated(tmp_path):
    sources = (
        "dokumanlar/PROJE_TEKNIK_DOKUMANI.md",
        "dokumanlar/KULLANIM_KILAVUZU.md",
    )
    for index, source in enumerate(sources):
        destination = tmp_path / f"document-{index}.docx"
        create_docx(markdown=Path(source), destination=destination)
        with ZipFile(destination) as archive:
            assert archive.testzip() is None
            document = archive.read("word/document.xml").decode("utf-8")
        assert "Sürüm İstasyonu" in document
        assert document.count("<w:p>") > 100
