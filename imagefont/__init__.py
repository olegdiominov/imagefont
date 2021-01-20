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
        glyph_order_entry_template = glyph_order.find('GlyphID[last()]')
        glyph_order.remove(glyph_order_entry_template)

        hmtx = template.find('hmtx')
        hmtx_entry_template = hmtx.find('mtx[last()]')
        hmtx.remove(hmtx_entry_template)

        cmap14 = template.find('cmap/cmap_format_14')
        cmap14_entry_template = cmap14.find('map')
        cmap14.remove(cmap14_entry_template)

        cmap12 = template.find('cmap/cmap_format_12')
        cmap12_entry_template = cmap12.find('map')
        cmap12.remove(cmap12_entry_template)

        cbdt = template.find('CBDT/strikedata')
        cbdt_entry_template = cbdt.find('cbdt_bitmap_format_17')
        cbdt.remove(cbdt_entry_template)

        eblc = template.find('CBLC/strike/eblc_index_sub_table_1')
        eblc_entry_template = eblc.find('glyphLoc')
        eblc.remove(eblc_entry_template)

        vmtx = template.find('vmtx')
        vmtx_entry_template = vmtx.find('mtx[last()]')
        vmtx.remove(vmtx_entry_template)

        template.find('maxp/numGlyphs').text = str(len(self.glyphs) + 1)
        template.find(
            'CBLC/strike/bitmapSizeTable/endGlyphIndex'
        ).attrib['value'] = str(len(self.glyphs))

        for i, glyph in enumerate(self.glyphs):
            image_buffer = BytesIO()
            glyph.save(image_buffer, 'png')
            image_buffer.seek(0)
            raw_image_data = image_buffer.read().hex()

            code_point = 0xe000 + i
            glyph_name = 'uni{:X}'.format(code_point)

            glyph_order_entry = deepcopy(glyph_order_entry_template)
            glyph_order_entry.attrib['id'] = str(i + 1)
            glyph_order_entry.attrib['name'] = glyph_name
            glyph_order.append(glyph_order_entry)

            hmtx_entry = deepcopy(hmtx_entry_template)
            hmtx_entry.attrib['name'] = glyph_name
            hmtx.append(hmtx_entry)

            cmap14_entry = deepcopy(cmap14_entry_template)
            cmap14_entry.attrib['uv'] = hex(code_point)
            cmap14.append(cmap14_entry)

            cmap12_entry = deepcopy(cmap14_entry_template)
            cmap12_entry.attrib['code'] = hex(code_point)
            cmap12_entry.attrib['name'] = glyph_name
            cmap12.append(cmap12_entry)

            cbdt_entry = deepcopy(cbdt_entry_template)
            cbdt_entry.attrib['name'] = glyph_name
            cbdt_entry.find('rawimagedata').text = raw_image_data
            cbdt.append(cbdt_entry)

            eblc_entry = deepcopy(eblc_entry_template)
            eblc_entry.attrib['id'] = str(i + 1)
            eblc_entry.attrib['name'] = glyph_name
            eblc.append(eblc_entry)

            vmtx_entry = deepcopy(vmtx_entry_template)
            vmtx_entry.attrib['name'] = glyph_name
            vmtx.append(vmtx_entry)

        ttx_buffer = BytesIO()
        template.write(ttx_buffer)
        ttx_buffer.seek(0)
        ttx.ttCompile(ttx_buffer, output_file, ttx.Options(
            [('--recalc-timestamp', False)], 1
        ))
