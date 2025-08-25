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


def createVDB(db_type="", path="", port=0, url="", **kwargs):
    if db_type.lower() == "chroma":
        return ChromaVDB(path, port, url, **kwargs)
    else:
        raise ValueError(f"unsuported db type : {db_type}")




class AgentRAG(Agent):
    def __init__(self , db_type ,model_name="gemma3:1b", embaded="" , path="",port=0, url=""):
        self.db_type = db_type
        self.embad = embaded
        self.vdb = createVDB(db_type,path=path , port=port,url=url )
        self.embad_agent = EmbadedAgent(modelName="numited_text")# اسم دقیق مدل رو نمیدونستم
        self.agent = Agent("" , model_name )
    def add_text(self , text , token_count=0):
        chunked = text.split(".")
        for id,item in enumerate(chunked):
            vector = ""
            count = 0
            print(chunked)
            print(item)
            print(id)
            vector += item + "."
            count+=1
            current_time = datetime.now().isoformat()
            metadata = {"timestamp": current_time , "token_count" : len(vector.split(" ")) , "sentence_count" : count}
            if len(vector.split(" ")) >= token_count :
                embeddings = self.embad_agent.embaded(text)
                self.vdb.add_vector(id=id , vector=embeddings , doc=vector , meta_data=metadata)
                count = 0
                vector = ""
    def text_find(self,text,prompt):
        intent_prompt = (
            "Analyze the following text and return ONLY the user's main intent in English, "
            "as a single short phrase without any extra words, explanations, or formatting.\n"
            f"User text: {text}"
        )
        intent = self.agent.message(intent_prompt)
        embedding = self.embad_agent.embaded(intent)
        query = self.vdb.query(query_vector=embedding)
        result_prompt = (
            "i will give you some word and a prompt and you should to do that prompt and give result just in prompt s answer "
            f"words:{query} , prompt : {prompt}"
        )
        result = self.agent.message(result_prompt)
        return result
        
            

    
ids = ["id1", "id2", "id3"]
embeddings = [[1.1, 2.3, 3.2], [4.5, 6.9, 4.4], [1.1, 2.3, 3.2]]
documents = ["doc1", "doc2", "doc3"]
metadatas = [
    {"chapter": 3, "verse": 16},
    {"chapter": 3, "verse": 5},
    {"chapter": 29, "verse": 11},
]

agent = AgentRAG(path = "/data" , db_type="chroma")
agent.add_text("i like cake.im going to school.im a baker")
print(agent.text_find("i need to buy a cake" , prompt= "is that correct ? i dont need to buy cake"))
