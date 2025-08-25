from pathlib import Path
import logging
import json

from yt_dlp import YoutubeDL

from yt_sdk.url import youtube_id2url

logger = logging.getLogger(__name__)
INDENT = 4  # ??
# Campos para borrar del info, son pesados, ver si sirve el dato.
# TODO: Envolver el output con pydantic para recibir el dato correctamente.
HARDCODED_INFO_FIELDS_TO_DELETE = [
    "formats",
    "thumbnails",
    "heatmap"       #TODO: heatmap -> Graficar esto. Creo que es la forma de las ondas.
]


def _serialize_yt_info(yt_info: dict) -> dict:
    # FIXME: Por que hice esto?
    yt_info_cleaned = {}

    for key, value in yt_info.items():
        try:
            # Intenta serializar el valor para ver si es serializable
            json.dumps(value)
            yt_info_cleaned[key] = value
        except (TypeError, ValueError):
            # Si el valor no es serializable, lo omite
            continue

    return yt_info_cleaned


def _extract_info(*, ydl: YoutubeDL, youtube_id: str) -> dict:
    url = youtube_id2url(youtube_id=youtube_id)
    yt_info = ydl.extract_info(url, download=True)  # TODO: Línea clave, que más puedo hacer?
    
    # Filtra los campos no serializables
    yt_info = _serialize_yt_info(yt_info)
    
    # ----> TODO: Esto se puede abstraer a un parámetro, por ahora lo dejo hardcodeado.
    for field_to_delete in HARDCODED_INFO_FIELDS_TO_DELETE:
        yt_info.pop(field_to_delete)
    return yt_info


class YoutubeDownloader:
    def __init__(self, *, path_folder_output: Path):
        self.path_folder_output = path_folder_output

    def video(self, *, youtube_id: str) -> None:
        raise NotImplementedError("Implement.")

    def audio(self, *, youtube_id: str) -> dict:
        """Solo descarga el audio del video en formato `mp3`.
        - TODO: Ver como descargar el resto de formatos y posibilidades, abstraer.
        """
        """
        - Crea un folder en `path_out/<youtube_id>/<youtube_id>.mp3`.
        """
        logger.info(f"- Download audio - youtube_id={youtube_id}")
        yt_options = self.get_options_youtube_dl(youtube_id=youtube_id)
        with YoutubeDL(yt_options) as ydl:
            yt_info = _extract_info(ydl=ydl, youtube_id=youtube_id)
            # --> TODO: Se puede seguir procesando el yt_info.
            return yt_info

    def get_options_youtube_dl(self, *, youtube_id: str) -> dict:
        return {
            "format": "bestaudio/best",
            "outtmpl": str(self.path_folder_output / f"{youtube_id}.%(ext)s"),
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",    # TODO: Ver que se puede tocar acá.
                    "preferredcodec": "mp3",        # TODO: Ver que se puede tocar acá.
                    "preferredquality": "192"       # TODO: Ver que se puede tocar acá.
                }
            ]
        }

