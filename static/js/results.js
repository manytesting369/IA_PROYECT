// Función para obtener y mostrar películas recomendadas
async function buscarPeliculas() {
    const searchQuery = document.getElementById('search-input').value;

    if (!searchQuery) {
        alert("Por favor ingresa palabras clave para la búsqueda.");
        return;
    }

    try {
        const response = await fetch(`/recomendar?palabras_clave=${searchQuery}&t=${new Date().getTime()}`);
        const peliculas = await response.json();

        if (response.ok) {
            mostrarPeliculasDetalles(peliculas);
        } else {
            console.error('Error al obtener las recomendaciones:', peliculas.error);
        }
    } catch (error) {
        console.error('Error en la solicitud:', error);
    }
}

// Función para mostrar las películas con detalles en el carrusel
function mostrarPeliculasDetalles(peliculas) {
    const carouselItemsContainer = document.getElementById('carousel-items');
    
    if (!carouselItemsContainer) {
        console.error("No se encontró el contenedor 'carousel-items' en el DOM.");
        return;
    }

    // Limpiar el contenido anterior del carrusel
    carouselItemsContainer.innerHTML = '';

    peliculas.forEach((pelicula, index) => {
        const isActive = index === 0 ? 'active' : '';

        const carouselItem = `
            <div class="carousel-item ${isActive}">
                <div class="movie-card text-center">
                    <img src="${pelicula.poster}" alt="${pelicula.titulo}" class="movie-poster">
                    <h5 class="mt-3">${pelicula.titulo}</h5>
                    <p>${pelicula.descripcion}</p>
                </div>
            </div>
        `;

        carouselItemsContainer.insertAdjacentHTML('beforeend', carouselItem);
    });

    // Mostrar el carrusel
    document.getElementById('movie-carousel').style.display = 'block';
}

// Conectar el evento del botón de búsqueda
document.getElementById('search-button').addEventListener('click', buscarPeliculas);
