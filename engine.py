def get_all_formats(url):
    ydl_opts = {'quiet': True, 'nocheckcertificate': True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        formats_btns = {} # هنا السر لمنع التكرار
        all_formats = info.get('formats', [])
        
        for f in all_formats:
            if f.get('vcodec') != 'none':
                res = f.get('height')
                if res:
                    label = f"🎬 {res}p"
                    # التحقق: إذا كانت الجودة موجودة لا تضفها مرة أخرى
                    if label not in formats_btns:
                        formats_btns[label] = f.get('format_id')
        
        return formats_btns
