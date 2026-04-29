"""
fetcher.py — Metadata extraction using yt-dlp (Title, Duration, Formats/Size only).
"""

import yt_dlp


def fetch_metadata(url: str) -> dict:
    """
    Extract video metadata (Title, Duration, Format/Size) without downloading.
    """
    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "skip_download": True,
        "noplaylist": True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)

    formats = []
    seen_res = set()
    for f in info.get("formats", []):
        vcodec = f.get("vcodec", "none")
        acodec = f.get("acodec", "none")
        
        # Skip audio-only
        if vcodec == "none":
            continue
            
        h = 0
        if f.get("height"):
            h = f["height"]
        elif f.get("resolution"):
            try:
                h = int(f["resolution"].replace("p", "").split("p")[0].split("x")[-1])
            except Exception:
                pass
                
        if h > 0:
            res_str = f"{h}p"
        else:
            res_str = f.get("format_note") or f.get("resolution") or "unknown"
            
        if "p" not in res_str and h == 0:
            continue
            
        if res_str in seen_res:
            continue
        seen_res.add(res_str)
        
        ext = f.get("ext", "mp4")
        fmt_id = f.get("format_id", "?")
        
        # Youtube DASH high-res merging
        if acodec != "none" and acodec is not None:
            final_fmt_id = fmt_id
        else:
            final_fmt_id = f"{fmt_id}+bestaudio/best"
            
        filesize = f.get("filesize") or f.get("filesize_approx")
        formats.append(
            {
                "format_id": final_fmt_id,
                "ext": ext,
                "resolution": res_str,
                "filesize": filesize,
            }
        )

    # Sort formats by height descending
    def _height(fmt):
        try:
            return int(fmt["resolution"].replace("p", ""))
        except Exception:
            return 0

    formats.sort(key=_height, reverse=True)

    # Add fallback "best"
    formats.insert(
        0,
        {
            "format_id": "bestvideo+bestaudio/best",
            "ext": "mp4",
            "resolution": "Best Available",
            "filesize": None,
        },
    )

    duration_secs = info.get("duration", 0)
    minutes, seconds = divmod(int(duration_secs or 0), 60)

    return {
        "title": info.get("title", "Unknown Title"),
        "duration": f"{minutes}:{seconds:02d}",
        "formats": formats,
        "webpage_url": info.get("webpage_url", url),
    }
