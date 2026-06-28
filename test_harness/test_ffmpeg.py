import subprocess
import imageio_ffmpeg

FFMPEG_PATH = imageio_ffmpeg.get_ffmpeg_exe()


def test_ffmpeg():
    img_path = "c:/1인기업/Apps/유튜브에이전트/assets/brand/deep_ocean_visual.png"
    audio_path = "c:/1인기업/Apps/유튜브에이전트/assets/brand/deep_ocean_432hz_healing.mp3"
    output_path = "c:/1인기업/Apps/유튜브에이전트/output/test_ffmpeg.mp4"
    srt_path = "c:/1인기업/Apps/유튜브에이전트/output/test.srt"

    with open(srt_path, "w", encoding="utf-8") as f:
        f.write("1\n00:00:01,000 --> 00:00:04,000\nHello World\n\n")

    safe_srt = srt_path.replace("\\", "/").replace(":", "\\:")
    vf = f"scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,subtitles='{safe_srt}'"

    # We will limit output to 5 seconds by using -t 5
    cmd = [
        FFMPEG_PATH,
        "-y",
        "-loop",
        "1",
        "-i",
        img_path,
        "-i",
        audio_path,
        "-vf",
        vf,
        "-c:v",
        "libx264",
        "-tune",
        "stillimage",
        "-c:a",
        "aac",
        "-b:a",
        "192k",
        "-pix_fmt",
        "yuv420p",
        "-t",
        "5",
        output_path,
    ]

    print("Running command:", " ".join(cmd))
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print("Error:", result.stderr)
    else:
        print("Success!")


if __name__ == "__main__":
    test_ffmpeg()
