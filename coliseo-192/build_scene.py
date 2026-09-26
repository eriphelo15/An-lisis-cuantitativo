"""Roma, año 192 d. C.: el Coliseo completo y sus alrededores, construido con código para Blender (Cycles).

Uso:  python3 build_scene.py <salida.blend>
Coordenadas en metros: x = este, y = norte, z = altura. El Coliseo está centrado en el origen.
"""
import bpy, math, random, sys
import numpy as np
from mathutils import Vector, Matrix

R = random.Random(192)
OUT = sys.argv[-1] if sys.argv[-1].endswith('.blend') else '/tmp/roma192.blend'

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene

# ------------------------------------------------------------------ materiales
def principled(name, color, rough=0.8, metal=0.0, extra=None):
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree; p = nt.nodes['Principled BSDF']
    p.inputs['Base Color'].default_value = (*color, 1)
    p.inputs['Roughness'].default_value = rough
    p.inputs['Metallic'].default_value = metal
    if extra: extra(nt, p)
    return m

def tex_coords(nt, kind='UV'):
    tc = nt.nodes.new('ShaderNodeTexCoord')
    return tc.outputs[kind]

def stone(nt, p, c1, c2, mortar, bw=1.9, rh=0.62, noise_scale=1.3, bump=0.25, joints=True):
    """Bloques de piedra en hiladas (Brick Texture en UV métricas) + manchas + relieve."""
    uv = tex_coords(nt, 'UV'); obj = tex_coords(nt, 'Object')
    n1 = nt.nodes.new('ShaderNodeTexNoise'); n1.inputs['Scale'].default_value = noise_scale; n1.inputs['Detail'].default_value = 8
    nt.links.new(obj, n1.inputs['Vector'])
    n2 = nt.nodes.new('ShaderNodeTexNoise'); n2.inputs['Scale'].default_value = 18; n2.inputs['Detail'].default_value = 6
    nt.links.new(obj, n2.inputs['Vector'])
    ramp = nt.nodes.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].color = (*c1, 1); ramp.color_ramp.elements[1].color = (*c2, 1)
    nt.links.new(n1.outputs['Fac'], ramp.inputs['Fac'])
    col = ramp.outputs['Color']
    if joints:
        br = nt.nodes.new('ShaderNodeTexBrick')
        br.inputs['Scale'].default_value = 1.0; br.inputs['Mortar Size'].default_value = 0.012
        br.inputs['Brick Width'].default_value = bw; br.inputs['Row Height'].default_value = rh
        br.inputs['Color1'].default_value = (1, 1, 1, 1); br.inputs['Color2'].default_value = (0.86, 0.84, 0.8, 1)
        br.inputs['Mortar'].default_value = (*mortar, 1); br.offset = 0.5
        nt.links.new(uv, br.inputs['Vector'])
        mul = nt.nodes.new('ShaderNodeMix'); mul.data_type = 'RGBA'; mul.blend_type = 'MULTIPLY'
        mul.inputs['Factor'].default_value = 1.0
        nt.links.new(col, mul.inputs[6]); nt.links.new(br.outputs['Color'], mul.inputs[7]); col = mul.outputs[2]
    speck = nt.nodes.new('ShaderNodeMix'); speck.data_type = 'RGBA'; speck.blend_type = 'OVERLAY'
    speck.inputs['Factor'].default_value = 0.35
    nt.links.new(col, speck.inputs[6]); nt.links.new(n2.outputs['Color'], speck.inputs[7])
    nt.links.new(speck.outputs[2], p.inputs['Base Color'])
    bmp = nt.nodes.new('ShaderNodeBump'); bmp.inputs['Strength'].default_value = bump; bmp.inputs['Distance'].default_value = 0.02
    h = n2.outputs['Fac']
    if joints:
        add = nt.nodes.new('ShaderNodeMath'); add.operation = 'MULTIPLY'
        nt.links.new(n2.outputs['Fac'], add.inputs[0]); nt.links.new(br.outputs['Fac'], add.inputs[1])
        inv = nt.nodes.new('ShaderNodeMath'); inv.operation = 'SUBTRACT'; inv.inputs[0].default_value = 1.0
        nt.links.new(add.outputs[0], inv.inputs[1]); h = inv.outputs[0]
    nt.links.new(h, bmp.inputs['Height'])
    nt.links.new(bmp.outputs['Normal'], p.inputs['Normal'])

def noisy(nt, p, c1, c2, scale=0.6, bump=0.15, fine=25):
    obj = tex_coords(nt, 'Object')
    n = nt.nodes.new('ShaderNodeTexNoise'); n.inputs['Scale'].default_value = scale; n.inputs['Detail'].default_value = 6
    nt.links.new(obj, n.inputs['Vector'])
    ramp = nt.nodes.new('ShaderNodeValToRGB'); ramp.color_ramp.elements[0].color = (*c1, 1); ramp.color_ramp.elements[1].color = (*c2, 1)
    nt.links.new(n.outputs['Fac'], ramp.inputs['Fac']); nt.links.new(ramp.outputs['Color'], p.inputs['Base Color'])
    n2 = nt.nodes.new('ShaderNodeTexNoise'); n2.inputs['Scale'].default_value = fine; nt.links.new(obj, n2.inputs['Vector'])
    b = nt.nodes.new('ShaderNodeBump'); b.inputs['Strength'].default_value = bump
    nt.links.new(n2.outputs['Fac'], b.inputs['Height']); nt.links.new(b.outputs['Normal'], p.inputs['Normal'])

def tiles(nt, p):
    uv = tex_coords(nt, 'UV')
    wv = nt.nodes.new('ShaderNodeTexWave'); wv.wave_type = 'BANDS'; wv.bands_direction = 'X'
    wv.inputs['Scale'].default_value = 1.6; wv.inputs['Distortion'].default_value = 0.0
    nt.links.new(uv, wv.inputs['Vector'])
    obj = tex_coords(nt, 'Object')
    n = nt.nodes.new('ShaderNodeTexNoise'); n.inputs['Scale'].default_value = 0.08; nt.links.new(obj, n.inputs['Vector'])
    ramp = nt.nodes.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].color = (0.33, 0.12, 0.06, 1); ramp.color_ramp.elements[1].color = (0.62, 0.3, 0.17, 1)
    nt.links.new(n.outputs['Fac'], ramp.inputs['Fac']); nt.links.new(ramp.outputs['Color'], p.inputs['Base Color'])
    b = nt.nodes.new('ShaderNodeBump'); b.inputs['Strength'].default_value = 0.6
    nt.links.new(wv.outputs['Fac'], b.inputs['Height']); nt.links.new(b.outputs['Normal'], p.inputs['Normal'])

MAT = {}
MAT['trav'] = principled('travertino', (0.8, 0.72, 0.58), 0.72, extra=lambda nt, p: stone(nt, p, (0.58, 0.51, 0.4), (0.71, 0.63, 0.51), (0.42, 0.36, 0.28)))
MAT['travIn'] = principled('travertino_int', (0.6, 0.55, 0.45), 0.85, extra=lambda nt, p: stone(nt, p, (0.52, 0.47, 0.39), (0.63, 0.57, 0.47), (0.4, 0.35, 0.29)))
MAT['marble'] = principled('marmol', (0.9, 0.88, 0.84), 0.32, extra=lambda nt, p: noisy(nt, p, (0.72, 0.7, 0.66), (0.84, 0.82, 0.78), 0.4, 0.05))
MAT['bronze'] = principled('bronce_dorado', (0.9, 0.62, 0.3), 0.22, 1.0)
MAT['bronzeDark'] = principled('bronce', (0.45, 0.3, 0.16), 0.35, 1.0)
MAT['sand'] = principled('arena', (0.78, 0.66, 0.48), 1.0, extra=lambda nt, p: noisy(nt, p, (0.72, 0.6, 0.43), (0.84, 0.73, 0.55), 0.15, 0.25, 40))
MAT['tile'] = principled('tejas', (0.55, 0.25, 0.14), 0.75, extra=lambda nt, p: tiles(nt, p))
MAT['goldRoof'] = principled('tejas_bronce', (0.85, 0.6, 0.3), 0.3, 1.0, extra=lambda nt, p: tiles(nt, p) or None)
MAT['goldRoof'].node_tree.nodes['Principled BSDF'].inputs['Metallic'].default_value = 1.0
MAT['brick'] = principled('ladrillo', (0.55, 0.3, 0.2), 0.9, extra=lambda nt, p: stone(nt, p, (0.46, 0.24, 0.15), (0.62, 0.36, 0.23), (0.62, 0.56, 0.47), 0.6, 0.08, 2.0, 0.35))
for k, c in {'ochre': (0.72, 0.5, 0.28), 'cream': (0.8, 0.7, 0.55), 'red': (0.55, 0.25, 0.16), 'pink': (0.76, 0.52, 0.42), 'white': (0.83, 0.8, 0.74)}.items():
    MAT['plaster_' + k] = principled('estuco_' + k, c, 0.9, extra=lambda nt, p, c=c: noisy(nt, p, tuple(x * 0.82 for x in c), c, 0.3, 0.2))
MAT['granite'] = principled('granito', (0.45, 0.44, 0.42), 0.45, extra=lambda nt, p: noisy(nt, p, (0.33, 0.32, 0.31), (0.55, 0.53, 0.5), 3, 0.1))
MAT['basalt'] = principled('basalto', (0.2, 0.2, 0.2), 0.7, extra=lambda nt, p: stone(nt, p, (0.14, 0.14, 0.15), (0.26, 0.25, 0.24), (0.1, 0.1, 0.1), 0.7, 0.55, 1.0, 0.4))
MAT['pave'] = principled('losas', (0.55, 0.5, 0.42), 0.8, extra=lambda nt, p: stone(nt, p, (0.46, 0.42, 0.35), (0.6, 0.55, 0.46), (0.3, 0.27, 0.22), 1.4, 1.0, 0.8, 0.3))
MAT['ground'] = principled('terreno', (0.42, 0.38, 0.26), 1.0, extra=lambda nt, p: noisy(nt, p, (0.3, 0.3, 0.17), (0.5, 0.43, 0.28), 0.01, 0.3, 3))
MAT['leaf'] = principled('follaje', (0.12, 0.2, 0.08), 0.85, extra=lambda nt, p: noisy(nt, p, (0.07, 0.13, 0.05), (0.18, 0.26, 0.1), 0.5, 0.6, 8))
MAT['wood'] = principled('madera', (0.35, 0.22, 0.12), 0.7)
MAT['dark'] = principled('sombra', (0.02, 0.018, 0.015), 1.0)
MAT['water'] = principled('agua', (0.3, 0.45, 0.5), 0.05)
MAT['water'].node_tree.nodes['Principled BSDF'].inputs['Transmission Weight'].default_value = 0.6
MAT['purple'] = principled('purpura', (0.28, 0.04, 0.12), 0.7)
MAT['canvas'] = principled('lona', (0.86, 0.8, 0.68), 0.9)
MAT['canvas2'] = principled('lona_ocre', (0.72, 0.5, 0.3), 0.9)
for m in (MAT['canvas'], MAT['canvas2']):
    m.node_tree.nodes['Principled BSDF'].inputs['Transmission Weight'].default_value = 0.0
    m.node_tree.nodes['Principled BSDF'].inputs['Subsurface Weight'].default_value = 0.15
# tonos de ropa para la multitud
CLOTH = {}
for i, c in enumerate([(0.85, 0.83, 0.76), (0.8, 0.78, 0.7), (0.55, 0.2, 0.14), (0.2, 0.28, 0.45), (0.62, 0.5, 0.3), (0.35, 0.42, 0.25), (0.7, 0.6, 0.45), (0.5, 0.12, 0.2), (0.25, 0.22, 0.2)]):
    CLOTH[i] = principled(f'tela_{i}', c, 0.95)
MAT['skin'] = principled('piel', (0.62, 0.42, 0.3), 0.6)
MAT['skin'].node_tree.nodes['Principled BSDF'].inputs['Subsurface Weight'].default_value = 0.2

# ------------------------------------------------------------------ constructor de mallas
class Builder:
    """Acumula caras con material; UV métricas por proyección según la normal de cada cara."""
    def __init__(self, name):
        self.name = name; self.V = []; self.F = []; self.M = []; self.mats = []
    def mi(self, key):
        m = MAT[key] if isinstance(key, str) else key
        if m not in self.mats: self.mats.append(m)
        return self.mats.index(m)
    def face(self, pts, mat):
        i = len(self.V); self.V.extend(pts); self.F.append(list(range(i, i + len(pts)))); self.M.append(self.mi(mat))
    def add(self, faces, M=None, mat=None):
        for pts, mk in faces:
            if M is not None:
                pts = [tuple((M @ Vector(p))) for p in pts]
            self.face(pts, mat or mk)
    def build(self, collection=None, smooth=False):
        me = bpy.data.meshes.new(self.name)
        me.from_pydata(self.V, [], self.F)
        for m in self.mats: me.materials.append(m)
        me.polygons.foreach_set('material_index', self.M)
        # UV métricas
        uvl = me.uv_layers.new(name='UV')
        n = len(me.polygons)
        normals = np.zeros(n * 3); me.polygons.foreach_get('normal', normals); normals = normals.reshape(-1, 3)
        co = np.zeros(len(me.vertices) * 3); me.vertices.foreach_get('co', co); co = co.reshape(-1, 3)
        lv = np.zeros(len(me.loops), dtype=np.int32); me.loops.foreach_get('vertex_index', lv)
        ls = np.zeros(n, dtype=np.int32); me.polygons.foreach_get('loop_start', ls)
        lt = np.zeros(n, dtype=np.int32); me.polygons.foreach_get('loop_total', lt)
        poly_of_loop = np.repeat(np.arange(n), lt)
        N = normals[poly_of_loop]; P = co[lv]
        horiz = np.abs(N[:, 2]) > 0.7
        t = np.stack([-N[:, 1], N[:, 0]], 1); tl = np.linalg.norm(t, axis=1, keepdims=True); tl[tl == 0] = 1; t = t / tl
        u = np.where(horiz, P[:, 0], P[:, 0] * t[:, 0] + P[:, 1] * t[:, 1])
        v = np.where(horiz, P[:, 1], P[:, 2])
        uvl.data.foreach_set('uv', np.stack([u, v], 1).ravel())
        me.validate(); me.update()
        if smooth: me.shade_smooth()
        ob = bpy.data.objects.new(self.name, me)
        (collection or scene.collection).objects.link(ob)
        return ob

# primitivas (listas de (puntos, material))
def box(x0, x1, y0, y1, z0, z1, m):
    v = [(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0), (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)]
    q = [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]
    return [([v[i] for i in f], m) for f in q]

def prism(outline, y0, y1, m, cap=True):
    """Contorno (x,z) extruido en y (de y0 a y1)."""
    out = []
    front = [(x, y1, z) for x, z in outline]; back = [(x, y0, z) for x, z in reversed(outline)]
    if cap: out += [(front, m), (back, m)]
    n = len(outline)
    for i in range(n):
        (xa, za), (xb, zb) = outline[i], outline[(i + 1) % n]
        out.append(([(xa, y0, za), (xb, y0, zb), (xb, y1, zb), (xa, y1, za)], m))
    return out

def cyl(cx, cy, r0, r1, z0, z1, m, seg=12, a0=0, a1=2 * math.pi, cap=True):
    out = []; full = abs(a1 - a0 - 2 * math.pi) < 1e-6
    k = seg if full else seg + 1
    ang = [a0 + (a1 - a0) * i / seg for i in range(k)]
    for i in range(seg):
        a, b = ang[i], ang[(i + 1) % k] if full else ang[i + 1]
        out.append(([(cx + r0 * math.cos(a), cy + r0 * math.sin(a), z0), (cx + r0 * math.cos(b), cy + r0 * math.sin(b), z0),
                     (cx + r1 * math.cos(b), cy + r1 * math.sin(b), z1), (cx + r1 * math.cos(a), cy + r1 * math.sin(a), z1)], m))
    if cap:
        top = [(cx + r1 * math.cos(a), cy + r1 * math.sin(a), z1) for a in ang]
        bot = [(cx + r0 * math.cos(a), cy + r0 * math.sin(a), z0) for a in reversed(ang)]
        if not full: top.append((cx, cy, z1)); bot.insert(0, (cx, cy, z0))
        out += [(top, m), (bot, m)]
    return out

def sphere(cx, cy, cz, r, m, seg=8, rings=6, sz=1.0):
    out = []
    for j in range(rings):
        p0, p1 = math.pi * j / rings - math.pi / 2, math.pi * (j + 1) / rings - math.pi / 2
        for i in range(seg):
            a0, a1 = 2 * math.pi * i / seg, 2 * math.pi * (i + 1) / seg
            pts = [(cx + r * math.cos(p0) * math.cos(a0), cy + r * math.cos(p0) * math.sin(a0), cz + r * sz * math.sin(p0)),
                   (cx + r * math.cos(p0) * math.cos(a1), cy + r * math.cos(p0) * math.sin(a1), cz + r * sz * math.sin(p0)),
                   (cx + r * math.cos(p1) * math.cos(a1), cy + r * math.cos(p1) * math.sin(a1), cz + r * sz * math.sin(p1)),
                   (cx + r * math.cos(p1) * math.cos(a0), cy + r * math.cos(p1) * math.sin(a0), cz + r * sz * math.sin(p1))]
            out.append((pts, m))
    return out

def arch_outline(L, w, spring, top, base=0.0):
    """Muro con arco abierto hasta el piso (contorno cóncavo en x,z)."""
    h, r = L / 2, w / 2
    pts = [(-h, base), (-r, base), (-r, spring)]
    for i in range(1, 12):
        a = math.pi - math.pi * i / 12
        pts.append((r * math.cos(a), spring + r * math.sin(a)))
    pts += [(r, spring), (r, base), (h, base), (h, top), (-h, top)]
    return pts

def archivolt(w, spring, band=0.42, y0=0.0, y1=0.14, m='trav'):
    out = []; r0, r1 = w / 2, w / 2 + band
    for i in range(12):
        a, b = math.pi * i / 12, math.pi * (i + 1) / 12
        q = [(r1 * math.cos(a), r1 * math.sin(a)), (r1 * math.cos(b), r1 * math.sin(b)), (r0 * math.cos(b), r0 * math.sin(b)), (r0 * math.cos(a), r0 * math.sin(a))]
        out += prism([(x, z + spring) for x, z in q], y0, y1, m)
    return out

def figure(x, y, z, h=1.7, m_body=None, m_skin=None, rot=0.0, pose=0, cloak=None):
    """Figura humana de bajo detalle (proporciones reales) orientada hacia +y girada rot."""
    mb = m_body or CLOTH[0]; ms = m_skin or MAT['skin']
    s = h / 1.7; out = []
    out += box(-0.16 * s, -0.02 * s, -0.09 * s, 0.09 * s, 0, 0.82 * s, mb)
    out += box(0.02 * s, 0.16 * s, -0.09 * s, 0.09 * s, 0, 0.82 * s, mb)
    out += cyl(0, 0, 0.2 * s, 0.17 * s, 0.78 * s, 1.42 * s, mb, seg=8)
    if cloak: out += cyl(0, -0.02 * s, 0.26 * s, 0.2 * s, 0.35 * s, 1.4 * s, cloak, seg=8, a0=math.pi * 0.95, a1=math.pi * 2.05)
    if pose == 1:
        out += box(0.17 * s, 0.26 * s, -0.05 * s, 0.05 * s, 1.3 * s, 1.95 * s, ms)
    else:
        out += box(0.17 * s, 0.26 * s, -0.05 * s, 0.05 * s, 0.75 * s, 1.36 * s, ms)
    out += box(-0.26 * s, -0.17 * s, -0.05 * s, 0.05 * s, 0.75 * s, 1.36 * s, ms)
    out += sphere(0, 0.01 * s, 1.55 * s, 0.11 * s, ms, seg=6, rings=4, sz=1.15)
    M = Matrix.Translation((x, y, z)) @ Matrix.Rotation(rot, 4, 'Z')
    return [([tuple(M @ Vector(p)) for p in pts], mm) for pts, mm in out]

def xf(faces, M):
    return [([tuple(M @ Vector(p)) for p in pts], m) for pts, m in faces]

# ------------------------------------------------------------------ elipse del Coliseo
A, B, NB = 94.0, 78.0, 80
ts = np.linspace(0, 2 * math.pi, 20001)
xy = np.stack([A * np.cos(ts), B * np.sin(ts)], 1)
seg_len = np.r_[0, np.cumsum(np.linalg.norm(np.diff(xy, axis=0), axis=1))]
PER = seg_len[-1]
def t_at(s): return float(np.interp(s % PER, seg_len, ts))
TB = [t_at(i * PER / NB + PER / NB / 2) for i in range(NB + 1)]
def pt(t, d): return ((A - d) * math.cos(t), (B - d) * math.sin(t))

def bay_matrix(i, d, L0):
    p0, p1 = pt(TB[i], d), pt(TB[i + 1], d)
    mx, my = (p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2
    L = math.hypot(p1[0] - p0[0], p1[1] - p0[1]); th = math.atan2(p1[1] - p0[1], p1[0] - p0[0])
    if -math.sin(th) * mx + math.cos(th) * my < 0: th += math.pi
    M = Matrix.Translation((mx, my, 0)) @ Matrix.Rotation(th, 4, 'Z') @ Matrix.Diagonal((L / L0, 1, 1, 1))
    return M, L, th

col_main = bpy.data.collections.new('Coliseo'); scene.collection.children.link(col_main)
col_env = bpy.data.collections.new('Entorno'); scene.collection.children.link(col_env)

# ---- anillo exterior (4 pisos, completo)
T1 = 2.3; L1 = PER / NB
STO = [dict(y0=0.0, spring=6.6, top=9.3, ent=(9.3, 10.5), w=4.2, r=0.66, order=0),
       dict(pod=(10.5, 12.0), y0=12.0, spring=17.9, top=20.9, ent=(20.9, 22.3), w=4.0, r=0.58, order=1),
       dict(pod=(22.3, 23.8), y0=23.8, spring=29.6, top=32.5, ent=(32.5, 33.9), w=4.0, r=0.52, order=2)]

def ring1_bay(i):
    f = []
    f += box(-L1 / 2 - .02, L1 / 2 + .02, -T1, 1.4, 0, .35, 'trav')
    for S in STO:
        f += prism(arch_outline(L1, S['w'], S['spring'], S['ent'][0], S['y0']), -T1, 0, 'trav')
        f += archivolt(S['w'], S['spring'])
        for sg in (-1, 1):
            f += box(sg * (S['w'] / 2 + .28) - .28, sg * (S['w'] / 2 + .28) + .28, 0, .3, S['spring'] - .32, S['spring'], 'trav')
        h = S['ent'][0] - S['y0']; r = S['r']
        f += cyl(-L1 / 2, 0, r * 1.04, r, S['y0'] + .35, S['ent'][0] - .45, 'trav', seg=12, a0=0, a1=math.pi)
        f += box(-L1 / 2 - r * 1.25, -L1 / 2 + r * 1.25, -.05, r + .35, S['y0'], S['y0'] + .35, 'trav')
        if S['order'] == 2:
            f += cyl(-L1 / 2, 0, r, r * 1.35, S['ent'][0] - .75, S['ent'][0], 'trav', seg=12, a0=0, a1=math.pi)
        else:
            f += box(-L1 / 2 - r * 1.3, -L1 / 2 + r * 1.3, -.05, r + .4, S['ent'][0] - .45, S['ent'][0], 'trav')
        e0, e1 = S['ent']; eh = e1 - e0
        f += box(-L1 / 2 - .02, L1 / 2 + .02, -T1, .85, e0, e0 + eh * .72, 'trav')
        f += box(-L1 / 2 - .02, L1 / 2 + .02, -T1, 1.15, e0 + eh * .72, e1, 'trav')
        if 'pod' in S:
            p0, p1 = S['pod']
            f += box(-L1 / 2 - .02, L1 / 2 + .02, -T1, .55, p0, p1, 'trav')
            f += box(-L1 / 2 - .85, -L1 / 2 + .85, -.05, .95, p0, p1, 'trav')
            # estatua en el arco
            f += box(-.5, .5, -1.3, -.3, S['y0'], S['y0'] + .6, 'marble')
            f += figure(0, -.8, S['y0'] + .6, 2.5, MAT['marble'], MAT['marble'], rot=0, pose=R.randint(0, 1), cloak=MAT['marble'])
    # ático
    y0, y1 = 33.9, 48.5
    if i % 2:
        f += box(-L1 / 2 - .01, -.65, -T1, 0, y0, y1 - 1.9, 'trav'); f += box(.65, L1 / 2 + .01, -T1, 0, y0, y1 - 1.9, 'trav')
        f += box(-.65, .65, -T1, 0, y0, y0 + 3.3, 'trav'); f += box(-.65, .65, -T1, 0, y0 + 5.3, y1 - 1.9, 'trav')
        f += box(-.66, .66, -T1 + .05, -.1, y0 + 3.3, y0 + 5.3, 'dark')
    else:
        f += box(-L1 / 2 - .01, L1 / 2 + .01, -T1, 0, y0, y1 - 1.9, 'trav')
        f += cyl(0, .06, .85, .85, y0 + 3.4, y0 + 3.5, 'bronze', seg=16)  # escudo de bronce (disco)
    f += box(-L1 / 2 - .02, L1 / 2 + .02, -T1, .45, y0, y0 + .6, 'trav')
    f += box(-L1 / 2 - .55, -L1 / 2 + .55, 0, .28, y0 + .6, y0 + 11.6, 'trav')
    f += box(-L1 / 2 - .7, -L1 / 2 + .7, 0, .42, y0 + 11.6, y0 + 12.1, 'trav')
    for x in (-L1 / 4, 0, L1 / 4):
        f += box(x - .25, x + .25, 0, .6, 42.7, 43.35, 'trav')
        f += cyl(x, .3, .19, .16, 43.35, 58.0, 'wood', seg=6)          # mástiles del velario
    f += box(-L1 / 2 - .02, L1 / 2 + .02, -T1, .6, y1 - 1.9, y1 - .75, 'trav')
    f += box(-L1 / 2 - .02, L1 / 2 + .02, -T1, 1.0, y1 - .75, y1, 'trav')
    # deambulatorios: pisos y bóvedas hasta el segundo anillo
    D2 = 6.4; span = D2 - T1
    for y in (10.5, 22.3, 33.9):
        f += box(-L1 / 2 - .02, L1 / 2 + .02, -D2, -T1, y - .8, y, 'travIn')
        cz = y - .8 - span / 2 + .2
        for k in range(10):
            a, b = math.pi * k / 10, math.pi * (k + 1) / 10
            ya, yb = -T1 - span / 2 + span / 2 * math.cos(a), -T1 - span / 2 + span / 2 * math.cos(b)
            za, zb = cz + span / 2 * math.sin(a), cz + span / 2 * math.sin(b)
            f.append(([(-L1 / 2 - .02, ya, za), (L1 / 2 + .02, ya, za), (L1 / 2 + .02, yb, zb), (-L1 / 2 - .02, yb, zb)], 'travIn'))
    f += box(-L1 / 2 - .02, L1 / 2 + .02, -D2, -T1, -.05, .02, 'basalt')
    return f

b_col = Builder('coliseo_anillo_exterior')
for i in range(NB):
    M, L, th = bay_matrix(i, 0, L1)
    b_col.add(ring1_bay(i), M)
b_col.build(col_main)

# ---- segundo anillo, pórtico superior, cávea
D2, T2 = 6.4, 1.9; L2 = PER * ((A - D2) / A) / NB
R2S = [dict(y0=0, spring=6.4, top=10.5, w=3.7), dict(y0=10.5, spring=17.6, top=22.3, w=3.6), dict(y0=22.3, spring=29.3, top=33.9, w=3.6)]
b2 = Builder('coliseo_interior')
for i in range(NB):
    M, L, th = bay_matrix(i, D2, L2)
    f = []
    for S in R2S:
        f += prism(arch_outline(L2, S['w'], S['spring'], S['top'] - .55, S['y0']), -T2, 0, 'travIn')
        f += box(-L2 / 2 - .02, L2 / 2 + .02, -T2, .3, S['top'] - .55, S['top'], 'travIn')
    # pórtico del último piso: columnas y techo contra el ático
    for x in (-L2 / 2, 0):
        f += cyl(x, -T2 - .9, .42, .36, 33.9, 44.2, 'granite', seg=10)
    f += box(-L2 / 2 - .05, L2 / 2 + .05, -T2 - 1.5, -T2 - .3, 44.2, 45.0, 'marble')
    b2.add(f, M)
    # techo inclinado del pórtico (entre el ático y la columnata)
    Mo, _, _ = bay_matrix(i, 2.3, L1 * (A - 2.3) / A)
    b2.add([([( -L1 * .52, 0, 47.2), (L1 * .52, 0, 47.2), (L1 * .52, -(D2 + T2 + 1.5 - 2.3), 45.0), (-L1 * .52, -(D2 + T2 + 1.5 - 2.3), 45.0)], 'tile')], Mo)

def ring_strip(builder, profile, mat_of_seg, tseg=720, zoff=None):
    nP = len(profile); T = [t_at(k / tseg * PER) for k in range(tseg + 1)]
    for k in range(tseg):
        for j in range(nP - 1):
            (d0, h0), (d1, h1) = profile[j], profile[j + 1]
            a0, a1 = pt(T[k], d0), pt(T[k + 1], d0); b0, b1 = pt(T[k], d1), pt(T[k + 1], d1)
            builder.face([(a0[0], a0[1], h0), (a1[0], a1[1], h0), (b1[0], b1[1], h1), (b0[0], b0[1], h1)], mat_of_seg(j, d0, h0, d1, h1))

DA = A - 43.5  # arena: 87 × 55 m
prof = [(DA, 0.0), (DA, 4.0), (DA - .15, 4.0), (DA - .15, 5.1), (DA - .35, 5.1), (DA - .35, 4.0), (DA - 3.6, 4.0)]
def steps(d0, d1, h0, h1, n):
    for k in range(1, n + 1):
        d, h = d0 + (d1 - d0) * k / n, h0 + (h1 - h0) * k / n
        pd = prof[-1][0]; prof.append((pd, h)); prof.append((d, h))
prof.append((DA - 3.6, 5.2)); steps(DA - 3.6, 36.2, 5.2, 13.4, 14)
prof += [(36.2, 16.0), (34.8, 16.0)]; steps(34.8, 21.6, 16.0, 25.0, 16)
prof += [(21.6, 27.4), (20.3, 27.4)]; steps(20.3, 12.6, 27.4, 32.6, 10)
prof += [(12.6, 33.9), (D2 + T2, 33.9)]
def cavea_mat(j, d0, h0, d1, h1):
    if abs(d0 - d1) < 1e-6:  # contrahuella / muro vertical
        return 'trav' if (h1 - h0) > 1.0 else 'marble'
    return 'marble'
bc = Builder('cavea'); ring_strip(bc, prof, cavea_mat, 720)
# muro del tercer anillo y techos del deambulatorio interno
ring_strip(bc, [(12.6, 0), (12.6, 33.9)], lambda *a: 'travIn', 400)
for y in (10.5, 22.3):
    ring_strip(bc, [(D2 + T2, y), (12.6, y)], lambda *a: 'travIn', 400)
ring_strip(bc, [(D2 + T2, .01), (12.6, .01)], lambda *a: 'basalt', 300)
# vomitorios
for i in range(0, NB, 2):
    tm = (TB[i] + TB[i + 1]) / 2
    for d, h in ((35.4, 13.4), (21.0, 25.0)):
        p = pt(tm, d); q = pt(tm + .01, d); th = math.atan2(q[1] - p[1], q[0] - p[0])
        bc.add(box(-.85, .85, -.2, .08, h + .05, h + 2.5, 'dark'), Matrix.Translation((p[0], p[1], 0)) @ Matrix.Rotation(th, 4, 'Z'))
b2.build(col_main); bc.build(col_main)

# ---- arena, podio, palco imperial, puertas
ba = Builder('arena')
aA, aB = 43.5, B - DA
ring = [(aA * math.cos(2 * math.pi * k / 128), aB * math.sin(2 * math.pi * k / 128), 0.0) for k in range(128)]
ba.face(ring, 'sand')
for sx in (-1, 1):  # Porta Triumphalis / Libitinensis
    ba.add(box(-.3, .3, -2.4, 2.4, 0, 4.6, 'dark'), Matrix.Translation((sx * (aA + .05), 0, 0)))
def pulvinar(side, w, depth, royal):
    tmid = -math.pi / 2 if side < 0 else math.pi / 2
    p = pt(tmid, DA); th = math.atan2(p[1], p[0])
    M = Matrix.Translation((p[0], p[1], 0)) @ Matrix.Rotation(th - math.pi / 2 if side > 0 else th + math.pi / 2, 4, 'Z')
    f = []
    f += box(-w / 2, w / 2, -.5, depth, 0, 4.2, 'marble')
    for x in (-w / 2 + .5, -w / 6, w / 6, w / 2 - .5):
        f += cyl(x, depth - .4, .28, .25, 4.2, 8.8, 'marble', seg=10)
    f += box(-w / 2 - .3, w / 2 + .3, -.6, depth + .2, 8.8, 9.4, 'marble')
    f += box(-w / 2, w / 2, -.5, depth, 9.4, 9.55, 'purple' if royal else 'canvas')
    f += box(-w / 2 + .3, w / 2 - .3, depth - .1, depth + .02, 5.8, 8.8, 'purple' if royal else 'canvas2')
    f += box(-w / 2, w / 2, -.5, depth - .3, 4.2, 4.3, 'purple' if royal else 'wood')
    ba.add(f, M)
    return M
M_PULV = pulvinar(-1, 13, 4.2, True)
pulvinar(1, 10, 3.2, False)
ba.build(col_main)

# ------------------------------------------------------------------ entorno
def ground_h(x, y):
    h = 0.0
    for cx, cy, rx, ry, hh in HILLS:
        dx, dy = (x - cx) / rx, (y - cy) / ry; d2 = dx * dx + dy * dy
        if d2 < 4: h += hh * math.exp(-d2 * 1.6)
    return h
HILLS = [(-360, -250, 190, 150, 36),   # Palatino
         (190, -330, 230, 170, 30),    # Celio
         (260, 300, 260, 200, 34),     # Esquilino / Opio
         (-330, 60, 90, 70, 9),        # Velia
         (-700, 150, 240, 190, 40),    # Capitolio / Quirinal lejanos
         (520, -60, 300, 260, 18)]

bg = Builder('terreno')
G, S = 110, 3000.0
for j in range(G):
    for i in range(G):
        x0, x1 = -S / 2 + S * i / G, -S / 2 + S * (i + 1) / G
        y0, y1 = -S / 2 + S * j / G, -S / 2 + S * (j + 1) / G
        c = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
        zs = [ground_h(a, b) - .08 for a, b in c]
        if max(abs(x0), abs(x1)) < 240 and max(abs(y0), abs(y1)) < 220 and max(zs) < .5:
            continue
        bg.face([(a, b, z) for (a, b), z in zip(c, zs)], 'ground')
# plaza de travertino alrededor del Coliseo y del valle
bp = Builder('plaza')
for j in range(-9, 9):
    for i in range(-10, 10):
        x0, y0 = i * 24.0, j * 24.0
        cx, cy = x0 + 12, y0 + 12
        if (cx / (A - 1)) ** 2 + (cy / (B - 1)) ** 2 < 1: continue
        bp.face([(x0, y0, -.05), (x0 + 24, y0, -.05), (x0 + 24, y0 + 24, -.05), (x0, y0 + 24, -.05)], 'pave' if (cx / (A + 30)) ** 2 + (cy / (B + 30)) ** 2 < 1 else 'basalt')
# cipos (postes de travertino del velario)
for k in range(160):
    t = t_at(k / 160 * PER); p = pt(t, -18)
    bp.add(box(-.35, .35, -.28, .28, 0, 1.75, 'trav'), Matrix.Translation((p[0], p[1], 0)) @ Matrix.Rotation(t, 4, 'Z'))
bp.build(col_env); bg.build(col_env)
bfar = Builder('horizonte')
for k in range(48):
    a0, a1 = 2 * math.pi * k / 48, 2 * math.pi * (k + 1) / 48
    bfar.face([(1500 * math.cos(a0) * 1.42, 1500 * math.sin(a0) * 1.42, -.5), (20000 * math.cos(a0), 20000 * math.sin(a0), 60), (20000 * math.cos(a1), 20000 * math.sin(a1), 60), (1500 * math.cos(a1) * 1.42, 1500 * math.sin(a1) * 1.42, -.5)], 'ground')
bfar.face([(-1500, -1500, -.6), (1500, -1500, -.6), (1500, 1500, -.6), (-1500, 1500, -.6)], 'ground')
bfar.build(col_env)

# Coloso de Nerón / Sol (remodelado por Cómodo)
bco = Builder('coloso')
CX, CY = -148.0, 32.0
bco.add(box(-8.5, 8.5, -7, 7, 0, 7.5, 'marble')); bco.add(box(-9.2, 9.2, -7.7, 7.7, 7.5, 8.2, 'marble'))
bco.add(box(-9.2, 9.2, -7.7, 7.7, 0, .6, 'marble'))
s = 20.0  # escala: figura de ~34 m
fig = figure(0, 0, 8.2, 34.0, MAT['bronze'], MAT['bronze'], rot=0, pose=1, cloak=MAT['bronze'])
bco.add(fig)
for k in range(7):
    a = math.pi * (0.15 + 0.7 * k / 6)
    hx, hz = 0, 8.2 + 34 * 1.58 / 1.7
    bco.add(cyl(0, 0, .5, .05, 0, 6.5, 'bronze', seg=5), Matrix.Translation((hx, 0, hz)) @ Matrix.Rotation(math.pi / 2 - a, 4, 'Y'))
bco.add(cyl(-8.4, 0, .35, .35, 8.2, 8.2 + 26, 'bronze', seg=8))  # timón / cetro
o = bco.build(col_env); o.location = (CX, CY, 0); o.rotation_euler = (0, 0, math.radians(-80))

# Meta Sudans
bm = Builder('meta_sudans'); MX, MY = -118.0, -52.0
bm.add(cyl(0, 0, 8, 8, 0, .9, 'marble', seg=32)); bm.add(cyl(0, 0, 7.5, 7.5, .5, .78, 'water', seg=32))
bm.add(cyl(0, 0, 4.2, 3.9, .9, 7.0, 'brick', seg=20)); bm.add(cyl(0, 0, 3.5, .7, 7.0, 17.0, 'marble', seg=20))
bm.add(sphere(0, 0, 17.3, .9, 'bronze'))
o = bm.build(col_env); o.location = (MX, MY, 0)

# Templo de Venus y Roma sobre la Velia
bt = Builder('templo_venus_roma'); TX, TY, TZ = -300.0, 48.0, 8.0
bt.add(box(-75, 75, -52, 52, -6, TZ, 'trav'))
for k in range(8):
    bt.add(box(-82 + k * .5 * 0, -75, -20, 20, TZ - k * 1.0 - 1, TZ - k * 1.0, 'marble'), Matrix.Translation((-k * .6, 0, 0)))
bt.add(box(-56, 56, -27, 27, TZ, TZ + 3, 'marble'))
bt.add(box(-44, 44, -16, 16, TZ + 3, TZ + 21, 'plaster_white'))
nx, ny = 22, 10
for i in range(nx):
    for j in range(ny):
        if 0 < i < nx - 1 and 0 < j < ny - 1: continue
        x = -52 + 104 * i / (nx - 1); y = -23 + 46 * j / (ny - 1)
        bt.add(cyl(x, y, .95, .85, TZ + 3, TZ + 20, 'marble', seg=12))
bt.add(box(-54, 54, -25, 25, TZ + 20, TZ + 22.6, 'marble'))
bt.add([([(-55, -26, TZ + 22.6), (55, -26, TZ + 22.6), (55, 0, TZ + 31), (-55, 0, TZ + 31)], 'goldRoof'),
        ([(55, 26, TZ + 22.6), (-55, 26, TZ + 22.6), (-55, 0, TZ + 31), (55, 0, TZ + 31)], 'goldRoof'),
        ([(-55, -26, TZ + 22.6), (-55, 0, TZ + 31), (-55, 26, TZ + 22.6)], 'marble'),
        ([(55, 26, TZ + 22.6), (55, 0, TZ + 31), (55, -26, TZ + 22.6)], 'marble')])
for side in (-1, 1):  # pórticos laterales de granito
    for k in range(38):
        x = -72 + 144 * k / 37
        bt.add(cyl(x, side * 48, .5, .45, TZ, TZ + 9, 'granite', seg=8))
    bt.add(box(-74, 74, side * 48 - 1, side * 48 + 1, TZ + 9, TZ + 10, 'marble'))
    bt.add([([(-74, side * 47.5, TZ + 10), (74, side * 47.5, TZ + 10), (74, side * 52, TZ + 8.6), (-74, side * 52, TZ + 8.6)], 'tile')])
o = bt.build(col_env); o.location = (TX, TY, 0)

# Ludus Magnus (escuela de gladiadores) al este
bl = Builder('ludus_magnus'); LX, LY = 175.0, 58.0
for (x0, x1, y0, y1) in ((-60, 60, -40, -32), (-60, 60, 32, 40), (-60, -52, -40, 40), (52, 60, -40, 40)):
    bl.add(box(x0, x1, y0, y1, 0, 13, 'plaster_ochre'))
bl.add([([(-61, -41, 13), (61, -41, 13), (61, -31, 15.5), (-61, -31, 15.5)], 'tile'), ([(61, 41, 13), (-61, 41, 13), (-61, 31, 15.5), (61, 31, 15.5)], 'tile'),
        ([(-61, -41, 13), (-61, 41, 13), (-51, 31, 15.5), (-51, -31, 15.5)], 'tile'), ([(61, 41, 13), (61, -41, 13), (51, -31, 15.5), (51, 31, 15.5)], 'tile')])
eln = [(31 * math.cos(2 * math.pi * k / 64), 20 * math.sin(2 * math.pi * k / 64), .05) for k in range(64)]
bl.face(eln, 'sand')
for k in range(64):
    a, b = 2 * math.pi * k / 64, 2 * math.pi * (k + 1) / 64
    for rr, z0, z1, mm in ((1.0, 0, 3.2, 'trav'), (1.25, 3.2, 3.2, 'marble')):
        pass
    bl.face([(31 * math.cos(a), 20 * math.sin(a), 0), (31 * math.cos(b), 20 * math.sin(b), 0), (31 * math.cos(b), 20 * math.sin(b), 3.2), (31 * math.cos(a), 20 * math.sin(a), 3.2)], 'trav')
    bl.face([(31 * math.cos(a), 20 * math.sin(a), 3.2), (31 * math.cos(b), 20 * math.sin(b), 3.2), (40 * math.cos(b), 29 * math.sin(b), 9), (40 * math.cos(a), 29 * math.sin(a), 9)], 'marble')
for k in range(24):  # celdas con pórtico interior
    x = -50 + 100 * k / 23
    for y in (-31.5, 31.5):
        bl.add(cyl(x, y, .35, .3, 0, 9, 'trav', seg=6))
o = bl.build(col_env); o.location = (LX, LY, 0)

# Termas de Trajano en el Opio (masas abovedadas)
bth = Builder('termas_trajano'); HX, HY = 300.0, 260.0
hz = ground_h(HX, HY) - 2
bth.add(box(-130, 130, -110, 110, hz - 5, hz + 6, 'brick'))
bth.add(box(-60, 60, -40, 40, hz + 6, hz + 30, 'brick'))
bth.add(box(-100, 100, -15, 15, hz + 6, hz + 22, 'brick'))
bth.add(cyl(0, 45, 18, 18, hz + 6, hz + 26, 'brick', seg=24)); bth.add(sphere(0, 45, hz + 26, 18, 'plaster_white', seg=16, rings=8, sz=.6))
bth.add(cyl(-95, -60, 14, 14, hz + 6, hz + 20, 'brick', seg=20)); bth.add(cyl(95, -60, 14, 14, hz + 6, hz + 20, 'brick', seg=20))
o = bth.build(col_env); o.location = (HX, HY, 0)

# Palatino: palacios imperiales en la colina
bpal = Builder('palatino')
for k in range(26):
    x = -360 + R.uniform(-150, 150); y = -250 + R.uniform(-110, 110)
    if math.hypot((x + 360) / 190, (y + 250) / 150) > .9: continue
    z = ground_h(x, y); w, d, h = R.uniform(25, 70), R.uniform(20, 55), R.uniform(12, 28)
    rot = Matrix.Translation((x, y, z - 3)) @ Matrix.Rotation(math.radians(R.choice([0, 8, -12])), 4, 'Z')
    bpal.add(box(-w / 2, w / 2, -d / 2, d / 2, 0, h, R.choice(['brick', 'plaster_cream', 'plaster_pink', 'plaster_white'])), rot)
    bpal.add([([(-w / 2 - 1, -d / 2 - 1, h), (w / 2 + 1, -d / 2 - 1, h), (0, 0, h + 5)], 'tile'), ([(w / 2 + 1, -d / 2 - 1, h), (w / 2 + 1, d / 2 + 1, h), (0, 0, h + 5)], 'tile'),
              ([(w / 2 + 1, d / 2 + 1, h), (-w / 2 - 1, d / 2 + 1, h), (0, 0, h + 5)], 'tile'), ([(-w / 2 - 1, d / 2 + 1, h), (-w / 2 - 1, -d / 2 - 1, h), (0, 0, h + 5)], 'tile')], rot)
    if R.random() < .5:
        for c in range(int(w / 5)):
            bpal.add(cyl(-w / 2 + 2.5 + c * 5, -d / 2 - 2.5, .45, .4, 0, h * .6, 'marble', seg=8), rot)
bpal.build(col_env)

# Acueducto (Arcus Neroniani) cruzando el Celio
baq = Builder('acueducto')
P0, P1 = Vector((620, -360, 0)), Vector((40, -250, 0))
n = int((P1 - P0).length / 7.5); dv = (P1 - P0).normalized(); th = math.atan2(dv.y, dv.x)
for k in range(n):
    p = P0 + dv * (k * 7.5 + 3.75); z = ground_h(p.x, p.y)
    H = 16.0 + (6 - min(6, z))
    M = Matrix.Translation((p.x, p.y, z - 1)) @ Matrix.Rotation(th, 4, 'Z')
    baq.add(prism(arch_outline(7.5, 4.8, H - 5.5, H), -1.6, 1.6, 'brick'), M)
    baq.add(box(-3.76, 3.76, -1.8, 1.8, H, H + 2.2, 'brick'), M)
baq.build(col_env)

# Ciudad: ínsulas con techos de teja (evitando monumentos y el valle)
bci = Builder('ciudad')
excl = [(0, 0, A + 70, B + 70), (-300, 48, 95, 70), (175, 58, 80, 60), (300, 260, 150, 125), (-148, 32, 30, 30), (-118, -52, 25, 25)]
def free(x, y):
    for cx, cy, rx, ry in excl:
        if ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 < 1: return False
    if math.hypot((x + 360) / 190, (y + 250) / 150) < .95: return False
    return True
placed = 0; tries = 0
while placed < 1100 and tries < 20000:
    tries += 1
    r = R.uniform(150, 1300); a = R.uniform(0, 2 * math.pi); x, y = r * math.cos(a), r * math.sin(a)
    if not free(x, y): continue
    z = ground_h(x, y); w, d = R.uniform(14, 36), R.uniform(12, 30); h = R.uniform(9, 20)
    rot = Matrix.Translation((x, y, z - 1.5)) @ Matrix.Rotation(math.radians(R.choice([0, 0, 5, -8, 15])), 4, 'Z')
    m = R.choice(['plaster_ochre', 'plaster_cream', 'plaster_red', 'plaster_pink', 'brick', 'plaster_ochre'])
    f = box(-w / 2, w / 2, -d / 2, d / 2, 0, h, m)
    for fl in range(1, int(h / 3.2)):
        for c in range(int(w / 3.5)):
            xx = -w / 2 + 1.5 + c * 3.5
            if xx + .9 < w / 2: f += box(xx, xx + .9, -d / 2 - .03, -d / 2 + .02, fl * 3.2 - 1.9, fl * 3.2 - .6, 'dark')
    rh = min(w, d) * .28
    f += [([(-w / 2 - .6, -d / 2 - .6, h), (w / 2 + .6, -d / 2 - .6, h), (w / 2 - rh, 0, h + rh), (-w / 2 + rh, 0, h + rh)], 'tile'),
          ([(w / 2 + .6, d / 2 + .6, h), (-w / 2 - .6, d / 2 + .6, h), (-w / 2 + rh, 0, h + rh), (w / 2 - rh, 0, h + rh)], 'tile'),
          ([(-w / 2 - .6, d / 2 + .6, h), (-w / 2 - .6, -d / 2 - .6, h), (-w / 2 + rh, 0, h + rh)], 'tile'),
          ([(w / 2 + .6, -d / 2 - .6, h), (w / 2 + .6, d / 2 + .6, h), (w / 2 - rh, 0, h + rh)], 'tile')]
    bci.add(f, rot); placed += 1
bci.build(col_env)

# Árboles: cipreses y pinos piñoneros en las colinas
btr = Builder('arboles')
for k in range(700):
    x, y = R.uniform(-900, 900), R.uniform(-800, 800)
    z = ground_h(x, y)
    if z < 6 and math.hypot(x, y) < 700: continue
    if not free(x, y) and R.random() < .8: continue
    if R.random() < .55:
        h = R.uniform(10, 18); btr.add(cyl(x, y, .25, .2, z - .5, z + 2, 'wood', seg=5)); btr.add(cyl(x, y, 1.3, .1, z + 1.5, z + h, 'leaf', seg=7))
    else:
        h = R.uniform(10, 16); btr.add(cyl(x, y, .35, .25, z - .5, z + h, 'wood', seg=5))
        for c in range(4):
            btr.add(sphere(x + R.uniform(-3, 3), y + R.uniform(-3, 3), z + h + R.uniform(0, 1.5), R.uniform(3, 5.5), 'leaf', seg=7, rings=4, sz=.4))
btr.build(col_env)

# ------------------------------------------------------------------ calles con adoquín de basalto
broad = Builder('calles')
for pts, w in (([(-94, 0), (-180, 30), (-230, 48)], 16), ([(94, 0), (230, 40), (500, 80)], 14), ([(-60, -60), (-140, -130), (-230, -200)], 14), ([(40, -70), (90, -160), (150, -260)], 12)):
    for (x0, y0), (x1, y1) in zip(pts[:-1], pts[1:]):
        dx, dy = x1 - x0, y1 - y0; L = math.hypot(dx, dy); nx_, ny_ = -dy / L * w / 2, dx / L * w / 2
        broad.face([(x0 + nx_, y0 + ny_, -.02), (x1 + nx_, y1 + ny_, -.02), (x1 - nx_, y1 - ny_, -.02), (x0 - nx_, y0 - ny_, -.02)], 'basalt')
broad.build(col_env)

# ------------------------------------------------------------------ mundo y render
world = bpy.data.worlds.new('cielo'); scene.world = world; world.use_nodes = True
sky = world.node_tree.nodes.new('ShaderNodeTexSky'); sky.name = 'Sky'
sky.sky_type = 'MULTIPLE_SCATTERING'
world.node_tree.links.new(sky.outputs[0], world.node_tree.nodes['Background'].inputs[0])
sun = bpy.data.lights.new('sol', 'SUN'); sun.angle = math.radians(0.8)
so = bpy.data.objects.new('sol', sun); scene.collection.objects.link(so)
cam = bpy.data.cameras.new('camara'); co = bpy.data.objects.new('camara', cam); scene.collection.objects.link(co); scene.camera = co

scene.render.engine = 'CYCLES'
scene.cycles.device = 'CPU'
scene.cycles.use_adaptive_sampling = True; scene.cycles.adaptive_threshold = 0.02
scene.cycles.use_denoising = True
scene.cycles.max_bounces = 6; scene.cycles.diffuse_bounces = 3; scene.cycles.glossy_bounces = 2
scene.cycles.transmission_bounces = 4; scene.cycles.volume_bounces = 0; scene.cycles.caustics_reflective = False; scene.cycles.caustics_refractive = False
try:
    scene.view_settings.view_transform = 'AgX'
    scene.view_settings.look = 'AgX - High Contrast'
except Exception as e:
    print('view transform', e)
bpy.ops.wm.save_as_mainfile(filepath=OUT, compress=True)
print('OK guardado', OUT, 'caras:', sum(len(o.data.polygons) for o in bpy.data.objects if o.type == 'MESH'))
