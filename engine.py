import yt_dlp
import os
import json

# دالة لإنشاء ملف الكوكيز برمجياً من البيانات التي قدمتها
def get_cookies_path():
    cookies_data = [
        {
            "domain": ".youtube.com",
            "expirationDate": 1766757959,
            "name": "GPS",
            "path": "/",
            "secure": True,
            "value": "1"
        },
        {
            "domain": ".youtube.com",
            "expirationDate": 1801316163,
            "name": "PREF",
            "path": "/",
            "secure": True,
            "value": "tz=Africa.Cairo&f7=100"
        },
        {
            "domain": ".youtube.com",
            "expirationDate": 1800424038,
            "name": "SOCS",
            "path": "/",
            "secure": True,
            "value": "CAISEwgDEgk4NDYxMjU0NDcaAmVuIAEaBgiA8ZzKBg"
        }
    ]
    
    cookie_file = "youtube_cookies.json"
    try:
        with open(cookie_file, "w") as f:
            json.dump(cookies_data, f)
    except Exception as e:
        print(f"Error creating cookie file: {e}")
    return cookie_file

def get_all_formats(url):
    """جلب جميع الجودات المتاحة للرابط"""
    cookie_path = get_cookies_path()
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'cookiefile': cookie_path,
        'cachedir': False
    }
    
    formats_dict = {}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(url, download=False)
            formats = info.get('formats', [])
            
            # 1. جلب جودة الصوت
            for f in formats:
                if f.get('vcodec') == 'none' and f.get('acodec') != 'none':
                    abr = f.get('abr', 128)
                    res = f"🎵 Audio ({abr}kbps)"
                    formats_dict[res] = f['format_id']
                    break # نكتفي بأول جودة صوت جيدة
            
            # 2. جلب جودات الفيديو (بصيغة mp4 لضمان التوافق)
            for f in formats:
                if f.get('vcodec') != 'none' and f.get('ext') == 'mp4':
                    height = f.get('height')
                    if height:
                        res = f"🎬 Video {height}p"
                        # نتأكد من عدم تكرار الجودة ونأخذ الأفضل
                        if res not in formats_dict:
                            formats_dict[res] = f['format_id']
                            
        except Exception as e:
            print(f"Error extracting formats: {e}")
            raise e
    
    # ترتيب الجودات تنازلياً (من الأعلى للأقل)
    return dict(sorted(formats_dict.items(), key=lambda x: x[0], reverse=True))

def run_download(url, format_id, output_path):
    """تحميل الملف المختار"""
    cookie_path = get_cookies_path()
    
    # إذا كان المختار فيديو، نحاول دمج الصوت معه تلقائياً
    ydl_opts = {
        'format': f'{format_id}+bestaudio/best',
        'outtmpl': output_path,
        'cookiefile': cookie_path,
        'merge_output_format': 'mp4',
        'quiet': True,
        'no_warnings': True,
        'postprocessors': [{
            'key': 'FFmpegVideoConvertor',
            'preferedformat': 'mp4',
        }],
    }
    
    # إذا كان المختار صوت فقط (format_id يحتوي على كلمة audio)
    if "audio" in format_id or "Audio" in format_id:
        ydl_opts['format'] = format_id

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            ydl.download([url])
        except Exception as e:
            print(f"Error during download: {e}")
            raise e
