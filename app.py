import sqlite3
import pandas as pd
import numpy as np
from flask import Flask, render_template, request, jsonify
from sklearn.metrics.pairwise import cosine_similarity
from gensim.models import Word2Vec

app = Flask(__name__)

# Conexión a la base de datos
db_path = './dataAll/pelicula4.db'
conn = sqlite3.connect(db_path, check_same_thread=False)  # Permitir que múltiples hilos usen la misma conexión

# Función para cargar los embeddings de la base de datos
def cargar_embeddings():
    df = pd.read_sql_query("SELECT id_pelicula, embedding FROM embeddings", conn)
    df['embedding'] = df['embedding'].apply(lambda x: np.frombuffer(x, dtype=np.float32))  # Convertir los bytes a un array numpy
    return df

df_embeddings = cargar_embeddings()
embeddings_matrix = np.vstack(df_embeddings['embedding'].values)

def recomendar_peliculas(palabras_clave):
    model = Word2Vec.load('./dataAll/word2vec_model.model')  # Cargar el modelo previamente entrenado
    palabras_clave = palabras_clave.lower().split()
    vector_clave = np.mean([model.wv[word] for word in palabras_clave if word in model.wv] or [np.zeros(100)], axis=0)
    similitudes = cosine_similarity([vector_clave], embeddings_matrix)
    indices_recomendadas = similitudes.argsort()[0][::-1][:5]  # Top 5
    recomendaciones = df_embeddings.iloc[indices_recomendadas]

    return recomendaciones[['id_pelicula']] 

# Ruta para la página principal
@app.route('/')
def home():
    return render_template('home.html')  # Renderiza el archivo home.html

@app.route('/main')
def main():
    return render_template('main.html')  # Renderiza el archivo main.html

@app.route('/equipos')
def equipos():
    return render_template('equipos.html')  # Renderiza el archivo equipos.html

# Realiza el filtrado mediante las palabras clave
@app.route('/recomendar', methods=['GET'])
def recomendar():
    palabras_clave = request.args.get('palabras_clave', '')  # Obtener las palabras clave desde la URL
    
    if not palabras_clave:
        return jsonify({'error': 'Debe ingresar palabras clave'}), 400

    recomendaciones = recomendar_peliculas(palabras_clave)

    peliculas_recomendadas = []
    for index, row in recomendaciones.iterrows():
        pelicula_query = f"SELECT titulo, descripcion, poster FROM peliculas WHERE id_pelicula = {row['id_pelicula']}"
        pelicula_data = pd.read_sql_query(pelicula_query, conn).iloc[0]
        
        peliculas_recomendadas.append({
            'titulo': pelicula_data['titulo'],
            'descripcion': pelicula_data['descripcion'],
            'poster': pelicula_data['poster']
        })
    
    return jsonify(peliculas_recomendadas)  


app.config['STATIC_FOLDER'] = 'static'
app.config['TEMPLATES_FOLDER'] = 'templates'
app.static_folder = 'static'

if __name__ == '__main__':
    app.run(debug=True)
