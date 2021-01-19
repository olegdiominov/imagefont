# imagefont

Generate a TTF font from a set of raster images.

The font is loosely based on Noto Color Emoji. All images are scaled down to
128x128 pixels and assigned to glyphs in `U+E000` private use area.

Here's an example of what it looks like:

![image](/uploads/9217607a33b127de0de303c734be4edc/image.png)

My original use case for this font is displaying arbitrary images in `i3bar`
(e.g. tiny album art for the currently playing song).

This is a quick proof of concept, so there may be problems with glyph alignment
and compatibility.

## Dependencies

- `fonttools` for converting human-readable/writable XML to TTF.

- `pillow` for image resizing.

## Usage

`python -m imagefont *.png -o imagefont.ttf`
