from typing import Any
from abc import ABC, abstractmethod
# import chromadb


class Base_VDB(ABC):
    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def add_vector(
        self,
        vector: list[int],
        meta: dict[str, Any],
        docs: str,
        data_id=None,
    ):
        pass

    def query(self, query_vector, top_k=5):
        pass

    @abstractmethod
    def delete(self, ids):
        pass

    def save(self):
        pass

    def load(self):
        pass


# class ChromaVDB(Base_VDB):
#     def __init__(self, path="", port=0, url=""):
#         if url == "" and port == 0:
#             self.client = chromadb.PersistentClient(path=path)
#         elif path == "":
#             self.client = chromadb.HttpClient(host=url, port=port)
#         else:
#             print("please write one of path or url")
#         listC = self.client.list_collections()
#         count = len(listC)
#         self.collection = self.client.get_or_create_collection(
#             name=f"collection{count + 1}"
#         )

#     def add_vector(self, vector, doc, meta_data, id=None):
#         print(vector)
#         self.collection.add(
#             embeddings=[vector],
#             ids=[id] if isinstance(id, str) else id,
#             metadatas=[meta_data],
#             documents=[doc],
#         )

#     def query(self, query_vector, limit=1):
#         result = self.collection.query(query_embeddings=[query_vector], n_result=limit)
#         return result

#     def delete(self, ids):
#         self.collection.delete(ids=ids)

#     def save(self):
#         pass

#     def load(self):
#         pass


class CacheVDB(Base_VDB):
    def __init__(self):
        self.collection = {
            "ids": [],
            "embaddeds": {},
            "meta": {},
            "docs": {},
        }

    @property
    def count(self):
        return len(self.collection["ids"])

    def add_vector(
        self,
        vector: list[int],
        meta: dict[str, Any],
        docs: str,
        data_id=None,
    ):
        # if id is None create auto id
        if data_id is None:
            data_id = self.count + 1

        # set vector in RAM
        self.collection["ids"].append(data_id)
        self.collection["embaddeds"][data_id] = vector
        self.collection["meta"][data_id] = meta
        self.collection["docs"][data_id] = docs

    def delete(self, ids):
        for data_id in ids:
            del self.collection[data_id]
