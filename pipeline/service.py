from .model import db, Graph, Vertex, Edge
from .utils import get_logger
from .config import LOGS_DIR
from functools import wraps

logger = get_logger(__name__, '{}/{}.log'.format(LOGS_DIR, __name__))


# 事务装饰器
def transaction(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            ret = fn(*args, **kwargs)
            db.session.commit()
            return ret
        except Exception as e:
            db.session.rollback()
    return wrapper


# 创建DAG
@transaction
def create_graph(name, desc=None):
    graph = Graph()
    graph.name = name
    graph.desc = desc
    db.session.add(graph)
    return graph


# 为DAG增加顶点
@transaction
def add_vertex(graph: Graph, name: str, script: str = None, in_put: str = None):
    vertex = Vertex()
    vertex.graph_id = graph.id
    vertex.name = name
    vertex.script = script
    vertex.input = in_put
    db.session.add(vertex)
    return vertex


# 为DAG增加边
@transaction
def add_edge(graph: Graph, tail: Vertex, head: Vertex):
    edge = Edge()
    edge.graph_id = graph.id
    edge.tail = tail.id
    edge.head = head.id
    db.session.add(edge)
    return edge


# 删除顶点
@transaction
def del_vertex(v_id):
    query = db.session.query(Vertex).filter(Vertex.id == v_id)
    v = query.first()
    if v:  # 如果找到该顶点
        # 去删除顶点对应的边
        db.session.query(Edge).filter((Edge.tail == v.id) | (Edge.head == v.id)).delete()  # 实际业务不应该真删除，使用增加字段做标识
        # 再删除顶点
        query.delete()
    return v




