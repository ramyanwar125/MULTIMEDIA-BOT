import yt_dlp
import os

def get_cookies_path():
    cookie_file = "youtube_cookies.txt"
    # تنسيق Netscape الذي يطلبه يوتيوب
    lines = [
        "# Netscape HTTP Cookie File\n",
        ".youtube.com\tTRUE\t/\tTRUE\t1766757959\tGPS\t1\n",
        ".youtube.com\tTRUE\t/\tTRUE\t1801316163\tPREF\ttz=Africa.Cairo&f7=100\n",
        ".youtube.com\tTRUE\t/\tTRUE\t1800424038\tSOCS\tCAISEwgDEgk4NDYxMjU0NDcaAmVuIAEaBgiA8ZzKBg\n"
    ]
    with open(cookie_file, "w", encoding="utf-8") as f:
        f.writelines(lines)
    return cookie_file

def get_all_formats(url):
    cookie_path = get_cookies_path()
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'cookiefile': cookie_path,
    }
    formats_dict = {}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        for f in info.get('formats', []):
            if f.get('vcodec') == 'none' and f.get('acodec') != 'none':
                formats_dict[f"🎵 Audio"] = f['format_id']
            if f.get('vcodec') != 'none' and f.get('ext') == 'mp4':
                height = f.get('height')
                if height:
                    formats_dict[f"🎬 {height}p"] = f['format_id']
    return formats_dict

def run_download(url, format_id, output_path):
    cookie_path = get_cookies_path()
    ydl_opts = {
        'format': format_id,
        'outtmpl': output_path,
        'cookiefile': cookie_path,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
