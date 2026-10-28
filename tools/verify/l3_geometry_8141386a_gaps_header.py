"""Narrow original runtime MonoBehaviour header, custom tail deliberately opaque.
provenance: arena/8141386a-windwings-space-shooter-game-p
Consulted native TPK/old captured header contract. No C# memory-offset serialization.
"""
import struct
from tools.verify.geometry_8141386a_atlas_io import sha


def header(blob):
    if len(blob)<32:raise ValueError('truncated runtime MonoBehaviour header')
    game_file,game_pid=struct.unpack_from('<iq',blob,0);enabled=blob[12]
    if enabled not in (0,1) or blob[13:16]!=b'\0'*3:raise ValueError('invalid enabled/padding')
    script_file,script_pid=struct.unpack_from('<iq',blob,16);n=struct.unpack_from('<i',blob,28)[0]
    if n<0 or n>65536 or 32+n>len(blob):raise ValueError('header name length extent')
    name=blob[32:32+n].decode('utf8');end=(32+n+3)//4*4
    if end>len(blob) or any(blob[32+n:end]):raise ValueError('name alignment extent')
    return dict(fields=dict(m_GameObject=dict(m_FileID=game_file,m_PathID=game_pid),m_Enabled=enabled,
                            m_Script=dict(m_FileID=script_file,m_PathID=script_pid),m_Name=name),
                header_end=end,header_sha256=sha(blob[:end]),tail_size=len(blob)-end,tail_sha256=sha(blob[end:]),
                custom_fields=None,scope='Exact native header and opaque original tail; nonempty tail is NOT parsed custom data or absent gameplay state')
