import os
import yt_dlp
import re

def prepare_engine():
    cookie_file = "cookies_stable.txt"
    if not os.path.exists(cookie_file):
        with open(cookie_file, "w") as f:
            f.write("# Netscape HTTP Cookie File\n")
    return cookie_file

def get_all_formats(url):
    ydl_opts = {
        'quiet': True, 
        'cookiefile': prepare_engine(), 
        'nocheckcertificate': True,
        'no_warnings': True,
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        formats_btns = {}
        all_formats = info.get('formats', [])
        
        for f in all_formats:
            # فلترة: نريد فقط الملفات التي تحتوي فيديو
            if f.get('vcodec') != 'none':
                res = f.get('height')
                if res:
                    label = f"🎬 {res}p"
                    # إذا كانت الجودة موجودة مسبقاً، لا نكررها (حل مشكلة الرسائل المتكررة)
                    if label not in formats_btns:
                        # تحسين التحميل: نطلب فيديو + صوت لضمان العمل على فيسبوك
                        formats_btns[label] = f"{f.get('format_id')}+bestaudio/best"
        
        # ترتيب رقمي تنازلي
        def extract_res(label):
            nums = re.findall(r'\d+', label)
            return int(nums[0]) if nums else 0

        sorted_labels = sorted(formats_btns.keys(), key=extract_res, reverse=True)
        final_formats = {label: formats_btns[label] for label in sorted_labels}
        
        # إضافة خيار الصوت
        if final_formats:
            final_formats["🎶 Audio | تحميل صوت"] = "bestaudio[ext=m4a]/bestaudio"
        
        return final_formats

def run_download(url, format_id, file_path):
    ydl_opts = {
        'outtmpl': file_path,
        'format': format_id,
        'cookiefile': 'cookies_stable.txt',
        'nocheckcertificate': True,
        'quiet': True,
        # هذا السطر ضروري جداً لفيسبوك لدمج الصوت والفيديو
        'merge_output_format': 'mp4',
        'postprocessor_args': ['-c:v', 'copy', '-c:a', 'aac'],
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
