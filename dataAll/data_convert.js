import sqlite3 from 'sqlite3';  // Importar sqlite3
import fetch from 'node-fetch';  // Importar fetch para solicitudes HTTP

// Inicializar sqlite3 en modo verbose
const db = new sqlite3.Database('./pelicula4.db', sqlite3.OPEN_READWRITE | sqlite3.OPEN_CREATE, (err) => {
  if (err) {
    console.error('Error al abrir la base de datos:', err.message);
  } else {
    console.log('Conectado a la base de datos.');
  }
});

// Función para crear la base de datos y la tabla con la columna 'etiqueta'
async function crearBaseDeDatos() {
  db.serialize(() => {
    db.run(`
      CREATE TABLE IF NOT EXISTS peliculas (
        id_pelicula INTEGER PRIMARY KEY AUTOINCREMENT,
        titulo TEXT UNIQUE,
        genero TEXT,
        anio_estreno INTEGER,
        descripcion TEXT,
        poster TEXT,
        puntuacion TEXT,
        etiqueta TEXT
      );
    `, (err) => {
      if (err) {
        console.error('Error al crear la tabla:', err.message);
      } else {
        console.log("Tabla 'peliculas' creada o verificada con éxito.");
      }
    });
  });
}

// Función para obtener y almacenar datos de películas desde OMDb
async function almacenarPeliculas() {
  const apiKey = 'eda582f';  // Tu API Key de OMDb
  const totalMovies = 300;  // Número total de películas a obtener
  const moviesPerPage = 10;  // Número de películas por página
  const totalPages = Math.ceil(totalMovies / moviesPerPage);  // Número total de páginas

  try {
    for (let page = 1; page <= totalPages; page++) {
      const url = `http://www.omdbapi.com/?s=movie&page=${page}&apikey=${apiKey}`;

      const response = await fetch(url);
      const data = await response.json();

      if (data.Search) {
        for (const movie of data.Search) {
          const detalles = await obtenerDetallesPelicula(movie.imdbID);
          if (!detalles) continue;

          const { Title, Year, Genre, Plot, Poster, Ratings } = detalles;
          const puntuacion = Ratings.length > 0 ? Ratings[0].Value : 'No disponible';
          const etiqueta = Genre ? Genre.split(", ")[0] : "Sin etiqueta";

          const query = `
            INSERT OR IGNORE INTO peliculas (titulo, genero, anio_estreno, descripcion, poster, puntuacion, etiqueta)
            VALUES (?, ?, ?, ?, ?, ?, ?);
          `;
          const values = [Title, Genre, Year, Plot, Poster, puntuacion, etiqueta];

          db.run(query, values, (err) => {
            if (err) {
              console.error('Error al almacenar la película:', err.message);
            } else {
              console.log(`Película almacenada: ${Title}`);
            }
          });
        }
      } else {
        console.log("No se encontraron películas en esta página.");
      }
    }
  } catch (error) {
    console.error("Error al obtener o almacenar los datos:", error);
  }
}

// Función para obtener detalles de una película por su ID
async function obtenerDetallesPelicula(imdbID) {
  const apiKey = 'eda582f';  // Tu API Key de OMDb
  const url = `http://www.omdbapi.com/?i=${imdbID}&apikey=${apiKey}`;

  try {
    const response = await fetch(url);
    const data = await response.json();

    return data.Response === "True" ? {
      Title: data.Title,
      Year: data.Year,
      Genre: data.Genre,
      Plot: data.Plot,
      Poster: data.Poster,
      Ratings: data.Ratings,
    } : null;
  } catch (error) {
    console.error(`Error al obtener detalles de la película ${imdbID}:`, error);
    return null;
  }
}

// Ejecutar las funciones de creación y almacenamiento de películas
(async () => {
  await crearBaseDeDatos();
  await almacenarPeliculas();
})();
