import os
import yt_dlp

def prepare_engine():
    # استخدام اسم الملف الذي اخترته
    cookie_file = "cookies_stable.txt"
    
    # الكوكيز القوية لتجاوز حظر (Sign in to confirm you’re not a bot)
    cookie_content = """# Netscape HTTP Cookie File
.youtube.com	TRUE	/	TRUE	0	__Secure-1PAPISID	5i84Die2RJBNC2ce/AT2hauHxI6F92xPj_
.youtube.com	TRUE	/	TRUE	0	__Secure-1PSID	g.a0004giEiFc2xdrGVpg52KCe5iEggWIlfVJTzLdmIY_shjAgvHHZJC__lOksy_V1shnK_eMU2QACgYKAWISARYSFQHGX2MiSRiVPtw6IQMxGYvEmCdH4RoVAUF8yKozwvkHQ0076
.youtube.com	TRUE	/	TRUE	0	LOGIN_INFO	AFmmF2swRQIhAJr_X_MAu1PKtQ7YbEoBme3ow5NsWSDax1gAtpwPVsLsAiA7viGmF4Tmg5dEWSZDbAGU_wD1X0KD0dyQCM_i8udTOg:QUQ3MjNmd1paTG9Rdm8tekRXSWxDb292WEQwZVBpbEVwYWNDUlNfVGppVUJxQ1JWYzNoMGRsbFY3cHU1MjRfX0Zwb1J3SmhwU2xrekF4Q3lQY19RTWFvZ01qeDFmVHVScS04WVFOV29nQk5TOTdpUWhTa1VPd3hQSDBENThBUjYwbUlYMUNuNlZQaGFMZVJEajJHU21OZklkV2tKS1FTTFJR
.youtube.com	TRUE	/	TRUE	0	SID	g.a0004giEiFc2xdrGVpg52KCe5iEggWIlfVJTzLdmIY_shjAgvHHZ6A00lT4BcAvf860P256R8QACgYKASISARYSFQHGX2MigyhtRA6u3mymovOefruTiBoVAUF8yKqXLVcp081Qmaiv3aJ2gJvh0076
"""
    
    # تحديث الملف دائماً لضمان عدم تلف الكوكيز
    with open(cookie_file, "w", encoding="utf-8") as f:
        f.write(cookie_content)
    return cookie_file

def get_all_formats(url):
    cookie_path = prepare_engine()
    
    ydl_opts = {
        'quiet': True,
        'cookiefile': cookie_path,
        'nocheckcertificate': True,
        'no_warnings': True,
        # إضافة العميل الأندرويد لتجاوز الحظر
        'extractor_args': {
            'youtube': {
                'player_client': ['android', 'ios'],
                'player_skip': ['webpage', 'configs']
            }
        },
        'user_agent': 'com.google.android.youtube/19.29.37 (Linux; U; Android 11) gzip'
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(url, download=False)
            formats_btns = {}
            
            # جلب الفيديو المدمج (صوت وصورة)
            for f in info.get('formats', []):
                if f.get('vcodec') != 'none' and f.get('acodec') != 'none' and f.get('ext') == 'mp4':
                    res = f.get('height')
                    if res: formats_btns[f"🎬 {res}p"] = f.get('format_id')
            
            # إذا لم يجد جودات محددة يضع الأفضل تلقائياً
            if not formats_btns:
                formats_btns["🎬 Best Quality"] = "best"
                
            # إضافة خيار الصوت
            formats_btns["🎶 Audio | تحميل صوت"] = "bestaudio[ext=m4a]/bestaudio"
            return formats_btns
        except Exception as e:
            print(f"❌ Extraction Error: {e}")
            return {}

def run_download(url, format_id, file_path):
    ydl_opts = {
        'outtmpl': file_path,
        'format': format_id,
        'cookiefile': 'cookies_stable.txt',
        'nocheckcertificate': True,
        'quiet': True,
        'concurrent_fragment_downloads': 15,
        'continuedl': True,
        'buffersize': 1024 * 1024,
        # نستخدم نفس العميل عند التحميل أيضاً
        'extractor_args': {'youtube': {'player_client': ['android']}}
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
