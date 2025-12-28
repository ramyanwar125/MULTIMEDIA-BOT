import os
import yt_dlp

def prepare_engine():
    cookie_file = "cookies.txt"
    
    # قائمة الكوكيز التي أرسلتها (تم وضعها هنا كمتغير)
    # ملاحظة: تم اختصار القائمة هنا للتبسيط، تأكد من وضع القائمة الكاملة التي أرسلتها في مكانها
    raw_cookies = [
        {"domain": ".youtube.com", "name": "__Secure-1PAPISID", "value": "5i84Die2RJBNC2ce/AT2hauHxI6F92xPj_"},
        {"domain": ".youtube.com", "name": "__Secure-1PSID", "value": "g.a0004giEiFc2xdrGVpg52KCe5iEggWIlfVJTzLdmIY_shjAgvHHZJC__lOksy_V1shnK_eMU2QACgYKAWISARYSFQHGX2MiSRiVPtw6IQMxGYvEmCdH4RoVAUF8yKozwvkHQM09piFqm1tD3qSe0076"},
        {"domain": ".youtube.com", "name": "LOGIN_INFO", "value": "AFmmF2swRQIhAJr_X_MAu1PKtQ7YbEoBme3ow5NsWSDax1gAtpwPVsLsAiA7viGmF4Tmg5dEWSZDbAGU_wD1X0KD0dyQCM_i8udTOg:QUQ3MjNmd1paTG9Rdm8tekRXSWxDb292WEQwZVBpbEVwYWNDUlNfVGppVUJxQ1JWYzNoMGRsbFY3cHU1MjRfX0Zwb1J3SmhwU2xrekF4Q3lQY19RTWFvZ01qeDFmVHVScS04WVFOV29nQk5TOTdpUWhTa1VPd3hQSDBENThBUjYwbUlYMUNuNlZQaGFMZVJEajJHU21OZklkV2tKS1FTTFJR"},
        {"domain": ".youtube.com", "name": "SID", "value": "g.a0004giEiFc2xdrGVpg52KCe5iEggWIlfVJTzLdmIY_shjAgvHHZ6A00lT4BcAvf860P256R8QACgYKASISARYSFQHGX2MigyhtRA6u3mymovOefruTiBoVAUF8yKqXLVcp081Qmaiv3aJ2gJvh0076"},
        # ... يمكنك إضافة باقي الأسماء والقيم المهمة هنا بنفس التنسيق
    ]

    # بناء ملف النص بتنسيق Netscape
    with open(cookie_file, "w", encoding="utf-8") as f:
        f.write("# Netscape HTTP Cookie File\n")
        # التنسيق المطلوب: domain, tailmatch, path, secure, expires, name, value
        for c in raw_cookies:
            domain = c.get("domain", ".youtube.com")
            name = c.get("name", "")
            value = c.get("value", "")
            # نضع قيم افتراضية للأعمدة الأخرى
            f.write(f"{domain}\tTRUE\t/\tTRUE\t0\t{name}\t{value}\n")
            
    return cookie_file

def get_all_formats(url):
    cookie_path = prepare_engine()
    ydl_opts = {
        'quiet': True, 
        'cookiefile': cookie_path,
        'nocheckcertificate': True, 
        'no_warnings': True,
        # إضافة User-Agent لزيادة الأمان
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        formats_btns = {}
        for f in info.get('formats', []):
            if f.get('vcodec') != 'none' and f.get('acodec') != 'none' and f.get('ext') == 'mp4':
                res = f.get('height')
                if res: formats_btns[f"🎬 {res}p"] = f.get('format_id')
        formats_btns["🎶 Audio | تحميل صوت"] = "bestaudio[ext=m4a]/bestaudio"
        return formats_btns

def run_download(url, format_id, file_path):
    ydl_opts = {
        'outtmpl': file_path,
        'format': format_id,
        'cookiefile': "cookies.txt",
        'nocheckcertificate': True,
        'quiet': True,
        'concurrent_fragment_downloads': 10,
        'continuedl': True,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
