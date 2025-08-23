import warnings
warnings.filterwarnings("ignore")

import os
import re
import jieba
import pickle
import pandas as pd
import numpy as np
from datetime import datetime
from tqdm import tqdm
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from langchain.embeddings.base import Embeddings
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores.faiss import FAISS
from .utils import SuppressPrint, load_config

class RetrieverBase:
    def __init__(self, config: str | dict | None = None):
        """
        初始化索引基类
        
        Args:
            config: 配置字典
        """
        self.config = load_config(config)
        
        
    @staticmethod
    def unify_score(array: np.ndarray):
        array = (array - array.min()) / (array.max() - array.min())
        return array

    def build_index(self, content_df):
        pass

    def save_index(self, file_prefix):
        pass
    
    def load_index(self, file_prefix):
        pass

    def score_index(self, query):
        pass


class SparseRetriever(RetrieverBase):
    def __init__(self, config: dict):
        super().__init__(config)
        self.tfidf_vectorizer = None
        self.tfidf_matrix = None
        self.content_df = pd.DataFrame()
        self.score_dict = {}
        # 参数设置
        self.max_features = 10000
        self.ngram_range = (1,2)
        self.min_df = 2
        self.max_df = 0.8
        
    @staticmethod
    def _tokenize(text: str) -> list[str]:
        """使用结巴分词进行中文分词"""
        return list(jieba.cut(text))

    def build_index(self, content_df: pd.DataFrame):
        """构建TF-IDF索引"""
        self.content_df = content_df
        try:
            # 使用研报内容构建TF-IDF
            texts = content_df['content'].tolist()
            self.tfidf_vectorizer = TfidfVectorizer(
                tokenizer=self._tokenize,
                max_features= self.max_features,
                ngram_range=self.ngram_range,
                min_df=self.min_df,
                max_df=self.max_df
            )
            self.tfidf_matrix = self.tfidf_vectorizer.fit_transform(texts)
            print(f"TF-IDF索引构建完成")
        except Exception as e:
            print(f"构建TF-IDF索引失败: {str(e)}")
            raise

    def save_index(self, file_prefix):
        try:
            if (self.tfidf_vectorizer is not None) and (self.tfidf_matrix is not None):                
                # 只保存vectorizer参数、vocabulary、idf，参照新闻系统的方式
                tfidf_index = {
                    'tfidf_vectorizer': self.tfidf_vectorizer,
                    'tfidf_matrix': self.tfidf_matrix
                }
                
                tfidf_file = f"{file_prefix}-tfidf.pkl"
                tfidf_path = os.path.join(self.config["embed_config"]["index_save_path"], tfidf_file)
                with open(tfidf_path, 'wb') as f:
                    pickle.dump(tfidf_index, f)
                print("TF-IDF索引已保存")
        except Exception as e:
            print(f"TF-IDF索引保存失败: {str(e)}")
            raise

    def clean_index(self, file_prefix):
        tfidf_file = f"{file_prefix}-tfidf.pkl"
        file_list = [tfidf_file]
        for file in file_list:
            try:
                os.remove(os.path.join(self.config["embed_config"]["index_save_path"], file))
            except Exception as e:
                raise Exception(f'TF-IDF索引删除失败({file})：{str(e)}')
        print('TF-IDF索引删除成功')

    def load_index(self, file_prefix):
       # 加载TF-IDF索引
        try:
            tfidf_path = os.path.join(self.config["embed_config"]["index_save_path"], f"{file_prefix}-tfidf.pkl")                
            with open(tfidf_path, 'rb') as f:
                tfidf_index = pickle.load(f)
            self.tfidf_vectorizer = tfidf_index['tfidf_vectorizer']
            self.tfidf_matrix = tfidf_index['tfidf_matrix']
            print(f"TF-IDF索引加载成功")
        except Exception as e:
            raise Exception(f"TF-IDF索引加载失败。{e}")

    def score_index(self, query: str, **params) -> dict[int, float]:
        """TF-IDF搜索"""
        if self.tfidf_vectorizer is None:
            raise Exception('TF-IDF索引正确加载！请检查')

        query_vector = self.tfidf_vectorizer.transform([query])
        similarities = cosine_similarity(query_vector, self.tfidf_matrix).flatten()
        scores = self.unify_score(similarities)
        
        # 返回(索引, 分数)对，按分数降序排列
        score_dict = dict(zip(self.content_df['id'].tolist(), scores))
        self.score_dict['sparse_score'] = score_dict
        return score_dict


class DenseRetriever(RetrieverBase):
    def __init__(self, config: dict, embed_model):
        super().__init__(config)
        # 模型缩略名和实际信息对照表
        self.model_name_dict =  {
            'xiaobu': ("local", 'xiaobu-embedding-v2'),
            'bge-v1.5': ("siliconflow", "BAAI/bge-large-zh-v1.5"),
            'bge-m3': ("siliconflow", "Pro/BAAI/bge-m3")
        }
        # 参数配置
        self.embed_model = embed_model
        self.embeddings = self.get_embeddings()
        self.faiss_vs = None
        self.content_df = pd.DataFrame()
        self.score_dict = {}
        # 固定参数
        self.chunk_size = 512 # 文本分块时，每段的长度大小
        self.chunk_overlap = 32
        self.embedding_batch_size = 64
        
    @staticmethod
    def _normalize_text(text: str) -> str:
        """标准化文本，去除特殊字符和多余空格"""
        if not text:
            return ""
        text = re.sub(r'<[^>]+>', '', text)
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'[^\w\s\u4e00-\u9fff.,!?;:()（）]', '', text)
        return text.strip()

    @staticmethod
    def _chunk_text(text, chunk_size=512, chunk_overlap=0):
        """将文本分块，每块不超过chunk_size个token"""
        if not text:
            return [""]
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        text_list = text_splitter.split_text(text)
        return text_list

    def get_embeddings(self) -> Embeddings:
        """获取嵌入模型"""
        try:
            if self.embed_model == 'xiaobu':            
                from .my_embedding import LocalEmbedding
                platform, model_name = self.model_name_dict[self.embed_model]
                origin_info = self.config["embed_config"][platform]
                model_path = os.path.join(
                    origin_info["model_path"],
                    model_name
                )
                embedding = LocalEmbedding(model_path)
            else:
                from .my_embedding import APIEmbedding
                platform, model_name = self.model_name_dict[self.embed_model]
                origin_info = self.config["embed_config"][platform]
                embedding = APIEmbedding(
                    model_name=model_name,
                    base_url=origin_info["base_url"], 
                    api_key=origin_info["api_key"],
                )
            return embedding
        except Exception as e:
            print(f"加载{self.embed_model}模型失败: {str(e)}")
            raise

    def df_to_docs_list(self, df: pd.DataFrame, content_field="content", skip_columns=[]):
        """将DataFrame转换为Document列表"""
        skip_columns += [content_field] if content_field not in skip_columns else []
        docs = []
                
        for _, row in tqdm(df.iterrows(), total=len(df), desc="处理研报"):
            idx = row['id']
            content = str(row[content_field])
            # 标准化文本
            content = self._normalize_text(content)
            if not content:
                continue
            # 文本分块
            chunks = self._chunk_text(content, chunk_size=self.chunk_size, chunk_overlap=self.chunk_overlap)
            for chunk_idx, chunk in enumerate(chunks):
                if not chunk.strip():
                    continue
                # 构建metadata, 添加分块信息
                metadata = row.drop(skip_columns).to_dict()
                metadata['chunk_id'] = f"{idx}-{chunk_idx}"
                doc = Document(page_content=chunk, metadata=metadata)
                docs.append(doc)
        
        print(f"总共生成了 {len(docs)} 个文本块")
        return docs

    def build_index(self, content_df):
        """构建FAISS索引"""
        self.content_df = content_df
        docs_list = self.df_to_docs_list(content_df)  #  list[Document]
        try:
            start_time = datetime.now()
            batch_size = self.embedding_batch_size
            total_nums = len(docs_list)
            iters = tqdm(range(0, total_nums, batch_size))
            for start_idx in iters:
                iters.set_description("正在分批向量化")
                batch_idx = slice(start_idx, min(start_idx+batch_size, total_nums))
                docs_batch = docs_list[batch_idx]

                with SuppressPrint():
                    if start_idx == 0:
                        # 首批, 创建Faiss
                        faiss_vectorstore = FAISS.from_documents(docs_batch, self.embeddings)
                    else:
                        faiss_vectorstore.merge_from(FAISS.from_documents(docs_batch, self.embeddings))
                    self.faiss_vs = faiss_vectorstore
            print(f"faiss库构建完成，耗时 {(datetime.now() - start_time).seconds / 60:.2f} 分钟")
        except Exception as e:
            print(f"构建FAISS索引失败: {str(e)}")
            raise

    def save_index(self, save_path, file_prefix):
        # 保存FAISS索引和元数据
        try:
            if self.faiss_vs is not None:
                self.faiss_vs.save_local(save_path, file_prefix+'-faiss')
                print("FAISS索引已保存")
        except Exception as e:
            print(f"FAISS索引保存失败: {str(e)}")
            raise

    def clean_index(self, file_prefix):
        faiss_index_file = f"{file_prefix}-faiss.pkl"
        faiss_data_file = f"{file_prefix}-faiss.faiss"
        file_list = [faiss_index_file, faiss_data_file]
        for file in file_list:
            try:
                os.remove(os.path.join(self.config["embed_config"]["index_save_path"], file))
            except Exception as e:
                raise Exception(f'FAISS索引删除失败({file})：{str(e)}')    
        print('FAISS索引删除成功')

    def load_index(self, file_prefix):
        try:
            self.faiss_vs = FAISS.load_local(
                folder_path=self.config["embed_config"]["index_save_path"], 
                embeddings=self.embeddings,
                name=file_prefix+'-faiss'
            )
            print(f"FAISS索引加载成功")
        except Exception as e:
            raise Exception(f"FAISS索引加载失败。{e}")

    def score_index(self, query: str, **params) -> dict[int, float]:
        """Embedding搜索获取索引分数"""
        if self.faiss_vs is None:
            raise Exception('FAISS数据库未正确加载！请检查')

        docs_scores_list = self.faiss_vs.similarity_search_with_score(
            query=query,
            k=min(100, self.faiss_vs.index.ntotal),
            # TODO: 可以进一步添加过滤条件
        )
        
        unique_scores_dict = {}
        for doc, score in docs_scores_list:
            original_idx = str(doc.metadata['chunk_id'].split('-')[0])
            if original_idx not in unique_scores_dict:
                unique_scores_dict[original_idx] = score
            else:
                unique_scores_dict[original_idx] = max(score, unique_scores_dict[original_idx])
                                
        scores = self.unify_score(np.array(list(unique_scores_dict.values())))
        idxs = list(unique_scores_dict.keys())
        score_dict = dict(zip(idxs, scores))
        self.score_dict['dense_score'] = score_dict
        return score_dict


class HybridRetriever(RetrieverBase):
    def __init__(self, config: dict, embed_model: str, mode: str = 'full'):
        super().__init__(config)
        self.sparse_retriever = SparseRetriever(self.config)
        self.dense_retriever = DenseRetriever(self.config, embed_model)
        self.content_df = pd.DataFrame()
        self.score_dict = {}
        self.mode = mode #  'full' / 'fast'

    def build_index(self, content_df):
        self.content_df = content_df
        self.sparse_retriever.build_index(content_df)
        if self.mode != 'fast':
            self.dense_retriever.build_index(content_df)

    def save_index(self, file_prefix):
        self.sparse_retriever.save_index(file_prefix)
        if self.mode != 'fast':
            self.dense_retriever.save_index(file_prefix)

    def clean_index(self, file_prefix):
        self.sparse_retriever.clean_index(file_prefix)
        if self.mode != 'fast':
            self.dense_retriever.clean_index(file_prefix)

    def load_index(self, file_prefix):
        self.sparse_retriever.save_index(file_prefix)
        if self.mode != 'fast':
            self.dense_retriever.save_index(file_prefix)

    def score_index(self, query: str, weight: float, **params) -> dict[int, float]:
        """
        计算混合检索分数

        Args:
            query: 查询字符串
            weight: TF-IDF分数权重（float，0~1之间）

        Returns:
            list[tuple[int, float]]: 返回每个文档的索引及其混合分数
        """
        # query = ",".join(keywords)
        if self.mode == 'fast':
            weight = 1 # 强制修改
        print(f"TF-IDF权重: {weight:.2f}, Embedding权重: {1-weight:.2f}")

        if weight == 1:
            sparse_score = self.sparse_retriever.score_index(query)
            dense_score = {}
        elif weight == 0:
            sparse_score = {}
            dense_score = self.dense_retriever.score_index(query)
        elif 0 < weight < 1:
            sparse_score = self.sparse_retriever.score_index(query)
            dense_score = self.dense_retriever.score_index(query)
        else:
            raise Exception('Wrong Hybrid Retrieve Weight!')

        # 合并分数
        union_idxs = list(set(sparse_score.keys()).union(dense_score.keys()))
        hybrid_score = {}
        for idx in union_idxs:
            hybrid_score[idx] = sparse_score.get(idx, 0) * weight + dense_score.get(idx, 0) * (1 - weight)
        self.score_dict['sparse_score'] = sparse_score
        self.score_dict['dense_score'] = dense_score
        self.score_dict['hybrid_score'] = hybrid_score
        return hybrid_score


class DataRetriever:
    def __init__(self, config, method, **params):
        self.config = config
        self.method = method
        if self.method == 'sparse':
            self.retriever = SparseRetriever(config)
        elif self.method == 'dense':
            if 'embed_model' not in params:
                raise Exception('向量检索缺失Embedding模型名称，请重新设置。')
            self.retriever = DenseRetriever(config, **params)
        elif self.method == 'hybrid':
            if 'embed_model' not in params:
                raise Exception('混合检索缺失Embedding模型名称，请重新设置。')
            self.retriever = HybridRetriever(config, **params)
        else:
            raise Exception(f'错误的检索方法{method}，请重新指定。')
        self.db_type = ''  # 'news' / 'report'
        self.content_df = pd.DataFrame()

    def _check_index_exists(self, file_prefix):
        tfidf_file = f"{file_prefix}-tfidf.pkl"
        faiss_index_file = f"{file_prefix}-faiss.pkl"
        faiss_data_file = f"{file_prefix}-faiss.faiss"
        if self.method == 'sparse':
            check_list = [tfidf_file]
        elif self.method == 'dense':
            check_list = [faiss_index_file, faiss_data_file]
        elif self.method == 'hybrid':
            check_list = [tfidf_file, faiss_index_file, faiss_data_file]

        index_save_path = self.config["embed_config"]["index_save_path"]
        for file in check_list:
            file_path = os.path.join(index_save_path, file)
            if not os.path.exists(file_path):
                return False
        return True

    @staticmethod
    def filter_news_after_retrieve(
            news_list: list[dict], 
            exclude_keywords: list[str] = [],
            include_keywords: list[str] = []
        ) -> list[dict]:
        """
        过滤新闻，保留消息面内容，排除行情复盘和分析师观点
        Args:
            news_list: 新闻列表
            exclude_keywords: 排除关键词列表
            include_keywords: 包含关键词列表（优先级更高）
        """
        if len(exclude_keywords) == 0:
            exclude_keywords = [
                "行情", "复盘", "分析师", "观点", "预测", "走势", "技术面",
                "支撑位", "阻力位", "突破", "回调", "震荡", "趋势", "指标", "买入", "卖出", 
                "涨超", "跌超", "涨停", "跌停", "大涨", "大跌", "上涨", "下跌"]
        
        if len(include_keywords) == 0:
            include_keywords = [
                "政策", "公告", "发布", "消息", "新闻", "通知", "规定", "条例",
                "决议", "决定", "批准", "同意", "签署", "发布", "实施",
                "公司", "企业", "业绩", "财报", "营收", "利润"
            ]
        
        title_start_exclude = ["行情", "分析", "预测", "复盘", "走势"]
        
        filtered_news = []
        for news in news_list:
            title = str(news.get('title', '')).lower()
            content = str(news.get('content', '')).lower()
            # 检查是否包含包含关键词（优先级更高）。如果包含包含关键词，直接保留
            should_include = False
            for keyword in include_keywords:
                if keyword in title or keyword in content:
                    should_include = True
                    break
            if should_include:
                filtered_news.append(news)
                continue
            
            # 检查是否包含排除关键词。如果包含排除关键词，跳过
            should_exclude = False
            for keyword in exclude_keywords:
                if keyword in title or keyword in content:
                    should_exclude = True
                    break
            if should_exclude:
                continue
            
            # 检测数字密度（数字字符占总字符比例）
            digit_ratio = len(re.findall(r'\d', content)) / max(len(content), 1)
            if digit_ratio > 0.12:  # 从8%提高到12%，避免误删财务数据
                continue
            
            # 排除以特定词汇开头的标题
            if any(title.startswith(keyword) for keyword in title_start_exclude):
                continue
            
            # 保留其他内容
            filtered_news.append(news)
        
        print(f"新闻过滤完成：原始 {len(news_list)} 条，过滤后 {len(filtered_news)} 条")
        return filtered_news

    def prepare_index(self, db_type, content_df, file_prefix, force_rebuild=False):
        self.db_type = db_type
        self.content_df = content_df
        # 检查是否已有索引，若没有则新建，否则读取
        if force_rebuild or not self._check_index_exists(file_prefix):
            print(f'索引文件{file_prefix}不存在，新建中...')
            self.retriever.build_index(content_df)
            self.retriever.save_index(file_prefix)
        else:
            print(f"索引文件{file_prefix}已存在，加载中...")
            self.retriever.load_index(file_prefix)

    def filter_result(self, sorted_results, filter_num):
        if self.db_type == 'news':
            filtered_results = self.filter_news_after_retrieve(sorted_results)
            # 如果过滤后结果太少，适当放宽条件
            if len(filtered_results) < filter_num and len(sorted_results) > filter_num:
                print("过滤后结果较少，适当放宽过滤条件...")
                filtered_results = self.filter_news_after_retrieve(
                    sorted_results, 
                    exclude_keywords=["分析师", "观点", "预测"],  # 只排除最明显的
                )
            final_results = filtered_results[:filter_num]

        elif self.db_type == 'report':
            # 研报不需要过滤，直接取前top_k条
            final_results = sorted_results[:filter_num]
        return final_results

    def main_search(self, query, top_k, **params) -> list[dict]:
        if len(self.content_df) == 0:
            raise Exception('未加载有效索引，请检查prepare_index中的原始数据')
        try:
            if (self.method == 'hybrid') and ('weight' not in params):
                raise Exception('混合检索未指定加权权重，请检查输入参数。')
            final_scores = self.retriever.score_index(query, **params)

            score_term_name = f'{self.method}_score'
            full_results = []
            for idx, score in final_scores.items():
                content_info = self.content_df.loc[self.content_df["id"] == idx, :].iloc[0, :].to_dict()
                content_info[score_term_name] = score            
                full_results.append(content_info)
            sorted_results = sorted(full_results, key=lambda x: x[score_term_name], reverse=True)
            final_results = self.filter_result(sorted_results, top_k)
            return final_results
        except Exception as e:
            print(f"混合搜索失败: {str(e)}")
            return []