from .model import db, Graph, Vertex, Edge
from .utils import get_logger
from .config import LOGS_DIR

logger = get_logger(__name__, '{}/{}.log'.format(LOGS_DIR, __name__))


# 创建DAG
def create_graph(name, desc=None):
    graph = Graph()
    graph.name = name
    graph.desc = desc
    db.session.add(graph)
    try:
        db.session.commit()
        return graph
    except Exception as e:
        db.session.rollback()


# 为DAG增加顶点
def add_vertex(graph: Graph, name: str, script: str = None, in_put: str = None):
    vertex = Vertex()
    vertex.graph_id = graph.id
    vertex.name = name
    vertex.script = script
    vertex.input = in_put
    db.session.add(vertex)
    try:
        db.session.commit()
        return vertex
    except Exception as e:
        db.session.rollback()


# 为DAG增加边
def add_edge(graph: Graph, tail: Vertex, head: Vertex):
    edge = Edge()
    edge.graph_id = graph.id
    edge.tail = tail.id
    edge.head = head.id
    db.session.add(edge)
    try:
        db.session.commit()
        return edge
    except Exception as e:
        db.session.rollback()


# 删除顶点
def del_vertex(v_id):
    query = db.session.query(Vertex).filter(Vertex.id == v_id)
    v = query.first()
    if v:  # 如果找到该顶点
        try:
            # 去删除顶点对应的边
            db.session.query(Edge).filter((Edge.tail == v.id) | (Edge.head == v.id)).delete()  # 实际业务不应该真删除，使用增加字段做标识
            # 再删除顶点
            query.delete()
            db.session.commit()
        except Exception as e:
            db.session.rollback()
    return v




