#!/usr/bin/env python3
"""Render compact 8x8 Korean glyphs into NES 2bpp tile data.

Pillow is imported only when raster rendering is requested. The ordinary
project test interpreter does not bundle Pillow, while the Codex workspace
Python runtime does. This keeps the binary patch logic testable without a
graphics dependency and makes the rendering dependency explicit.
"""

from __future__ import annotations

import argparse
from pathlib import Path


DEFAULT_FONT_CANDIDATES = (
    Path(r"C:\Windows\Fonts\gulim.ttc"),
    Path(r"C:\Windows\Fonts\malgun.ttf"),
    Path(r"C:\Windows\Fonts\NanumGothic.ttf"),
)
TILE_WIDTH = 8
TILE_HEIGHT = 8
TALL_TILE_HEIGHT = 16
SQUARE_TILE_WIDTH = 16
SQUARE_TILE_HEIGHT = 16

# The first proof scene has a deliberately small glyph set. These glyphs are
# drawn as native 8x8 bitmaps instead of downscaling a TrueType outline. Each
# row is an 8-pixel scanline; this keeps the comparison deterministic and lets
# a reviewer judge the actual pixels that go into CHR.
HANDCRAFTED_BITMAPS = {
    "\uCFE0": (".#####..", ".#......", ".#####..", ".#......", "...#....", "...#....", ".#####..", "........"),
    "\uB2C8": (".#...#..", ".#...#..", ".#...#..", ".#...#..", ".#...#..", ".###.#..", ".....#..", "........"),
    "\uB9C8": (".###.#..", ".#.#.#..", ".#.####.", ".###.#..", ".....#..", ".....#..", ".....#..", "........"),
    "\uC0AC": ("...#.#..", "..#..#..", ".#...###", ".#...#..", ".....#..", ".....#..", ".....#..", "........"),
    "\uC11C": ("...#.#..", "..#..#..", ".#.###..", ".#...#..", ".....#..", ".....#..", ".....#..", "........"),
    "\uB458": (".#####..", ".#...#..", ".#####..", "...#....", ".#####..", ".###....", "...#....", ".###...."),
    "\uB7EC": (".###.#..", "...#.#..", ".###.#..", ".#...#..", ".###.#..", ".....#..", ".....#..", "........"),
    "\uBD84": (".#####..", ".#.#.#..", ".#####..", "...#....", ".#####..", ".#......", ".###....", "........"),
    "\uC870": (".#####..", "...#....", ".#####..", ".#####..", "...#....", "...#....", "........", "........"),
    "\uB450": (".#####..", ".#...#..", ".#####..", "...#....", ".#####..", "........", "........", "........"),
    "\uBAA9": (".#####..", ".#...#..", ".#####..", ".#####..", "...#....", "...#....", ".###....", ".#......"),
    "\uC774": ("..###.#.", ".#...#..", ".#...#..", "..###.#.", "......#.", "......#.", "......#.", "........"),
    "\uD070": (".#####..", ".#......", ".#####..", "........", ".#####..", ".#......", ".###....", "........"),
    "\uC77C": ("..###.#.", ".#...#..", ".#...#..", "..###.#.", ".###..#.", "...#..#.", ".###..#.", "........"),
    "\uC57C": ("..###.#.", ".#...#..", ".#.####.", "..###.#.", "....###.", "......#.", "......#.", "........"),
}


def find_korean_font(candidate: str | Path | None = None) -> Path:
    if candidate is not None:
        path = Path(candidate).expanduser()
        if path.is_file():
            return path
        raise FileNotFoundError(f"Korean font not found: {path}")
    for path in DEFAULT_FONT_CANDIDATES:
        if path.is_file():
            return path
    raise FileNotFoundError(
        "No Korean TrueType font found. Pass --font with a readable font path."
    )


def _pillow():
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError as exc:
        raise RuntimeError(
            "Pillow is required to rasterize Korean glyphs. Use the bundled "
            "workspace Python runtime or install Pillow."
        ) from exc
    return Image, ImageDraw, ImageFont


def normalize_glyph_to_bitmap(
    character: str,
    *,
    font_path: str | Path | None = None,
    target_pixels: int = 7,
    source_size: int = 48,
    threshold: int = 92,
) -> list[list[int]]:
    """Return an 8x8 one-bit bitmap with a centered, normalized glyph.

    A high-resolution source glyph is cropped and scaled into a seven-pixel
    box, leaving one pixel of breathing room. This is intentionally compact:
    the target renderer displays one 8x8 sprite tile per source text byte.
    """

    if len(character) != 1:
        raise ValueError("A tile renderer accepts exactly one character")
    if not 1 <= target_pixels <= TILE_WIDTH:
        raise ValueError("target_pixels must fit inside an 8x8 tile")
    Image, ImageDraw, ImageFont = _pillow()
    font = ImageFont.truetype(str(find_korean_font(font_path)), source_size)
    canvas = Image.new("L", (source_size * 2, source_size * 2), 0)
    draw = ImageDraw.Draw(canvas)
    bbox = draw.textbbox((0, 0), character, font=font)
    width = bbox[2] - bbox[0]
    height = bbox[3] - bbox[1]
    if width <= 0 or height <= 0:
        raise ValueError(f"font produced an empty glyph for {character!r}")
    draw.text((source_size // 2 - bbox[0], source_size // 2 - bbox[1]), character, font=font, fill=255)
    content = canvas.getbbox()
    if content is None:
        raise ValueError(f"font produced an empty pixel bitmap for {character!r}")
    glyph = canvas.crop(content)
    scale = min(target_pixels / glyph.width, target_pixels / glyph.height)
    resized = glyph.resize(
        (
            max(1, round(glyph.width * scale)),
            max(1, round(glyph.height * scale)),
        ),
        Image.Resampling.LANCZOS,
    )

    bitmap = [[0 for _ in range(TILE_WIDTH)] for _ in range(TILE_HEIGHT)]
    left = (TILE_WIDTH - resized.width) // 2
    top = (TILE_HEIGHT - resized.height) // 2
    for y in range(resized.height):
        for x in range(resized.width):
            if resized.getpixel((x, y)) >= threshold:
                bitmap[top + y][left + x] = 1
    return bitmap


def normalize_glyph_to_tall_bitmap(
    character: str,
    *,
    font_path: str | Path | None = None,
    source_size: int = 48,
    threshold: int = 92,
) -> list[list[int]]:
    """Return an 8x16 bitmap for the dialogue renderer's vertical tile pair.

    The dialogue queue already reserves two vertical nametable cells per
    source byte. Unlike the 8x8 fallback, this intentionally scales the
    cropped Korean outline to the full 8x16 cell so the additional vertical
    detail becomes real CHR pixels rather than whitespace.
    """

    if len(character) != 1:
        raise ValueError("A tile renderer accepts exactly one character")
    Image, ImageDraw, ImageFont = _pillow()
    font = ImageFont.truetype(str(find_korean_font(font_path)), source_size)
    canvas = Image.new("L", (source_size * 2, source_size * 2), 0)
    draw = ImageDraw.Draw(canvas)
    bbox = draw.textbbox((0, 0), character, font=font)
    width = bbox[2] - bbox[0]
    height = bbox[3] - bbox[1]
    if width <= 0 or height <= 0:
        raise ValueError(f"font produced an empty glyph for {character!r}")
    draw.text(
        (source_size // 2 - bbox[0], source_size // 2 - bbox[1]),
        character,
        font=font,
        fill=255,
    )
    content = canvas.getbbox()
    if content is None:
        raise ValueError(f"font produced an empty pixel bitmap for {character!r}")
    glyph = canvas.crop(content).resize(
        (TILE_WIDTH, TALL_TILE_HEIGHT), Image.Resampling.LANCZOS
    )
    return [
        [1 if glyph.getpixel((x, y)) >= threshold else 0 for x in range(TILE_WIDTH)]
        for y in range(TALL_TILE_HEIGHT)
    ]


def normalize_glyph_to_square_bitmap(
    character: str,
    *,
    font_path: str | Path | None = None,
    target_pixels: int = 15,
    source_size: int = 64,
    threshold: int = 100,
) -> list[list[int]]:
    """Return a centered 16x16 bitmap for a paired 8x16 dialogue cell.

    The dialogue renderer can place two existing 8x16 cells side by side.
    This produces a native 16x16 Korean syllable without inventing a second
    VRAM queue format. Preserve the source aspect ratio while fitting it in a
    15-pixel box so adjacent syllables retain a one-pixel breathing margin.
    """

    if len(character) != 1:
        raise ValueError("A tile renderer accepts exactly one character")
    if not 1 <= target_pixels <= SQUARE_TILE_WIDTH:
        raise ValueError("target_pixels must fit inside a 16x16 tile square")
    Image, ImageDraw, ImageFont = _pillow()
    font = ImageFont.truetype(str(find_korean_font(font_path)), source_size)
    canvas = Image.new("L", (source_size * 2, source_size * 2), 0)
    draw = ImageDraw.Draw(canvas)
    bbox = draw.textbbox((0, 0), character, font=font)
    width = bbox[2] - bbox[0]
    height = bbox[3] - bbox[1]
    if width <= 0 or height <= 0:
        raise ValueError(f"font produced an empty glyph for {character!r}")
    draw.text(
        (source_size // 2 - bbox[0], source_size // 2 - bbox[1]),
        character,
        font=font,
        fill=255,
    )
    content = canvas.getbbox()
    if content is None:
        raise ValueError(f"font produced an empty pixel bitmap for {character!r}")
    glyph = canvas.crop(content)
    scale = min(target_pixels / glyph.width, target_pixels / glyph.height)
    resized = glyph.resize(
        (
            max(1, round(glyph.width * scale)),
            max(1, round(glyph.height * scale)),
        ),
        Image.Resampling.LANCZOS,
    )
    bitmap = [[0 for _ in range(SQUARE_TILE_WIDTH)] for _ in range(SQUARE_TILE_HEIGHT)]
    left = (SQUARE_TILE_WIDTH - resized.width) // 2
    top = (SQUARE_TILE_HEIGHT - resized.height) // 2
    for y in range(resized.height):
        for x in range(resized.width):
            if resized.getpixel((x, y)) >= threshold:
                bitmap[top + y][left + x] = 1
    return bitmap


def handcrafted_glyph_to_bitmap(character: str) -> list[list[int]]:
    """Return a manually designed 8x8 bitmap for a reviewed Korean glyph."""

    if len(character) != 1:
        raise ValueError("A tile renderer accepts exactly one character")
    rows = HANDCRAFTED_BITMAPS.get(character)
    if rows is None:
        raise ValueError(f"No handcrafted 8x8 bitmap is defined for {character!r}")
    if len(rows) != TILE_HEIGHT or any(len(row) != TILE_WIDTH for row in rows):
        raise AssertionError(f"invalid handcrafted bitmap for {character!r}")
    return [[1 if pixel == "#" else 0 for pixel in row] for row in rows]


def glyph_to_bitmap(
    character: str,
    *,
    style: str = "raster",
    **kwargs: object,
) -> list[list[int]]:
    """Render one glyph using an explicitly selected source style."""

    if style == "raster":
        return normalize_glyph_to_bitmap(character, **kwargs)
    if style == "handcrafted":
        if kwargs:
            unsupported = ", ".join(sorted(kwargs))
            raise ValueError(f"handcrafted style does not accept: {unsupported}")
        return handcrafted_glyph_to_bitmap(character)
    raise ValueError(f"unsupported Korean tile style: {style}")


def bitmap_to_nes_2bpp(bitmap: list[list[int]]) -> bytes:
    if len(bitmap) != TILE_HEIGHT or any(len(row) != TILE_WIDTH for row in bitmap):
        raise ValueError("expected an 8x8 bitmap")
    plane0 = bytearray()
    plane1 = bytearray()
    for row in bitmap:
        value = 0
        for column, pixel in enumerate(row):
            if pixel not in (0, 1):
                raise ValueError("bitmap pixels must be 0 or 1")
            value |= pixel << (7 - column)
        # The English reference alphabet uses identical planes, selecting the
        # darkest palette entry for every ink pixel. Match that readable style.
        plane0.append(value)
        plane1.append(value)
    return bytes(plane0 + plane1)


def tall_bitmap_to_nes_2bpp_tiles(bitmap: list[list[int]]) -> tuple[bytes, bytes]:
    """Split one 8x16 bitmap into its top and bottom NES 8x8 tiles."""

    if len(bitmap) != TALL_TILE_HEIGHT or any(len(row) != TILE_WIDTH for row in bitmap):
        raise ValueError("expected an 8x16 bitmap")
    return (
        bitmap_to_nes_2bpp(bitmap[:TILE_HEIGHT]),
        bitmap_to_nes_2bpp(bitmap[TILE_HEIGHT:]),
    )


def square_bitmap_to_nes_2bpp_tiles(
    bitmap: list[list[int]],
) -> tuple[bytes, bytes, bytes, bytes]:
    """Split a 16x16 bitmap into top-left, top-right, bottom-left, bottom-right."""

    if len(bitmap) != SQUARE_TILE_HEIGHT or any(
        len(row) != SQUARE_TILE_WIDTH for row in bitmap
    ):
        raise ValueError("expected a 16x16 bitmap")
    top = bitmap[:TILE_HEIGHT]
    bottom = bitmap[TILE_HEIGHT:]
    return (
        bitmap_to_nes_2bpp([row[:TILE_WIDTH] for row in top]),
        bitmap_to_nes_2bpp([row[TILE_WIDTH:] for row in top]),
        bitmap_to_nes_2bpp([row[:TILE_WIDTH] for row in bottom]),
        bitmap_to_nes_2bpp([row[TILE_WIDTH:] for row in bottom]),
    )


def render_tile(character: str, *, style: str = "raster", **kwargs: object) -> bytes:
    return bitmap_to_nes_2bpp(glyph_to_bitmap(character, style=style, **kwargs))


def render_tall_tiles(
    character: str,
    *,
    font_path: str | Path | None = None,
    threshold: int = 92,
) -> tuple[bytes, bytes]:
    return tall_bitmap_to_nes_2bpp_tiles(
        normalize_glyph_to_tall_bitmap(
            character,
            font_path=font_path,
            threshold=threshold,
        )
    )


def render_square_tiles(
    character: str,
    *,
    font_path: str | Path | None = None,
    target_pixels: int = 15,
    threshold: int = 100,
) -> tuple[bytes, bytes, bytes, bytes]:
    """Render one Korean syllable into four NES tiles for a 16x16 cell."""

    return square_bitmap_to_nes_2bpp_tiles(
        normalize_glyph_to_square_bitmap(
            character,
            font_path=font_path,
            target_pixels=target_pixels,
            threshold=threshold,
        )
    )


def write_preview(
    characters: list[str],
    output: Path,
    *,
    font_path: str | Path | None = None,
    target_pixels: int = 7,
    threshold: int = 92,
    style: str = "raster",
) -> None:
    Image, ImageDraw, ImageFont = _pillow()
    scale = 10
    label_height = 14
    columns = 8
    rows = (len(characters) + columns - 1) // columns
    cell_width = TILE_WIDTH * scale + 12
    cell_height = TILE_HEIGHT * scale + label_height + 8
    image = Image.new("RGB", (columns * cell_width, rows * cell_height), "white")
    draw = ImageDraw.Draw(image)
    label_font = ImageFont.load_default()
    for index, character in enumerate(characters):
        render_options: dict[str, object] = {}
        if style == "raster":
            render_options = {
                "font_path": font_path,
                "target_pixels": target_pixels,
                "threshold": threshold,
            }
        bitmap = glyph_to_bitmap(character, style=style, **render_options)
        origin_x = (index % columns) * cell_width + 6
        origin_y = (index // columns) * cell_height + label_height
        draw.text((origin_x, origin_y - label_height), character, fill="black", font=label_font)
        for y, row in enumerate(bitmap):
            for x, pixel in enumerate(row):
                color = "black" if pixel else "white"
                draw.rectangle(
                    (
                        origin_x + x * scale,
                        origin_y + y * scale,
                        origin_x + (x + 1) * scale - 1,
                        origin_y + (y + 1) * scale - 1,
                    ),
                    fill=color,
                )
    output.parent.mkdir(parents=True, exist_ok=True)
    image.save(output)


def write_tall_preview(
    characters: list[str],
    output: Path,
    *,
    font_path: str | Path | None = None,
    threshold: int = 92,
) -> None:
    """Write an enlarged preview of the literal 8x16 tile pairs."""

    Image, ImageDraw, ImageFont = _pillow()
    scale = 8
    label_height = 14
    columns = 8
    rows = (len(characters) + columns - 1) // columns
    cell_width = TILE_WIDTH * scale + 12
    cell_height = TALL_TILE_HEIGHT * scale + label_height + 8
    image = Image.new("RGB", (columns * cell_width, rows * cell_height), "white")
    draw = ImageDraw.Draw(image)
    label_font = ImageFont.load_default()
    for index, character in enumerate(characters):
        bitmap = normalize_glyph_to_tall_bitmap(
            character,
            font_path=font_path,
            threshold=threshold,
        )
        origin_x = (index % columns) * cell_width + 6
        origin_y = (index // columns) * cell_height + label_height
        draw.text((origin_x, origin_y - label_height), character, fill="black", font=label_font)
        for y, row in enumerate(bitmap):
            for x, pixel in enumerate(row):
                draw.rectangle(
                    (
                        origin_x + x * scale,
                        origin_y + y * scale,
                        origin_x + (x + 1) * scale - 1,
                        origin_y + (y + 1) * scale - 1,
                    ),
                    fill="black" if pixel else "white",
                )
    output.parent.mkdir(parents=True, exist_ok=True)
    image.save(output)


def write_square_preview(
    characters: list[str],
    output: Path,
    *,
    font_path: str | Path | None = None,
    target_pixels: int = 15,
    threshold: int = 100,
) -> None:
    """Write an enlarged preview of literal 16x16 paired-cell glyphs."""

    Image, ImageDraw, ImageFont = _pillow()
    scale = 7
    label_height = 14
    columns = 8
    rows = (len(characters) + columns - 1) // columns
    cell_width = SQUARE_TILE_WIDTH * scale + 12
    cell_height = SQUARE_TILE_HEIGHT * scale + label_height + 8
    image = Image.new("RGB", (columns * cell_width, rows * cell_height), "white")
    draw = ImageDraw.Draw(image)
    label_font = ImageFont.load_default()
    for index, character in enumerate(characters):
        bitmap = normalize_glyph_to_square_bitmap(
            character,
            font_path=font_path,
            target_pixels=target_pixels,
            threshold=threshold,
        )
        origin_x = (index % columns) * cell_width + 6
        origin_y = (index // columns) * cell_height + label_height
        draw.text((origin_x, origin_y - label_height), character, fill="black", font=label_font)
        for y, row in enumerate(bitmap):
            for x, pixel in enumerate(row):
                draw.rectangle(
                    (
                        origin_x + x * scale,
                        origin_y + y * scale,
                        origin_x + (x + 1) * scale - 1,
                        origin_y + (y + 1) * scale - 1,
                    ),
                    fill="black" if pixel else "white",
                )
    output.parent.mkdir(parents=True, exist_ok=True)
    image.save(output)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("characters", help="Characters to render into a preview sheet")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--font")
    parser.add_argument("--target-pixels", type=int, default=7)
    parser.add_argument("--threshold", type=int, default=92)
    parser.add_argument("--style", choices=("raster", "handcrafted"), default="raster")
    args = parser.parse_args()
    write_preview(
        list(args.characters),
        args.output,
        font_path=args.font,
        target_pixels=args.target_pixels,
        threshold=args.threshold,
        style=args.style,
    )
    print(f"preview={args.output}")
    print(f"font={find_korean_font(args.font)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
