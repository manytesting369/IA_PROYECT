import sqlite3
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from gensim.models import Word2Vec

# Conectar a la base de datos existente
db_path = './dataAll/pelicula4.db'  # Asegúrate de que este sea el path correcto
conn = sqlite3.connect(db_path)

# Función para cargar los embeddings desde la tabla 'embeddings'
def cargar_embeddings():
    # Cargar los embeddings desde la tabla 'embeddings'
    df = pd.read_sql_query("SELECT id_pelicula, embedding FROM embeddings", conn)
    
    # Asegurarse de que los embeddings están en el formato correcto
    # La columna 'embedding' es un objeto de tipo bytes en la base de datos, así que la convertimos de nuevo a un array numpy
    df['embedding'] = df['embedding'].apply(lambda x: np.frombuffer(x, dtype=np.float32))  # Usar np.frombuffer para convertir los bytes a un array numpy
    return df

# Cargar los embeddings de las películas desde la base de datos
df_embeddings = cargar_embeddings()

# Asegurarse de que todos los embeddings tengan el mismo tamaño
embeddings_matrix = np.vstack(df_embeddings['embedding'].values)

# Función de recomendación
def recomendar_peliculas(palabras_clave):
    # Cargar el modelo Word2Vec de gensim
    model = Word2Vec.load('./dataAll/word2vec_model.model')  # Aquí cargamos el modelo previamente entrenado
    
    # Preprocesar las palabras clave
    palabras_clave = palabras_clave.lower().split()
    
    # Obtener el vector de las palabras clave
    vector_clave = np.mean([model.wv[word] for word in palabras_clave if word in model.wv] or [np.zeros(100)], axis=0)
    
    # Calcular las similitudes entre el vector de las palabras clave y los embeddings
    similitudes = cosine_similarity([vector_clave], embeddings_matrix)
    
    # Ordenar las películas por similitud
    indices_recomendadas = similitudes.argsort()[0][::-1][:5]  # Top 5

    # Obtener las recomendaciones
    recomendaciones = df_embeddings.iloc[indices_recomendadas]

    return recomendaciones[['id_pelicula']]  # Si deseas mostrar las recomendaciones solo por ID de película

# Solicitar palabras clave y recomendar
palabras_clave = input("Ingrese palabras clave para la recomendación: ")
recomendaciones = recomendar_peliculas(palabras_clave)
print("Recomendaciones de películas:")
print(recomendaciones)
