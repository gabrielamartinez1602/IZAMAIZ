# IZAMAIZ · El viaje del maíz

Primera página del proyecto: reproduce la versión 25 (publicación) aprobada del recorrido, con la música Jaroeno Calma, composición vertical y recursos originales. Es una reproducción del video; la navegación interactiva por escenas queda pendiente de implementación.

## Estructura

- `docs/`: página lista para GitHub Pages, video y recursos web.
- `source-assets/`: fotografías, ilustraciones y música del proyecto.
- `work/`: recortes y recursos empleados para componer el recorrido.
- `tools/render_video.py`: fuente de la animación actual, conservada para futuras revisiones. Requiere Python, Pillow, NumPy, FFmpeg y las fuentes Georgia y Helvetica en macOS. La música está en `source-assets/musica-ajustada.m4a` para combinarla con el video renderizado.

## Publicación

GitHub Pages publica desde la rama `main` y la carpeta `/docs`. Los cambios de la página se despliegan al subirlos a esa rama.

La URL prevista es `https://gabrielamartinez1602.github.io/IZAMAIZ/`; solo se considera publicada después de un despliegue exitoso.

## Vista local

Desde la raíz: `python3 -m http.server 8000 --directory docs` y abrir `http://localhost:8000`.

Los navegadores requieren una interacción para activar el audio. El recorrido comienza en silencio y ofrece un control discreto para activar la música o pausarlo.

## Contenidos

Se conserva la narrativa y el texto proporcionados por la marca. Los apartados que dicen “por documentar” o “por confirmar” son contenido provisional del boceto. Los recursos se aportaron para este proyecto; su publicación no implica una licencia abierta para terceros.
