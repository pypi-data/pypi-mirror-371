import requests
import math


class EmbadedAgent:
    def __init__(
        self,
        modelName: str,
        baseUrl="http://localhost:11434",
    ):
        self.modelName = modelName
        self.baseUrl = baseUrl

    def embaded(self, text: str):
        """
        this function return embaded data of text

        Args:
            text (str): input text

        Returns:
            list[float]: embaded data
        """
        response = requests.post(
            url=f"{self.baseUrl}/api/embeddings",
            json={
                "model": self.modelName,
                "prompt": text,
            },
        )

        if response.status_code != 200:
            raise RuntimeError(
                f"Failed to get embedding: {response.status_code} - {response.text}"
            )

        return response.json()["embedding"]

    def cosine_similarity(self, vec1: list[float], vec2: list[float]) -> float:
        if len(vec1) != len(vec2):
            raise ValueError("vectors not have same lenght")

        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        norm1 = math.sqrt(sum(a * a for a in vec1))
        norm2 = math.sqrt(sum(b * b for b in vec2))

        if norm1 == 0.0 or norm2 == 0.0:
            return 0.0  # اگر یکی از بردارها تهی باشه، تشابه صفره

        return dot_product / (norm1 * norm2)

    def optionsSimScore(self, text: str, options: dict[str, str]) -> dict[str, float]:
        """
        calc score of each option in simulatary on text

        Args:
            text (str): main text;
            options (dict[str, str]): key is select option and value is description

        Returns:
            dict[str, float]: key option and simulatary to text
        """

        result = {}
        embedded_text = self.embaded(text)

        for opt, desc in options.items():
            embedded_option = self.embaded(desc)
            result[opt] = self.cosine_similarity(embedded_text, embedded_option)

        return result
