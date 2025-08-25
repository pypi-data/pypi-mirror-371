from __future__ import annotations
import numpy as np
from aaaai.agent import Agent
from datetime import datetime
from sentence_transformers import SentenceTransformer
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from aaaai.VDB import Base_VDB


class AgentRAG(Agent):
    def __init__(
        self,
        text_model_name: str,
        embedded_model_name: str,
        vdb: Base_VDB,
        system_prompt="",
    ):
        self.vdb = vdb
        self.agent = Agent(system_prompt, text_model_name)
        self.transformer = SentenceTransformer(embedded_model_name)

    def add_chunk(self, chunk, metadata=None):
        # check for meta data and overwrite for meta data
        if metadata is None:
            metadata = {}
        metadata = {"timestamp": datetime.now().isoformat(), **metadata}

        # add vector to db for response from database
        vector = self.transformer.encode(chunk)
        self.vdb.add_vector(vector=vector, meta=metadata, docs=chunk)

    def text_find(self, text, minimum_accept=0.8):
        # pre-proccesing
        input_vector = self.transformer.encode(text)
        vdb_vectors = np.array(list(self.vdb.collection["embaddeds"].values()))

        # check vectors similarity
        # it's 0 index cause we have one sentence to check
        sims = self.transformer.similarity(input_vector, vdb_vectors)[0]

        # check for similutari is greather than setting and filter that
        ids = [
            self.vdb.collection["ids"][index]
            for index, sim in enumerate(sims)
            if sim >= minimum_accept
        ]

        return ids

    def message(self, text):
        # find simular ids
        ids = self.text_find(text)

        # get data focs from VDB
        docs = [self.vdb.collection["docs"][data_id] for data_id in ids]

        # create prompt in XML format
        prompt = (
            "<system>according by knowladge just return RESPONSE of prompt</system>"
            f"<Knowladge>{', '.join(docs)}</Knowladge>",
            f"<prompt>{text}</prompt>",
        )

        # response from LLM
        return self.agent.message(prompt)
