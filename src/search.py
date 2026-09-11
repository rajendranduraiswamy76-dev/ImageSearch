"""Text-to-image and image-to-image similarity search over the vector index."""


def _resolve(results, metadata_store):
    resolved = []
    for photo_id, score in results:
        path = metadata_store.get_path_by_id(photo_id)
        if path:
            resolved.append((path, score))
    return resolved


def text_search(query, embedder, index_store, metadata_store, top_k=20):
    vector = embedder.encode_text(query)
    return _resolve(index_store.search(vector, top_k), metadata_store)


def image_search(image_path, embedder, index_store, metadata_store, top_k=20):
    vector = embedder.encode_image(image_path)
    return _resolve(index_store.search(vector, top_k), metadata_store)
