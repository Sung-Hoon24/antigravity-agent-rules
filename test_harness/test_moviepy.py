import os
from moviepy import ImageClip, TextClip, CompositeVideoClip


def run():
    img_path = "c:/1인기업/Apps/유튜브에이전트/assets/brand/deep_ocean_visual.png"
    if not os.path.exists(img_path):
        print("Image not found")
        return

    try:
        # Load image
        img_clip = ImageClip(img_path).set_duration(3)

        # Create text
        txt_clip = TextClip("Hello World", fontsize=70, color="white")
        txt_clip = txt_clip.set_position("center").set_duration(3)

        # Compose
        video = CompositeVideoClip([img_clip, txt_clip])

        # Export
        out_path = "c:/1인기업/Apps/유튜브에이전트/output/test_moviepy.mp4"
        video.write_videofile(out_path, fps=24, codec="libx264")
        print(f"Success! Output saved to {out_path}")

    except Exception:
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    run()
