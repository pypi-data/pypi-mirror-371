#!/usr/bin/env python3
"""
VPS downloader with:
- Modern UA, IPv4, robust retries, YouTube extractor hints
- Desktop: choose best <=1080p by resolution (any codec/container)
- iOS (prefer_avc1=True): same selection, but post-enforce MP4/H.264/AAC via ffmpeg
- No embed-thumbnail (fragile); keep embed-metadata
- Minimal <=720p fallback if 1080p tier not available
Requires: ffmpeg (ffprobe included)
"""

import subprocess
import os
import time
import shutil
import json
import shlex

MODERN_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)

# ----------------------------
# Shell helpers
# ----------------------------
def run_command(cmd, check=True):
    try:
        result = subprocess.run(
            cmd, shell=True, check=check,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Command failed: {cmd}\n{e.output.strip()}") from e

# ----------------------------
# Environment / Mullvad
# ----------------------------
def get_venv_path():
    return "/opt/yt-dlp-mullvad/venv"

def validate_environment():
    """Only ensure yt-dlp exists in our venv; do NOT hard-require VIRTUAL_ENV match."""
    venv_path = get_venv_path()
    ytdlp_path = f"{venv_path}/bin/yt-dlp"
    if not os.path.exists(ytdlp_path):
        raise RuntimeError(
            f"yt-dlp not found at {ytdlp_path}. Reinstall inside the venv."
        )
    return venv_path

def check_mullvad():
    if not shutil.which("mullvad"):
        raise RuntimeError(
            "Mullvad CLI not found.\n"
            "Install:\n"
            "  curl -fsSLo /tmp/mullvad.deb https://mullvad.net/download/app/deb/latest/\n"
            "  sudo apt install -y /tmp/mullvad.deb"
        )

def is_logged_in() -> bool:
    out = run_command("mullvad account get", check=False) or ""
    return "not logged in" not in out.lower()

def manual_login(mullvad_account: str):
    if not mullvad_account:
        raise RuntimeError("Missing Mullvad account for manual login.")
    if is_logged_in():
        print("Already logged into Mullvad on this server.")
        return
    print("Logging into Mullvad (one-time)…")
    run_command(f"mullvad account login {mullvad_account}")
    print("Login complete. No VPN connection was started.")

def require_logged_in():
    if not is_logged_in():
        raise RuntimeError(
            "Mullvad is not logged in on this server. "
            "SSH in and run: mullvad account login <ACCOUNT> (one-time)."
        )

def wait_for_connection(timeout=10):
    for _ in range(timeout):
        status = run_command("mullvad status", check=False) or ""
        if "Connected" in status:
            print("Mullvad VPN connected.")
            return True
        time.sleep(1)
    print("Failed to confirm Mullvad VPN connection within timeout.")
    return False

def _maybe_self_update_ytdlp(venv_path: str):
    if os.environ.get("YTPDL_AUTO_UPDATE", "1") != "1":
        return
    pip = f"{venv_path}/bin/python -m pip install -U --no-input yt-dlp"
    try:
        print("Checking yt-dlp update…")
        run_command(pip, check=False)
    except Exception:
        pass  # non-fatal

# ----------------------------
# yt-dlp flags / fallbacks
# ----------------------------
def _build_common_flags():
    return (
        f"--force-ipv4 "
        f"--retries 6 --fragment-retries 6 --retry-sleep 2 "
        f"--extractor-args \"youtube:player_client=android,web\" "
        f"--user-agent '{MODERN_UA}' "
        f"--no-cache-dir --ignore-config "
    )

def _try_run(ytdlp_cmd: str):
    try:
        return run_command(ytdlp_cmd)
    except RuntimeError as e:
        # Classify fallback-eligible errors
        low = str(e).lower()
        if ("requested format is not available" in low
            or "no such format" in low
            or "unable to download video data" in low
            or "this video is only available in certain formats" in low):
            raise ValueError(str(e))
        raise

def _extract_downloaded_filename(output: str):
    filename = None
    for line in output.splitlines():
        if line.startswith("[download]"):
            if "Destination:" in line:
                filename = line.split("Destination: ")[1].strip()
            elif "has already been downloaded" in line:
                start = line.find("] ") + 2
                end = line.find(" has already been downloaded")
                filename = line[start:end].strip()
            if filename and filename.startswith("'") and filename.endswith("'"):
                filename = filename[1:-1]
            if filename:
                break
    return filename

# ----------------------------
# iOS safety (post-download)
# ----------------------------
def _ffprobe_streams(path):
    cmd = f"ffprobe -v error -print_format json -show_streams -select_streams v:0,a:0 {shlex.quote(path)}"
    out = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True).stdout
    try:
        return json.loads(out).get("streams", [])
    except Exception:
        return []

def _is_ios_safe_mp4(path):
    # MP4/.m4v container + H.264 video + (AAC or no audio)
    streams = _ffprobe_streams(path)
    v = next((s for s in streams if s.get("codec_type") == "video"), None)
    a = next((s for s in streams if s.get("codec_type") == "audio"), None)
    _, ext = os.path.splitext(path)
    is_mp4 = ext.lower() in (".mp4", ".m4v")
    v_ok = (v and v.get("codec_name") in ("h264", "avc1"))
    a_ok = (a is None) or (a.get("codec_name") in ("aac", "mp4a", "alac", "mp3"))
    return is_mp4 and v_ok and a_ok

def _transcode_to_ios_mp4(src_path):
    base, _ = os.path.splitext(src_path)
    dst_path = base + ".ios.mp4"
    cmd = (
        "ffmpeg -y -i {src} -map 0:v:0 -map 0:a:0? "
        "-c:v libx264 -preset veryfast -crf 20 -pix_fmt yuv420p "
        "-c:a aac -b:a 160k -movflags +faststart {dst}"
    ).format(src=shlex.quote(src_path), dst=shlex.quote(dst_path))
    subprocess.run(cmd, shell=True, check=True)
    return dst_path

# ----------------------------
# Public API
# ----------------------------
def download_video(url, resolution=None, extension=None, prefer_avc1=False):
    """
    Download via yt-dlp behind Mullvad.
    Desktop (prefer_avc1=False): best <=1080p by resolution (any codec/container).
    iOS (prefer_avc1=True): same, but post-enforce MP4/H.264/AAC if needed.
    """
    venv_path = validate_environment()
    _maybe_self_update_ytdlp(venv_path)
    check_mullvad()
    require_logged_in()

    # Rotate relay each job (optional, preserves your previous behavior)
    run_command("mullvad disconnect", check=False)
    run_command("mullvad relay set location any", check=False)
    print("Connecting to Mullvad VPN...")
    run_command("mullvad connect")
    if not wait_for_connection():
        raise RuntimeError("Could not establish Mullvad VPN connection.")

    print(f"Downloading: {url}")
    common = _build_common_flags()
    cap = str(resolution or 1080)
    out_tpl = "--output '/root/%(title)s.%(ext)s'"

    try:
        # Audio-only path
        audio_exts = {"mp3", "m4a", "aac", "wav", "flac", "opus", "ogg"}
        if extension and extension.lower() in audio_exts:
            ytdlp_cmd = (
                f"{venv_path}/bin/yt-dlp -x --audio-format {extension} "
                f"{common} --embed-metadata "
                f"{out_tpl} {url}"
            )
            output = _try_run(ytdlp_cmd)

        else:
            # ---- VIDEO: best <=1080p first, sorted by resolution; then single <=720p fallback
            sort_generic = '-S "res,codec,ext,filesize"'
            fmt_1080_best = f'bv*[height<={cap}]+ba/b[height<={cap}]'
            fmt_720_best  = 'bv*[height<=720]+ba/b[height<=720]'

            if prefer_avc1:
                # iOS will be made MP4/H.264/AAC after download if needed
                try:
                    ytdlp_cmd = (
                        f"{venv_path}/bin/yt-dlp "
                        f"-f \"{fmt_1080_best}\" {sort_generic} "
                        f"{common} --embed-metadata "
                        f"{out_tpl} {url}"
                    )
                    output = _try_run(ytdlp_cmd)
                except ValueError:
                    ytdlp_cmd = (
                        f"{venv_path}/bin/yt-dlp "
                        f"-f \"{fmt_720_best}\" {sort_generic} "
                        f"{common} --embed-metadata "
                        f"{out_tpl} {url}"
                    )
                    output = _try_run(ytdlp_cmd)
            else:
                # Desktop: do NOT bias to H.264, otherwise we might stop at 720p H.264
                try:
                    ytdlp_cmd = (
                        f"{venv_path}/bin/yt-dlp "
                        f"-f \"{fmt_1080_best}\" {sort_generic} "
                        f"{common} --embed-metadata "
                        f"{out_tpl} {url}"
                    )
                    output = _try_run(ytdlp_cmd)
                except ValueError:
                    ytdlp_cmd = (
                        f"{venv_path}/bin/yt-dlp "
                        f"-f \"{fmt_720_best}\" {sort_generic} "
                        f"{common} --embed-metadata "
                        f"{out_tpl} {url}"
                    )
                    output = _try_run(ytdlp_cmd)

        # Resolve output file path
        filename = _extract_downloaded_filename(output)
        if filename and os.path.exists(filename):
            # Enforce iOS-safe MP4/H.264/AAC when requested
            if prefer_avc1 and not _is_ios_safe_mp4(filename):
                try:
                    print("Selected format is not iOS-safe; transcoding to MP4/H.264…")
                    filename = _transcode_to_ios_mp4(filename)
                    print(f"Transcoded to: {filename}")
                except Exception as e:
                    print(f"Transcode failed ({e}); returning original file.")
            print(f"DOWNLOADED_FILE:{filename}")
            return filename

        # Rare: fall back to most recent file in /root
        try:
            candidates = sorted(
                (os.path.join("/root", f) for f in os.listdir("/root")),
                key=lambda p: os.path.getmtime(p),
                reverse=True
            )
            if candidates:
                filename = candidates[0]
                if prefer_avc1 and not _is_ios_safe_mp4(filename):
                    try:
                        print("Selected format is not iOS-safe; transcoding to MP4/H.264…")
                        filename = _transcode_to_ios_mp4(filename)
                        print(f"Transcoded to: {filename}")
                    except Exception as e:
                        print(f"Transcode failed ({e}); returning original file.")
                return filename
        except Exception:
            pass

        print("Download failed: File not found")
        return None

    finally:
        print("Disconnecting VPN...")
        run_command("mullvad disconnect", check=False)
