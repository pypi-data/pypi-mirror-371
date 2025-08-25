from urllib.parse import urlparse
import re


def is_valid_youtube_id(*, youtube_id: str) -> bool:
    """
    Check if is a valid `youtube_id`.

    ## A valid `youtube_id`:
    - Is exactly 11 characters long.
    - Contains only letters, digits, '-' or '_'.
    """
    if not isinstance(youtube_id, str):
        return False

    pattern = r"^[0-9A-Za-z_-]{11}$"
    return bool(re.match(pattern, youtube_id))


def raise_if_not_valid_youtube_id(*, youtube_id: str) -> None:
    if not is_valid_youtube_id(youtube_id=youtube_id):
        raise ValueError(f"Invalid youtube_id={youtube_id}")


def url2youtube_id(*, url: str) -> str:
    """
    Extrae el `youtube_id` a partir de una URL.

    La función valida que la URL pertenezca a los dominios oficiales 
    de YouTube (`www.youtube.com` o `youtube.com`) y luego busca un 
    identificador de video válido (11 caracteres alfanuméricos, 
    incluyendo '-' y '_') en parámetros comunes como `v=` o rutas 
    como `/embed/` o `/v/`.
    """
    parsed_url = urlparse(url)
    if parsed_url.netloc not in ["www.youtube.com", "youtube.com"]:
        youtube_id = None
    else:
        # Buscar el ID del video en la URL
        pattern = r"(?:v=|/)([0-9A-Za-z_-]{11})(?=$|[^0-9A-Za-z_-])"
        match = re.search(pattern, url)
        youtube_id = match.group(1) if match else None

    raise_if_not_valid_youtube_id(youtube_id=youtube_id)

    return youtube_id

def youtube_id2url(*, youtube_id: str) -> str:
    """TODO: Esto es correcto?"""
    return f"https://www.youtube.com/watch?v={youtube_id}"
