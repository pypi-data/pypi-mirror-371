from langchain.embeddings.base import Embeddings
from sentence_transformers import SentenceTransformer
from openai import OpenAI
from tqdm import tqdm
from datetime import datetime


class LocalEmbedding(Embeddings):
    def __init__(self, model_path: str,  device: str = 'cuda'):
        self.model = SentenceTransformer(model_path, device=device)

    def embed_documents_tqdm(self, texts: list) -> list:
        """
        输入的是一个文本段列表，有num段文本，返回的是一个[num, 1792]的向量
        采用了tqdm展示出执行的情况，但是这样会比较慢，因为是一个一个的encode，不是并行的，实测切分长度500时，10分钟内处理了15516条数据

        Args:
            texts: list of str

        Returns:
            list: list of embeddings with shape [num, 1792]
        """
        # 为了记录 encode 内部的处理过程，我们在这里分步进行
        embeddings = []

        start_time = datetime.now()
        for text in tqdm(texts):
            # Encode the individual text
            embedding = self.model.encode([text], normalize_embeddings=True)[0]
            embeddings.append(embedding)

        end_time = datetime.now()
        print(f"Encoding {len(texts)} texts took {end_time - start_time}.")

        return embeddings

    def embed_documents(self, texts: list):
        """
        输入的是一个文本段列表，有num段文本，返回的是一个[num, 1792]的向量

        这个版本是直接调用encode函数，返回[num, 1792]的向量，没有tqdm的执行时间统计，但是应该会更快，因为这样按道理是并行的。
        83092条数据，耗时耗时 2366.05 秒，接近40min。还是比串行的方法快了25%的
        Args:
            texts:

        Returns:

        """
        print(f'Encoding {len(texts)} texts...')
        start_time = datetime.now()

        # 这里的normalize_embeddings=True，是将向量归一化
        embeddings = self.model.encode(texts, normalize_embeddings=True)

        end_time = datetime.now()
        duration = end_time - start_time
        print(f'Finished encoding {len(texts)} texts in {duration}.')

        return embeddings

    def embed_query(self, text: str):
        """

        输入是一个句子的话，返回的是一个[1792] 的向量

        Args:
            text:

        Returns:

        """
        return self.model.encode(text, normalize_embeddings=True)


class APIEmbedding(Embeddings):
    def __init__(self, model_name: str, base_url: str, api_key: str):
        self.client = OpenAI(base_url=base_url, api_key=api_key)
        self.model = model_name

    def embed_documents(self, texts: list) -> list:
        reponse = self.client.embeddings.create(
            input=texts,
            model=self.model,
        )
        return [i.embedding for i in reponse.data]

    def embed_query(self, text: str) -> list:
        response = self.client.embeddings.create(
            input=text,
            model=self.model
        )
        return response.data[0].embedding