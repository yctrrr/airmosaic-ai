"""Small strict BPCH reader/writer matching the selected native BPCH2 format."""
import pathlib
import struct
import numpy as np

def read(path):
    stream = pathlib.Path(path).open('rb')
    def record():
        raw = stream.read(4)
        if not raw:
            return None
        assert len(raw) == 4
        n = struct.unpack('>i', raw)[0]
        assert 0 <= n <= 100000000
        body = stream.read(n)
        assert len(body) == n and stream.read(4) == raw
        return body
    with stream:
        filetype, title = record(), record()
        assert filetype.strip() == b'CTM bin 02' and len(title) == 80
        blocks = []
        while True:
            a = record()
            if a is None:
                break
            model, dx, dy, halfpolar, center180 = struct.unpack('>20s2f2i', a)
            h = list(struct.unpack('>40si40s2d40s7i', record()))
            body = record()
            assert len(body) == 4*h[6]*h[7]*h[8] and h[-1] == len(body)+8
            data = np.frombuffer(body, dtype='>f4').reshape(tuple(h[6:9]), order='F').copy()
            assert np.isfinite(data).all()
            blocks.append({'model': model, 'dx': dx, 'dy': dy, 'halfpolar': halfpolar, 'center180': center180,
                'header': h, 'data': data})
    return title, blocks

def write(path, title, blocks):
    def pad(v, n):
        return (v.encode('ascii') if isinstance(v, str) else v).ljust(n, b' ')[:n]
    with pathlib.Path(path).open('xb') as stream:
        def record(v):
            size = struct.pack('>i', len(v))
            stream.write(size + v + size)
        record(pad('CTM bin 02', 40)); record(pad(title, 80))
        for b in blocks:
            data = np.asarray(b['data'], dtype='>f4')
            assert data.ndim == 3 and np.isfinite(data).all()
            h = list(b['header'])
            h[0], h[2], h[5] = pad(h[0],40), pad(h[2],40), pad(h[5],40)
            h[6:9] = data.shape
            h[-1] = data.size*4+8
            record(struct.pack('>20s2f2i',pad(b['model'],20),b['dx'],b['dy'],b['halfpolar'],b['center180']))
            record(struct.pack('>40si40s2d40s7i',*h))
            record(data.tobytes(order='F'))

def block(model, dx, dy, category, tracer, units, tau0, tau1, data):
    return {'model':model, 'dx':dx, 'dy':dy, 'halfpolar':1, 'center180':1,
        'header':[category,tracer,units,tau0,tau1,b'',*data.shape,1,1,1,data.size*4+8], 'data':data}
