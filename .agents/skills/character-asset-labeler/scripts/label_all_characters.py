import os
import shutil
import datetime
from PIL import Image, ImageDraw, ImageFont

# Define characters mapping
CHARACTERS = {
    "Rubia": {"name": "Rubia", "role": "Project Director"},
    "Ravia": {"name": "Ravia", "role": "Planning Director"},
    "Intella": {"name": "Intella", "role": "Research Lead"},
    "Cordia": {"name": "Cordia", "role": "Technical Lead"},
    "Signa": {"name": "Signa", "role": "Optimization Lead"},
    "Guardia": {"name": "Guardia", "role": "Safety Lead"},
}


def label_image_premium_v2(img_path, name, role, font_dir):
    try:
        img = Image.open(img_path)
        if img.mode != "RGBA":
            img = img.convert("RGBA")

        width, height = img.size
        overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)

        # Bar height: 18% of image height
        bar_height = int(height * 0.18)
        bar_y_start = height - bar_height

        # Draw Sleek Horizontal Two-Stage Gradient
        base_color = (10, 10, 22)
        for x in range(width):
            ratio = x / width
            if ratio < 0.55:
                sub_ratio = ratio / 0.55
                a = int(242 * (1 - sub_ratio) + 190 * sub_ratio)
            else:
                sub_ratio = (ratio - 0.55) / 0.45
                a = int(190 * (1 - sub_ratio) + 0 * sub_ratio)
            draw.line(
                [(x, bar_y_start), (x, height)],
                fill=(base_color[0], base_color[1], base_color[2], a),
            )

        # Draw Top Gold Glowing Border Line
        for x in range(width):
            ratio = x / width
            if ratio < 0.6:
                a = int(220 * (1 - ratio / 0.6 * 0.3))
            else:
                a = int(154 * (1 - (ratio - 0.6) / 0.4))
            draw.point((x, bar_y_start), fill=(230, 190, 120, a))
            if height > 500:
                draw.point((x, bar_y_start + 1), fill=(230, 190, 120, int(a * 0.6)))

        # Fonts
        cursive_path = os.path.join(font_dir, "DancingScript-Variable.ttf")
        sans_path = "C:\\Windows\\Fonts\\segoeuib.ttf"
        if not os.path.exists(sans_path):
            sans_path = "C:\\Windows\\Fonts\\arialbd.ttf"

        name_font_size = int(bar_height * 0.52)
        role_font_size = int(bar_height * 0.28)

        try:
            name_font = ImageFont.truetype(cursive_path, name_font_size)
        except Exception:
            name_font = ImageFont.load_default()

        try:
            role_font = ImageFont.truetype(sans_path, role_font_size)
        except Exception:
            role_font = ImageFont.load_default()

        role_text = role.upper()
        try:
            bbox_name = draw.textbbox((0, 0), name, font=name_font)
            name_w = bbox_name[2] - bbox_name[0]
            bbox_name[3] - bbox_name[1]
        except Exception:
            name_w = int(name_font_size * len(name) * 0.55)

        try:
            bbox_role = draw.textbbox((0, 0), role_text, font=role_font)
            bbox_role[2] - bbox_role[0]
            role_h = bbox_role[3] - bbox_role[1]
        except Exception:
            int(role_font_size * len(role_text) * 0.6)
            role_h = role_font_size

        padding_x = int(width * 0.08)
        name_x = padding_x
        name_y = (
            bar_y_start + (bar_height - name_font_size) // 2 - int(name_font_size * 0.1)
        )

        divider_x = name_x + name_w + int(width * 0.03)
        divider_y_start = bar_y_start + int(bar_height * 0.25)
        divider_y_end = height - int(bar_height * 0.25)

        role_x = divider_x + int(width * 0.03)
        role_y = bar_y_start + (bar_height - role_h) // 2

        # A. Draw Name
        draw.text((name_x + 1, name_y + 1), name, fill=(0, 0, 0, 150), font=name_font)
        draw.text((name_x, name_y), name, fill=(255, 255, 255, 255), font=name_font)

        # B. Draw Divider
        draw.line(
            [(divider_x, divider_y_start), (divider_x, divider_y_end)],
            fill=(230, 190, 120, 150),
            width=2,
        )

        # C. Draw Role
        for dx, dy in [
            (-1, -1),
            (-1, 1),
            (1, -1),
            (1, 1),
            (0, -1),
            (0, 1),
            (-1, 0),
            (1, 0),
        ]:
            draw.text(
                (role_x + dx, role_y + dy),
                role_text,
                fill=(0, 0, 0, 180),
                font=role_font,
            )
        draw.text(
            (role_x, role_y), role_text, fill=(255, 255, 255, 255), font=role_font
        )

        combined = Image.alpha_composite(img, overlay)
        combined.save(img_path, "PNG")
        return True
    except Exception as e:
        print(f"Error labeling {img_path}: {e}")
        return False


def run_label_batch(project_root):
    base_dir = os.path.join(project_root, "assets", "characters")
    backup_base = os.path.join(project_root, "backups")
    font_dir = os.path.join(project_root, "assets", "fonts")

    # 1. Create Backup
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = os.path.join(backup_base, f"characters_backup_{timestamp}")
    os.makedirs(backup_dir, exist_ok=True)

    print(f"Backing up characters directory to: {backup_dir}")
    for char in CHARACTERS.keys():
        char_src = os.path.join(base_dir, char)
        char_dst = os.path.join(backup_dir, char)
        if os.path.exists(char_src):
            shutil.copytree(char_src, char_dst)

    # 2. Process Files (Skipping group photos)
    total_files = 0
    success_files = 0
    skipped_files = 0
    for folder, info in CHARACTERS.items():
        folder_path = os.path.join(base_dir, folder)
        if not os.path.exists(folder_path):
            continue

        for filename in os.listdir(folder_path):
            if not filename.lower().endswith(".png"):
                continue
            if "_test" in filename.lower():
                continue

            # Skip group photos: with_leader and vacation
            if "with_leader" in filename.lower() or "vacation" in filename.lower():
                skipped_files += 1
                continue

            file_path = os.path.join(folder_path, filename)
            total_files += 1
            if label_image_premium_v2(file_path, info["name"], info["role"], font_dir):
                success_files += 1

    print(
        f"Successfully processed {success_files}/{total_files} files (skipped {skipped_files} group photos)."
    )


if __name__ == "__main__":
    project_root = r"c:\1인기업\Apps\유튜브에이전트"
    run_label_batch(project_root)
