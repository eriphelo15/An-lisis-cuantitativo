# Se ejecuta dentro de build_scene.py (exec) cuando se pide la versión "día de espectáculo".
# Añade: público en las gradas (instancias con Geometry Nodes), velario, corte imperial,
# y los grupos de actores de cada momento del día (ocultos; cada toma enciende los suyos).

def coll(name, hidden=True):
    c = bpy.data.collections.new(name); scene.collection.children.link(c)
    c.hide_render = hidden; c.hide_viewport = hidden
    return c

# ------------------------------------------------------------ materiales extra
def random_cloth(name, colors):
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree; p = nt.nodes['Principled BSDF']; p.inputs['Roughness'].default_value = .95
    oi = nt.nodes.new('ShaderNodeObjectInfo'); ramp = nt.nodes.new('ShaderNodeValToRGB')
    ramp.color_ramp.interpolation = 'CONSTANT'
    els = ramp.color_ramp.elements
    while len(els) < len(colors): els.new(0.5)
    for k, c in enumerate(colors):
        els[k].position = k / len(colors); els[k].color = (*c, 1)
    nt.links.new(oi.outputs['Random'], ramp.inputs['Fac']); nt.links.new(ramp.outputs['Color'], p.inputs['Base Color'])
    return m
MAT['crowd'] = random_cloth('ropa_publico', [(0.82, 0.8, 0.72), (0.74, 0.7, 0.6), (0.55, 0.2, 0.13), (0.22, 0.28, 0.42), (0.62, 0.48, 0.28),
                                             (0.36, 0.4, 0.24), (0.8, 0.76, 0.66), (0.45, 0.12, 0.18), (0.3, 0.26, 0.22), (0.68, 0.58, 0.44)])
MAT['toga'] = random_cloth('toga_blanca', [(0.86, 0.84, 0.78), (0.82, 0.8, 0.74), (0.88, 0.86, 0.8)])
MAT['women'] = random_cloth('ropa_mujeres', [(0.72, 0.4, 0.3), (0.4, 0.5, 0.62), (0.8, 0.72, 0.52), (0.55, 0.3, 0.45), (0.85, 0.82, 0.74), (0.5, 0.58, 0.4)])
MAT['skinR'] = random_cloth('piel_publico', [(0.62, 0.42, 0.3), (0.55, 0.36, 0.25), (0.7, 0.5, 0.37), (0.45, 0.3, 0.2)])
MAT['skinR'].node_tree.nodes['Principled BSDF'].inputs['Subsurface Weight'].default_value = .15
MAT['gold'] = principled('oro', (1.0, 0.78, 0.4), .25, 1.0)
MAT['iron'] = principled('hierro', (0.55, 0.55, 0.56), .35, 1.0)
MAT['red'] = principled('rojo_escudo', (0.5, 0.07, 0.05), .6)
MAT['lion'] = principled('leon', (0.62, 0.45, 0.25), .9, extra=lambda nt, p: noisy(nt, p, (0.5, 0.36, 0.2), (0.7, 0.52, 0.3), 4, .3, 60))
MAT['mane'] = principled('melena', (0.3, 0.17, 0.08), .95, extra=lambda nt, p: noisy(nt, p, (0.2, 0.11, 0.05), (0.42, 0.26, 0.12), 8, .8, 90))
MAT['elephant'] = principled('elefante', (0.36, 0.34, 0.32), .9, extra=lambda nt, p: noisy(nt, p, (0.28, 0.27, 0.26), (0.42, 0.4, 0.37), 3, .6, 50))
MAT['ostrich'] = principled('avestruz', (0.08, 0.07, 0.06), .8)
MAT['ostrichS'] = principled('avestruz_piel', (0.72, 0.52, 0.45), .7)
MAT['bear'] = principled('oso', (0.22, 0.14, 0.08), .95, extra=lambda nt, p: noisy(nt, p, (0.16, 0.1, 0.06), (0.3, 0.2, 0.11), 6, .8, 80))

# ------------------------------------------------------------ público
crowd_lib = bpy.data.collections.new('PublicoLib'); LIB.children.link(crowd_lib)
toga_lib = bpy.data.collections.new('TogaLib'); LIB.children.link(toga_lib)
women_lib = bpy.data.collections.new('MujeresLib'); LIB.children.link(women_lib)
def lib_fig(target, name, pose, garment, mcloth, seed):
    ob = make_figure(name, pose, R.uniform(1.62, 1.8), garment, mcloth, MAT['skinR'], seed=seed, res=0.045)
    LIB.objects.unlink(ob); target.objects.link(ob); ob.location = (0, 0, 0)
    return ob
for k in range(10): lib_fig(crowd_lib, f'pub{k}', 'sit', 'tunic', MAT['crowd'], 100 + k)
for k in range(4): lib_fig(toga_lib, f'sen{k}', 'sit', 'toga', MAT['toga'], 200 + k)
for k in range(5): lib_fig(women_lib, f'muj{k}', 'sit', 'toga', MAT['women'], 300 + k)

def crowd_group(name):
    ng = bpy.data.node_groups.new(name, 'GeometryNodeTree')
    ng.interface.new_socket('Geometry', in_out='INPUT', socket_type='NodeSocketGeometry')
    ng.interface.new_socket('Coleccion', in_out='INPUT', socket_type='NodeSocketCollection')
    ng.interface.new_socket('Geometry', in_out='OUTPUT', socket_type='NodeSocketGeometry')
    N = ng.nodes; L = ng.links
    gi = N.new('NodeGroupInput'); go = N.new('NodeGroupOutput')
    ci = N.new('GeometryNodeCollectionInfo')
    ci.inputs['Separate Children'].default_value = True; ci.inputs['Reset Children'].default_value = True
    iop = N.new('GeometryNodeInstanceOnPoints'); iop.inputs['Pick Instance'].default_value = True
    rv = N.new('FunctionNodeRandomValue'); rv.data_type = 'INT'
    [i for i in rv.inputs if i.name == 'Max' and i.type == 'INT'][0].default_value = 99
    rot = N.new('GeometryNodeInputNamedAttribute'); rot.data_type = 'FLOAT_VECTOR'; rot.inputs['Name'].default_value = 'rot'
    scl = N.new('GeometryNodeInputNamedAttribute'); scl.data_type = 'FLOAT'; scl.inputs['Name'].default_value = 'scl'
    L.new(gi.outputs[0], iop.inputs['Points']); L.new(gi.outputs[1], ci.inputs['Collection'])
    L.new(ci.outputs[0], iop.inputs['Instance'])
    L.new([o for o in rv.outputs if o.type == 'INT'][0], iop.inputs['Instance Index'])
    L.new(rot.outputs['Attribute'], iop.inputs['Rotation']); L.new(scl.outputs['Attribute'], iop.inputs['Scale'])
    L.new(iop.outputs[0], go.inputs[0])
    return ng
CROWD_NG = crowd_group('multitud')

def point_cloud(name, pts, rots, scls, collection, lib):
    me = bpy.data.meshes.new(name); me.from_pydata(pts, [], [])
    a = me.attributes.new('rot', 'FLOAT_VECTOR', 'POINT'); a.data.foreach_set('vector', np.array(rots, np.float32).ravel())
    b = me.attributes.new('scl', 'FLOAT', 'POINT'); b.data.foreach_set('value', np.array(scls, np.float32))
    ob = bpy.data.objects.new(name, me); collection.objects.link(ob)
    md = ob.modifiers.new('multitud', 'NODES'); md.node_group = CROWD_NG
    key = [it.identifier for it in CROWD_NG.interface.items_tree if getattr(it, 'in_out', '') == 'INPUT' and it.socket_type == 'NodeSocketCollection'][0]
    md[key] = lib
    return ob

def facing(px, py):
    return math.atan2(px, -py)  # rota +y hacia el centro de la arena

C_CROWD = coll('Publico', hidden=True)
pts, rots, scls = [], [], []
tpts, trots, tscl = [], [], []
wpts, wrots, wscl = [], [], []
treads = [(prof[j][0], prof[j + 1][0], prof[j][1]) for j in range(len(prof) - 1)
          if abs(prof[j][1] - prof[j + 1][1]) < 1e-6 and abs(prof[j][0] - prof[j + 1][0]) > .4]
for (d0, d1, h) in treads:
    dm = (d0 + d1) / 2 + .15
    podium = h < 4.5
    upper = dm < 20
    per = PER * (A - dm) / A
    n = int(per / (1.1 if podium else 0.62))
    for k in range(n):
        if R.random() > (0.55 if podium else 0.93): continue
        t = t_at(k / n * PER + R.uniform(-.1, .1))
        px, py = pt(t, dm - .3)
        # pasillos de los vomitorios
        bayf = (t % (2 * math.pi)) / (2 * math.pi) * NB
        if not podium and abs((bayf % 2) - 1.0) < .09: continue
        z = h - (0.0 if podium else 0.44)
        th = facing(px, py) + R.uniform(-.25, .25)
        if podium: tpts.append((px, py, h)); trots.append((0, 0, th)); tscl.append(R.uniform(.95, 1.05))
        elif upper: wpts.append((px, py, z)); wrots.append((0, 0, th)); wscl.append(R.uniform(.9, 1.02))
        else: pts.append((px, py, z)); rots.append((0, 0, th)); scls.append(R.uniform(.92, 1.06))
point_cloud('publico', pts, rots, scls, C_CROWD, crowd_lib)
point_cloud('senadores', tpts, trots, tscl, C_CROWD, toga_lib)
point_cloud('mujeres_plebe', wpts, wrots, wscl, C_CROWD, women_lib)
print('publico', len(pts), 'senadores', len(tpts), 'arriba', len(wpts))

# ------------------------------------------------------------ corte imperial en el pulvinar
fig_comm = make_figure('comodo_trono', 'sit', 1.82, 'toga', MAT['purple'], MAT['skin'], seed=11, res=0.03)
court = [make_figure(f'corte{k}', 'sit', 1.72, 'toga', [MAT['marble'], MAT['purple'], CLOTH[4], CLOTH[0]][k % 4], MAT['skin'], seed=20 + k, res=0.035) for k in range(6)]
guard = make_figure('pretoriano', 'stand', 1.82, 'tunic', MAT['red'], MAT['skin'], seed=30, res=0.035)
def at_pulv(x, y, z): return tuple(M_PULV @ Vector((x, y, z)))
place(fig_comm, at_pulv(0, -2.0, 4.3), PULV_ROT, 1.0, C_CROWD)
for k, x in enumerate((-4.6, -3.2, -1.8, 1.8, 3.2, 4.6)):
    place(court[k], at_pulv(x, -1.4 - (k % 2) * .9, 4.3), PULV_ROT + R.uniform(-.2, .2), 1.0, C_CROWD)
for x in (-6.0, 6.0):
    place(guard, at_pulv(x, -.2, 4.3), PULV_ROT, 1.0, C_CROWD)
TRONO = Builder('trono'); TRONO.add(box(-.6, .6, -.9, 0, 0, .5, 'gold') + box(-.6, .6, -1.05, -.9, .5, 1.7, 'gold'), M_PULV @ Matrix.Translation((0, -1.6, 4.3)))
TRONO.build(C_CROWD)

# ------------------------------------------------------------ velario desplegado
C_VEL = coll('Velario', hidden=True)
bv = Builder('velario')
NM = 240; J = 16
Tm = [t_at(k / NM * PER) for k in range(NM + 1)]
def vel_pt(t, f):
    d = -0.8 + (DA + 6) * f
    x, y = pt(t, d)
    return (x, y, 57.0 - 15.5 * f)
for k in range(NM):
    m = 'canvas' if (k // 2) % 2 == 0 else 'canvas2'
    for j in range(J):
        f0, f1 = j / J, (j + 1) / J
        q = []
        for (t, f) in ((Tm[k], f0), (Tm[k + 1], f0), (Tm[k + 1], f1), (Tm[k], f1)):
            x, y, z = vel_pt(t, f)
            q.append((x, y, z))
        # comba del lienzo entre cuerdas
        tm = (Tm[k] + Tm[k + 1]) / 2
        sag = .45 * math.sin(math.pi * (f0 + f1) / 2)
        q = [(x, y, z - (sag if (i in (1, 2) and k % 2 == 0) or (i in (0, 3) and k % 2 == 1) else 0)) for i, (x, y, z) in enumerate(q)]
        bv.face(q, m)
for k in range(0, NM, 1):
    a = vel_pt(Tm[k], 0); b = vel_pt(Tm[k], 1)
    d = Vector(b) - Vector(a)
    bv.add(cyl(0, 0, .05, .05, 0, d.length, 'wood', seg=4), Matrix.Translation(a) @ Vector((0, 0, 1)).rotation_difference(d.normalized()).to_matrix().to_4x4())
# anillo tensor interior
for k in range(NM):
    a, b = Vector(vel_pt(Tm[k], 1)), Vector(vel_pt(Tm[k + 1], 1)); d = b - a
    bv.add(cyl(0, 0, .12, .12, 0, d.length, 'wood', seg=5), Matrix.Translation(a) @ Vector((0, 0, 1)).rotation_difference(d.normalized()).to_matrix().to_4x4())
bv.build(C_VEL)
# marineros de la flota de Miseno en lo alto del ático
sailor = make_figure('marinero', 'raise', 1.75, 'tunic', CLOTH[3], MAT['skin'], seed=41, res=0.04)
for k in range(0, NM, 3):
    x, y = pt(Tm[k], -.2)
    place(sailor, (x, y, 48.5), facing(x, y) + math.pi, 1.0, C_VEL)

# ------------------------------------------------------------ animales (metaballs)
def quadruped(name, L, H, body_m, head_m=None, kind='lion'):
    parts, head = [], []
    s = L
    parts += [('ell', (0, 0, H * .72), (1.7, .75, .75), .26 * s), ('ell', (0, .38 * s, H * .74), (1, .9, .95), .24 * s)]
    for sx in (-1, 1):
        for fy, bend in ((.45, .06), (-.42, -.06)):
            parts += [('cap', (sx * .12 * s, fy * s, H * .7), (sx * .13 * s, fy * s + bend * s, H * .32), .075 * s),
                      ('cap', (sx * .13 * s, fy * s + bend * s, H * .32), (sx * .13 * s, fy * s, .04 * s), .055 * s)]
    parts += [('cap', (0, -.6 * s, H * .75), (0, -1.0 * s, H * .5), .035 * s)]
    if kind == 'lion':
        head += [('ell', (0, .82 * s, H * .92), (1, 1.1, 1), .17 * s), ('ell', (0, .98 * s, H * .86), (.7, 1, .6), .09 * s)]
        mane = [('ell', (0, .7 * s, H * .95), (1.2, .8, 1.25), .3 * s)]
        items = [(_meta_mesh(parts, .04 * s), body_m), (_meta_mesh(head, .03 * s), body_m), (_meta_mesh(mane, .05 * s), MAT['mane'])]
    elif kind == 'bear':
        head += [('ell', (0, .78 * s, H * .88), (1, 1.2, 1), .19 * s), ('ell', (0, .98 * s, H * .83), (.6, 1, .6), .09 * s)]
        items = [(_meta_mesh(parts + head, .045 * s), body_m)]
    return join_meshes(name, items)

def elephant(name):
    s = 1.0; parts = []
    parts += [('ell', (0, 0, 2.0), (1.55, 1.0, 1.0), 1.2), ('ell', (0, 1.55, 2.4), (1, 1, 1.05), .75)]
    for sx in (-1, 1):
        for fy in (.9, -.9):
            parts += [('cap', (sx * .55, fy, 1.7), (sx * .55, fy, .1), .32)]
        parts += [('ell', (sx * .7, 1.35, 2.5), (.25, .9, 1.1), .6)]
    trunk = [(0, 2.1, 2.2), (0, 2.35, 1.5), (0, 2.4, .8), (0, 2.55, .35)]
    for a, b in zip(trunk[:-1], trunk[1:]): parts.append(('cap', a, b, .18))
    tusks = Builder(name + 't')
    for sx in (-1, 1): tusks.add(cyl(sx * .28, 2.1, .08, .03, 1.7, 2.6, 'marble', seg=6), Matrix.Rotation(-0.5, 4, 'X'))
    me = join_meshes(name, [(_meta_mesh(parts, .08), MAT['elephant'])])
    return me

def ostrich(name):
    parts = [('ell', (0, 0, 1.2), (1.3, .9, .8), .42), ('ell', (0, -.35, 1.3), (1, 1, .7), .3)]
    skin = [('cap', (0, .3, 1.35), (0, .45, 2.2), .06), ('ell', (0, .5, 2.25), (1, 1.5, 1), .08)]
    for sx in (-1, 1): skin += [('cap', (sx * .15, 0, 1.0), (sx * .17, .1, .55), .07), ('cap', (sx * .17, .1, .55), (sx * .17, 0, .05), .045)]
    return join_meshes(name, [(_meta_mesh(parts, .04), MAT['ostrich']), (_meta_mesh(skin, .03), MAT['ostrichS'])])

def lib_mesh_obj(me):
    ob = bpy.data.objects.new(me.name, me); LIB.objects.link(ob); return ob
LION = lib_mesh_obj(quadruped('leon', 1.0, 1.15, MAT['lion'], kind='lion'))
BEAR = lib_mesh_obj(quadruped('oso', 1.05, 1.2, MAT['bear'], kind='bear'))
ELEPH = lib_mesh_obj(elephant('elefante'))
OSTR = lib_mesh_obj(ostrich('avestruz'))

# ------------------------------------------------------------ gladiadores y otros actores
def kit(kind):
    """Accesorios en coordenadas de una figura de 1.78 m mirando a +y."""
    f = []
    if kind == 'murmillo':
        f += sphere(0, .01, 1.63, .17, 'bronze', seg=10, rings=6, sz=1.1) + box(-.02, .02, -.18, .2, 1.72, 1.98, 'red')
        f += box(-.33, .33, .42, .5, .45, 1.45, 'red') + sphere(0, .52, .95, .09, 'bronze', seg=6, rings=3)
        f += box(.3, .34, .3, .95, 1.33, 1.37, 'iron')
        f += cyl(-.12, .02, .09, .085, .08, .45, 'bronze', seg=6)
    elif kind == 'thraex':
        f += sphere(0, .01, 1.63, .16, 'bronze', seg=10, rings=6, sz=1.15) + box(-.03, .03, -.12, .16, 1.75, 1.95, 'bronze')
        f += box(-.36, -.02, .38, .44, .85, 1.35, 'bronze')
        f += box(.29, .33, .3, .75, 1.33, 1.37, 'iron') + box(.29, .33, .7, .85, 1.28, 1.34, 'iron')
        for sx in (-1, 1): f += cyl(sx * .2, .13, .09, .085, .08, .75, 'bronze', seg=6)
    elif kind == 'bestiario':
        f += cyl(.3, .4, .025, .025, .6, 2.9, 'wood', seg=4) + box(.27, .33, .37, .43, 2.9, 3.1, 'iron')
    elif kind == 'referee':
        f += cyl(.3, .3, .02, .02, .6, 1.9, 'wood', seg=4)
    elif kind == 'tuba':
        f += cyl(.1, .35, .03, .12, 1.45, 2.8, 'gold', seg=8)
    elif kind == 'hercules':
        f += cyl(.32, .4, .06, .11, 1.0, 2.1, 'wood', seg=6)
        f += sphere(0, -.05, 1.66, .15, 'lion', seg=8, rings=5, sz=1.0) + box(-.3, .3, -.28, -.15, .6, 1.62, 'lion')
    return f
def gladiator(name, kind, pose='fight', cloth=None, seed=0):
    ob = make_figure(name, pose, 1.78, 'loin' if kind in ('murmillo', 'thraex', 'hercules') else 'tunic',
                     cloth or CLOTH[0], MAT['skin'], seed=seed, res=0.03, extra=kit(kind))
    return ob
MURM = gladiator('murmillo', 'murmillo', cloth=CLOTH[0], seed=51)
THRX = gladiator('thraex', 'thraex', cloth=CLOTH[2], seed=52)
BEST = gladiator('bestiario', 'bestiario', 'stand', CLOTH[6], 53)
REF = gladiator('arbitro', 'referee', 'stand', CLOTH[1], 54)
TUBA = gladiator('tubicen', 'tuba', 'raise', CLOTH[7], 55)
HERC = gladiator('comodo_hercules', 'hercules', 'fight', MAT['purple'], 56)
PARADE = [gladiator(f'desfile{k}', ['murmillo', 'thraex', 'murmillo', 'thraex'][k], 'stand', [MAT['purple'], CLOTH[7], MAT['purple'], CLOTH[3]][k], 60 + k) for k in range(4)]

C_POMPA = coll('Pompa'); C_VENATIO = coll('Venatio'); C_GLAD = coll('Gladiadores'); C_HERC = coll('ComodoArena')
C_LLEGADA = coll('Llegada'); C_SALIDA = coll('Salida')
# desfile de apertura desde la Porta Triumphalis (oeste) por el eje mayor
for row in range(14):
    for col in range(-2, 3):
        x = -38 + row * 2.6; y = col * 1.4
        src = TUBA if row < 2 else PARADE[(row + col) % 4] if row < 11 else BEST
        place(src, (x + R.uniform(-.2, .2), y + R.uniform(-.15, .15), 0), -math.pi / 2, 1.0, C_POMPA)
# carro con la estatua de la diosa (pompa)
cart = Builder('carro_pompa'); cart.add(box(-2.2, 2.2, -1.1, 1.1, .6, 1.5, 'gold') + cyl(-1.5, -1.2, .6, .6, 0, .1, 'wood') + cyl(1.5, -1.2, .6, .6, 0, .1, 'wood'), Matrix.Translation((-2, 0, 0)))
ob = cart.build(C_POMPA)
st = place(STATUES[0], (-2, 0, 1.5), -math.pi / 2, .8, C_POMPA)
# cacería: fieras, avestruces, un elefante, bestiarios y escenografía de bosque
for k in range(7):
    place(LION, (R.uniform(-25, 25), R.uniform(-16, 16), 0), R.uniform(0, 2 * math.pi), 1.0, C_VENATIO)
for k in range(3):
    place(BEAR, (R.uniform(-30, 30), R.uniform(-15, 15), 0), R.uniform(0, 2 * math.pi), 1.0, C_VENATIO)
for k in range(14):
    place(OSTR, (R.uniform(-35, 10), R.uniform(-18, 18), 0), R.uniform(0, 2 * math.pi), 1.0, C_VENATIO)
for k in range(12):
    a = R.uniform(0, 2 * math.pi); r = R.uniform(8, 20)
    place(BEST, (r * math.cos(a) * 1.5, r * math.sin(a), 0), a + math.pi, 1.0, C_VENATIO)
silva = Builder('silva')
for k in range(16):
    x, y = R.uniform(-40, 40), R.uniform(-24, 24)
    if (x / 42) ** 2 + (y / 26) ** 2 > 1: continue
    h = R.uniform(4, 8)
    silva.add(cyl(x, y, .18, .12, 0, h, 'wood', seg=5))
    for c in range(6): silva.add(sphere(x + R.uniform(-1.3, 1.3), y + R.uniform(-1.3, 1.3), h + R.uniform(-.8, .9), R.uniform(.8, 1.5), 'leaf', seg=12, rings=7, sz=.85))
for k in range(18):
    x, y = R.uniform(-40, 40), R.uniform(-24, 24)
    if (x / 42) ** 2 + (y / 26) ** 2 < 1: silva.add(sphere(x, y, .3, R.uniform(.8, 1.6), 'granite', seg=6, rings=3, sz=.6))
silva.build(C_VENATIO)
# combates de gladiadores (varias parejas) con árbitros
for k, (x, y, a) in enumerate(((-6, 2, .3), (10, -6, 2.0), (-20, -8, 1.2), (22, 8, -0.8))):
    place(MURM, (x, y, 0), a, 1.0, C_GLAD)
    place(THRX, (x - 1.3 * math.sin(a) * -1 + math.sin(a) * 1.5, y + math.cos(a) * 1.5, 0), a + math.pi, 1.0, C_GLAD)
    place(REF, (x + 2.2 * math.cos(a), y + 2.2 * math.sin(a), 0), a + math.pi / 2, 1.0, C_GLAD)
# Cómodo como Hércules en la arena, con pretorianos y avestruces
place(HERC, (0, -6, 0), math.pi * .1, 1.0, C_HERC)
for k in range(6):
    place(OSTR, (R.uniform(-12, 12), R.uniform(0, 14), 0), R.uniform(0, 2 * math.pi), 1.0, C_HERC)
for x in (-9, -6, 6, 9):
    place(guard, (x, -14, 0), math.pi * .5 if x < 0 else -math.pi * .5, 1.0, C_HERC)

# gente llegando y saliendo por la plaza (figuras de pie)
walk_lib = [make_figure(f'peaton{k}', 'stand', R.uniform(1.6, 1.8), ['tunic', 'toga', 'tunic'][k % 3], CLOTH[k % 9], MAT['skin'], seed=500 + k, res=0.045) for k in range(9)]
def plaza_people(collection, n, inward):
    for k in range(n):
        t = R.uniform(0, 2 * math.pi); d = R.uniform(-45, -3)
        x, y = pt(t, d)
        base = facing(x, y) + (0 if inward else math.pi)
        place(walk_lib[k % 9], (x, y, 0), base + R.uniform(-.5, .5), R.uniform(.95, 1.05), collection)
plaza_people(C_LLEGADA, 2600, True)
plaza_people(C_SALIDA, 3200, False)
print('dia de espectaculo listo')
