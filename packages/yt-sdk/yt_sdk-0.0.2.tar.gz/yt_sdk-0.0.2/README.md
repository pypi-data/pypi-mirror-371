# Youtube SDK
## youtube_id
- String de `11 caracteres alfanuméricos (incluye '-' y '_')` identificador único de un video.
- `Example:`
1. `url:` https://www.youtube.com/watch?v=5ViMA_qDKTU
2. `youtube_id:` 5ViMA_qDKTU

## QuickStart
- Install package.
```bash
pip install yt-sdk
```

- Download audio from video.
```python
from yt_sdk.downloader import YoutubeDownloader
YOUTUBE_ID = "5ViMA_qDKTU"
path_data = Path("data")
downloader = YoutubeDownloader(path_folder=path_data)
info = downloader.audio_by_youtube_id(youtube_id=YOUTUBE_ID)
```