from pathlib import Path
import logging

from yt_sdk.downloader import YoutubeDownloader

logger = logging.getLogger(__name__)


def test_audio_real(tmp_path: Path, youtube_id_real: str):
    logger.info(f"tmp_path={tmp_path}")
    logger.info(f"youtube_id_real={youtube_id_real}")
    downloader = YoutubeDownloader(path_folder_output=tmp_path)

    info = downloader.audio(youtube_id=youtube_id_real)
    logger.info("TODO: Testear el info que llega.")

    # Verifica que el archivo mp3 se haya creado
    file_mp3 = tmp_path / f"{youtube_id_real}.mp3"
    assert file_mp3.exists()
    assert file_mp3.stat().st_size > 0

#with open(self.paths.info, "w") as f:
#    json.dump(yt_info, f, indent=INDENT)
