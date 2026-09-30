"""Casa Volado en distintos estilos, renderizada con Blender Cycles al atardecer.

Uso: python3 casa_estilos.py <estilo> <salida.png> <ancho> <muestras> [vista]
Estilos: minimalista, cristal, elegante, tropical, concreto, nordico
Vistas: jardin (por defecto), calle
Coordenadas en metros: x = ancho del terreno (0-10), y = fondo (0 = calle, 20 = fondo), z = altura.
"""
import bpy, math, random, sys
import numpy as np
from mathutils import Vector, Matrix

style, OUT, W, SAMPLES = sys.argv[-5:-1] if len(sys.argv) > 5 and sys.argv[-1] in ('jardin', 'calle') else sys.argv[-4:]
VIEW = sys.argv[-1] if sys.argv[-1] in ('jardin', 'calle') else 'jardin'
W, SAMPLES = int(W), int(SAMPLES)
R = random.Random(7)
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene

# ------------------------------------------------------------------ materiales
def mat(name, color, rough=.6, metal=0., extra=None, **inputs):
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree; p = nt.nodes['Principled BSDF']
    p.inputs['Base Color'].default_value = (*color, 1); p.inputs['Roughness'].default_value = rough; p.inputs['Metallic'].default_value = metal
    for k, v in inputs.items(): p.inputs[k.replace('_', ' ')].default_value = v
    if extra: extra(nt, p)
    return m
def coord(nt, kind): return nt.nodes.new('ShaderNodeTexCoord').outputs[kind]
def noise_color(nt, p, c1, c2, scale, bump=0.1, fine=30, kind='Object'):
    n = nt.nodes.new('ShaderNodeTexNoise'); n.inputs['Scale'].default_value = scale; n.inputs['Detail'].default_value = 8
    nt.links.new(coord(nt, kind), n.inputs['Vector'])
    r = nt.nodes.new('ShaderNodeValToRGB'); r.color_ramp.elements[0].color = (*c1, 1); r.color_ramp.elements[1].color = (*c2, 1)
    nt.links.new(n.outputs['Fac'], r.inputs['Fac']); nt.links.new(r.outputs['Color'], p.inputs['Base Color'])
    if bump:
        n2 = nt.nodes.new('ShaderNodeTexNoise'); n2.inputs['Scale'].default_value = fine; nt.links.new(coord(nt, kind), n2.inputs['Vector'])
        b = nt.nodes.new('ShaderNodeBump'); b.inputs['Strength'].default_value = bump; b.inputs['Distance'].default_value = .01
        nt.links.new(n2.outputs['Fac'], b.inputs['Height']); nt.links.new(b.outputs['Normal'], p.inputs['Normal'])
def planks(nt, p, c1, c2, width=.15, along='v', bump=.3, gap=.004):
    """Tablas o lamas en UV métricas: vetas con Wave + juntas con Brick."""
    uv = coord(nt, 'UV')
    br = nt.nodes.new('ShaderNodeTexBrick'); br.offset = .5
    br.inputs['Scale'].default_value = 1; br.inputs['Mortar Size'].default_value = gap
    if along == 'v':
        mp = nt.nodes.new('ShaderNodeMapping'); mp.inputs['Rotation'].default_value = (0, 0, math.pi / 2); nt.links.new(uv, mp.inputs['Vector']); uv = mp.outputs['Vector']
    br.inputs['Brick Width'].default_value = 2.4; br.inputs['Row Height'].default_value = width
    br.inputs['Color1'].default_value = (*c1, 1); br.inputs['Color2'].default_value = (*c2, 1); br.inputs['Mortar'].default_value = (*[c * .35 for c in c1], 1)
    nt.links.new(uv, br.inputs['Vector'])
    wv = nt.nodes.new('ShaderNodeTexWave'); wv.inputs['Scale'].default_value = 6; wv.inputs['Distortion'].default_value = 8; wv.inputs['Detail'].default_value = 4
    nt.links.new(uv, wv.inputs['Vector'])
    mix = nt.nodes.new('ShaderNodeMix'); mix.data_type = 'RGBA'; mix.blend_type = 'MULTIPLY'; mix.inputs['Factor'].default_value = .35
    nt.links.new(br.outputs['Color'], mix.inputs[6]); nt.links.new(wv.outputs['Color'], mix.inputs[7]); nt.links.new(mix.outputs[2], p.inputs['Base Color'])
    b = nt.nodes.new('ShaderNodeBump'); b.inputs['Strength'].default_value = bump; b.inputs['Distance'].default_value = .02
    nt.links.new(br.outputs['Fac'], b.inputs['Height']); nt.links.new(b.outputs['Normal'], p.inputs['Normal'])
def stone_blocks(nt, p, c1, c2, mortar, bw=1.2, rh=.6, gap=.006, bump=.2):
    uv = coord(nt, 'UV')
    br = nt.nodes.new('ShaderNodeTexBrick'); br.offset = .5; br.inputs['Scale'].default_value = 1
    br.inputs['Mortar Size'].default_value = gap; br.inputs['Brick Width'].default_value = bw; br.inputs['Row Height'].default_value = rh
    br.inputs['Color1'].default_value = (*c1, 1); br.inputs['Color2'].default_value = (*c2, 1); br.inputs['Mortar'].default_value = (*mortar, 1)
    nt.links.new(uv, br.inputs['Vector'])
    n = nt.nodes.new('ShaderNodeTexNoise'); n.inputs['Scale'].default_value = 9; nt.links.new(coord(nt, 'Object'), n.inputs['Vector'])
    mix = nt.nodes.new('ShaderNodeMix'); mix.data_type = 'RGBA'; mix.blend_type = 'OVERLAY'; mix.inputs['Factor'].default_value = .25
    nt.links.new(br.outputs['Color'], mix.inputs[6]); nt.links.new(n.outputs['Color'], mix.inputs[7]); nt.links.new(mix.outputs[2], p.inputs['Base Color'])
    b = nt.nodes.new('ShaderNodeBump'); b.inputs['Strength'].default_value = bump
    inv = nt.nodes.new('ShaderNodeMath'); inv.operation = 'SUBTRACT'; inv.inputs[0].default_value = 1; nt.links.new(br.outputs['Fac'], inv.inputs[1])
    nt.links.new(inv.outputs[0], b.inputs['Height']); nt.links.new(b.outputs['Normal'], p.inputs['Normal'])
def emission(name, color, strength):
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree; nt.nodes.clear()
    e = nt.nodes.new('ShaderNodeEmission'); e.inputs['Color'].default_value = (*color, 1); e.inputs['Strength'].default_value = strength
    o = nt.nodes.new('ShaderNodeOutputMaterial'); nt.links.new(e.outputs[0], o.inputs[0]); return m

WARM = (1.0, 0.66, 0.36)
M = {
 'white': mat('estuco_blanco', (.86, .85, .82), .75, extra=lambda nt, p: noise_color(nt, p, (.82, .81, .78), (.9, .89, .86), 2, .05, 60)),
 'offwhite': mat('estuco_hueso', (.84, .8, .72), .8, extra=lambda nt, p: noise_color(nt, p, (.8, .76, .68), (.88, .84, .76), 2, .05, 60)),
 'concrete': mat('concreto', (.5, .5, .48), .85, extra=lambda nt, p: planks(nt, p, (.46, .46, .44), (.54, .53, .51), .3, 'h', .15, .002)),
 'concrete_dark': mat('concreto_oscuro', (.26, .26, .26), .8, extra=lambda nt, p: noise_color(nt, p, (.22, .22, .22), (.3, .3, .29), 1.5, .08, 40)),
 'glass': mat('vidrio', (.92, .96, .96), .0, Transmission_Weight=1.0, IOR=1.5),
 'frame': mat('marco_negro', (.025, .025, .025), .35, .6),
 'bronze': mat('bronce', (.42, .27, .15), .32, 1.0),
 'steel': mat('acero_blanco', (.9, .9, .9), .3, .2),
 'wood': mat('madera_teca', (.45, .27, .14), .55, extra=lambda nt, p: planks(nt, p, (.42, .25, .12), (.55, .34, .18), .12, 'v', .25)),
 'wood_light': mat('madera_roble', (.72, .56, .38), .55, extra=lambda nt, p: planks(nt, p, (.68, .52, .35), (.8, .64, .45), .14, 'h', .15)),
 'charred': mat('madera_quemada', (.03, .03, .03), .7, extra=lambda nt, p: planks(nt, p, (.02, .02, .02), (.05, .045, .04), .16, 'v', .5)),
 'deck': mat('deck', (.5, .32, .18), .6, extra=lambda nt, p: planks(nt, p, (.46, .29, .16), (.6, .4, .23), .14, 'h', .3)),
 'travertine': mat('travertino', (.8, .72, .6), .45, extra=lambda nt, p: stone_blocks(nt, p, (.78, .7, .58), (.86, .78, .66), (.62, .55, .46), .9, .45, .003, .1)),
 'marble': mat('marmol', (.9, .89, .86), .2, extra=lambda nt, p: noise_color(nt, p, (.84, .83, .8), (.95, .94, .92), 1.3, .02, 20)),
 'stone': mat('piedra', (.35, .33, .3), .9, extra=lambda nt, p: stone_blocks(nt, p, (.3, .28, .25), (.44, .41, .37), (.18, .17, .16), .55, .22, .01, .5)),
 'slate': mat('piedra_oscura', (.16, .16, .16), .7, extra=lambda nt, p: stone_blocks(nt, p, (.12, .12, .13), (.2, .2, .2), (.08, .08, .08), 1.2, .6, .004, .2)),
 'water': mat('agua', (.55, .85, .9), .02, Transmission_Weight=1.0, IOR=1.33),
 'pooltile': mat('azulejo', (.35, .7, .78), .25, extra=lambda nt, p: stone_blocks(nt, p, (.3, .66, .75), (.4, .75, .82), (.8, .85, .85), .1, .1, .06, .1)),
 'grass': mat('pasto', (.16, .3, .08), .9, extra=lambda nt, p: noise_color(nt, p, (.1, .22, .05), (.2, .34, .1), 3, .6, 300)),
 'leaf': mat('hoja', (.08, .2, .05), .6, Subsurface_Weight=.1, extra=lambda nt, p: noise_color(nt, p, (.05, .15, .03), (.13, .28, .07), 2, .3, 50)),
 'trunk': mat('tronco', (.35, .3, .24), .9, extra=lambda nt, p: noise_color(nt, p, (.28, .24, .19), (.42, .37, .3), 5, .6, 40)),
 'floor_in': mat('piso_interior', (.72, .66, .58), .3),
 'wall_in': mat('muro_interior', (.85, .83, .8), .8),
 'fabric': mat('tela', (.62, .58, .52), .9),
 'fabric_dark': mat('tela_oscura', (.18, .17, .16), .9),
 'neighbor': mat('vecino', (.4, .39, .37), .9),
 'hedge': mat('seto', (.07, .17, .05), .9, extra=lambda nt, p: noise_color(nt, p, (.04, .12, .03), (.12, .24, .06), 6, 1.0, 40)),
 'lamp': emission('lampara', WARM, 18),
 'led': emission('led', WARM, 30),
 'poollight': emission('luz_alberca', (.4, .85, 1.0), 60),
}

# ------------------------------------------------------------------ geometría
class B:
    def __init__(s, name): s.name = name; s.V = []; s.F = []; s.Mi = []; s.mats = []
    def face(s, pts, m):
        mm = M[m] if isinstance(m, str) else m
        if mm not in s.mats: s.mats.append(mm)
        i = len(s.V); s.V += pts; s.F.append(list(range(i, i + len(pts)))); s.Mi.append(s.mats.index(mm))
    def box(s, x0, x1, y0, y1, z0, z1, m, Mx=None):
        v = [(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0), (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)]
        if Mx: v = [tuple(Mx @ Vector(p)) for p in v]
        for f in ((0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)): s.face([v[i] for i in f], m)
    def cyl(s, cx, cy, r0, r1, z0, z1, m, seg=16, Mx=None):
        for i in range(seg):
            a, b = 2 * math.pi * i / seg, 2 * math.pi * (i + 1) / seg
            q = [(cx + r0 * math.cos(a), cy + r0 * math.sin(a), z0), (cx + r0 * math.cos(b), cy + r0 * math.sin(b), z0), (cx + r1 * math.cos(b), cy + r1 * math.sin(b), z1), (cx + r1 * math.cos(a), cy + r1 * math.sin(a), z1)]
            if Mx: q = [tuple(Mx @ Vector(p)) for p in q]
            s.face(q, m)
        top = [(cx + r1 * math.cos(2 * math.pi * i / seg), cy + r1 * math.sin(2 * math.pi * i / seg), z1) for i in range(seg)]
        if Mx: top = [tuple(Mx @ Vector(p)) for p in top]
        s.face(top, m)
    def build(s, smooth=False):
        me = bpy.data.meshes.new(s.name); me.from_pydata(s.V, [], s.F)
        for m in s.mats: me.materials.append(m)
        me.polygons.foreach_set('material_index', s.Mi)
        uvl = me.uv_layers.new(name='UV'); n = len(me.polygons)
        nr = np.zeros(n * 3); me.polygons.foreach_get('normal', nr); nr = nr.reshape(-1, 3)
        co = np.zeros(len(me.vertices) * 3); me.vertices.foreach_get('co', co); co = co.reshape(-1, 3)
        lv = np.zeros(len(me.loops), np.int32); me.loops.foreach_get('vertex_index', lv)
        lt = np.zeros(n, np.int32); me.polygons.foreach_get('loop_total', lt)
        N = nr[np.repeat(np.arange(n), lt)]; P = co[lv]
        hz = np.abs(N[:, 2]) > .7
        t = np.stack([-N[:, 1], N[:, 0]], 1); tl = np.linalg.norm(t, axis=1, keepdims=True); tl[tl == 0] = 1; t /= tl
        u = np.where(hz, P[:, 0], P[:, 0] * t[:, 0] + P[:, 1] * t[:, 1]); v = np.where(hz, P[:, 1], P[:, 2])
        uvl.data.foreach_set('uv', np.stack([u, v], 1).ravel())
        me.update()
        if smooth: me.shade_smooth()
        ob = bpy.data.objects.new(s.name, me); sc.collection.objects.link(ob); return ob

def glazing(b, axis, c, a0, a1, z0, z1, panes, depth=0.0, frame=.05, fm='frame', mullion=True):
    """Muro cortina: vidrio + marco perimetral + parteluces. axis 'x' = fachada paralela a x en y=c."""
    def bx(p0, p1, q0, q1, zz0, zz1, m):
        if axis == 'x': b.box(p0, p1, q0, q1, zz0, zz1, m)
        else: b.box(q0, q1, p0, p1, zz0, zz1, m)
    bx(a0, a1, c - .012, c + .012, z0, z1, 'glass')
    bx(a0, a1, c - .05, c + .05, z0, z0 + frame, fm); bx(a0, a1, c - .05, c + .05, z1 - frame, z1, fm)
    bx(a0, a0 + frame, c - .05, c + .05, z0, z1, fm); bx(a1 - frame, a1, c - .05, c + .05, z0, z1, fm)
    if mullion:
        for k in range(1, panes):
            x = a0 + (a1 - a0) * k / panes; bx(x - frame / 2, x + frame / 2, c - .05, c + .05, z0, z1, fm)

def interior(b, lights, level_z, y0, y1, dense=True):
    """Pisos, plafón, muebles y lámparas visibles a través del vidrio."""
    b.box(.2, 9.8, y0, y1, level_z, level_z + .02, 'floor_in')
    b.box(.2, 9.8, y0, y1, level_z + 2.83, level_z + 2.85, 'wall_in')
    b.box(.2, .3, y0, y1, level_z, level_z + 2.85, 'wall_in'); b.box(9.7, 9.8, y0, y1, level_z, level_z + 2.85, 'wall_in')
    b.box(.2, 9.8, y0, y0 + .1, level_z, level_z + 2.85, 'wall_in')
    if dense:
        b.box(6.6, 9.4, y1 - 3.6, y1 - 2.7, level_z, level_z + .42, 'fabric'); b.box(6.6, 9.4, y1 - 3.6, y1 - 3.4, level_z, level_z + .8, 'fabric')
        b.box(9.0, 9.4, y1 - 3.6, y1 - 1.8, level_z, level_z + .6, 'fabric')
        b.box(7.2, 8.4, y1 - 2.2, y1 - 1.5, level_z, level_z + .38, 'wood_light')
        b.box(3.6, 5.6, y1 - 3.4, y1 - 2.4, level_z + .72, level_z + .76, 'wood_light'); b.box(4.4, 4.8, y1 - 3.1, y1 - 2.7, level_z, level_z + .72, 'frame')
        for x in (3.8, 4.4, 5.0):
            b.cyl(x + .2, y1 - 2.9, .1, .1, level_z + 2.05, level_z + 2.25, 'lamp', 10)
        b.box(.4, 1.0, y1 - 5, y1 - 1, level_z, level_z + .9, 'wood_light'); b.box(1.6, 2.6, y1 - 4.2, y1 - 1.8, level_z, level_z + .92, 'marble')
        b.box(.3, .45, y1 - 6, y1 - 3, level_z + 1.5, level_z + 2.3, 'wood_light')
        b.box(1.5, 3.0, y1 - 1.2, y1 - .5, level_z, level_z + .05, 'fabric_dark')
    for (x, y) in lights:
        L = bpy.data.lights.new('luz', 'AREA'); L.energy = 150; L.color = WARM; L.size = 1.4
        o = bpy.data.objects.new('luz', L); sc.collection.objects.link(o); o.location = (x, y, level_z + 2.75); o.rotation_euler = (0, 0, 0)

def palm(b, x, y, h, lean=.1, fronds=13):
    segs = 10
    for k in range(segs):
        z0, z1 = h * k / segs, h * (k + 1) / segs
        x0, x1 = x + lean * (z0 / h) ** 2, x + lean * (z1 / h) ** 2
        r0, r1 = .2 - .07 * k / segs, .2 - .07 * (k + 1) / segs
        for i in range(12):
            a, c = 2 * math.pi * i / 12, 2 * math.pi * (i + 1) / 12
            b.face([(x0 + r0 * math.cos(a), y + r0 * math.sin(a), z0), (x0 + r0 * math.cos(c), y + r0 * math.sin(c), z0),
                    (x1 + r1 * math.cos(c), y + r1 * math.sin(c), z1), (x1 + r1 * math.cos(a), y + r1 * math.sin(a), z1)], 'trunk')
    tx, tz = x + lean, h
    for f in range(fronds):
        a = 2 * math.pi * f / fronds + R.uniform(-.2, .2); L = R.uniform(2.4, 3.2); droop = R.uniform(.3, .6)
        prev = None
        for s in range(8):
            t0, t1 = s / 8, (s + 1) / 8
            def pnt(t, side):
                r = L * t; z = tz + .6 * math.sin(math.pi * t * .6) - droop * L * t * t
                w = .55 * math.sin(math.pi * min(1, t * 1.2)) + .05
                return (tx + r * math.cos(a) - side * w * math.sin(a), y + r * math.sin(a) + side * w * math.cos(a), z - abs(side) * .12)
            b.face([pnt(t0, -1), pnt(t1, -1), pnt(t1, 0), pnt(t0, 0)], 'leaf'); b.face([pnt(t0, 0), pnt(t1, 0), pnt(t1, 1), pnt(t0, 1)], 'leaf')

def shrub(b, x, y, r, m='hedge'):
    for k in range(5):
        cx, cy, cz = x + R.uniform(-r, r) * .6, y + R.uniform(-r, r) * .6, r * R.uniform(.5, 1.1)
        rr = r * R.uniform(.55, .85); seg = 10
        for j in range(6):
            p0, p1 = math.pi * j / 6 - math.pi / 2, math.pi * (j + 1) / 6 - math.pi / 2
            for i in range(seg):
                a0, a1 = 2 * math.pi * i / seg, 2 * math.pi * (i + 1) / seg
                q = [(cx + rr * math.cos(p) * math.cos(a), cy + rr * math.cos(p) * math.sin(a), cz + rr * .8 * math.sin(p)) for p, a in ((p0, a0), (p0, a1), (p1, a1), (p1, a0))]
                b.face(q, m)

# ------------------------------------------------------------------ casa por estilo
S = dict(
 minimalista=dict(wall='white', pa='white', base='white', slab='white', deck='deck', frame='frame', fin=None, overhang=.4, parapet=.5, led=False, recess=1.1, palms=2),
 cristal=dict(wall='white', pa='glass', base='slate', slab='steel', deck='marble', frame='frame', fin=None, overhang=.7, parapet=0, led=True, recess=0, palms=2, glass_side=True),
 elegante=dict(wall='travertine', pa='travertine', base='travertine', slab='travertine', deck='marble', frame='bronze', fin='bronze', overhang=.6, parapet=.4, led=True, recess=.6, palms=3),
 tropical=dict(wall='offwhite', pa='wood', base='stone', slab='concrete', deck='deck', frame='frame', fin='wood', overhang=1.6, parapet=0, led=True, recess=.3, palms=5),
 concreto=dict(wall='concrete', pa='concrete', base='concrete', slab='concrete', deck='deck', frame='frame', fin=None, overhang=1.0, parapet=.3, led=False, recess=.9, palms=2, soffit='wood'),
 nordico=dict(wall='charred', pa='charred', base='concrete_dark', slab='charred', deck='wood_light', frame='wood_light', fin=None, overhang=.5, parapet=.2, led=True, recess=.5, palms=1),
)[style]

h = B('casa')
Z0, Z1, Z2, Z3 = .15, 3.0, 3.35, 6.1
# losas (con borde visible) y techo
h.box(0, 10, 5.0, 14.5, 0, Z0, S['base'])
ov = S['overhang']
h.box(-.05, 10.05, 2.0 - .1, 14.5 + 1.2, Z1, Z2, S['slab'])                    # losa PA + balcón
h.box(-.05 - (ov if style == 'tropical' else 0), 10.05 + (ov if style == 'tropical' else 0), 1.6 - ov * .4, 14.5 + ov, Z3, Z3 + .32, S['slab'])  # techo con alero
if S.get('soffit'): h.box(0, 10, 14.5, 14.5 + ov, Z3 - .02, Z3, S['soffit']); h.box(0, 10, 14.5, 15.7, Z1 - .02, Z1, S['soffit'])
if S['parapet']:
    h.box(-.05, 10.05, 1.6 - ov * .4, 1.8 - ov * .4, Z3 + .32, Z3 + .32 + S['parapet'], S['slab'])
    h.box(-.05, .15, 1.6 - ov * .4, 14.5 + ov, Z3 + .32, Z3 + .32 + S['parapet'], S['slab']); h.box(9.85, 10.05, 1.6 - ov * .4, 14.5 + ov, Z3 + .32, Z3 + .32 + S['parapet'], S['slab'])
    h.box(-.05, 10.05, 14.5 + ov - .2, 14.5 + ov, Z3 + .32, Z3 + .32 + S['parapet'], S['slab'])
# muros laterales (medianeras) y frente
side_m = S['wall'] if not S.get('glass_side') else None
for x0, x1 in ((0, .2), (9.8, 10)):
    if side_m: h.box(x0, x1, 5.0, 14.5, Z0, Z1, side_m)
    h.box(x0, x1, 2.0, 14.5 - S['recess'], Z2, Z3, S['pa'] if S['pa'] != 'glass' else 'slate')
if S.get('glass_side'):
    glazing(h, 'y', .1, 5.0, 14.5, Z0, Z1, 4); h.box(9.8, 10, 5.0, 14.5, Z0, Z1, 'slate')
    for yy in (5.0, 14.5): h.box(-.05, .15, yy - .1, yy + .1, Z0, Z1, 'steel')
h.box(0, 10, 4.9, 5.1, Z0, Z1, S['wall'])
h.box(0, 10, 1.9, 2.1, Z2, Z3, S['pa'] if S['pa'] != 'glass' else 'slate')
# fachada trasera PB: cancelería hacia la terraza y muro de acento según el estilo
ACC = dict(minimalista='white', cristal=None, elegante='travertine', tropical='stone', concreto='concrete', nordico='charred')[style]
if ACC:
    h.box(0, 2.2, 14.4, 14.62, Z0, Z1, ACC)
    glazing(h, 'x', 14.5, 2.2, 9.7, Z0, Z1 - .05, 3, fm=S['frame'])
else:
    glazing(h, 'x', 14.5, .3, 9.7, Z0, Z1 - .05, 4, fm=S['frame'])
# fachada trasera PA (retranqueada según el estilo)
yr = 14.5 - S['recess']
if S['pa'] == 'glass':
    glazing(h, 'x', yr, .2, 9.8, Z2, Z3, 5, fm=S['frame'])
else:
    h.box(.2, 9.8, 2.0, yr - .15, Z3 - .15, Z3, S['pa'])
    glazing(h, 'x', yr, .6, 4.9, Z2 + .02, Z3 - .05, 2, fm=S['frame']); glazing(h, 'x', yr, 5.7, 9.4, Z2 + .02, Z3 - .05, 2, fm=S['frame'])
    h.box(4.9, 5.7, yr - .2, yr, Z2, Z3, S['pa']); h.box(.2, .6, yr - .2, yr, Z2, Z3, S['pa']); h.box(9.4, 9.8, yr - .2, yr, Z2, Z3, S['pa'])
    if S['recess'] > .2:  # marco profundo del volumen superior
        h.box(0, .3, yr, 14.5 + .02, Z2, Z3 + .32, S['pa']); h.box(9.7, 10, yr, 14.5 + .02, Z2, Z3 + .32, S['pa'])
# lamas / celosía
if S['fin'] == 'bronze':
    for k in range(34):
        x = .35 + k * .28
        if 4.9 < x < 5.7: continue
        h.box(x, x + .05, 14.5 + .05, 14.5 + .3, Z2, Z3 + .32, 'bronze')
elif S['fin'] == 'wood':
    for k in range(60):
        x = .1 + k * .165; h.box(x, x + .07, 14.5 + .5, 14.5 + .6, Z2 + .2, Z3 + .32, 'wood')
    h.box(0, 10, 14.5 + .45, 14.5 + .65, Z2 + .1, Z2 + .2, 'frame'); h.box(0, 10, 14.5 + .45, 14.5 + .65, Z3 + .25, Z3 + .32, 'frame')
# barandal de vidrio del balcón
h.box(.1, 9.9, 15.62, 15.66, Z2, Z2 + 1.05, 'glass'); h.box(.1, 9.9, 15.6, 15.68, Z2 + 1.05, Z2 + 1.09, S['frame'])
# LED bajo losas
if S['led']:
    h.box(.2, 9.8, 15.6, 15.66, Z1 - .04, Z1 - .01, 'led'); h.box(.2, 9.8, 14.5 + ov - .08, 14.5 + ov - .02, Z3 - .03, Z3, 'led')
# muros bajos de piedra y jardineras
# interiores con luz cálida
interior(h, [(2.5, 11.5), (7.5, 11.5), (5, 8), (2.5, 8)], Z0, 5.1, 14.4)
interior(h, [(2.5, 11.5), (7.5, 11.5), (5, 7)], Z2, 2.1, yr - .05)
casa = h.build()

# ------------------------------------------------------------------ jardín, terraza y alberca
g = B('jardin')
g.box(-40, 50, -30, 60, -.3, -.02, 'grass')
g.box(0, 10, 14.5, 16.7, 0, .12, S['deck'])
g.box(0, 10, 0, 5.0, 0, .08, 'concrete' if style != 'elegante' else 'marble')
# alberca: borde, vaso y agua
px0, px1, py0, py1 = 3.6, 9.6, 17.0, 19.6
g.box(px0 - .35, px1 + .35, py0 - .35, py0, 0, .14, 'marble' if style in ('elegante', 'cristal') else 'white' if style == 'minimalista' else 'stone')
g.box(px0 - .35, px1 + .35, py1, py1 + .35, 0, .14, 'marble' if style in ('elegante', 'cristal') else 'white' if style == 'minimalista' else 'stone')
g.box(px0 - .35, px0, py0, py1, 0, .14, 'marble' if style in ('elegante', 'cristal') else 'white' if style == 'minimalista' else 'stone')
g.box(px1, px1 + .35, py0, py1, 0, .14, 'marble' if style in ('elegante', 'cristal') else 'white' if style == 'minimalista' else 'stone')
g.box(px0, px1, py0, py1, -1.4, -1.35, 'pooltile')
for (a0, a1, b0, b1) in ((px0, px1, py0, py0 + .05), (px0, px1, py1 - .05, py1), (px0, px0 + .05, py0, py1), (px1 - .05, px1, py0, py1)):
    g.box(a0, a1, b0, b1, -1.4, .02, 'pooltile')
g.box(px0 + .05, px1 - .05, py0 + .05, py1 - .05, -1.3, .04, 'water')
for x in (4.8, 6.6, 8.4): g.box(x - .15, x + .15, py0 + .06, py0 + .09, -.6, -.45, 'poollight')
# muros perimetrales y vegetación
g.box(-.3, 0, 14.5, 20.3, 0, 1.6, 'stone' if style not in ('minimalista', 'cristal') else 'white')
g.box(10, 10.3, 14.5, 20.3, 0, 1.6, 'stone' if style not in ('minimalista', 'cristal') else 'white')
g.box(.3, 3.2, 16.9, 19.9, 0, .2, 'grass')
for x in (.8, 2.0, 3.0): shrub(g, x, 19.6, .55)
for yy in (15.5, 17, 18.5): shrub(g, 9.7, yy, .4)
# camastros
for x in (1.0, 2.1):
    g.box(x, x + .7, 17.3, 19.2, .15, .35, 'wood_light' if style != 'nordico' else 'wood_light'); g.box(x + .02, x + .68, 17.35, 18.9, .35, .45, 'fabric')
g.box(4.2, 7.0, 15.0, 15.8, .12, .5, 'fabric'); g.box(4.2, 7.0, 15.0, 15.2, .5, .85, 'fabric')
for i in range(S['palms']):
    palm(g, [-.9, 11.2, -1.6, 12.2, .8][i], [21, 21.8, 17.5, 18, 19.5][i], [7.8, 8.8, 6.5, 7.2, 5.5][i], [-.8, .9, -.5, .6, -.3][i])
gj = g.build()
# vecinos y fondo
n = B('vecinos')
n.box(-18, -7, 3, 15, 0, 5.4, 'neighbor'); n.box(17, 28, 2, 15, 0, 5.8, 'neighbor')
n.box(-14, 24, 34, 44, 0, 7.5, 'neighbor')
for k in range(18): shrub(n, R.choice([R.uniform(-18, -3), R.uniform(13, 28)]), R.uniform(8, 26), R.uniform(1.5, 3), 'leaf')
for k in range(4): palm(n, R.choice([R.uniform(-14, -4), R.uniform(14, 24)]), R.uniform(6, 22), R.uniform(9, 13), .8)
n.build(smooth=True)

# ------------------------------------------------------------------ cielo al atardecer, sol y cámara
world = bpy.data.worlds.new('cielo'); sc.world = world; world.use_nodes = True
sky = world.node_tree.nodes.new('ShaderNodeTexSky'); sky.sky_type = 'MULTIPLE_SCATTERING'
sky.sun_elevation = math.radians(1.2); sky.sun_rotation = math.radians(262); sky.sun_disc = False; sky.aerosol_density = 1.6
world.node_tree.links.new(sky.outputs[0], world.node_tree.nodes['Background'].inputs[0])
world.node_tree.nodes['Background'].inputs[1].default_value = 0.55
az, el = math.radians(262), math.radians(4)
sd = Vector((math.sin(az) * math.cos(el), math.cos(az) * math.cos(el), math.sin(el)))
sl = bpy.data.lights.new('sol', 'SUN'); sl.energy = 1.6; sl.color = (1, .55, .3); sl.angle = math.radians(2)
so = bpy.data.objects.new('sol', sl); sc.collection.objects.link(so); so.rotation_euler = (-sd).to_track_quat('-Z', 'Y').to_euler()
cam = bpy.data.cameras.new('cam'); co = bpy.data.objects.new('cam', cam); sc.collection.objects.link(co); sc.camera = co
if VIEW == 'jardin':
    co.location = (5.0, 30.5, 3.3); tgt = Vector((5.0, 13.0, 3.5)); cam.lens = 26
else:
    co.location = (14.5, -14, 2.2); tgt = Vector((4.5, 6, 3.6)); cam.lens = 24
co.rotation_euler = (tgt - co.location).to_track_quat('-Z', 'Y').to_euler()
cam.shift_y = .05; cam.clip_end = 2000
sc.render.engine = 'CYCLES'; sc.cycles.device = 'CPU'; sc.cycles.samples = SAMPLES
sc.cycles.use_adaptive_sampling = True; sc.cycles.adaptive_threshold = .015; sc.cycles.use_denoising = True
sc.cycles.max_bounces = 10; sc.cycles.diffuse_bounces = 4; sc.cycles.glossy_bounces = 4; sc.cycles.transmission_bounces = 10
sc.cycles.caustics_reflective = False; sc.cycles.caustics_refractive = False; sc.cycles.blur_glossy = 1.0
sc.render.resolution_x = W; sc.render.resolution_y = int(W * 9 / 16)
sc.view_settings.view_transform = 'AgX'; sc.view_settings.look = 'AgX - Medium High Contrast'; sc.view_settings.exposure = .6
sc.render.filepath = OUT
bpy.ops.render.render(write_still=True)
print('OK', OUT)
