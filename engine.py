import os
import yt_dlp

def prepare_engine():
    """تجهيز ملف الكوكيز لضمان عدم الحظر من يوتيوب وفيسبوك"""
    cookie_file = "cookies_stable.txt"
    if not os.path.exists(cookie_file):
        with open(cookie_file, "w") as f:
            f.write("# Netscape HTTP Cookie File\n")
            f.write(".youtube.com\tTRUE\t/\tTRUE\t1766757959\tGPS\t1\n")
            f.write(".youtube.com\tTRUE\t/\tTRUE\t1801316163\tPREF\ttz=Africa.Cairo&f7=100\n")
            f.write(".youtube.com\tTRUE\t/\tTRUE\t1800424038\tSOCS\tCAISEwgDEgk4NDYxMjU0NDcaAmVuIAEaBgiA8ZzKBg\n")
    return cookie_file

def get_all_formats(url):
    """جلب كافة الجودات المتاحة مع ضمان دمج الصوت والصورة لفيسبوك"""
    ydl_opts = {
        'quiet': True, 
        'cookiefile': prepare_engine(), 
        'nocheckcertificate': True, 
        'no_warnings': True,
        'format': 'best' # محاولة جلب أفضل صيغة مدمجة تلقائياً
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(url, download=False)
            formats_btns = {}
            
            # جلب جودات الفيديو (التي تحتوي على صوت وصورة معاً)
            for f in info.get('formats', []):
                # شرط أساسي لفيسبوك: وجود كودك فيديو وكودك صوت في نفس الملف
                if f.get('vcodec') != 'none' and f.get('acodec') != 'none':
                    res = f.get('height')
                    if res and res >= 144:
                        # إضافة الرمز والجودة للازرار
                        formats_btns[f"🎬 {res}p"] = f.get('format_id')
            
            # إذا لم يتم العثور على جودات مفصلة (حالة فيسبوك المعقدة أحياناً)
            if not formats_btns:
                formats_btns["🎬 Best Quality | أفضل جودة"] = "best"
                
            # إضافة خيار الصوت دائماً في النهاية
            formats_btns["🎶 Audio | تحميل صوت"] = "bestaudio[ext=m4a]/bestaudio"
            
            # ترتيب الجودات من الأعلى للأقل (تنازلياً)
            # نقوم بالترتيب فقط للمفاتيح التي تبدأ بـ 🎬 لضمان عدم حدوث خطأ
            sorted_btns = {}
            video_keys = sorted([k for k in formats_btns.keys() if "p" in k], 
                               key=lambda x: int(''.join(filter(str.isdigit, x))), reverse=True)
            
            for k in video_keys: sorted_btns[k] = formats_btns[k]
            # إضافة باقي الخيارات (أفضل جودة أو صوت)
            for k, v in formats_btns.items():
                if k not in sorted_btns: sorted_btns[k] = v
                
            return sorted_btns
        except Exception as e:
            print(f"Engine Error: {e}")
            return {"❌ Error Analyzing": "error"}

def run_download(url, format_id, file_path):
    """تنفيذ التحميل بأقصى سرعة ممكنة"""
    ydl_opts = {
        'outtmpl': file_path,
        'format': format_id,
        'cookiefile': prepare_engine(),
        'nocheckcertificate': True,
        'quiet': True,
        'no_warnings': True,
        # إعدادات السرعة
        'concurrent_fragment_downloads': 10,
        'continuedl': True,
        'buffersize': 1024 * 1024,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
