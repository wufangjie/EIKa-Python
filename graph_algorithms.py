from collections import deque, defaultdict
import heapq
from copy import deepcopy
import itertools
import numpy as np
from utils import memo


class Graph():
    def __init__(self, G=None, weighted=None, guarantee_vertex=True):
        """NOTE: Always make sure every vertex in G.keys()"""
        self.G = {} if G is None else G
        if weighted is None:
            weighted = (bool(self.G)
                        and isinstance(next(iter(self.G.values())), dict))
        self.weighted = weighted
        if guarantee_vertex:
            self.add_no_outdegree_vertex()

    def copy(self):
        """Graph merely need deepcopy"""
        return Graph(deepcopy(self.G), self.weighted, False)

    @staticmethod
    def made_up_by_edges(edges):
        G = {}
        if edges and len(edges[0]) == 3:
            weighted = True
            for u, v, w in edges:
                for x in (u, v):
                    if x not in G:
                        G[x] = {}
                G[u][v] = w
        else:
            weighted = False
            for u, v in edges:
                for x in (u, v):
                    if x not in G:
                        G[x] = set()
                G[u].add(v)
        return Graph(G, weighted, False)

    @staticmethod
    def _add_reverse_edges(g, G):
        """NOTE: make sure there is no reverse edges!"""
        if g.weighted:
            for k, vs in g.G.items():
                for v, w in vs.items():
                    if w != G[v].get(k, w):
                        raise Exception(
                            'reverse edge conflict: {}, {}!'.format(k, v))
                    G[v][k] = w
        else:
            for k, vs in g.G.items():
                for v in vs:
                    G[v].add(k)

    @staticmethod
    def made_up_by_reverse_graph(g):
        typ = dict if g.weighted else set
        G_rev = {k: typ() for k in g.G}
        Graph._add_reverse_edges(g, G_rev)
        return Graph(G_rev, g.weighted, False)

    def add_reverse_edges(self):
        self._add_reverse_edges(self, self.G)

    def add_no_outdegree_vertex(self):
        to_add = {v for vs in self.G.values() for v in vs if v not in self.G}
        typ = dict if self.weighted else set
        for v in to_add:
            self.G[v] = typ()

    def bfs(self, s, visited=None): # visited=None is for traversal
        if visited is None:
            visited = set()
        queue = deque((s,))
        while queue:
            u = queue.popleft()
            if u not in visited:
                yield u
                visited.add(u)
                queue.extend(self.G[u]) # iterable is ok

    def dfs(self, s, visited=None):
        if visited is None:
            visited = set()
        stack = list((s,))
        while stack:
            u = stack.pop()
            if u not in visited:
                yield u
                visited.add(u)
                stack.extend(self.G[u])


#     def _get_dfs_rec_func(self, visited=None, mode='last'):
#         if visited is None:
#             visited = set()
#         global_ns = locals()
#         _dfs_rec_template = '''
# def _dfs(u):
#     if u not in visited:
#         {}
#         visited.add(u)
#         for v in self.G[u]:
#             yield from _dfs(v)
#         {}
#         '''
#         args = ('', 'yield u') if mode == 'last' else ('yield u', '')
#         src = _dfs_rec_template.format(*args)
#         code = compile(src, '<dummy_dfs_{}>'.format(mode), 'exec')
#         exec(code, global_ns)
#         return global_ns['_dfs']

    def _get_dfs_rec_func(self, visited=None, mode='last'):
        if visited is None:
            visited = set()
        if mode == "first":
            def _dfs_first(u):
                if u not in visited:
                    yield u
                    visited.add(u)
                    for v in self.G[u]:
                        yield from _dfs_first(v)
            return _dfs_first

        def _dfs_last(u):
            if u not in visited:
                visited.add(u)
                for v in self.G[u]:
                    yield from _dfs_last(v)
                yield u
        return _dfs_last


    def dfs_rec(self, s, visited=None, mode="first"):
        return self._get_dfs_rec_func(visited, mode)(s)

    def iddfs(self, s, visited=None):
        """Iterative Deepening Depth-First Search

        There is really only one situation where IDDFS would be
        preferable over BFS: when searching a huge acyclic graph
        (saving a significant amount of memory, with little or
        no asymptotic slowdown)

        Note: this implemention assume G is an **acyclic** graph
        """
        if visited is None:
            visited = set()
        def _iddfs(u, d):
            if u not in visited:
                yield u
                visited.add(u)
            if d == 0:
                return
            for v in self.G[u]:
                yield from _iddfs(v, d - 1)
        n = len(self.G)
        for d in range(n):
            if len(visited) == n:
                break
            yield from _iddfs(s, d)

    def tsort(self):
        """Topological Sort (reference counting)
        NOTE: the reference one point to the being referenced one,
        and the reference one must be satisfied (occur) first.
        """
        counts = {u: 0 for u in self.G}
        for u, vs in self.G.items():
            for v in vs:
                counts[v] += 1
        stack = [k for k, v in counts.items() if v == 0]
        while stack:
            u = stack.pop()
            yield u
            for v in self.G[u]:
                counts[v] -= 1
                if counts[v] == 0:
                    stack.append(v)

    def tsort_dfs(self):
        """
        NOTE: to cyclic graph, we can only expect at least one point
        occur before next scc, but this feature is the base of scc()
        """
        visited = set()
        _dfs = self._get_dfs_rec_func(visited)
        seq = []
        for u in self.G:
            if u not in visited:
                for v in _dfs(u):
                    seq.append(v)
        while seq:
            yield seq.pop()

    #tsort_rec = tsort_dfs

    def scc(self):
        """Strongly Connected Components (Kosaraju's Algorithm)"""
        visited = set()
        G_rev = Graph.made_up_by_reverse_graph(self)
        for u in self.tsort_dfs():
            if u not in visited:
                yield list(G_rev.dfs_rec(u, visited))

    def kruskal(self):
        """Elog(V) implemention (slower if add reverse edges)"""
        dsf = {k: DisjointSet(k) for k in self.G.keys()}
        heap = [(w, u, v) for u, vs in self.G.items() for v, w in vs.items()]
        heapq.heapify(heap)
        while heap:
            w, u, v = heapq.heappop(heap)
            s1, s2 = dsf[u].find_set(), dsf[v].find_set()
            if s1 != s2:
                DisjointSet.union(s1, s2)
                yield w, u, v

    def prim(self, s=None):
        """Elog(V) implemention (will add reverse edges)"""
        self.add_reverse_edges()
        if s is None:
            s = next(iter(self.G.keys()))
        generator = self._greedy_search(s, mode='prim')
        next(generator)
        yield from generator

    # def prim(self):
    #     """CLRS. Not recommend, since a C complemetion may be take in heapq"""
    #     self.add_reverse_edges()
    #     pq = PriorityQueue(self.G)
    #     used = set()
    #     _, _, u, _ = pq.extract_min()
    #     while pq.size:
    #         used.add(u)
    #         for v, w in self.G[u].items():
    #             if v not in used and w < pq.map[v][0]:
    #                 pq.decrease_key(pq.map[v][1], w, u)
    #         w, _, u, v = pq.extract_min()
    #         yield w, u, v

    def sp_dag_rec(self, s, t):
        """shortest path in DAG"""
        def _rec(u):
            if u == t:
                return 0
            return min((_rec(v)+w for v, w in self.G[u].items()),
                       default=float('inf'))
        return _rec(s)

    def sp_dag(self, s, t):
        D = {k: float('inf') for k in self.G}
        D[s] = 0
        skip = True
        for u in self.tsort():
            if u == t:
                break
            if u == s:
                skip = False
            if not skip:
                for v, w in self.G[u].items():
                    D[v] = min(D[v], D[u] + w)
        return D[t]

    def relax(self, u, v, D, P):
        d = D[u] + self.G[u][v]
        if d < D[v]:
            D[v], P[v] = d, u
            return True
        return False

    def bellman_ford(self, s):
        """
        Single-Source Shortest Paths

        worst case: the graph is 1 -> 2 -> 3 -> ... 8 -> -> 9,
        while the loop sequence is [9, 8, ..., 1]
        """
        D = {k: float('inf') for k in self.G}
        D[s] = 0
        P = {s: None}
        for _ in self.G:
            improved = False
            for u in self.G:
                for v in self.G[u]:
                    if self.relax(u, v, D, P):
                        improved = True
            if not improved:
                break
        else:
            raise Exception('Negative cycle detected!')
        return D, P

    def bellman_ford_improved(self, s):
        """
        stack or queue?

        suppose edge (i, j) exist for any i < j.
        stack implemention behave bad on long tail graph
        #queue implemention may not good at finding negative cycle.
        """
        D = {k: float('inf') for k in self.G}
        D[s] = 0
        P = {s: None}
        stack = [s]
        in_stack = {k: False for k in self.G}
        improve_count = {k: 0 for k in self.G}
        n = len(self.G)
        while stack:
            #import pdb; pdb.set_trace()
            u = stack.pop()
            in_stack[u] = False
            for v in self.G[u]:
                if self.relax(u, v, D, P):
                    if not in_stack[v]:
                        improve_count[v] += 1
                        if improve_count[v] == n:
                            raise Exception('Negative cycle detected!')
                        stack.append(v)
                        in_stack[v] = True
        return D, P

    def _greedy_search(self, s, mode='dijkstra', t=object(), **kwargs):
        """Single-Source Shortest Paths

        Parameters
        ----------
        mode: {'dijkstra', 'prim', 'A*'}
        t: target, the vertex to stop. If not specify,
           search the entire graph
        h: if mode == 'A*', a dict specify (vertex, heuristic) pairs
           should be given. For example, an Euclidean Distance
           between each vertex and `t`

        When to calculate single-pair's shortest path, a generator
        implemention can stop as soon as the other vertex reached
        """
        if mode == 'A*':
            h = kwargs['h']
        used = set()
        heap = [(0, s, None)]
        while heap:
            d, u, v = heapq.heappop(heap)
            if u not in used:
                used.add(u)
                yield d, u, v
                if t == u:
                    return
                for v, w in self.G[u].items():
                    if v not in used:
                        if mode == 'dijkstra':
                            heapq.heappush(heap, (d + w, v, u))
                        elif mode == 'prim':
                            heapq.heappush(heap, (w, v, u))
                        elif mode == 'A*':
                            heapq.heappush(heap, (d + w - h[u] + h[v], v, u))
                        else:
                            raise Exception('Unknown mode')

    def dijkstra(self, s, t=object()):
        """
        NOTE: assume no negative edge exist,
        otherwise see johnson's algorithm.
        """
        D, P = {}, {}
        for d, u, v in self._greedy_search(s, 'dijkstra', t):
            D[u], P[u] = d, v
        return D, P


    def a_star(self, s, t, h):
        P = {}
        d, u = float('inf'), s # init value
        for d, u, v in self._greedy_search(s, mode='A*', t=t, h=h):
            P[u] = v
        if u == t:
            return d - h(t), P
        return d, P

    # def dijkstra(self, s):
    #     """CLRS. Not recommend, since a C complemetion may be take in heapq"""
    #     D = {k: float('inf') for k in self.G}
    #     D[s] = 0
    #     P = {}
    #     used = set()
    #     pq = PriorityQueue(self.G)
    #     pq.build(s)
    #     while pq.size:
    #         w, _, u, v = pq.extract_min()
    #         used.add(u)
    #         D[u], P[u] = w, v
    #         for v, w in self.G[u].items():
    #             if v not in used and D[u] + w < pq.map[v][0]:
    #                 pq.decrease_key(pq.map[v][1], D[u] + w, u)
    #     return D, P

    def johnson(self):
        """All-Pairs Short Paths (for sparse graphs)

        Note: this implemention allow negative edge exists, but no
        negative cycle.
        D[v] <= D[u] + E[u][v] => E[u][v] + D[u] - D[v] >= 0
        """
        g_new = self.copy()
        v_new = object()
        g_new.G[v_new] = {k: 0 for k in self.G}
        D, _ = g_new.bellman_ford(v_new)
        for u in self.G:
            for v in self.G[u]:
                g_new.G[u][v] += D[u] - D[v]
        for u in self.G:
            generator = g_new._greedy_search(u, 'dijkstra')
            next(generator)
            for w, v, _ in generator:
                yield (u, v), w - D[u] + D[v]

    def floyd_warshall_rec(self):
        """
        Normal dynamic programming
        TODO: self cycling
        """
        keys = list(self.G)
        n = len(keys) - 1
        @memo
        def _rec(u, v, k):
            if k < 0:
                return self.G[u].get(v, float('inf'))
            return min(_rec(u, v, k - 1),
                       _rec(u, keys[k], k - 1) + _rec(keys[k], v, k - 1))
        for u in self.G:
            for v in self.G:
                if u != v:
                    yield (u, v), _rec(u, v, n)

    def bipartite_match(self):
        matched = {}
        def find_augmenting_path(s):
            path = {}
            Q = deque([s])
            while Q:
                u = Q.popleft()
                if not self.G[u] and u not in matched:
                    return path, u
                for v in itertools.chain(self.G[u], [matched.get(u, u)]):
                    if v not in path: # u != matched[v] # no need
                        path[v] = u
                        Q.append(v)
            return {}, s

        def augment(path, _from, s):
            while _from != s:
                _to, _from = _from, path[_from]
                if _from not in matched:
                    matched[_to] = _from

        for u in self.G:
            if self.G[u]:
                path, t = find_augmenting_path(u)
                augment(path, t, u)
        return matched

    def edge_disjoint_paths(self, s, t):
        """
        you can the count of disjoint paths: len(matched[t])

        you can get one possible group of paths:

        paths = [[t, p] for p in matched[t]]
        for path in paths:
            while path[-1] != s:
                path.append(matched[path[-1]].pop())
        for path in paths:
            print(*path[::-1], sep=' -> ')

        NOTE: get all possible groups of paths is hard, since the augmenting path
        can only find one more path (not all equivalence paths)
        """
        matched = defaultdict(set)
        def find_augmenting_path():
            path = {}
            Q = deque([s])
            while Q:
                u = Q.popleft()
                if u == t:
                    return path
                for v in itertools.chain(self.G[u], matched[u]): # forward first
                    if u not in matched[v] and v not in path:
                        path[v] = u
                        Q.append(v)
            return {}

        def augment(path):
            _from = t
            while _from != s:
                _to, _from = _from, path[_from]
                if _to in matched[_from]:
                    matched[_from].remove(_to)
                else:
                    matched[_to].add(_from)

        while True:
            path = find_augmenting_path()
            if path:
                augment(path)
            else:
                return matched

    def vertex_disjoint_paths(self, s, t):
        matched = {}
        matched[t] = []
        def find_augmenting_path():
            path = {}
            Q = deque([s])
            while Q:
                u = Q.popleft()
                if u == t:
                    return path
                if u in matched:
                    v = matched[u] # cancel
                    if matched.get(path[u]) != v:
                        if v not in path:
                            path[v] = u
                            Q.append(v)
                        continue
                for v in self.G[u]: # forward
                    if v not in path:
                        path[v] = u
                        Q.append(v)
            return {}

        def augment(path):
            _from = t
            while _from != s:
                _to, _from = _from, path[_from]
                if _to == t:
                    matched[t].append(_from)
                elif _to in matched:
                    assert matched[_to] == _from
                    matched.pop(_to)
                else:
                    matched[_to] = _from

        while True:
            path = find_augmenting_path()
            if path:
                augment(path)
            else:
                return matched

    def vertex_disjoint_paths_deprecated(self, s, t):
        """
        deprecated
        through edge disjoint paths i.e. split vertex,
        the idea is good, but not efficient

        Program directly is hard (actually It's not hard)
        """
        _new = object()
        G_new = {}
        for k, vs in self.G.items():
            if k in {s, t}:
                G_new[k] = vs
            else:
                G_new[k] = {(k, _new)}
                G_new[k, _new] = vs
        # TODO: guarantee vertex or not?
        matched = Graph(G_new, self.weighted).edge_disjoint_paths(s, t)
        result = {t: {v[0] for v in matched[t]}}
        stack = list(result[t])
        while stack:
            u = stack.pop()
            v = matched[u].pop()
            if v != s:
                v = v[0]
                stack.append(v)
            result[u] = v
        return result

    def max_flow(self, s, t):
        """
        Ford-Fulkerson method
        this implement use bfs to find augmenting, i.e. edmonds-karp algorithm
        what if we use heap based greedy search to increase weight per round, will it accelerate?

        I do not use residual network
        """
        matched = {u: defaultdict(float) for u in self.G}
        def find_augmenting_path():
            path = {}
            Q = deque([(s, float('inf'))])
            while Q:
                u, w = Q.popleft()
                if u == t:
                    return path, w
                for v in itertools.chain(self.G[u], matched[u]):
                    if v not in path:
                        w2 = (matched[u][v] if matched[u][v] > 0 # cancel
                              else self.G[u].get(v, 0) - matched[v][u]) # residual
                        if w2 > 0:
                            path[v] = u
                            Q.append((v, min(w, w2)))
            return path, 0

        def augment(path, w):
            _from = t
            while _from != s:
                _to, _from = _from, path[_from]
                if matched[_from][_to] > 0:
                    matched[_from][_to] -= w
                else:
                    matched[_to][_from] += w

        while True:
            path, w = find_augmenting_path()
            if w <= 0:
                return {k: {v: w for v, w in vs.items() if w > 0}
                        for k, vs in matched.items()}
            augment(path, w)





class PriorityQueue:
    """Abandon"""
    def __init__(self, iterable):
        """(weight, position, current_vertex, from_vertex)"""
        self.heap = []
        self.map = {}
        for i, k in enumerate(iterable):
            self.heap.append([float('inf'), i, k, None])
            self.map[k] = self.heap[-1]
        self.size = i + 1

    def _exchange(self, i, j):
        self.heap[i], self.heap[j] = self.heap[j], self.heap[i]
        self.heap[i][1], self.heap[j][1] = i, j

    def build(self, s=None, weight=0):
        """Move self.map[s] to the heap top and set weight to `weight`"""
        if s is not None:
            self._exchange(0, self.map[s][1])
        self.heap[0][0] = weight

    def heapify(self, i):
        right = (i + 1) << 1
        left = right - 1
        if right < self.size and self.heap[i] > self.heap[right]:
            top = right
        else:
            top = i
        if left < self.size and self.heap[top] > self.heap[left]:
            top = left
        if top != i:
            self._exchange(i, top)
            self.heapify(top)

    def extract_min(self):
        assert self.size > 0
        max = self.heap[0]
        self.size -= 1
        self.heap[0] = self.heap[self.size]
        self.heapify(0)
        return max

    def decrease_key(self, i, weight, from_vertex=None):
        assert weight < self.heap[i][0]
        self.heap[i][0] = weight
        if from_vertex is not None:
            self.heap[i][-1] = from_vertex
        while i > 0:
            j = (i - 1) >> 1
            if self.heap[i] >= self.heap[j]:
                break
            self._exchange(i, j)
            i = j


class DisjointSet:
    __slots__ = ['key', 'p', 'rank']
    def __init__(self, key, p=None, rank=0): # p means parent
        self.key = key
        if p is None:
            self.p = self
        else:
            self.p = p
        self.rank = rank

    def __str__(self):
        return '({}, {})'.format(self.key, self.rank)

    def __repr__(self):
        return self.__str__()

    def find_set(self):
        if self.p != self:
            self.p = self.p.find_set() # path compression
        return self.p

    def link(self, other):
        self.union(self.find_set(), other.find_set())

    @staticmethod
    def union(s1, s2):
        if s1.rank > s2.rank: # union by rank
            s2.p = s1
        else:
            s1.p = s2
            if s1.rank == s2.rank:
                s2.rank += 1




if __name__ == '__main__':

    # p119. Python Algorithms: Mastering Basic Algorithms in the Python Language
    g1 = Graph({'a': {'b', 'c'},
                'b': {'d', 'e', 'i'},
                'c': {'d'},
                'd': {'a', 'h'},
                'e': {'f'},
                'f': {'g'},
                'g': {'e', 'h'},
                'h': {'i'},
                'i': {'h'}})


    # p632-p635. Introduction to Algorithms (Third Edition)
    g2 = Graph({'a': {'b': 4, 'h': 8},
                'b': {'c': 8, 'h': 11},
                'c': {'d': 7, 'f': 4, 'i': 2},
                'd': {'e': 9, 'f': 14},
                'e': {'f': 10},
                'f': {'g': 2},
                'g': {'h': 1, 'i': 6},
                'h': {'i': 7},
                'i': {}})

    g3 = g2.copy()
    g3.add_reverse_edges()


    # p703. Introduction to Algorithms (Third Edition)
    g4 = Graph({1: {2: 3, 3: 8, 5: -4},
                2: {4: 1, 5: 7},
                3: {2: 4},
                4: {1: 2, 3: -5},
                5: {4: 6}})


    # p222. Python Algorithms: Mastering Basic Algorithms in the Python Language
    g5 = Graph({'a': {'e', 'f'},
                'b': {'g'},
                'c': {'e', 'g'},
                'd': {'h'}})


    g6 = Graph({'x1': {'y1', 'y4', 'y5'},
                'x2': {'y4', 'y6'},
                'x3': {'y1', 'y3'},
                'x4': {'y2'},
                'x5': {'y3'},
                'x6': {'y1', 'y3'}})


    g7 = Graph({'s': {'a', 'c', 'e'},
                'a': {'b'},
                'b': {'t'},
                'c': {'b', 'd', 't'},
                'd': {'t'},
                'e': {'c'},
                't': {}})


    # p727. Introduction to Algorithms (Third Edition)
    g8 = Graph({'s': {'v1': 16, 'v2': 13},
                'v1': {'v3': 12},
                'v2': {'v1': 4, 'v4': 14},
                'v3': {'v2': 9, 't': 20},
                'v4': {'v3': 7, 't': 4},
                't': {}})


    from pprint import pprint

    def ff(l, convert_to_list_first=True):
        print()
        if convert_to_list_first:
            pprint(list(l))
        else:
            pprint(l)

    ff(g1.bfs('a'))
    ff(g1.dfs('a'))
    ff(g1.dfs_rec('a'))
    ff(g1.iddfs('a'))
    ff(g2.tsort())
    ff(g2.tsort_dfs())
    ff(g1.scc())
    ff(g2.copy().prim('a')) # deepcopy
    ff(g2.kruskal())
    ff(g3.bellman_ford('h'))
    ff(g3.bellman_ford_improved('h'))
    ff(g3.dijkstra('h'))
    ff(g4.johnson())
    ff(g4.floyd_warshall_rec())

    assert g2.sp_dag('a', 'g') == g2.sp_dag_rec('a', 'g') == 18
    print('-' * 60)

    ff(g6.bipartite_match(), False)
    ff(g7.edge_disjoint_paths('s', 't'), False)
    ff(g7.vertex_disjoint_paths('s', 't'), False)
    ff(g7.vertex_disjoint_paths_deprecated('s', 't'), False)

    ff(g8.max_flow('s', 't'), False)



# Python Algorithms 这本书的用递归表达式来粗略的计算时间复杂度的方法很好

# 有负权的无向图就是存在负环, 没有最短路

# 证明 O(log(n!)) = O(nlog(n))
# 基本不等式证明用数学归纳法
# O(log(n!)) <= O(log(n **n)) = O(nlog(n))
# O(log(n!)) = O(2 * log(n!)) = O(log(n! * n!)) >= O(nlog(n))
# 最后一个不等号成立, 因为
# (n + 1 - i) * i >= n (i = 1, 2, ..., n) 不等号成立的条件为 n >= i, 显然

# 最小割的定义见 clrs (cut, flow, capacity)

# 最大流 可以按增广路的权重大小, 做 heap based greedy search, 减少收敛时间?

# 最小费用最大流, 可以用贪心算法实现, 每次找最短路 (可以用 bellman ford, 也可以用 dijkstra (有负权, 要做 johnson 相同的操作, 如果只有开始做一次, 那么 a->b->c->a, 就会存在负环 (但实际过程中不会出现负环); 如果每次都做, 那为什么不只用 bellman ford))
