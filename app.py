from __future__ import annotations

import os
from typing import Any, Dict, List, Optional

from flask import Flask, jsonify, render_template, request
from pydub import AudioSegment
from pytube import YouTube

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__, template_folder=BASE_DIR)

DOWNLOAD_FOLDER = os.path.join(BASE_DIR, "downloads")
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)


def _human_size(num: Optional[int]) -> str:
    if not num:
        return "—"
    num = float(num)
    units = ["B", "KB", "MB", "GB", "TB"]
    for unit in units:
        if num < 1024.0:
            return f"{num:.1f} {unit}" if unit != "B" else f"{int(num)} {unit}"
        num /= 1024.0
    return f"{num:.1f} PB"


def _format_duration(seconds: Optional[int]) -> str:
    if seconds is None:
        return "Live / Unknown"
    minutes, sec = divmod(int(seconds), 60)
    hours, minutes = divmod(minutes, 60)
    if hours:
        return f"{hours}:{minutes:02d}:{sec:02d}"
    return f"{minutes}:{sec:02d}"


def _serialize_video_streams(streams) -> List[Dict[str, Any]]:
    results: List[Dict[str, Any]] = []
    seen = set()

    ordered = sorted(
        streams,
        key=lambda s: (int((s.resolution or "0p").rstrip("p")), s.fps or 0),
        reverse=True,
    )
    for stream in ordered:
        resolution = stream.resolution or "unknown"
        ext = (stream.mime_type or "").split("/")[-1]
        key = (resolution, ext)
        if key in seen:
            continue

        label_parts = []
        if stream.resolution:
            label_parts.append(stream.resolution)
        if stream.fps:
            label_parts.append(f"{stream.fps}fps")
        label = " • ".join(label_parts) or "Video"

        results.append({
            "format_id": str(stream.itag),
            "ext": ext,
            "label": label,
            "sub_label": f"{ext.upper()} • Progressive",
            "size_label": _human_size(stream.filesize or stream.filesize_approx),
        })
        seen.add(key)
    return results


def _serialize_audio_streams(streams) -> List[Dict[str, Any]]:
    results: List[Dict[str, Any]] = []
    seen = set()
    ordered = sorted(
        streams,
        key=lambda s: int("".join(filter(str.isdigit, s.abr or "0"))),
        reverse=True,
    )
    for stream in ordered:
        abr_raw = (stream.abr or "").replace("bps", "")
        abr = abr_raw.replace("kb", "kbps") if "kb" in abr_raw and "kbps" not in abr_raw else abr_raw
        ext = (stream.mime_type or "").split("/")[-1]
        key = (abr, ext)
        if key in seen:
            continue
        label = f"{abr}".strip() if abr else "High quality"
        results.append({
            "format_id": str(stream.itag),
            "ext": ext,
            "label": label,
            "sub_label": f"{ext.upper()} • Audio only",
            "size_label": _human_size(stream.filesize or stream.filesize_approx),
        })
        seen.add(key)
    return results


def _get_video(url: str) -> YouTube:
    try:
        return YouTube(url)
    except Exception as exc:  # noqa: BLE001
        raise ValueError(f"Unable to access this video: {exc}") from exc


def extract_video_metadata(url: str) -> Dict[str, Any]:
    yt = _get_video(url)

    progressive_streams = yt.streams.filter(progressive=True)
    audio_streams = yt.streams.filter(only_audio=True)

    return {
        "title": yt.title,
        "channel": yt.author,
        "duration": yt.length,
        "duration_label": _format_duration(yt.length),
        "thumbnail": yt.thumbnail_url,
        "video_formats": _serialize_video_streams(progressive_streams),
        "audio_formats": _serialize_audio_streams(audio_streams),
    }


def _convert_audio(source_path: str, target_ext: str) -> str:
    audio = AudioSegment.from_file(source_path)
    base, _ = os.path.splitext(source_path)
    target_path = f"{base}.{target_ext}"
    audio.export(target_path, format=target_ext)
    os.remove(source_path)
    return target_path


def download_specific_format(url: str, itag: str, convert_to: Optional[str] = None) -> str:
    yt = _get_video(url)
    stream = yt.streams.get_by_itag(itag)
    if not stream:
        raise ValueError("The requested format is no longer available.")

    os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)
    output_path = stream.download(output_path=DOWNLOAD_FOLDER)

    if convert_to:
        convert_to = convert_to.lower()
        if convert_to not in {"mp3", "m4a"}:
            raise ValueError("Unsupported conversion target.")
        if stream.includes_video_track:
            raise ValueError("Conversion to MP3/M4A is only available for audio formats.")
        output_path = _convert_audio(output_path, convert_to)
        return f"Audio saved as .{convert_to} in {DOWNLOAD_FOLDER}."

    return f"File saved to {DOWNLOAD_FOLDER}."


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.post("/api/info")
def api_info():
    data = request.get_json(silent=True) or {}
    url = (data.get("url") or "").strip()

    if not url:
        return jsonify({"error": "Please provide a YouTube URL."}), 400

    try:
        payload = extract_video_metadata(url)
        return jsonify(payload)
    except Exception as exc:  # noqa: BLE001
        return jsonify({"error": str(exc)}), 500


@app.post("/api/download")
def api_download():
    data = request.get_json(silent=True) or {}
    url = (data.get("url") or "").strip()
    format_id = (data.get("format_id") or "").strip()
    convert_to = (data.get("convert_to") or "").strip() or None

    if not url:
        return jsonify({"error": "Missing video URL."}), 400
    if not format_id:
        return jsonify({"error": "Select a format before downloading."}), 400

    try:
        message = download_specific_format(url, format_id, convert_to)
        return jsonify({"message": message, "message_type": "success"})
    except Exception as exc:  # noqa: BLE001
        return jsonify({"error": str(exc)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
