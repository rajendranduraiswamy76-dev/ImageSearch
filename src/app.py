"""Streamlit UI: index a local photo folder and search it by text or image."""
import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).parent))

from config import load_config
from embed import ClipEmbedder
from index_store import VectorIndexStore
from ingest import run_ingest
from metadata_store import MetadataStore
from search import image_search, text_search

st.set_page_config(page_title="Multi-Modal Image Search", layout="wide")

CONFIG_PATH = Path(__file__).parent.parent / "config.yaml"


@st.cache_resource
def load_resources():
    config = load_config(CONFIG_PATH)
    embedder = ClipEmbedder(config["model_name"])
    metadata_store = MetadataStore(config["sqlite_path"])
    index_store = VectorIndexStore(config["vector_index_path"])
    return config, embedder, metadata_store, index_store


config, embedder, metadata_store, index_store = load_resources()

st.title("Multi-Modal Image Search")

with st.sidebar:
    st.header("Library")
    st.write(f"Photo folder: `{config['photo_dir']}`")
    st.write(f"Indexed photos: {len(index_store)}")

    if st.button("Scan / Re-index library"):
        progress = st.progress(0)
        status = st.empty()

        def on_progress(i, total, path):
            progress.progress(i / total if total else 1.0)
            status.write(f"{i}/{total}: {path.name}")

        count = run_ingest(config, metadata_store, index_store, embedder, on_progress)
        st.success(f"Indexed {count} new/changed photos.")
        st.rerun()

tab_text, tab_image = st.tabs(["Text search", "Image search"])


def render_results(results):
    cols = st.columns(4)
    for idx, (path, score) in enumerate(results):
        with cols[idx % 4]:
            st.image(path, caption=f"{score:.3f}", use_container_width=True)


with tab_text:
    query = st.text_input("Describe the photo you're looking for")
    top_k = st.slider("Results", 1, 50, config.get("top_k", 20), key="text_top_k")
    if query:
        render_results(text_search(query, embedder, index_store, metadata_store, top_k))

with tab_image:
    uploaded = st.file_uploader("Upload a reference photo", type=["jpg", "jpeg", "png", "bmp", "webp"])
    top_k_img = st.slider("Results", 1, 50, config.get("top_k", 20), key="image_top_k")
    if uploaded:
        tmp_path = Path(config["data_dir"]) / f"_query_{uploaded.name}"
        tmp_path.write_bytes(uploaded.getvalue())
        st.image(str(tmp_path), caption="Reference image", width=200)
        render_results(image_search(tmp_path, embedder, index_store, metadata_store, top_k_img))
