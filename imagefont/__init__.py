from copy import deepcopy
from io import BytesIO
from pathlib import Path
from xml.etree import ElementTree

from fontTools import ttx
from PIL import Image


class ImageFont:
    def __init__(self):
        self.glyphs = []

    def add(self, image):
        glyph = Image.open(image)
        glyph.thumbnail((128, 128))
        canvas = Image.new('RGBA', (136, 128))
        canvas.paste(glyph, (
            (canvas.width - glyph.width) // 2,
            (canvas.height - glyph.height) // 2
        ))
        self.glyphs.append(canvas)

    def write(self, output_file):
        template = ElementTree.parse(Path(__file__).parent / 'template.ttx')
        glyph_order = template.find('GlyphOrder')
        hmtx = template.find('hmtx')
        cmap14 = template.find('cmap/cmap_format_14')
        cmap12 = template.find('cmap/cmap_format_12')
        cbdt = template.find('CBDT/strikedata')
        eblc = template.find('CBLC/strike/eblc_index_sub_table_1')
        vmtx = template.find('vmtx')

        template.find('maxp/numGlyphs').text = str(len(self.glyphs) + 2)
        template.find(
            'CBLC/strike/bitmapSizeTable/endGlyphIndex'
        ).attrib['value'] = str(len(self.glyphs) + 1)

        for i, glyph in enumerate(self.glyphs):
            image_buffer = BytesIO()
            glyph.save(image_buffer, 'png')
            image_buffer.seek(0)
            raw_image_data = image_buffer.read().hex()

            code_point = 0xe001 + i
            glyph_name = 'uni{:X}'.format(code_point)

            glyph_order_entry = deepcopy(glyph_order.find('GlyphID'))
            glyph_order_entry.attrib['id'] = str(i + 2)
            glyph_order_entry.attrib['name'] = glyph_name
            glyph_order.append(glyph_order_entry)

            hmtx_entry = deepcopy(hmtx.find('mtx'))
            hmtx_entry.attrib['name'] = glyph_name
            hmtx.append(hmtx_entry)

            cmap14_entry = deepcopy(cmap14.find('map'))
            cmap14_entry.attrib['uv'] = hex(code_point)
            cmap14.append(cmap14_entry)

            cmap12_entry = deepcopy(cmap12.find('map'))
            cmap12_entry.attrib['code'] = hex(code_point)
            cmap12_entry.attrib['name'] = glyph_name
            cmap12.append(cmap12_entry)

            cbdt_entry = deepcopy(cbdt.find('cbdt_bitmap_format_17'))
            cbdt_entry.attrib['name'] = glyph_name
            cbdt_entry.find('rawimagedata').text = raw_image_data
            cbdt.append(cbdt_entry)

            eblc_entry = deepcopy(eblc.find('glyphLoc'))
            eblc_entry.attrib['id'] = str(i + 2)
            eblc_entry.attrib['name'] = glyph_name
            eblc.append(eblc_entry)

            vmtx_entry = deepcopy(vmtx.find('mtx'))
            vmtx_entry.attrib['name'] = glyph_name
            vmtx.append(vmtx_entry)

        ttx_buffer = BytesIO()
        template.write(ttx_buffer)
        ttx_buffer.seek(0)
        ttx.ttCompile(ttx_buffer, output_file, ttx.Options(
            [('--recalc-timestamp', False)], 1
        ))
