import yt_dlp
import os

def prepare_engine():
    # يبحث عن ملف الكوكيز في حال قمت برفعه يدوياً
    if os.path.exists("cookies_stable.txt"):
        return "cookies_stable.txt"
    return None

def get_all_formats(url):
    cookie_path = prepare_engine()
    
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'cookiefile': cookie_path,
        # هذه الإعدادات هي السر في تجاوز حظر يوتيوب الجديد
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
        },
        'nocheckcertificate': True,
        'geo_bypass': True,
        'extract_flat': False, # لمحاولة استخراج البيانات كاملة
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(url, download=False)
            if not info:
                raise Exception("No info found")
            
            formats = {}
            # استخراج جودات الفيديو المباشرة (Direct Links)
            for f in info.get('formats', []):
                # نفلتر الجودات التي تحتوي على فيديو وصوت معاً لسهولة الرفع
                if f.get('vcodec') != 'none' and f.get('acodec') != 'none':
                    res = f.get('resolution', f.get('format_note', 'HD'))
                    # نأخذ الصيغ المشهورة فقط mp4
                    if f.get('ext') == 'mp4':
                        formats[f"{res} (MP4)"] = f['format_id']
            
            # إضافة خيار الصوت دائماً
            formats["🎵 Audio (High Quality)"] = "bestaudio/best"
            
            # إذا لم يجد جودات محددة، نستخدم الخيار التلقائي
            if not formats:
                formats["🎬 Best Quality (Auto)"] = "best"
                
            return formats
        except Exception as e:
            print(f"Error in engine: {str(e)}")
            raise e

def run_download(url, format_id, output_path):
    cookie_path = prepare_engine()
    ydl_opts = {
        'format': format_id,
        'outtmpl': output_path,
        'cookiefile': cookie_path,
        'nocheckcertificate': True,
        'postprocessors': [{
            'key': 'FFmpegVideoConvertor',
            'preferedformat': 'mp4',
        }] if "audio" not in format_id else [],
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
