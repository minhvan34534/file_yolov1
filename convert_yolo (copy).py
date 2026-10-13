import json
import os
import random
import shutil

SOURCE = "braille_image"
OUTPUT = "dataset"

# Label của model
CLASS_NAMES = {
    "braille_dot": 0,
    "braille_cell": 1,
    "braille_line": 2,
}

# Tạo thư mục
for folder in [
    "images/train",
    "images/val",
    "labels/train",
    "labels/val",
]:
    os.makedirs(os.path.join(OUTPUT, folder), exist_ok=True)

files = [
    f for f in os.listdir(SOURCE)
    if f.endswith(".json")
]

random.seed(42)
random.shuffle(files)

split = int(len(files) * 0.8)

train_files = files[:split]
val_files = files[split:]


def convert(json_file, split_name):

    json_path = os.path.join(SOURCE, json_file)

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    image_name = os.path.basename(data["imagePath"])
    image_path = os.path.join(SOURCE, image_name)

    width = data["imageWidth"]
    height = data["imageHeight"]

    label_lines = []

    for shape in data["shapes"]:

        label = shape["label"]

        if label not in CLASS_NAMES:
            print(f"⚠️ Bỏ qua label: {label}")
            continue

        class_id = CLASS_NAMES[label]

        points = shape["points"]

        x1 = min(p[0] for p in points)
        y1 = min(p[1] for p in points)
        x2 = max(p[0] for p in points)
        y2 = max(p[1] for p in points)

        center_x = ((x1 + x2) / 2) / width
        center_y = ((y1 + y2) / 2) / height

        box_width = (x2 - x1) / width
        box_height = (y2 - y1) / height

        label_lines.append(
            f"{class_id} {center_x} {center_y} "
            f"{box_width} {box_height}"
        )

    base_name = os.path.splitext(json_file)[0]

    txt_path = os.path.join(
        OUTPUT,
        "labels",
        split_name,
        base_name + ".txt"
    )

    with open(txt_path, "w", encoding="utf-8") as f:
        f.write("\n".join(label_lines))

    shutil.copy(
        image_path,
        os.path.join(
            OUTPUT,
            "images",
            split_name,
            image_name
        )
    )


for f in train_files:
    convert(f, "train")

for f in val_files:
    convert(f, "val")


# Tạo data.yaml
yaml_path = os.path.join(OUTPUT, "data.yaml")

with open(yaml_path, "w", encoding="utf-8") as f:
    f.write(
        "path: " + os.path.abspath(OUTPUT).replace("\\", "/") + "\n"
        "train: images/train\n"
        "val: images/val\n\n"
        "names:\n"
        "  0: braille_dot\n"
        "  1: braille_cell\n"
        "  2: braille_line\n"
    )

print("✅ CONVERT HOÀN TẤT!")
print("Dataset nằm trong thư mục:", OUTPUT)