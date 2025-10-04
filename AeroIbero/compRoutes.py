import pandas as pd
import os

class PathHandler:
    def __init__(self, subfolders: list, filename : str = 'None'):
        self.absPath = self.get_path_from_project(subfolders, filename)
        self.dir = os.path.dirname(self.absPath)
        self.file = filename
    
    def get_path_from_project(self, subfolders, filename = None):
        dir = os.path.dirname(os.path.abspath(__file__))
        for subfolder in subfolders:
            dir = os.path.join(dir, subfolder)
        if filename is not None:
            return os.path.join(dir, filename)
        return dir

class Graph:
    def __init__(self):
        # dict[str, dict[str, float]]
        self.adj: dict[str, dict[str, float]] = {}

    def load_from_csv(self, filepath: PathHandler | str):
        csv_path = filepath.absPath if hasattr(filepath, "absPath") else str(filepath)
        df = pd.read_csv(csv_path, index_col=0, encoding="utf-8-sig")
        df.index = df.index.astype(str).str.strip()
        df.columns = df.columns.astype(str).str.strip()
        df = df.apply(pd.to_numeric, errors="coerce")

        nodes = list(dict.fromkeys(list(df.index) + list(df.columns)))
        self.adj = {node: {} for node in nodes}
        for src in df.index:
            row = df.loc[src]
            for dst, w in row.items():
                if pd.notna(w) and float(w) != 0.0:
                    self.adj[src][dst] = float(w)

    def edge_weight(self, u: str, v: str):
        return self.adj.get(u, {}).get(v)

    def _neighbors(self, u: str):
        return self.adj.get(u, {}).items()

    def _dijkstra_heap(self, start: str, goal: str | None = None):
        import heapq
        if start not in self.adj:
            raise ValueError(f"Start node '{start}' not found in graph.")
        for u, nbrs in self.adj.items():
            for v, w in nbrs.items():
                if w < 0:
                    raise ValueError(f"Negative edge weight detected: {u}->{v} = {w}")

        inf = float('inf')
        dist = {n: inf for n in self.adj}
        parent: dict[str, str | None] = {n: None for n in self.adj}
        dist[start] = 0.0

        pq = [(0.0, start)]
        visited = set()
        while pq:
            d, u = heapq.heappop(pq)
            if u in visited:
                continue
            visited.add(u)

            if goal is not None and u == goal:
                break

            for v, w in self._neighbors(u):
                nd = d + w
                if nd < dist[v]:
                    dist[v] = nd
                    parent[v] = u
                    heapq.heappush(pq, (nd, v))
        return dist, parent

    def shortest_path(self, start: str, goal: str):
        dist, parent = self._dijkstra_heap(start, goal)
        total = dist.get(goal, float('inf'))
        if total == float('inf'):
            return [], float('inf')

        path = []
        cur = goal
        while cur is not None:
            path.append(cur)
            cur = parent[cur]
        path.reverse()
        return path, total

# --- helpers ---
def sum_path(graph: Graph, path: list[str]) -> float:
    total = 0.0
    for u, v in zip(path, path[1:]):
        w = graph.edge_weight(u, v)
        if w is None:
            raise ValueError(f"Edge {u}->{v} not found in this graph when summing path.")
        total += w
    return total

def bestRoutes(origin, dest):
    costoCsvPath     = PathHandler(['Graphs'], 'matriz_costo.csv')
    distanciaCsvPath = PathHandler(['Graphs'], 'matriz_distancia.csv')
    tiempoCsvPath    = PathHandler(['Graphs'], 'matriz_tiempo.csv')

    gCosto = Graph(); gCosto.load_from_csv(costoCsvPath)
    gDist  = Graph(); gDist.load_from_csv(distanciaCsvPath)
    gTime  = Graph(); gTime.load_from_csv(tiempoCsvPath)
    
    results = []

    # Best by COST
    path_costo, best_cost = gCosto.shortest_path(origin, dest)
    if path_costo:
        totals = {
            "costo": best_cost,
            "distancia": sum_path(gDist, path_costo),
            "tiempo": sum_path(gTime, path_costo)
        }
        results.append({
            "criterion": "costo",
            "path": path_costo,                          # ordered nodes
            "route_str": " -> ".join(path_costo),        # pretty string
            "totals": totals
        })
    else:
        results.append({"criterion": "costo", "path": [], "route_str": "", "totals": None})

    # Best by DISTANCE
    path_dist, best_dist = gDist.shortest_path(origin, dest)
    if path_dist:
        totals = {
            "costo": sum_path(gCosto, path_dist),
            "distancia": best_dist,
            "tiempo": sum_path(gTime, path_dist)
        }
        results.append({
            "criterion": "distancia",
            "path": path_dist,
            "route_str": " -> ".join(path_dist),
            "totals": totals
        })
    else:
        results.append({"criterion": "distancia", "path": [], "route_str": "", "totals": None})

    # Best by TIME
    path_time, best_time = gTime.shortest_path(origin, dest)
    if path_time:
        totals = {
            "costo": sum_path(gCosto, path_time),
            "distancia": sum_path(gDist, path_time),
            "tiempo": best_time
        }
        results.append({
            "criterion": "tiempo",
            "path": path_time,
            "route_str": " -> ".join(path_time),
            "totals": totals
        })
    else:
        results.append({"criterion": "tiempo", "path": [], "route_str": "", "totals": None})

    return results
