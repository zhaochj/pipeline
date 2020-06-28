from .model import db, Graph, Vertex, Edge
from .utils import get_logger
from .config import LOGS_DIR
from functools import wraps
import json

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
            raise e
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
def add_vertex(graph: Graph, name: str, in_put: str = None, script: str = None):
    vertex = Vertex()
    vertex.graph_id = graph.id
    vertex.name = name
    vertex.input = in_put
    vertex.script = script
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


def test_create_dag():
    try:
        # 创建DAG
        g = create_graph('test1')  # 返回一个Graph对象

        # 增加顶点
        in_put = """
        {
            "ip":{
                "type": "str",
                "required": true,
                "default":"192.168.0.100"
            }
        }
        """
        script = {
            "script":"echo test1.A",
            "next": "B"
        }  # script中next表示下一节点，可以是下一节点的id，也可以是名称

        a = add_vertex(g, 'A', None, json.dumps(script))
        b = add_vertex(g, 'B', None, 'echo B')
        c = add_vertex(g, 'C', None, 'echo C')
        d = add_vertex(g, 'D', None, 'echo D')

        # 增加边
        ab = add_edge(g, a, b)
        ac = add_edge(g, a, c)
        cb = add_edge(g, c, b)
        bd = add_edge(g, b, d)

        # 创建一个环图
        g = create_graph('test2')
        # 增加顶点
        a = add_vertex(g, 'A', None, 'echo A')
        b = add_vertex(g, 'B', None, 'echo B')
        c = add_vertex(g, 'C', None, 'echo C')
        d = add_vertex(g, 'D', None, 'echo D')
        # 增加边，abc形成一个环
        ba = add_edge(g, b, a)
        ac = add_edge(g, a, c)
        cb = add_edge(g, c, b)
        bd = add_edge(g, b, d)

        # 创建多个终点的DAG
        g = create_graph('test3')
        # 增加顶点
        a = add_vertex(g, 'A', None, 'echo A')
        b = add_vertex(g, 'B', None, 'echo B')
        c = add_vertex(g, 'C', None, 'echo C')
        d = add_vertex(g, 'D', None, 'echo D')
        # 增加边
        ba = add_edge(g, b, a)
        ac = add_edge(g, a, c)
        bc = add_edge(g, b, c)
        bd = add_edge(g, b, d)

        # 创建一个有多个入口的DAG
        g = create_graph('test4')
        # 增加顶点
        a = add_vertex(g, 'A', None, 'echo A')
        b = add_vertex(g, 'B', None, 'echo B')
        c = add_vertex(g, 'C', None, 'echo C')
        d = add_vertex(g, 'D', None, 'echo D')
        # 增加边
        ab = add_edge(g, a, b)
        ac = add_edge(g, a, c)
        cb = add_edge(g, c, b)
        db = add_edge(g, d, b)
    except Exception as e:
        print(e)


def check_graph(graph: Graph) -> bool:
    """验证是否是一个合法的DAG"""
    # 在数据库中找出指定graph的所有顶点和边，存放在内存中进行遍历处理
    query = db.session.query(Vertex).filter(Vertex.graph_id == graph.id)
    vertexes = [vertex.id for vertex in query]  # 顶点的id列表
    query = db.session.query(Edge).filter(Edge.graph_id == graph.id)
    edges = [(edge.tail, edge.head) for edge in query]  # 边的弧尾弧头列表

    # vertexes: [1, 2, 3, 4]
    # edges: [(1, 2), (1, 3), (3, 2), (2, 4)]
    # 需要找入度为0的顶点，那顶点的id在边的head中找不到

    while True:
        for i, v in enumerate(vertexes):
            for _, h in edges:
                if v == h:  # 顶点有入度
                    break
            else:  # 没有break，说明遍历一遍边后，没有找到以该顶点作为弧头的边，即没有入度为0
                # 能进else中，说明该顶点入度为0，满足顶点删除条件
                vertexes.pop(i)

                # 找出以此顶点作为弧尾的边，需要删除
                ejs = []  # 记录需要删除边的索引
                for j, (t, _) in enumerate(edges):
                    if t == v:
                        ejs.append(j)

                for j in reversed(ejs):  # 循环删除一个列表中的元素，需要从后往前删除
                    edges.pop(j)
                break  # 一旦找到入度为0的顶点，删除以该顶点为出度的边及顶点，删除后再循环
        else:  # 遍历顶点，入度没有为0的顶点，检验不通过
            return False
        print(vertexes, edges)
        if len(vertexes) + len(edges) == 0:  # 最后vertexes和edges都是空列表时是一个合法的DAG
            try:
                graph = db.session.query(Graph).filter(Graph.id == graph.id).first()
                if graph:
                    graph.checked = 1
                db.session.add(graph)
                db.session.commit()
                return True
            except Exception as e:
                db.session.rollback()
                raise e












