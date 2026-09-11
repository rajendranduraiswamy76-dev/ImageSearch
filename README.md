# Project 1 — Multi-Modal Image Search

Search your local photo library using natural language text queries or a
reference image, powered by CLIP (`SentenceTransformer('clip-ViT-B-32')`).

See also: [Specification](../docs/SPECIFICATION.md#project-1--multi-modal-image-search-01-multimodal-image-search) ·
[High-Level Design](../docs/HIGH_LEVEL_DESIGN.md#3-project-1--multi-modal-image-search-component-design)

## Folder Structure

```
01-multimodal-image-search/
├── config.yaml            # photo_dir, index/db paths, model name
├── requirements.txt
├── notebooks/
│   └── 01_clip_prototype_colab.ipynb   # Colab prototyping (model choice, tuning)
├── src/
│   ├── ingest.py           # scan photo_dir, detect new/changed files
│   ├── embed.py            # CLIP embedding generation
│   ├── index_store.py      # FAISS/ChromaDB wrapper
│   ├── metadata_store.py   # SQLite metadata schema + CRUD
│   ├── search.py           # text-to-image / image-to-image search
│   └── app.py              # Streamlit UI
├── data/                    # gitignored: sqlite db, vector index, thumbnails
└── tests/
```

## Status

Implemented:
- `src/ingest.py` — recursive photo scan + incremental hashing (only new/changed
  files are re-embedded).
- `src/embed.py` — `ClipEmbedder` wrapping `SentenceTransformer('clip-ViT-B-32')`.
- `src/index_store.py` — FAISS `IndexIDMap` wrapper keyed by SQLite photo id.
- `src/metadata_store.py` — SQLite table for path/hash/mtime/EXIF metadata.
- `src/search.py` — text-to-image and image-to-image top-K search.
- `src/app.py` — Streamlit UI: sidebar "Scan / Re-index library" + text/image
  search tabs.
- `notebooks/01_clip_prototype_colab.ipynb` — Colab prototype (mount Drive, embed a
  sample, build FAISS index, run text/image queries, plot thumbnail grid).
- `tests/test_ingest.py` — unit tests for file scanning/hashing.

Next steps:
1. Set `photo_dir` in `config.yaml` to your real local photo folder.
2. `pip install -r requirements.txt` and run the app (below).
3. Click "Scan / Re-index library" once to build the initial index.

## Local Setup

```powershell
cd 01-multimodal-image-search
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run src/app.py
```

Run tests:

```powershell
pytest tests/
```
