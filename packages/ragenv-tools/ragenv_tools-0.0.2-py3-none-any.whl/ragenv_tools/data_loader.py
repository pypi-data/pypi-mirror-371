import pymysql
import pandas as pd
from .utils import load_config


class LoaderBase:
    def __init__(self, config: str | dict | None = None):
        if config is None:
            self.config = load_config("config.json")
        elif isinstance(config, str) and str(config).endswith('.json'):
            self.config = load_config(config)
        elif isinstance(config, dict):
            self.config = config
        else:
            raise Exception('No Valid config. Please Reset.')

    def get_db_connect(self, db_type):
        """
        连接数据库 
        db_type in ['report', 'news']
        """
        try:
            target_config = self.config['database_config'][db_type]
            conn = pymysql.connect(
                host=target_config['host'],
                user=target_config['user'],
                password=target_config['password'],
                database=target_config['database'],
                port=target_config['port'],
                charset='utf8'
            )
            print(f"{db_type}数据库连接成功")
            return conn
        except Exception as e:
            raise Exception(f"{db_type}数据库连接失败: {str(e)}")

    @staticmethod
    def _filter_repetitive_titles(df: pd.DataFrame) -> pd.DataFrame:
        """过滤包含重复字符的标题"""
        def _has_repetitive_chars(text: str, min_repeat: int = 6) -> bool:
            """检查文本是否包含重复字符"""
            if not text:
                return False
            
            for i in range(len(text) - min_repeat + 1):
                if text[i] * min_repeat in text:
                    return True
            return False
        df = df.loc[~df['title'].apply(_has_repetitive_chars), :]
        return df

    @staticmethod
    def _remove_duplicates(df: pd.DataFrame) -> pd.DataFrame:
        """去除重复研报"""
        df = df.drop_duplicates(subset=['title'], keep='first')
        return df

    @staticmethod
    def _remove_irrelevance(df: pd.DataFrame) -> pd.DataFrame:
        """主要剔除新闻中明显无关的内容"""
        negative_list = ['尚未开展', '暂无产品', '不涉及', '尚未涉及', '暂未涉及', '不提供', '尚未提供', '暂未提供']
        df = df.loc[~df['title'].str.contains('|'.join(negative_list)), :]
        return df

    def get_sql_query(self, query, db_type):
        conn = self.get_db_connect(db_type)
        data = pd.read_sql(query, conn)
        return data

    def load_content(self, start_date, end_date, limit, keyword_list, brokers_list):
        pass

    def format_content(self, content_df):
        pass


class ReportLoader(LoaderBase):
    def __init__(self, config):
        super().__init__(config)

    def load_content(
        self, 
        start_date, 
        end_date, 
        load_num = None, 
        keyword_list = [],
        source_list = [],
        other_conditions = ''
    ):
        """从研报数据库加载研报，支持按天数或日期范围，以及券商和关键词筛选"""
        try:
            conn = self.get_db_connect('report')
            sql_query = f"""SELECT * FROM report_info WHERE infopubldate BETWEEN '{start_date}' AND '{end_date}' """            
            # 添加券商筛选条件
            if len(source_list) > 0:
                placeholders = '|'.join(source_list)
                sql_query += f" AND organization REGEXP '{placeholders}'"
            # 添加关键词筛选条件
            if len(keyword_list) > 0:
                placeholders = ' '.join([i+"*" for i in keyword_list])
                sql_query += f" AND MATCH(infotitle, abstract) AGAINST('{placeholders}' IN BOOLEAN MODE)"
            sql_query += " AND classification NOT REGEXP '商品期货|金融期货|债券研究|投资组合|期权研究'"
            sql_query += other_conditions
            if load_num:
                sql_query += f" LIMIT {load_num}"

            df = pd.read_sql(sql_query, conn)
            conn.close()
            if df.empty:
                print("未找到研报数据")
                return pd.DataFrame()
            print(f"从研报数据库加载了 {len(df)} 条研报")

            return df
        except Exception as e:
            raise Exception(f"从研报数据库加载研报失败: {str(e)}")

    @staticmethod
    def format_content(df):
        col_name_dict = {
            'id': 'id',
            'infopubldate': 'date',
            'organization': 'source',
            'researchers': 'author',
            'infotitle': 'title',
            'abstract': 'abstract',
            'content': 'content',
            'stocks': 'stocks',
        }
        df = df.rename(columns=col_name_dict)
        df = df.loc[:, list(col_name_dict.values())]
        # 组合标题、摘要和内容作为搜索文本
        df['content'] = df['title'].fillna("") + '\n' + df['abstract'].fillna("") # + '\n' + df['content'].fillna("")
        return df


class NewsLoader(LoaderBase):
    def __init__(self, config):
        super().__init__(config)

    def load_content(
        self, 
        start_date, 
        end_date,
        load_num = None,
        keyword_list = [],
        source_list = [],
        other_conditions = ''
    ):
        """从数据库加载新闻，支持按天数或日期范围"""
        try:
            conn = self.get_db_connect('news')
            sql_query = f"""
            SELECT news_code, info_date, source_name, author,
                 orig_title, abstract, full_content, stocks
            FROM news_info 
            WHERE info_date BETWEEN '{start_date}' AND '{end_date}'
            """
            if len(keyword_list) > 0:
                placeholders = ' '.join([i+"*" for i in keyword_list])
                sql_query += f" AND MATCH(orig_title, full_content) AGAINST('{placeholders}' IN BOOLEAN MODE)"
            sql_query += " AND orig_title NOT REGEXP '两融余额|盘中异动|基金|资金净流|ETF|期货|速览|涨停雷达' AND author <> '港美智能写手' AND source_name <> '同花顺期货通'"
            sql_query += other_conditions
            if load_num:
                sql_query += f" LIMIT {load_num}"

            df = pd.read_sql(sql_query, conn)
            conn.close()
            if df.empty:
                print("未找到新闻数据")
                return pd.DataFrame()
            print(f"从数据库加载了 {len(df)} 条新闻")
            return df
        except Exception as e:
            raise Exception(f"从数据库加载新闻失败: {str(e)}")

    @staticmethod
    def format_content(df):
        col_name_dict = {
            'news_code': 'id',
            'info_date': 'date',
            'source_name': 'source',
            'author': 'author',
            'orig_title': 'title',
            'abstract': 'abstract',
            'full_content': 'content',
            'stocks': 'stocks'
        }
        df = df.rename(columns=col_name_dict)
        df = df.loc[:, list(col_name_dict.values())]
        # 组合标题、摘要和内容作为搜索文本
        df['content'] = df['title'].fillna("") + '\n' + df['abstract'].fillna("") + '\n' + df['content'].fillna("")
        return df


class DataLoader:
    def __init__(self, config, db_type):
        self.config = config
        if db_type == 'news':
            self.loader = NewsLoader(self.config)
        elif db_type == 'report':
            self.loader = ReportLoader(self.config)
        else:
            raise Exception(f'Wrong Database type: {db_type}')

    def loader_main(self, start_date, end_date, **params):
        """
        返回的DataFrame包含标准化格式：
            columns=['id', 'date', 'source', 'author', 'title', 'abstract', 'content', 'stocks']
        """
        df = self.loader.load_content(start_date, end_date, **params)
        df = self.loader.format_content(df)
        origin_num = len(df)
        # 数据预处理
        df = self.loader._filter_repetitive_titles(df)
        df = self.loader._remove_duplicates(df)
        df = self.loader._remove_irrelevance(df)
        df = df.reset_index(drop=True)
        remain_num = len(df)
        if df.empty:
            print("预处理后没有研报数据")
            return
        # 保存研报数据
        print(f"去重后保留 {remain_num} 条文本，去重 {origin_num - remain_num} 条")
        return df