import os
import subprocess
import tempfile
from typing import Dict, Any, Optional

from loguru import logger

from media_agent_mcp.install_tools.installer import which_ffmpeg
from media_agent_mcp.storage.tos_client import upload_to_tos
from media_agent_mcp.video.processor import download_video_from_url, get_video_info
from media_agent_mcp.audio.tts import get_audio_duration

FFMPEG_PATH = which_ffmpeg()


def combine_audio_video(
    video_url: str, audio_url: str, audio_start_time_ms: int = 0
) -> Dict[str, Any]:
    """
    Downloads a video and an audio file from URLs, combines them with a specified audio start time,
    and uploads the result to TOS.

    Args:
        video_url: The URL of the video file.
        audio_url: The URL of the audio file.
        audio_start_time_ms: The time in milliseconds where the audio should start in the video.

    Returns:
        A dictionary containing the status of the operation and the URL of the combined video.
    """
    video_path = None
    audio_path = None
    output_path = None

    try:
        # Download video and audio files
        video_download_result = download_video_from_url(video_url)
        if video_download_result["status"] == "error":
            return video_download_result
        video_path = video_download_result["data"]["file_path"]

        audio_download_result = download_video_from_url(audio_url)  # Reusing the same downloader
        if audio_download_result["status"] == "error":
            return audio_download_result
        audio_path = audio_download_result["data"]["file_path"]

        # Get video and audio duration
        _, _, _, video_frame_count = get_video_info(video_path)
        video_duration = video_frame_count / get_video_info(video_path)[2] if get_video_info(video_path)[2] > 0 else 0
        audio_duration = get_audio_duration(audio_path)

        if video_duration == 0:
            return {"status": "error", "message": "Could not determine video duration."}

        # Create a temporary file for the output
        output_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
        output_path = output_file.name
        output_file.close()

        # Convert start time to seconds
        audio_start_time_s = audio_start_time_ms / 1000.0

        # Prepare ffmpeg command
        cmd = [
            FFMPEG_PATH,
            "-i",
            video_path,
            "-i",
            audio_path,
            "-filter_complex",
            f"[1:a]adelay={audio_start_time_ms}|{audio_start_time_ms}[aud];[0:a][aud]amix=inputs=2[a]",
            "-map",
            "0:v",
            "-map",
            "[a]",
            "-c:v",
            "copy",
            "-c:a",
            "aac",
            "-strict",
            "experimental",
            "-t",
            str(video_duration),
            "-y",
            output_path,
        ]

        # If audio is longer than video, it will be truncated by the -t option
        
        subprocess.run(cmd, check=True, capture_output=True, text=True)

        # Upload to TOS
        upload_result = upload_to_tos(output_path)
        return upload_result

    except Exception as e:
        logger.error(f"Error combining audio and video: {e}")
        if isinstance(e, subprocess.CalledProcessError):
            logger.error(f"FFmpeg stderr: {e.stderr}")
            return {"status": "error", "message": f"FFmpeg error: {e.stderr}"}
        return {"status": "error", "message": str(e)}

    finally:
        # Cleanup temporary files
        if video_path and os.path.exists(video_path):
            os.unlink(video_path)
        if audio_path and os.path.exists(audio_path):
            os.unlink(audio_path)
        if output_path and os.path.exists(output_path):
            os.unlink(output_path)