import os, sys, struct, glob

def scan(path):
    """返回 [(type, body_start, box_end)]，深度遍历 moov 子树。"""
    out = []
    with open(path, 'rb') as f:
        def walk(start, end, depth):
            f.seek(start)
            while f.tell() < end:
                pos = f.tell()
                hdr = f.read(8)
                if len(hdr) < 8:
                    return
                size, typ = struct.unpack('>I4s', hdr)
                hdrlen = 8
                if size == 1:
                    size = struct.unpack('>Q', f.read(8))[0]; hdrlen = 16
                if size == 0:
                    size = end - pos
                typ = typ.decode('latin1')
                bs, be = pos + hdrlen, pos + size
                out.append((typ, bs, be, depth))
                if typ in ('moov', 'trak', 'mdia', 'minf', 'stbl', 'edts'):
                    walk(bs, be, depth + 1)
                f.seek(be)
        f.seek(0, 2)
        walk(0, f.tell(), 0)
        return out, f

def probe(path):
    boxes, _ = scan(path)
    info = {'file': os.path.basename(path), 'mb': round(os.path.getsize(path)/1048576, 2)}
    by = {}
    for t, b, e, d in boxes:
        by.setdefault(t, []).append((b, e))
    with open(path, 'rb') as f:
        if 'mvhd' in by:
            b, e = by['mvhd'][0]; f.seek(b)
            ver = f.read(1)[0]; f.read(3)
            if ver == 1:
                f.read(16); ts = struct.unpack('>I', f.read(4))[0]
                dur = struct.unpack('>Q', f.read(8))[0]
            else:
                f.read(8); ts = struct.unpack('>I', f.read(4))[0]
                dur = struct.unpack('>I', f.read(4))[0]
            info['dur_s'] = round(dur / ts, 3)
        for b, e in by.get('tkhd', []):
            f.seek(b); ver = f.read(1)[0]; f.read(3)
            f.read(32 if ver == 1 else 20)   # create/modify/trackID/reserved/duration
            f.read(16)                        # reserved + layer + alt_group + volume + reserved
            f.read(36)                        # matrix
            w = struct.unpack('>I', f.read(4))[0] >> 16
            h = struct.unpack('>I', f.read(4))[0] >> 16
            if w and h:
                info['w'], info['h'] = w, h
                break
        if 'stsz' in by:
            b, e = by['stsz'][0]; f.seek(b); f.read(8)
            info['frames'] = struct.unpack('>I', f.read(4))[0]
        if 'stsd' in by:
            b, e = by['stsd'][0]; f.seek(b + 12)
            ct = f.read(4).decode('latin1', 'replace')
            info['codec'] = ct
    if info.get('frames') and info.get('dur_s'):
        info['fps'] = round(info['frames'] / info['dur_s'], 2)
    return info

d = sys.argv[1]
for p in sorted(glob.glob(os.path.join(d, '*.mp4'))):
    print(probe(p))
