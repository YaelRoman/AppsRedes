import pandas as pd
from sqlalchemy import create_engine
import os
import numpy as np

# Clase para manejar rutas de archivos como objetos.
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

class DirectedWeightedGraph:
    def __init__(self):
        self.edges = {}  # {source: {target: {attr_dict}}}

    def add_edge(self, source, target, **attrs):
        if source not in self.edges:
            self.edges[source] = {}
        self.edges[source][target] = attrs

    def neighbors(self, node):
        return self.edges.get(node, {}).keys()

    def get_edge_data(self, source, target):
        return self.edges.get(source, {}).get(target, None)

def build_weighted_graphs_from_resumen(resumen_df):
    """
    Construye un grafo dirigido ponderado para cada categoría de búsqueda:
    'Distancia (Km)', 'Tiempo total (Hrs)', 'Costo total'.
    Retorna un diccionario con los grafos.
    """
    graphs = {}
    weight_columns = {
        'Distancia': 'Distancia (Km)',
        'Tiempo': 'Tiempo total (Hrs)',
        'Costo': 'Costo total'
    }
    for key, col in weight_columns.items():
        G = DirectedWeightedGraph()
        for _, row in resumen_df.iterrows():
            G.add_edge(
                row['Origen'].strip(),
                row['Destino'].strip(),
                tipo_viaje=row['Tipo Viaje'],
                weight=row[col]
            )
        graphs[key] = G
    return graphs

def load_resumen_df(db_path: PathHandler):
    engine = create_engine(f"sqlite:///{db_path.absPath}")
    with engine.connect() as conn:
        resumen_df = pd.read_sql_table('Resumen', conn)
        resumen_df.columns = [col.strip() for col in resumen_df.columns]
    return resumen_df

# Ejemplo de uso:
# resumen_df = load_resumen_df(aeroIberoDBPath)
# graphs = build_weighted_graphs_from_resumen(resumen_df)
# graphs['Distancia'], graphs['Tiempo'], graphs['Costo']

def csvToDBTable(csv_path: PathHandler, db_path: PathHandler, tableName: str):
    # Cargar del CSv utilizando Header como columnas
    header = pd.read_csv(csv_path.absPath, nrows=0).columns.tolist()
    engine = create_engine(f"sqlite:///{db_path.absPath}")
    df = pd.read_csv(csv_path.absPath, usecols=header)
    # Guardar en base de datos remplazando la tabla si ya existe
    df.to_sql(tableName, engine, if_exists='replace')

ciudadesCsvPath = PathHandler(['Raw'], 'Ciudades.csv')
resumenCsvPath = PathHandler(['Raw'], 'resumen.csv')
rutasCsvPath = PathHandler(['Raw'], 'rutas.csv')

aeroIberoDBPath = PathHandler(['Databases'], 'AeroIbero.db')
csvToDBTable(ciudadesCsvPath, aeroIberoDBPath, 'Ciudades')
csvToDBTable(resumenCsvPath, aeroIberoDBPath, 'Resumen')
csvToDBTable(rutasCsvPath, aeroIberoDBPath, 'Rutas')

# # Verificar si los datos se almacenaron correctamente leyendo la tabla desde la base de datos
# with create_engine(f"sqlite:///{aeroIberoDBPath.absPath}").connect() as conn:
#     pd.set_option('display.max_rows', None)
#     pd.set_option('display.max_columns', None)
#     pd.set_option('display.width', None)
#     pd.set_option('display.max_colwidth', None)
#     ciudades = pd.read_sql_table('Ciudades', conn)
#     resumen = pd.read_sql_table('Resumen', conn)
#     rutas = pd.read_sql_table('Rutas', conn)
#     print(ciudades)
#     print(resumen)
#     print(rutas)
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', None)
resumen_df = load_resumen_df(aeroIberoDBPath)
graphs = build_weighted_graphs_from_resumen(resumen_df)

def graph_matrix_df(graph, nodes):
    matrix = np.zeros((len(nodes), len(nodes)))
    node_idx = {node: idx for idx, node in enumerate(nodes)}
    for src in nodes:
        for dst in nodes:
            edge = graph.get_edge_data(src, dst)
            matrix[node_idx[src], node_idx[dst]] = edge['weight'] if edge else 0
    return pd.DataFrame(matrix, index=nodes, columns=nodes)

nodes = list(dict.fromkeys(
    [r['Origen'].strip() for _, r in resumen_df.iterrows()] +
    [r['Destino'].strip() for _, r in resumen_df.iterrows()]
))

dist_df = graph_matrix_df(graphs['Distancia'], nodes)
tiempo_df = graph_matrix_df(graphs['Tiempo'], nodes)
costo_df = graph_matrix_df(graphs['Costo'], nodes)

dist_df.to_csv('matriz_distancia.csv', encoding='utf-8-sig')
tiempo_df.to_csv('matriz_tiempo.csv', encoding='utf-8-sig')
costo_df.to_csv('matriz_costo.csv', encoding='utf-8-sig')
