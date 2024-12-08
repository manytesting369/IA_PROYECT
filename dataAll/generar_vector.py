from gensim.models import Word2Vec
import sqlite3
import pandas as pd
import re

# Conectar a la base de datos
db_path = './dataAll/pelicula4.db'  # Ruta de tu base de datos
conn = sqlite3.connect(db_path)

# Leer las descripciones de las películas
df = pd.read_sql_query("SELECT descripcion FROM peliculas", conn)

# Preprocesar el texto
def preprocess_text(text):
    text = re.sub(r'\W+', ' ', text.lower())  # Eliminar caracteres especiales y poner en minúsculas
    return text.split()  # Dividir en palabras

# Generar las oraciones (palabras de cada descripción)
sentences = [preprocess_text(desc) for desc in df['descripcion'].dropna()]

# Entrenar el modelo Word2Vec
model = Word2Vec(sentences, vector_size=100, window=5, min_count=1, workers=4)

# Guardar el modelo entrenado
model.save('./dataAll/word2vec_model.model')  # Aquí guardas el modelo entrenado
print("Modelo Word2Vec entrenado y guardado correctamente.")



