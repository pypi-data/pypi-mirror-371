from typing import Optional
from urllib.parse import urlparse
import re

from yt_sdk.typings import T_YoutubeId


def url2youtube_id(*, url: str) -> Optional[T_YoutubeId]:
    """
    Extrae el `youtube_id` a partir de una URL.

    La función valida que la URL pertenezca a los dominios oficiales 
    de YouTube (`www.youtube.com` o `youtube.com`) y luego busca un 
    identificador de video válido (11 caracteres alfanuméricos, 
    incluyendo '-' y '_') en parámetros comunes como `v=` o rutas 
    como `/embed/` o `/v/`.

    Args:
        url (str): URL completa del video de YouTube.

    Returns:
        `youtube_id`: String de 11 caracteres.
        si se encuentra y la URL es válida; de lo contrario, `None`.

    Ejemplos:
        >>> youtube_id_from_url(url="https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        'dQw4w9WgXcQ'
        >>> youtube_id_from_url(url="https://www.google.com/")
        None
    """
    parsed_url = urlparse(url)
    if parsed_url.netloc not in ["www.youtube.com", "youtube.com"]:
        return None

    # Buscar el ID del video en la URL
    pattern = r"(?:v=|/)([0-9A-Za-z_-]{11})(?=$|[^0-9A-Za-z_-])"
    match = re.search(pattern, url)
    return match.group(1) if match else None

def youtube_id2url(*, youtube_id: str) -> str:
    """TODO: Esto es correcto?"""
    return f"https://www.youtube.com/watch?v={youtube_id}"
