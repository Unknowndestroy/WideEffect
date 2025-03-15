import subprocess

input_video = "video.mp4"
output_video = "video_wide.mp4"

# Videoyu yatayda 3 kat genişletme (en-boy oranını bozarak yayık hale getirme)
ffmpeg_command = [
    "ffmpeg",
    "-i", input_video,
    "-vf", "scale=iw*3:ih,setsar=1",
    "-c:a", "copy",
    output_video
]

# Komutu çalıştır
subprocess.run(ffmpeg_command)
print("İşlem tamamlandı! Yeni video:", output_video)
