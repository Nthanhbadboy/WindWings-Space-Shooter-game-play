import base64
import copy
from pathlib import Path
import struct
import sys
import unittest
sys.path.insert(0,str(Path('tools/recovery').resolve()))
from sprite_pixel_audit import decode_mesh,edge_padding,rounded_box,reconstruct


def mesh_fixture():
    positions=[(0.,0.,0.),(2.,0.,0.),(2.,2.,0.),(0.,2.,0.)]
    blob=b''.join(struct.pack('<3f',*p) for p in positions)
    blob+=b'\x00'*((-len(blob))%16)+b'\x00'*32
    return dict(m_VertexData=dict(m_VertexCount=4,m_Channels=[dict(stream=0,offset=0,format=0,dimension=3),
        dict(stream=0,offset=0,format=0,dimension=0),dict(stream=0,offset=0,format=0,dimension=0),
        dict(stream=0,offset=0,format=0,dimension=0),dict(stream=1,offset=0,format=0,dimension=2)],
        m_DataSize=dict(bytes_base64=base64.b64encode(blob).decode())),
        m_IndexBuffer=list(struct.pack('<6H',0,1,2,0,2,3)),m_SubMeshes=[dict(firstByte=0,indexCount=6,topology=0,baseVertex=0)])


class SpritePixelAuditTests(unittest.TestCase):
    def test_decode_float_positions_and_uint16_triangles(self):
        positions,triangles,proof=decode_mesh(mesh_fixture())
        self.assertEqual(positions,[(0,0,0),(2,0,0),(2,2,0),(0,2,0)])
        self.assertEqual(triangles,[(0,1,2),(0,2,3)])
        self.assertTrue(proof['uv_all_zero'])

    def test_nonzero_uv_is_not_silently_masked(self):
        mesh=mesh_fixture();blob=bytearray(base64.b64decode(mesh['m_VertexData']['m_DataSize']['bytes_base64']))
        blob[48:52]=struct.pack('<f',.5)
        mesh['m_VertexData']['m_DataSize']['bytes_base64']=base64.b64encode(blob).decode()
        with self.assertRaises(ValueError):decode_mesh(mesh)

    def test_invalid_channels_indices_and_truncation_rejected(self):
        for mutation in ('layout','index','truncated','topology'):
            with self.subTest(mutation=mutation):
                mesh=mesh_fixture()
                if mutation=='layout':mesh['m_VertexData']['m_Channels'][0]['format']=1
                elif mutation=='index':mesh['m_IndexBuffer'][0]=255
                elif mutation=='topology':mesh['m_SubMeshes'][0]['topology']=1
                else:mesh['m_VertexData']['m_DataSize']['bytes_base64']='AA=='
                with self.assertRaises(ValueError):decode_mesh(mesh)

    def test_fractional_boundary_rounding_and_padding_not_clamping(self):
        rect=dict(x=0.,y=201.9034881591797,width=311.,height=311.)
        self.assertEqual(rounded_box(rect),[0,202,311,513])
        self.assertEqual(edge_padding(rect,512,512),dict(left=0,bottom=0,right=0,top=1))

    def test_round_each_boundary_not_width(self):
        self.assertEqual(rounded_box(dict(x=.5,y=0.,width=1.,height=2.)),[0,0,2,2])

    def test_bottom_origin_crop_and_final_flip(self):
        try:from PIL import Image
        except ImportError:self.skipTest('Pillow only needed for pixel fixtures; CI pixel audit installs pinned Pillow')
        texture=Image.new('RGBA',(2,2));texture.putdata([(255,0,0,255),(0,255,0,255),(0,0,255,255),(255,255,0,255)])
        g=dict(texture_rect=dict(x=0,y=0,width=2,height=2),settings=dict(packed=False,packing_rotation=0,packing_mode=0))
        rendered,_=reconstruct(texture,g,mesh_fixture(),1.)
        self.assertEqual(rendered.tobytes(),texture.tobytes())
        g['settings'].update(packed=True,packing_rotation=1)
        flipped,_=reconstruct(texture,g,mesh_fixture(),1.)
        self.assertEqual(flipped.tobytes(),texture.transpose(Image.Transpose.FLIP_LEFT_RIGHT).tobytes())

    def test_transparent_triangle_mask_keeps_original_alpha(self):
        try:from PIL import Image
        except ImportError:self.skipTest('Pillow only needed for pixel fixtures; CI pixel audit installs pinned Pillow')
        texture=Image.new('RGBA',(2,2),(12,34,56,99))
        mesh=mesh_fixture();mesh['m_IndexBuffer']=list(struct.pack('<3H',0,1,2));mesh['m_SubMeshes'][0]['indexCount']=3
        g=dict(texture_rect=dict(x=0,y=0,width=2,height=2),settings=dict(packed=False,packing_rotation=0,packing_mode=0))
        image,_=reconstruct(texture,g,mesh,1.)
        self.assertEqual(set(image.getchannel('A').getdata()),{0,99})

if __name__=='__main__':unittest.main()
