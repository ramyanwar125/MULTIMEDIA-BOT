import os
import yt_dlp

def get_all_formats(url):
    """استخراج الجودات باستخدام الكوكيز المرفوعة"""
    # استخدام ملف cookies.txt الذي أنشأته
    cookie_file = "cookies.txt"
    
    ydl_opts = {
        'quiet': True, 
        'nocheckcertificate': True, 
        'no_warnings': True,
    }
    
    # إذا كان الملف موجوداً نستخدمه، وإلا سيحاول بدون كوكيز
    if os.path.exists(cookie_file):
        ydl_opts['cookiefile'] = cookie_file

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        formats_btns = {}

        is_social = any(x in url for x in ["facebook.com", "fb.watch", "instagram.com"])

        if is_social:
            formats_btns["🎬 Best Quality | أفضل جودة"] = "bestvideo+bestaudio/best"
        else:
            for f in info.get('formats', []):
                if f.get('vcodec') != 'none' and f.get('acodec') != 'none' and f.get('ext') == 'mp4':
                    res = f.get('height')
                    if res:
                        formats_btns[f"🎬 {res}p"] = f.get('format_id')
        
        formats_btns["🎶 Audio | تحميل صوت"] = "bestaudio[ext=m4a]/bestaudio"
        return formats_btns

def run_download(url, format_id, file_path):
    cookie_file = "cookies.txt"
    ydl_opts = {
        'outtmpl': file_path,
        'format': format_id,
        'nocheckcertificate': True,
        'quiet': True,
        'concurrent_fragment_downloads': 15, 
        'continuedl': True,
        'merge_output_format': 'mp4',
        'postprocessor_args': ['-c:v', 'copy', '-c:a', 'aac'],
    }
    
    if os.path.exists(cookie_file):
        ydl_opts['cookiefile'] = cookie_file

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
