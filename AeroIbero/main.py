import pandas as pd
import os
class PathHandler:
    def __init__(self, subfolders: list, filename : str = 'None'):
        self.absPath = self.get_path_from_project(subfolders, filename)
        self.dir = os.path.dirname(self.absPath)
        self.file = filename
    
    # Método para construir la ruta absoluta desde subcarpetas 
    # y nombre de archivo.
    def get_path_from_project(self, subfolders, filename = None):
        dir = os.path.dirname(os.path.abspath(__file__))
        for subfolder in subfolders:
            dir = os.path.join(dir, subfolder)
        if filename is not None:
            return os.path.join(dir, filename)
        return dir

class Graph:
    def __init__(self):
        # dict[str, list[tuple[str, float]]]
        self.adj: dict[str, list[tuple[str, float]]] = {}

    def load_from_csv(self, filepath: PathHandler | str):
        import pandas as pd
        csv_path = filepath.absPath if hasattr(filepath, "absPath") else str(filepath)

        df = pd.read_csv(csv_path, index_col=0, encoding="utf-8-sig")
        # Normalize names and coerce numeric
        df.index = df.index.astype(str).str.strip()
        df.columns = df.columns.astype(str).str.strip()
        df = df.apply(pd.to_numeric, errors="coerce")

        # Build union of nodes (preserve order)
        nodes = list(dict.fromkeys(list(df.index) + list(df.columns)))
        self.adj = {node: [] for node in nodes}

        for src in df.index:
            for dst in df.columns:
                w = df.at[src, dst]
                if pd.notna(w) and float(w) != 0.0:
                    self.adj[src].append((dst, float(w)))

    def dijkstra(self, start: str):
        """Legacy: distances from start to all nodes (no parents)."""
        if start not in self.adj:
            raise ValueError(f"Start node '{start}' not found in graph.")
        distances = {node: float('inf') for node in self.adj}
        distances[start] = 0.0
        visited = set()
        remaining = set(self.adj.keys())

        while remaining:
            # pick unvisited node with smallest distance
            min_node, min_dist = None, float('inf')
            for node in remaining:
                d = distances[node]
                if d < min_dist:
                    min_node, min_dist = node, d
            if min_node is None:
                break

            remaining.remove(min_node)
            visited.add(min_node)

            for neighbor, weight in self.adj.get(min_node, []):
                if neighbor in visited:
                    continue
                new_d = distances[min_node] + weight
                if new_d < distances.get(neighbor, float('inf')):
                    distances[neighbor] = new_d
        return distances

    # -------- New: heap-optimized Dijkstra with parents --------
    def _dijkstra_heap(self, start: str, goal: str | None = None):
        """Return (dist, parent) maps. Early-exits if goal is reached."""
        import heapq
        if start not in self.adj:
            raise ValueError(f"Start node '{start}' not found in graph.")

        # Ensure no negative weights (Dijkstra requirement)
        for u, nbrs in self.adj.items():
            for v, w in nbrs:
                if w < 0:
                    raise ValueError(f"Negative edge weight detected: {u}->{v} = {w}")

        inf = float('inf')
        dist = {node: inf for node in self.adj}
        parent: dict[str, str | None] = {node: None for node in self.adj}
        dist[start] = 0.0

        pq = [(0.0, start)]  # (distance, node)
        visited = set()

        while pq:
            d, u = heapq.heappop(pq)
            if u in visited:
                continue
            visited.add(u)

            if goal is not None and u == goal:
                break

            for v, w in self.adj.get(u, []):
                nd = d + w
                if nd < dist[v]:
                    dist[v] = nd
                    parent[v] = u
                    heapq.heappush(pq, (nd, v))

        return dist, parent

    def shortest_path(self, start: str, goal: str):
        """
        Compute shortest path and total cost from start to goal.
        Returns (path_list, total_cost). If unreachable, returns ([], inf).
        """
        dist, parent = self._dijkstra_heap(start, goal)
        total = dist.get(goal, float('inf'))
        if total == float('inf'):
            return [], float('inf')

        # Reconstruct path from goal back to start
        path = []
        cur = goal
        while cur is not None:
            path.append(cur)
            cur = parent[cur]
        path.reverse()
        return path, total

    
costoCsvPath = PathHandler(['Graphs'], 'matriz_costo.csv')
distanciaCsvPath = PathHandler(['Graphs'], 'matriz_distancia.csv')
tiempoCsvPath = PathHandler(['Graphs'], 'matriz_tiempo.csv')

graphCosto = Graph()
graphCosto.load_from_csv(costoCsvPath)

graphDistancia = Graph()
graphDistancia.load_from_csv(distanciaCsvPath)

graphTiempo = Graph()
graphTiempo.load_from_csv(tiempoCsvPath)

origin = "Reino del Bosque"   # replace with a node from your CSV
dest   = "Isengard"   # replace with a node from your CSV

path, cost = graphCosto.shortest_path(origin, dest)
if path:
    print("Route:", " -> ".join(path))
    print("Total cost:", cost)
else:
    print(f"No route from {origin} to {dest}")

path, distance = graphDistancia.shortest_path(origin, dest)
if path:
    print("Route:", " -> ".join(path))
    print("Total distance:", distance)
else:
    print(f"No route from {origin} to {dest}")

path, time = graphTiempo.shortest_path(origin, dest)
if path:
    print("Route:", " -> ".join(path))
    print("Total time:", time)
else:
    print(f"No route from {origin} to {dest}")

