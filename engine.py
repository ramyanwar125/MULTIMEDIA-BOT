import os
import yt_dlp
import re

def prepare_engine():
    """تهيئة ملف الكوكيز لضمان عدم حظر الطلبات"""
    cookie_file = "cookies_stable.txt"
    if not os.path.exists(cookie_file):
        with open(cookie_file, "w") as f:
            f.write("# Netscape HTTP Cookie File\n")
    return cookie_file

def get_all_formats(url):
    """استخراج جميع جودات الفيديو التي تحتوي على صوت وصورة معاً"""
    ydl_opts = {
        'quiet': True, 
        'cookiefile': prepare_engine(), 
        'nocheckcertificate': True,
        'no_warnings': True,
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            formats_btns = {}
            all_formats = info.get('formats', [])
            
            for f in all_formats:
                # الشرط الأساسي: وجود فيديو وصوت في نفس الملف
                if f.get('vcodec') != 'none' and f.get('acodec') != 'none':
                    res = f.get('height')
                    if res:
                        label = f"🎬 {res}p"
                        formats_btns[label] = f.get('format_id')
            
            # دالة لاستخراج الرقم من النص للترتيب (مثلاً 720 من "720p")
            def extract_res(label):
                nums = re.findall(r'\d+', label)
                return int(nums[0]) if nums else 0

            # ترتيب الجودات من الأعلى (1080, 720...) إلى الأقل
            sorted_keys = sorted(formats_btns.keys(), key=extract_res, reverse=True)
            final_formats = {k: formats_btns[k] for k in sorted_keys}
            
            # إضافة خيار الصوت فقط في النهاية لمن يحتاجه
            final_formats["🎶 Audio | تحميل صوت"] = "bestaudio[ext=m4a]/bestaudio"
            
            return final_formats
    except Exception as e:
        print(f"حدث خطأ أثناء جلب الجودات: {e}")
        return {}

def run_download(url, format_id, file_path):
    """بدء عملية التحميل للجودة المختارة"""
    ydl_opts = {
        'outtmpl': file_path,
        'format': format_id,
        'cookiefile': 'cookies_stable.txt',
        'nocheckcertificate': True,
        'quiet': False, # جعلناه False لتتمكن من رؤية التقدم في الشاشة
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
            return True
    except Exception as e:
        print(f"حدث خطأ أثناء التحميل: {e}")
        return False
