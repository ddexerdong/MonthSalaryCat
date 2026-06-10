#!/usr/bin/env python3
from pathlib import Path
from PIL import Image, ImageSequence, ImageOps


PROJECT_ROOT = Path(__file__).resolve().parents[1]
INPUT_GIF = PROJECT_ROOT / "assets" / "yuexinmiao_original.gif"
HEADER_OUT = PROJECT_ROOT / "Core" / "Inc" / "yuexinmiao_oled_frames.h"
PREVIEW_DIR = PROJECT_ROOT / "build" / "oled_preview"

WIDTH = 128
HEIGHT = 64
FRAME_SIZE = 1024
MIN_FRAMES = 6
MAX_FRAMES = 10


def load_frames(path):
    image = Image.open(path)
    frames = []
    durations = []

    for frame in ImageSequence.Iterator(image):
        rgba = frame.convert("RGBA")
        if rgba.size != (WIDTH, HEIGHT):
            if rgba.size[0] % WIDTH == 0 and rgba.size[1] % HEIGHT == 0:
                rgba = rgba.resize((WIDTH, HEIGHT), Image.Resampling.NEAREST)
            else:
                rgba.thumbnail((WIDTH, HEIGHT), Image.Resampling.LANCZOS)
                canvas = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 255))
                canvas.alpha_composite(rgba, ((WIDTH - rgba.width) // 2, (HEIGHT - rgba.height) // 2))
                rgba = canvas

        gray = ImageOps.grayscale(rgba)
        # Preserve line-art previews without introducing filled regions: pixels that
        # are already bright remain white, dark background remains black.
        bw = gray.point(lambda p: 255 if p >= 96 else 0, mode="1")
        frames.append(bw.convert("1"))
        durations.append(frame.info.get("duration", 100))

    if len(frames) < MIN_FRAMES:
        raise SystemExit(f"Need at least {MIN_FRAMES} frames, got {len(frames)}")
    if len(frames) > MAX_FRAMES:
        step = (len(frames) - 1) / (MAX_FRAMES - 1)
        indices = [round(i * step) for i in range(MAX_FRAMES)]
        frames = [frames[i] for i in indices]
        durations = [durations[i] for i in indices]

    return frames, durations


def frame_to_page_bytes(frame):
    pixels = frame.load()
    data = []
    for page in range(HEIGHT // 8):
        for x in range(WIDTH):
            value = 0
            for bit in range(8):
                y = page * 8 + bit
                if pixels[x, y] != 0:
                    value |= 1 << bit
            data.append(value)
    if len(data) != FRAME_SIZE:
        raise AssertionError(len(data))
    return data


def write_header(frames, durations):
    all_bytes = [frame_to_page_bytes(frame) for frame in frames]
    delay = durations[0] if durations else 100

    lines = [
        "#ifndef YUEXINMIAO_OLED_FRAMES_H",
        "#define YUEXINMIAO_OLED_FRAMES_H",
        "",
        "#include <stdint.h>",
        "",
        "#define YUEXINMIAO_FRAME_WIDTH 128",
        "#define YUEXINMIAO_FRAME_HEIGHT 64",
        "#define YUEXINMIAO_FRAME_SIZE 1024",
        f"#define YUEXINMIAO_FRAME_COUNT {len(frames)}",
        f"#define YUEXINMIAO_FRAME_DELAY_MS {delay}",
        "",
        "#define YXM_FRAME_WIDTH YUEXINMIAO_FRAME_WIDTH",
        "#define YXM_FRAME_HEIGHT YUEXINMIAO_FRAME_HEIGHT",
        "#define YXM_FRAME_SIZE YUEXINMIAO_FRAME_SIZE",
        "#define YXM_FRAME_COUNT YUEXINMIAO_FRAME_COUNT",
        "#define YXM_FRAME_DELAY_MS YUEXINMIAO_FRAME_DELAY_MS",
        "",
        "/*",
        " * Generated from assets/yuexinmiao_original.gif.",
        " * Source in this workspace is the preprocessed preview_128x64.gif.",
        " * Format: 128x64 SSD1306/SSD1315 page order, black background, white pixels.",
        " */",
        "",
        "static const uint8_t yuexinmiao_frames[YUEXINMIAO_FRAME_COUNT][YUEXINMIAO_FRAME_SIZE] = {",
    ]

    for frame_index, data in enumerate(all_bytes):
        lines.append(f"    /* frame {frame_index} */")
        lines.append("    {")
        for i in range(0, FRAME_SIZE, 16):
            chunk = ", ".join(f"0x{byte:02X}" for byte in data[i : i + 16])
            suffix = "," if i + 16 < FRAME_SIZE else ""
            lines.append(f"        {chunk}{suffix}")
        lines.append("    }" + ("," if frame_index + 1 < len(all_bytes) else ""))

    lines.extend(["};", "", "#endif /* YUEXINMIAO_OLED_FRAMES_H */", ""])
    HEADER_OUT.write_text("\n".join(lines), encoding="ascii")


def write_previews(frames, durations):
    PREVIEW_DIR.mkdir(parents=True, exist_ok=True)
    enlarged = []

    for index, frame in enumerate(frames):
        frame_rgb = frame.convert("RGB")
        frame_rgb.save(PREVIEW_DIR / f"frame_{index:02d}.png")
        enlarged.append(frame_rgb.resize((WIDTH * 4, HEIGHT * 4), Image.Resampling.NEAREST))

    first_duration = durations[0] if durations else 100
    enlarged[0].save(
        PREVIEW_DIR / "preview.gif",
        save_all=True,
        append_images=enlarged[1:],
        duration=[d if d else first_duration for d in durations],
        loop=0,
    )

    sheet_cols = len(enlarged)
    sheet = Image.new("RGB", (sheet_cols * WIDTH, HEIGHT), "black")
    for index, frame in enumerate(frames):
        sheet.paste(frame.convert("RGB"), (index * WIDTH, 0))
    sheet.save(PREVIEW_DIR / "contact_sheet.png")


def main():
    if not INPUT_GIF.exists():
        raise SystemExit(f"Missing input: {INPUT_GIF}")

    frames, durations = load_frames(INPUT_GIF)
    write_header(frames, durations)
    write_previews(frames, durations)
    print(f"generated_frames={len(frames)}")
    print(f"header={HEADER_OUT}")
    print(f"preview_dir={PREVIEW_DIR}")


if __name__ == "__main__":
    main()
