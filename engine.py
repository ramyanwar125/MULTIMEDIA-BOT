import os, yt_dlp, re

def get_all_formats(url):
    ydl_opts = {'quiet': True, 'nocheckcertificate': True, 'no_warnings': True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        formats_btns = {}
        all_formats = info.get('formats', [])
        
        for f in all_formats:
            if f.get('vcodec') != 'none':
                res = f.get('height')
                if res:
                    label = f"🎬 {res}p"
                    # منع التكرار: إذا ظهرت الجودة مرة لا تضفها ثانية
                    if label not in formats_btns:
                        # دمج الصوت تلقائياً للجودات العالية وفيسبوك
                        formats_btns[label] = f"{f.get('format_id')}+bestaudio/best"
        
        # ترتيب الجودات
        def extract_res(label):
            nums = re.findall(r'\d+', label)
            return int(nums[0]) if nums else 0

        sorted_labels = sorted(formats_btns.keys(), key=extract_res, reverse=True)
        final = {l: formats_btns[l] for l in sorted_labels}
        final["🎶 Audio | صوت"] = "bestaudio[ext=m4a]/bestaudio"
        return final

def run_download(url, format_id, file_path):
    ydl_opts = {
        'outtmpl': file_path,
        'format': format_id,
        'merge_output_format': 'mp4',
        'quiet': True
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
