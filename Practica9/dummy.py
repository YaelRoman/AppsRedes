class Graph():
    def __init__(self, vertices):
        self.vertices = vertices
        # Inicializa matriz de adyacencia en 0
        self.graph = [[0 for _ in range(vertices)]
                      for _ in range(vertices)]
    
    def printSolution(self, distance):
        print("#Vertice \t Distancia")
        for node in range(self.vertices):
            val = distance[node]
            print(node+1, "\t\t", "INF" if val == float('inf') else val)
    
    # Encuentra el vértice con la mínima distancia entre los no incluidos en spt
    def minDistance(self, distance, sptSet):
        min_val = float('inf')
        min_index = -1
        for vertex in range(self.vertices):
            if not sptSet[vertex] and distance[vertex] < min_val:
                min_val = distance[vertex]
                min_index = vertex
        return min_index


    # Dijkstra
    def dijkstra(self, src):
        distance = [float('inf')] * self.vertices
        distance[src-1] = 0
        sptSet = [False] * self.vertices

        for _ in range(self.vertices):
            u = self.minDistance(distance, sptSet)
            # Si no queda vértice alcanzable, terminamos
            if u == -1 or distance[u] == float('inf'):
                break
            sptSet[u] = True

            for vertex in range(self.vertices):
                w = self.graph[u][vertex]
                if w > 0 and not sptSet[vertex] and distance[u] + w < distance[vertex]:
                    distance[vertex] = distance[u] + w
        
        self.printSolution(distance)

### IV
g = Graph(7)
g.graph = [[0, 0, 3, 0, 0, 0, 0],
           [3, 0, 0, 0, 0, 0, 0],
           [0, 0, 0, 0, 3, 2, 0],
           [0, 0, 0, 0, 0, 0, 2],
           [0, 0, 0, 0, 0, 0, 0],
           [0, 0, 0, 0, 0, 0, 1],
           [0, 0, 2, 0, 0, 0, 0]]
print("\nGrafo IV\n")
src = 1
print(f"Distancia más corta desde el nodo {src}")
g.dijkstra(src)

### V
g = Graph(6)
g.graph = [[0, 1, 3, 0, 0, 0],
           [0, 0, 0, 0, 0, 0],
           [0, 2, 0, 0, 0, 7],
           [0, 0, 0, 0, 0, 0],
           [4, 0, 0, 5, 0, 0],
           [0, 0, 0, 6, 0, 0]]
print("\nGrafo V\n")
src = 1
print(f"Distancia más corta desde el nodo {src}")
g.dijkstra(src)

### VII
g = Graph(9)
g.graph = [[0, 7, 2, 6, 0, 0, 0, 9, 0],
           [7, 0, 6, 0, 0, 0, 0, 0, 0],
           [2, 6, 0, 1, 3, 0, 0, 0, 0],
           [6, 0, 1, 0, 0, 0, 0, 5, 0],
           [0, 0, 3, 0, 0, 2, 8, 0, 1],
           [0, 0, 0, 0, 2, 0, 3, 0, 0],
           [0, 0, 0, 0, 8, 3, 0, 0, 0],
           [9, 0, 0, 5, 0, 0, 0, 0, 0],
           [0, 0, 0, 0, 1, 0, 0, 0, 0]
           ]
print("\nGrafo VII\n")
src = 1
print(f"Distancia más corta desde el nodo {src}")
g.dijkstra(src)