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
                     sun_col=(1.0, 0.58, 0.34), sun_str=6.5, aerosol=3.0, haze=(0.86, 0.66, 0.54), haze_amt=0.5,
                     mist=(280, 2600), exposure=-0.2, world=0.45),
}
S = SHOTS[shot]

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
mr.inputs['From Min'].default_value, mr.inputs['From Max'].default_value = S['mist']
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
bpy.ops.render.render(write_still=True)

from PIL import Image
img = np.asarray(Image.open(beauty).convert('RGB')).astype(np.float32) / 255
msk = np.asarray(Image.open(mask_path).convert('L')).astype(np.float32) / 255
f = np.clip(msk / 0.97, 0, 1) ** 1.3 * S['haze_amt']
haze = np.array(S['haze'], np.float32)
# el cielo no se toca; la bruma solo aclara la ciudad y las colinas lejanas
sky_px = msk > 0.995
f[sky_px] = 0
res = img * (1 - f[..., None]) + haze * f[..., None]
Image.fromarray((np.clip(res, 0, 1) * 255 + .5).astype(np.uint8)).save(out)
os.remove(mask_path)
print('OK', out)
