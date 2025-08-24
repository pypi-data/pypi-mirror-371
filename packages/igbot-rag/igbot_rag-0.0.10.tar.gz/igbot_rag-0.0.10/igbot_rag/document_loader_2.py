# memory_langchain_loader_strict.py
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Iterable
import io
import os

from langchain_core.documents import Document
from langchain_community.document_loaders import UnstructuredFileIOLoader
# file_loader.py
import os
from pathlib import Path
from typing import List, Optional


@dataclass
class InMemoryFile:
    name: str                 # np. "plik.pdf"
    data: bytes               # zawartość pliku
    mime: Optional[str] = None
    metadata: Dict = field(default_factory=dict)


ALLOWED_EXTS = {"pdf", "txt", "docx", "csv", "md"}
# mapowanie na 'file_type' unstructured (dla I/O loadera)
UNSTRUCTURED_TYPES = {
    "pdf": "pdf",
    "docx": "docx",
    "csv": "csv",
    "md": "md",
}

def load_docs_from_memory_strict(
    files: Iterable[InMemoryFile],
    *,
    add_source_metadata: bool = True,
) -> List[Document]:
    """
    Ładuje dokumenty z pamięci (bytes) bez chunkowania.
    Dozwolone rozszerzenia: PDF, TXT, DOCX, CSV, MD.
    Reszta -> ValueError.
    Zwraca listę Document (dla PDF/DOCX/MD/CSV unstructured może zwrócić wiele).
    """
    out: List[Document] = []

    for f in files:
        name = f.name or "uploaded"
        ext = os.path.splitext(name)[1].lstrip(".").lower()

        if ext not in ALLOWED_EXTS:
            raise ValueError(
                f"Nieobsługiwane rozszerzenie: .{ext}. Dozwolone: {sorted(ALLOWED_EXTS)}"
            )

        # TXT wczytujemy bez parsera (jeden Document na plik)
        if ext == "txt":
            try:
                text = f.data.decode("utf-8", errors="replace")
            except Exception:
                text = f.data.decode("latin-1", errors="replace")
            meta = {**(f.metadata or {})}
            if add_source_metadata:
                meta.update({"source": name, "file_name": name})
            out.append(Document(page_content=text, metadata=meta))
            continue

        # Pozostałe (PDF, DOCX, CSV, MD) przez UnstructuredFileIOLoader z BytesIO
        file_type = UNSTRUCTURED_TYPES[ext]
        bio = io.BytesIO(f.data)
        loader = UnstructuredFileIOLoader(file=bio, file_type=file_type, metadata=(f.metadata or {}))
        docs = loader.load()

        if add_source_metadata:
            for d in docs:
                d.metadata = {**d.metadata, "source": name, "file_name": name}

        out.extend(docs)

    return out


# Async wariant (uruchomienie w executorze; dalej bez chunkowania)
import asyncio
def _sync_wrapper(args):
    return load_docs_from_memory_strict(**args)

async def aload_docs_from_memory_strict(**kwargs) -> List[Document]:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _sync_wrapper, kwargs)



def load_files_from_folder(
    folder_path: str | Path,
    *,
    recursive: bool = True,
    include_hidden: bool = False,
) -> List[InMemoryFile]:
    """
    Ładuje pliki z podanego folderu do listy InMemoryFile.
    Obsługiwane rozszerzenia: PDF, TXT, DOCX, CSV, MD.
    """
    folder = Path(folder_path)
    if not folder.exists() or not folder.is_dir():
        raise ValueError(f"Ścieżka {folder} nie istnieje albo nie jest folderem")

    in_memory_files: List[InMemoryFile] = []
    for root, dirs, files in os.walk(folder):
        if not include_hidden:
            # pomiń ukryte katalogi
            dirs[:] = [d for d in dirs if not d.startswith(".")]

        for fname in files:
            if not include_hidden and fname.startswith("."):
                continue

            ext = Path(fname).suffix.lstrip(".").lower()
            if ext not in ALLOWED_EXTS:
                continue  # ignoruj nieobsługiwane pliki

            fpath = Path(root) / fname
            with open(fpath, "rb") as f:
                data = f.read()

            in_memory_files.append(InMemoryFile(name=fname, data=data))

        if not recursive:
            break

    return in_memory_files
