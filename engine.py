import yt_dlp

def get_all_formats(url):
    """جلب الجودات المتاحة للفيديو"""
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'format': 'best',
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(url, download=False)
            formats = info.get('formats', [])
            res_dict = {}
            
            for f in formats:
                # نختار الملفات التي تحتوي على صوت وفيديو معاً لسهولة التحميل
                if f.get('vcodec') != 'none' and f.get('acodec') != 'none':
                    res = f.get('height')
                    if res:
                        res_name = f"{res}p"
                        res_dict[res_name] = f.get('format_id')
            
            # ترتيب الجودات من الأعلى للأقل
            return dict(sorted(res_dict.items(), key=lambda x: int(x[0].replace('p','')), reverse=True))
        except Exception as e:
            print(f"Error in engine: {e}")
            return None

def run_download(url, format_id, output_path):
    """تنفيذ عملية التحميل الفعلي"""
    ydl_opts = {
        'format': format_id,
        'outtmpl': output_path,
        'quiet': True,
        'no_warnings': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
