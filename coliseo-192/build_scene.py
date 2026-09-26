"""Roma, año 192 d. C.: el Coliseo completo y sus alrededores, construido con código para Blender (Cycles).

Uso:  python3 build_scene.py <salida.blend>
Coordenadas en metros: x = este, y = norte, z = altura. El Coliseo está centrado en el origen.
"""
import bpy, math, random, sys
import numpy as np
from mathutils import Vector, Matrix, Quaternion

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
MAT['sand'] = principled('arena', (0.78, 0.66, 0.48), 1.0, extra=lambda nt, p: noisy(nt, p, (0.42, 0.33, 0.23), (0.53, 0.42, 0.29), 0.15, 0.25, 40))
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


# ------------------------------------------------------------------ figuras orgánicas (metaballs)
LIB = bpy.data.collections.new('Biblioteca'); scene.collection.children.link(LIB); LIB.hide_render = True
_fig_n = [0]
def _meta_mesh(parts, res):
    _fig_n[0] += 1; nm = f'mb{_fig_n[0]}x'
    mb = bpy.data.metaballs.new(nm); mb.resolution = res; mb.render_resolution = res; mb.threshold = 0.6
    for pr in parts:
        if pr[0] == 'cap':
            _, a, b, r = pr; a, b = Vector(a), Vector(b); d = b - a
            e = mb.elements.new(type='CAPSULE'); e.co = (a + b) / 2; e.radius = r; e.size_x = max(d.length / 2, 1e-3)
            e.rotation = Vector((1, 0, 0)).rotation_difference(d.normalized()) if d.length > 1e-4 else Quaternion()
        elif pr[0] == 'ell':
            _, c, sz, r = pr; e = mb.elements.new(type='ELLIPSOID'); e.co = c; e.radius = r; e.size_x, e.size_y, e.size_z = sz
        else:
            _, c, r = pr; e = mb.elements.new(type='BALL'); e.co = c; e.radius = r
    ob = bpy.data.objects.new(nm, mb); scene.collection.objects.link(ob)
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(ob.evaluated_get(dg))
    bpy.data.objects.remove(ob); bpy.data.metaballs.remove(mb)
    return me

def join_meshes(name, items):
    """items: [(mesh, material)] -> una malla con varios materiales, sombreado suave."""
    V, F, MI, mats = [], [], [], []
    for me, m in items:
        if m not in mats: mats.append(m)
        off = len(V)
        co = np.zeros(len(me.vertices) * 3); me.vertices.foreach_get('co', co); V += list(map(tuple, co.reshape(-1, 3)))
        for poly in me.polygons: F.append([off + v for v in poly.vertices]); MI.append(mats.index(m))
        bpy.data.meshes.remove(me)
    out = bpy.data.meshes.new(name); out.from_pydata(V, [], F)
    for m in mats: out.materials.append(m)
    out.polygons.foreach_set('material_index', MI); out.update(); out.shade_smooth()
    return out

def human(pose='stand', h=1.75, garment='tunic', seed=0, res=0.035):
    """Partes (ropa, piel) de un cuerpo humano en metros, mirando hacia +y."""
    rr = random.Random(seed); s = h / 1.75
    P = lambda x, y, z: (x * s, y * s, z * s)
    skin, cloth = [], []
    hip = 0.95; sit = pose == 'sit'
    if sit: hip = 0.5
    up = hip - 0.95
    lean = rr.uniform(-.03, .05)
    skin += [('ell', P(0, .01 + lean, 1.63 + up), (1, .95, 1.18), .118 * s), ('cap', P(0, lean, 1.44 + up), P(0, lean, 1.56 + up), .055 * s)]
    cloth += [('ell', P(0, lean * .7, 1.23 + up), (1, .62, 1.25), .205 * s), ('ell', P(0, 0, .96 + up), (1, .72, .8), .175 * s)]
    # piernas
    for sx in (-1, 1):
        if sit:
            skin += [('cap', P(sx * .1, .02, .5), P(sx * .11, .44, .49), .075 * s), ('cap', P(sx * .11, .44, .49), P(sx * .12, .47, .07), .058 * s),
                     ('ell', P(sx * .12, .52, .04), (.6, 1.4, .4), .07 * s)]
        elif pose == 'fight':
            skin += [('cap', P(sx * .12, 0, .9), P(sx * .2, sx * .12, .5), .08 * s), ('cap', P(sx * .2, sx * .12, .5), P(sx * .24, sx * .14, .08), .062 * s),
                     ('ell', P(sx * .24, sx * .14 + .06, .04), (.6, 1.4, .4), .07 * s)]
        else:
            st = rr.uniform(-.06, .06) * sx
            skin += [('cap', P(sx * .095, 0, .9), P(sx * .1, .02 + st, .49), .077 * s), ('cap', P(sx * .1, .02 + st, .49), P(sx * .1, st, .08), .06 * s),
                     ('ell', P(sx * .1, st + .06, .04), (.6, 1.4, .4), .07 * s)]
    # brazos
    arms = {'stand': [((.27, .02, 1.13), (.28, .06, .88)), ((-.27, .02, 1.13), (-.28, .06, .88))],
            'sit': [((.26, .1, 1.13 + up), (.2, .34, 1.02 + up)), ((-.26, .1, 1.13 + up), (-.2, .34, 1.02 + up))],
            'raise': [((.3, .02, 1.72), (.33, .05, 2.0)), ((-.27, .02, 1.13), (-.28, .06, .88))],
            'cheer': [((.32, 0, 1.75 + up), (.36, .05, 2.02 + up)), ((-.32, 0, 1.75 + up), (-.36, .05, 2.02 + up))],
            'fight': [((.3, .25, 1.3), (.3, .55, 1.35)), ((-.3, .2, 1.2), (-.2, .45, 1.15))]}[pose]
    if pose == 'sit' and rr.random() < .35: arms = [((.32, 0, 1.75 + up), (.36, .05, 2.02 + up)), arms[1]]
    for (e, w), sx in zip(arms, (1, -1)):
        sh = P(sx * .2, 0, 1.42 + up)
        skin += [('cap', sh, P(*e), .052 * s), ('cap', P(*e), P(*w), .045 * s), ('ball', P(w[0], w[1], w[2] - .04), .05 * s)]
    if garment == 'tunic':
        cloth += [('ell', P(0, .02 if not sit else .2, .74 + (0 if not sit else -.25)), (1, .85 if not sit else 1.6, 1.45 if not sit else .5), .23 * s)]
    elif garment == 'toga':
        cloth += [('ell', P(0, .02 if not sit else .22, .6 if not sit else .32), (1.05, .9 if not sit else 1.7, 2.3 if not sit else .7), .24 * s),
                  ('cap', P(-.22, .02, 1.44 + up), P(.16, .06, .85 + up), .12 * s), ('ell', P(-.2, 0, 1.3 + up), (.6, .8, 1.3), .13 * s)]
    elif garment == 'loin':
        cloth += [('ell', P(0, .01, .88), (1.05, .8, .55), .2 * s)]
    return cloth, skin

def make_figure(name, pose, h, garment, m_cloth, m_skin, seed=0, res=0.035, extra=None):
    cloth, skin = human(pose, h, garment, seed, res)
    items = [(_meta_mesh(cloth, res * h / 1.75), m_cloth), (_meta_mesh(skin, res * h / 1.75), m_skin)]
    me = join_meshes(name, items)
    if extra:
        b = Builder(name + '_x'); b.add(extra); ob = b.build(LIB)
        tmp = ob.data; items2 = [(me, None)]
        # unir accesorios (escudo, casco, espada) a la figura
        V0 = len(me.vertices)
        bm = __import__('bmesh').new(); bm.from_mesh(me); bm2 = __import__('bmesh').new(); bm2.from_mesh(tmp)
        for m in tmp.materials:
            if m.name not in me.materials: me.materials.append(m)
        remap = {i: list(me.materials).index(m) for i, m in enumerate(tmp.materials)}
        for f in bm2.faces: f.material_index = remap[f.material_index]
        tmpm = bpy.data.meshes.new('t'); bm2.to_mesh(tmpm); bm2.free()
        bm.from_mesh(tmpm); bm.to_mesh(me); bm.free()
        bpy.data.meshes.remove(tmpm); bpy.data.objects.remove(ob); bpy.data.meshes.remove(tmp)
    ob = bpy.data.objects.new(name, me); LIB.objects.link(ob)
    return ob

def place(lib_ob, loc, rot=0.0, scale=1.0, coll=None):
    o = bpy.data.objects.new(lib_ob.name + '_i', lib_ob.data); (coll or scene.collection).objects.link(o)
    o.location = loc; o.rotation_euler = (0, 0, rot); o.scale = (scale, scale, scale); return o

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
STATUES = [make_figure(f'estatua{k}', ['stand', 'raise', 'stand', 'raise'][k], 2.5, ['toga', 'tunic', 'tunic', 'toga'][k], MAT['marble'], MAT['marble'], seed=k) for k in range(4)]
col_stat = bpy.data.collections.new('Estatuas'); col_main.children.link(col_stat)
for i in range(NB):
    M, L, th = bay_matrix(i, 0, L1)
    for S in STO[1:]:
        p = M @ Vector((0, -.8, S['y0'] + .6))
        place(STATUES[(i + len(S)) % 4], p, th, 1.0, col_stat)

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
    """Palco en el podio; su +y local mira hacia el centro de la arena y el palco se hunde hacia -y."""
    tmid = -math.pi / 2 if side < 0 else math.pi / 2
    p = pt(tmid, DA); rot = math.atan2(p[0], -p[1])
    M = Matrix.Translation((p[0], p[1], 0)) @ Matrix.Rotation(rot, 4, 'Z')
    cl = 'purple' if royal else 'canvas'
    f = []
    f += box(-w / 2, w / 2, -depth, .6, 0, 4.2, 'marble')
    f += box(-w / 2, w / 2, -depth, .6, 4.2, 4.3, cl)
    for x in (-w / 2 + .4, -w / 6, w / 6, w / 2 - .4):
        f += cyl(x, .2, .28, .25, 4.3, 8.9, 'marble', seg=10)
        f += cyl(x, -depth + .3, .28, .25, 4.3, 8.9, 'marble', seg=10)
    f += box(-w / 2 - .3, w / 2 + .3, -depth - .2, .8, 8.9, 9.5, 'marble')
    f += [([(-w / 2 - .3, .8, 9.5), (w / 2 + .3, .8, 9.5), (w / 2 + .3, -depth / 2, 11.2), (-w / 2 - .3, -depth / 2, 11.2)], 'marble'),
          ([(w / 2 + .3, -depth - .2, 9.5), (-w / 2 - .3, -depth - .2, 9.5), (-w / 2 - .3, -depth / 2, 11.2), (w / 2 + .3, -depth / 2, 11.2)], 'marble')]
    f += box(-w / 2 + .3, w / 2 - .3, .5, .56, 4.3, 5.25, cl)
    f += box(-w / 2, w / 2, .5, .62, 8.2, 8.9, cl)
    ba.add(f, M)
    return M, rot
M_PULV, PULV_ROT = pulvinar(-1, 13, 4.2, True)
pulvinar(1, 10, 3.2, False)
ba.build(col_main)

# ------------------------------------------------------------------ entorno
def ground_h(x, y):
    h = 0.0
    for cx, cy, rx, ry, hh in HILLS:
        dx, dy = (x - cx) / rx, (y - cy) / ry; d2 = dx * dx + dy * dy
        if d2 < 4: h += hh * math.exp(-d2 * 1.6)
    e = math.sqrt((x / 250) ** 2 + (y / 230) ** 2)
    return h * min(1.0, max(0.0, (e - 1.0) / 0.8))
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
        if max(abs(x0), abs(x1)) < 240 and max(abs(y0), abs(y1)) < 220:
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
def far_h(r, az):
    h = 25 * math.sin(az * 5 + r / 3000) + 18 * math.sin(az * 11 + 1.3) + 12 * math.sin(r / 900 + az * 3)
    h = max(h, 0) + 10
    def mount(az0, w, r0, r1, H):
        da = math.atan2(math.sin(az - az0), math.cos(az - az0))
        return H * math.exp(-(da / w) ** 2) * math.exp(-((r - (r0 + r1) / 2) / ((r1 - r0) / 2)) ** 2)
    h += mount(math.radians(150), .28, 16000, 30000, 900)   # Colli Albani (sureste)
    h += mount(math.radians(62), .35, 22000, 40000, 1100)   # Montes Sabinos / Tiburtinos (noreste)
    h += mount(math.radians(290), .25, 2500, 5000, 110)     # Janículo y Monte Mario (oeste)
    h *= min(1, (r - 2100) / 1500) if r < 3600 else 1
    return h
rs = [2100 * (45000 / 2100) ** (k / 40) for k in range(41)]
na = 144
for k in range(40):
    for j in range(na):
        a0, a1 = 2 * math.pi * j / na, 2 * math.pi * (j + 1) / na
        q = []
        for r, a in ((rs[k], a0), (rs[k], a1), (rs[k + 1], a1), (rs[k + 1], a0)):
            q.append((r * math.sin(a), r * math.cos(a), far_h(r, a) - .5))
        bfar.face(q, 'ground')
bfar.face([(-1500, -1500, -.6), (1500, -1500, -.6), (1500, 1500, -.6), (-1500, 1500, -.6)], 'ground')
bfar.build(col_env)

# Coloso de Nerón / Sol (remodelado por Cómodo)
CX, CY = -148.0, 32.0
bco = Builder('coloso_base')
bco.add(box(-8.5, 8.5, -7, 7, 0, 7.5, 'marble')); bco.add(box(-9.2, 9.2, -7.7, 7.7, 7.5, 8.2, 'marble')); bco.add(box(-9.2, 9.2, -7.7, 7.7, 0, .6, 'marble'))
H = 34.0; hz = 8.2 + H * 1.63 / 1.75
for k in range(9):
    a = math.radians(-70 + 140 * k / 8)
    bco.add(cyl(0, 0, .55, .05, 0, 6.8, 'bronze', seg=6), Matrix.Translation((0, 0, hz)) @ Matrix.Rotation(a, 4, 'Y'))
bco.add(cyl(-.3 * H / 1.75 - .3, 1.2, .45, .45, 8.2, 8.2 + 28, 'bronze', seg=10))
bco.add(box(-.3 * H / 1.75 - 2.6, -.3 * H / 1.75 + 2.0, 1.0, 1.4, 8.2, 8.2 + 7, 'bronze'))
o = bco.build(col_env); o.location = (CX, CY, 0); o.rotation_euler = (0, 0, math.radians(-80))
colf = make_figure('coloso', 'raise', H, 'toga', MAT['bronze'], MAT['bronze'], seed=7, res=0.011)
col_o = place(colf, (CX, CY, 8.2), math.radians(-80), 1.0, col_env)

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

# Ciudad: ínsulas con patio, tejados a dos aguas, tiendas y balcones
bci = Builder('ciudad'); bcf = Builder('ciudad_lejana')
excl = [(0, 0, A + 62, B + 62), (-300, 48, 92, 68), (175, 58, 76, 56), (300, 260, 150, 125), (-148, 32, 28, 28), (-118, -52, 24, 24), (-10, -40, 150, 70)]
def free(x, y):
    for cx, cy, rx, ry in excl:
        if ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 < 1: return False
    if math.hypot((x + 360) / 190, (y + 250) / 150) < .95: return False
    return True
def gable(x0, x1, y0, y1, z, over=.7):
    sx, sy = x1 - x0, y1 - y0
    if sx >= sy:
        rh = sy * .28; ym = (y0 + y1) / 2
        return [([(x0 - over, y0 - over, z), (x1 + over, y0 - over, z), (x1 + over, ym, z + rh), (x0 - over, ym, z + rh)], 'tile'),
                ([(x1 + over, y1 + over, z), (x0 - over, y1 + over, z), (x0 - over, ym, z + rh), (x1 + over, ym, z + rh)], 'tile'),
                ([(x0, y0, z), (x0, ym, z + rh), (x0, y1, z)], None), ([(x1, y1, z), (x1, ym, z + rh), (x1, y0, z)], None)]
    rh = sx * .28; xm = (x0 + x1) / 2
    return [([(x1 + over, y0 - over, z), (x1 + over, y1 + over, z), (xm, y1 + over, z + rh), (xm, y0 - over, z + rh)], 'tile'),
            ([(x0 - over, y1 + over, z), (x0 - over, y0 - over, z), (xm, y0 - over, z + rh), (xm, y1 + over, z + rh)], 'tile'),
            ([(x0, y1, z), (xm, y1, z + rh), (x1, y1, z)], None), ([(x1, y0, z), (xm, y0, z + rh), (x0, y0, z)], None)]
def facade(x0, x1, y, z0, floors, outward, rng):
    """Ventanas y tiendas sobre una fachada paralela a x en y (outward = ±1)."""
    f = []; yy = y + outward * .03; w = x1 - x0
    n = max(1, int(w / 3.4))
    for c in range(n):
        xa = x0 + (c + .5) * w / n
        if rng.random() < .75: f.append(([(xa - 1.1, yy, z0), (xa + 1.1, yy, z0), (xa + 1.1, yy, z0 + 2.6), (xa - 1.1, yy, z0 + 2.6)][::outward], 'dark'))
        for fl in range(1, floors):
            if rng.random() < .85:
                zb = z0 + fl * 3.2 + .9
                f.append(([(xa - .45, yy, zb), (xa + .45, yy, zb), (xa + .45, yy, zb + 1.3), (xa - .45, yy, zb + 1.3)][::outward], 'dark'))
    if floors > 2 and rng.random() < .5:
        f += box(x0 + 1, x1 - 1, *sorted((y, y + outward * 1.1)), z0 + 3.2, z0 + 3.4, 'wood')
        f += box(x0 + 1, x1 - 1, *sorted((y + outward * 1.0, y + outward * 1.1)), z0 + 3.4, z0 + 4.3, 'wood')
    return f
def insula(bld, M, w, d, floors, court, wall, rng, detail):
    h = floors * 3.2; f = []
    if court:
        g = min(w, d) * .3
        wings = [(-w / 2, w / 2, -d / 2, -d / 2 + g), (-w / 2, w / 2, d / 2 - g, d / 2), (-w / 2, -w / 2 + g, -d / 2 + g, d / 2 - g), (w / 2 - g, w / 2, -d / 2 + g, d / 2 - g)]
    else:
        wings = [(-w / 2, w / 2, -d / 2, d / 2)]
    for (x0, x1, y0, y1) in wings:
        f += box(x0, x1, y0, y1, 0, h, wall)
        f += [(pts, m or wall) for pts, m in gable(x0, x1, y0, y1, h)]
    if detail:
        f += facade(-w / 2, w / 2, -d / 2, 0, floors, -1, rng)
        f += facade(-w / 2, w / 2, d / 2, 0, floors, 1, rng)
        Mr = Matrix.Rotation(math.pi / 2, 4, 'Z')
        f += xf(facade(-d / 2, d / 2, w / 2, 0, floors, -1, rng), Mr)
        f += xf(facade(-d / 2, d / 2, -w / 2, 0, floors, 1, rng), Mr)
    bld.add(f, M)
SP = 46.0
walls = ['plaster_ochre', 'plaster_cream', 'plaster_red', 'plaster_pink', 'brick', 'plaster_ochre', 'plaster_white']
count = 0
for gx in range(-30, 31):
    for gy in range(-30, 31):
        x, y = gx * SP + R.uniform(-5, 5), gy * SP + R.uniform(-5, 5)
        r = math.hypot(x, y)
        if r < 140 or r > 1400 or not free(x, y): continue
        if R.random() < .08: continue  # huertos y plazas
        z = ground_h(x, y)
        ang = .25 * math.sin(x / 420) + .22 * math.cos(y / 380) + R.uniform(-.05, .05)
        on_hill = z > 12
        w, d = R.uniform(26, 38), R.uniform(22, 34)
        floors = R.choice([2, 2, 3]) if on_hill else R.choice([3, 4, 4, 5] if r < 700 else [2, 3, 3, 4])
        M = Matrix.Translation((x, y, z - 1.2)) @ Matrix.Rotation(ang, 4, 'Z')
        insula(bci if r < 750 else bcf, M, w, d, floors, w > 28 and R.random() < .65, R.choice(walls), R, r < 750)
        count += 1
bci.build(col_env); bcf.build(col_env)
print('insulas', count)

# Árboles: cipreses y pinos piñoneros en colinas, jardines y calles
btr = Builder('arboles')
for k in range(1400):
    x, y = R.uniform(-1300, 1300), R.uniform(-1300, 1300)
    z = ground_h(x, y); rr_ = math.hypot(x, y)
    if rr_ < 125: continue
    if z < 8 and R.random() < .6: continue
    if R.random() < .5:
        h = R.uniform(11, 19); btr.add(cyl(x, y, .25, .2, z - .5, z + 2, 'wood', seg=5)); btr.add(cyl(x, y, 1.2, .08, z + 1.5, z + h, 'leaf', seg=7))
    else:
        h = R.uniform(11, 17); lean = R.uniform(-2, 2)
        btr.add([([(x, y, z - .5), (x + .5, y, z - .5), (x + .5 + lean, y, z + h), (x + lean, y, z + h)], 'wood')])
        for c in range(5):
            btr.add(sphere(x + lean + R.uniform(-3.5, 3.5), y + R.uniform(-3.5, 3.5), z + h + R.uniform(-.5, 1.2), R.uniform(3, 5.5), 'leaf', seg=8, rings=4, sz=.35))
btr.build(col_env)

# ------------------------------------------------------------------ calles con adoquín de basalto
broad = Builder('calles')
for pts, w in (([(-94, 0), (-180, 30), (-230, 48)], 16), ([(94, 0), (230, 40), (500, 80)], 14), ([(-60, -60), (-140, -130), (-230, -200)], 14), ([(40, -70), (90, -160), (150, -260)], 12)):
    for (x0, y0), (x1, y1) in zip(pts[:-1], pts[1:]):
        dx, dy = x1 - x0, y1 - y0; L = math.hypot(dx, dy); nx_, ny_ = -dy / L * w / 2, dx / L * w / 2
        broad.face([(x0 + nx_, y0 + ny_, -.02), (x1 + nx_, y1 + ny_, -.02), (x1 - nx_, y1 - ny_, -.02), (x0 - nx_, y0 - ny_, -.02)], 'basalt')
broad.build(col_env)

if 'dia' in sys.argv:
    exec(open(__file__.replace('build_scene.py', 'dia_espectaculo.py')).read())

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
