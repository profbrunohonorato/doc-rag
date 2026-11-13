import hashlib
import chromadb


class ChromaDBVectorStore:
    def __init__(self, path, embedding_model):
        self.client = chromadb.PersistentClient(path=path)
        # Cada modelo tem seu índice; nunca misturar espaços vetoriais.
        name = 'documents-' + hashlib.sha256(embedding_model.encode()).hexdigest()[:16]
        self.collection = self.client.get_or_create_collection(name, metadata={'hnsw:space': 'cosine'})

    def delete(self, document_id):
        self.collection.delete(where={'document_id': document_id})

    def replace(self, document_id, chunks, embeddings):
        self.delete(document_id)
        for start in range(0, len(chunks), 64):
            batch = chunks[start:start + 64]
            self.collection.add(ids=[f'{document_id}:{start+i}' for i in range(len(batch))],
                documents=[c['text'] for c in batch], embeddings=embeddings[start:start + 64],
                metadatas=[{'document_id': document_id, 'name': c['name'], 'page': c['page']} for c in batch])

    def search(self, embedding, limit):
        count = self.collection.count()
        if not count:
            return []
        result = self.collection.query(query_embeddings=[embedding], n_results=min(count, limit))
        return [dict(meta, text=text, score=round(1 - distance, 4))
                for meta, text, distance in zip(result['metadatas'][0], result['documents'][0],
                                               result['distances'][0])]
