from abc import ABC, abstractmethod
import chromadb
from agent import Agent
from embaded_temp import EmbadedAgent
from datetime import datetime


class Base_VDB(ABC):
    @abstractmethod
    def __init__(self, path="", port=0, url=""):
        pass

    @abstractmethod
    def add_vector(self, vector, id=None):
        pass

    @abstractmethod
    def query(self, query_vector, top_k=5):
        pass

    @abstractmethod
    def delete(self, ids):
        pass

    @abstractmethod
    def save(self):
        pass

    @abstractmethod
    def load(self):
        pass


class ChromaVDB(Base_VDB):
    def __init__(self, path="", port=0, url=""):
        if url == "" and port == 0:
            self.client = chromadb.PersistentClient(path=path)
        elif path == "":
            self.client = chromadb.HttpClient(host=url, port=port)
        else:
            print("please write one of path or url")
        listC = self.client.list_collections()
        count = len(listC)
        self.collection = self.client.create_collection(name=f"collection{count + 1}")

    def add_vector(self, vector, doc, meta_data, id=None):
        self.collection.add(
            embeddings=vector,
            ids=[id] if isinstance(id, str) else id,
            metadatas=meta_data,
            documents=doc,
        )

    def query(self, query_vector, top_k=5):
        result = self.collection.query(query_embeddings=[query_vector], n_result=top_k)
        return result

    def delete(self, ids):
        self.collection.delete(ids=ids)

    def save(self):
        pass

    def load(self):
        pass


class AgentRAG(Agent):
    def __init__(self, model_name, vdb, system_prompt=""):
        self.vdb: Base_VDB = vdb
        self.agent = Agent(system_prompt, model_name)
        self.embed_agent = EmbadedAgent(modelName="numited_text")

    def add_chunk(self, chunk, metadata):
        metadata = {"timestamp": datetime.now().isoformat(), **metadata}
        vector = self.embed_agent.embaded(chunk)
        self.vdb.add_vector(id=id, vector=vector, doc=chunk, meta_data=metadata)

    def text_find(self, text, prompt):
        intent_prompt = (
            "Analyze the following text and return ONLY the user's main intent in English, "
            "as a single short phrase without any extra words, explanations, or formatting.\n"
            f"User text: {text}"
        )
        intent = self.agent.message(intent_prompt)
        embedding = self.embed_agent.embaded(intent)
        query = self.vdb.query(query_vector=embedding)
        result_prompt = (
            "i will give you some word and a prompt and you should to do that prompt and give result just in prompt s answer "
            f"words:{query} , prompt : {prompt}"
        )
        result = self.agent.message(result_prompt)
        return result
