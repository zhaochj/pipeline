from sqlalchemy import Column, String, Integer, Text
from sqlalchemy import ForeignKey, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

from . import config

# 顶点状态
STATE_WAITING = 0
STATE_RUNNING = 1
STATE_SUCCEED = 2
STATE_FAILED = 3
STATE_FINISHED = 4


Base = declarative_base()


class Graph(Base):
    """
    图定义
    """
    __tablename__ = 'graph'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(48), nullable=False)
    desc = Column(String(200), nullable=True)

    # 一个图有哪些顶点，有哪些边
    vertexes = relationship('Vertex')
    edges = relationship('Edge')


class Vertex(Base):
    """
    顶点定义
    """
    __tablename__ = 'vertex'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(48), nullable=False)
    script = Column(Text, nullable=True)
    input = Column(Text, nullable=True)
    graph_id = Column(Integer, ForeignKey('graph.id'), nullable=False)

    # 一个顶点查属于哪个图
    graph = relationship('Graph')

    # 一个顶点有哪些弧头，弧尾
    tails = relationship('Edge', foreign_keys='Edge.tail')  # 可以写成 tails = relationship('Edge', Foreign_Key='[Edge.tail]')
    heads = relationship('Edge', foreign_keys='Edge.head')


class Edge(Base):
    """
    边定义
    """
    __tablename__ = 'edge'

    id = Column(Integer, primary_key=True, autoincrement=True)
    graph_id = Column(Integer, ForeignKey('graph.id'), nullable=False)
    tail = Column(Integer, ForeignKey('vertex.id'), nullable=False)
    head = Column(Integer, ForeignKey('vertex.id'), nullable=False)


class Pipeline(Base):
    """
    定义流程，根据图定义出一个个流程
    """
    __tablename__ = 'pipeline'

    id = Column(Integer, primary_key=True, autoincrement=True)
    graph_id = Column(Integer, ForeignKey('graph.id'), nullable=False)
    current_vertex_id = Column(Integer, ForeignKey('vertex.id'), nullable=False)
    state = Column(Integer, nullable=False, default=STATE_WAITING, comment='当前顶点的执行状态')

    # 当前运行的流程中的顶点属于哪个图，顶点的属性等
    graph = relationship('Graph')
    vertex = relationship('Vertex')


class Track(Base):
    """
    历史记录表
    """
    __tablename__ = 'track'

    id = Column(Integer, primary_key=True, autoincrement=True)
    input = Column(Text, nullable=True)
    output = Column(Text, nullable=True)
    state = Column(Integer, nullable=True, comment='当前流程中当前顶点执行的状态')
    pipeline_id = Column(Integer, ForeignKey('pipeline.id'), nullable=False)
    vertex_id = Column(Integer, ForeignKey('vertex.id'), nullable=False)

    # 通过外键可以查询到pipeline和vertex表中相应属性
    pipeline = relationship('Pipeline')
    vertex = relationship('Vertex')


class Single:
    """
    单例
    """
    _instance = None

    def __init__(self, cls):
        self.cls = cls

    def __call__(self, *args, **kwargs):
        if self._instance is None:
            self._instance = self.cls(*args, **kwargs)
        return self._instance


# 数据库引擎，会话封装
@Single   # DataBase = Single(DataBase)
class DataBase:
    def __init__(self, connection: str, **kwargs):
        self._engine = create_engine(connection, **kwargs)
        self._Session = sessionmaker(self._engine)
        self._session = self._Session()

    @property
    def session(self):
        return self._session

    @property
    def engine(self):
        return self._engine

    # 创建定义的所有表
    def create_all_tables(self):
        Base.metadata.create_all(self._engine)

    # 删除定义的所有表
    def drop_all_tables(self):
        Base.metadata.drop_all(self._engine)


db = DataBase(config.URL, echo=config.DATABASE_DEBUG)
