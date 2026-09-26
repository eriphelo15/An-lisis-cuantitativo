"""Renderiza una toma de la escena con Cycles y le aplica bruma atmosférica por distancia.

Uso: python3 render_shot.py <escena.blend> <toma> <salida.png> <ancho> <muestras>
"""
import bpy, math, sys, os
import numpy as np
from mathutils import Vector

blend, shot, out, width, samples = sys.argv[-5:]
width, samples = int(width), int(samples)
bpy.ops.wm.open_mainfile(filepath=blend)
sc = bpy.context.scene

SHOTS = {
    # amanecer sobre Roma desde el Esquilino
    'amanecer': dict(cam=(150, 190, 70), look=(-40, -30, 12), lens=30, sun_az=100, sun_el=5.5,
                     sun_col=(1.0, 0.58, 0.34), sun_str=6.5, aerosol=2.2, haze=(0.84, 0.68, 0.58), haze_amt=0.7,
                     haze_k=7000, exposure=-0.2, world=0.45),
    'llegada': dict(cam=(-20, -112, 2.4), look=(-4, -70, 18), lens=28, sun_az=112, sun_el=18, sun_col=(1.0, 0.8, 0.62), sun_str=6.0,
                    aerosol=1.6, haze=(0.8, 0.76, 0.72), haze_amt=0.6, haze_k=6000, exposure=-0.35, world=0.6, show=['Publico', 'Llegada']),
    'velario': dict(cam=(70, -104, 66), look=(-25, 18, 44), lens=26, sun_az=135, sun_el=32, sun_col=(1.0, 0.9, 0.78), sun_str=6.5,
                    aerosol=0.7, haze=(0.78, 0.8, 0.84), haze_amt=0.6, haze_k=7000, exposure=-1.35, world=0.6, show=['Publico', 'Velario']),
    'gradas': dict(cam=(12, 47, 23.5), look=(0, -26, 7), lens=24, sun_az=160, sun_el=42, sun_col=(1.0, 0.92, 0.82), sun_str=6.5,
                   aerosol=0.7, haze=(0.8, 0.8, 0.82), haze_amt=0.5, haze_k=8000, exposure=-1.35, world=0.6, show=['Publico', 'Velario']),
    'pompa': dict(cam=(-26, 22, 5.2), look=(-18, 0, 1.4), lens=30, sun_az=170, sun_el=45, sun_col=(1.0, 0.93, 0.84), sun_str=6.5,
                  aerosol=0.7, haze=(0.8, 0.8, 0.82), haze_amt=0.4, haze_k=8000, exposure=-1.35, world=0.6, show=['Publico', 'Velario', 'Pompa']),
    'venatio': dict(cam=(30, -17, 6.5), look=(4, 3, 1.2), lens=30, sun_az=175, sun_el=52, sun_col=(1.0, 0.94, 0.86), sun_str=6.5,
                    aerosol=0.7, haze=(0.8, 0.8, 0.82), haze_amt=0.4, haze_k=8000, exposure=-1.35, world=0.6, show=['Publico', 'Velario', 'Venatio']),
    'mediodia': dict(cam=(175, -170, 150), look=(0, 0, 18), lens=30, sun_az=185, sun_el=62, sun_col=(1.0, 0.96, 0.9), sun_str=7.0,
                     aerosol=0.7, haze=(0.76, 0.8, 0.86), haze_amt=0.65, haze_k=6500, exposure=-1.35, world=0.6, show=['Publico', 'Velario', 'Venatio']),
    'gladiadores': dict(cam=(4, -13, 3.2), look=(-6, 1.5, 1.3), lens=32, sun_az=225, sun_el=38, sun_col=(1.0, 0.88, 0.72), sun_str=6.5,
                        aerosol=0.7, haze=(0.8, 0.78, 0.76), haze_amt=0.4, haze_k=8000, exposure=-1.35, world=0.6, show=['Publico', 'Velario', 'Gladiadores']),
    'comodo': dict(cam=(5, 9, 2.6), look=(-.5, -8, 2.2), lens=32, sun_az=245, sun_el=28, sun_col=(1.0, 0.82, 0.62), sun_str=6.5,
                   aerosol=1.6, haze=(0.82, 0.76, 0.7), haze_amt=0.4, haze_k=8000, exposure=-0.45, world=0.6, show=['Publico', 'Velario', 'ComodoArena']),
    'atardecer': dict(cam=(-226, -64, 42), look=(-40, 6, 20), lens=32, sun_az=288, sun_el=3.2, sun_col=(1.0, 0.5, 0.26), sun_str=7.0,
                      aerosol=2.6, haze=(0.86, 0.6, 0.45), haze_amt=0.75, haze_k=6000, exposure=-0.1, world=0.5, show=['Publico', 'Salida']),
}
S = SHOTS[shot]
lc = bpy.context.scene.view_layers[0].layer_collection
for ch in lc.children:
    if ch.name in ('Publico', 'Velario', 'Pompa', 'Venatio', 'Gladiadores', 'ComodoArena', 'Llegada', 'Salida'):
        on = ch.name in S.get('show', [])
        ch.exclude = not on; ch.collection.hide_render = not on; ch.collection.hide_viewport = not on

cam = sc.camera
cam.location = S['cam']
d = Vector(S['look']) - Vector(S['cam'])
cam.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
cam.data.lens = S['lens']; cam.data.clip_end = 40000

az, el = math.radians(S['sun_az']), math.radians(S['sun_el'])
sky = sc.world.node_tree.nodes['Sky']
sky.sun_elevation = el; sky.sun_rotation = az; sky.sun_disc = False
sc.world.node_tree.nodes['Background'].inputs[1].default_value = S.get('world', 1.0)
sky.air_density = 1.0; sky.aerosol_density = S['aerosol']; sky.ozone_density = 1.0
sun = bpy.data.objects['sol']
sdir = Vector((math.sin(az) * math.cos(el), math.cos(az) * math.cos(el), math.sin(el)))
sun.rotation_euler = (-sdir).to_track_quat('-Z', 'Y').to_euler()
sun.data.energy = S['sun_str']; sun.data.color = S['sun_col']

sc.render.resolution_x = width; sc.render.resolution_y = int(width * 9 / 16)
sc.cycles.samples = samples
sc.view_settings.exposure = S['exposure']
sc.render.image_settings.file_format = 'PNG'
beauty = out.replace('.png', '_raw.png')
sc.render.filepath = beauty
bpy.ops.render.render(write_still=True)

# pasada de profundidad para la bruma (material de emisión según distancia a la cámara)
mm = bpy.data.materials.new('mascara_bruma'); mm.use_nodes = True
nt = mm.node_tree; nt.nodes.clear()
cd = nt.nodes.new('ShaderNodeCameraData'); mr = nt.nodes.new('ShaderNodeMapRange')
mr.inputs['From Min'].default_value, mr.inputs['From Max'].default_value = 0.0, 60000.0
em = nt.nodes.new('ShaderNodeEmission'); ou = nt.nodes.new('ShaderNodeOutputMaterial')
mr.inputs['To Max'].default_value = 0.97
nt.links.new(cd.outputs['View Distance'], mr.inputs['Value']); nt.links.new(mr.outputs['Result'], em.inputs['Color'])
nt.links.new(em.outputs[0], ou.inputs[0])
vl = sc.view_layers[0]; vl.material_override = mm
bg = sc.world.node_tree.nodes['Background']; link = bg.inputs[0].links[0]; sc.world.node_tree.links.remove(link)
bg.inputs[0].default_value = (1, 1, 1, 1)  # el cielo cuenta como lejano
sc.cycles.samples = 8; sc.cycles.use_denoising = False
sc.view_settings.view_transform = 'Standard'; sc.view_settings.look = 'None'; sc.view_settings.exposure = 0
mask_path = out.replace('.png', '_mask.png'); sc.render.filepath = mask_path
sc.render.image_settings.color_mode = 'BW'; sc.render.image_settings.color_depth = '16'
bpy.ops.render.render(write_still=True)

from PIL import Image
img = np.asarray(Image.open(beauty).convert('RGB')).astype(np.float32) / 255
msk = np.asarray(Image.open(mask_path)).astype(np.float32) / 65535
if msk.ndim == 3: msk = msk[..., 0]
dist = np.clip(msk / 0.97, 0, 1) * 60000
f = (1 - np.exp(-np.maximum(dist - 150, 0) / S['haze_k'])) * S['haze_amt']
haze = np.array(S['haze'], np.float32)
# el cielo no se toca; la bruma solo aclara la ciudad y las colinas lejanas
sky_px = msk > 0.995
f[sky_px] = 0
res = img * (1 - f[..., None]) + haze * f[..., None]
Image.fromarray((np.clip(res, 0, 1) * 255 + .5).astype(np.uint8)).save(out)
os.remove(mask_path)
print('OK', out)
