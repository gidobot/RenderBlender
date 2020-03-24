# A simple script that uses blender to render views of a single object by rotation the camera around it.
# Also produces depth map at the same time.
#
# Example:
# blender --background --python mytest.py -- --views 10 /path/to/my.obj
#

import argparse, sys, os
import scipy.io
import bpy
import numpy as np
from mathutils import *
from math import *

def fish2polar(x, y, f):
    # project to sphere to get cartesian coordinates
    R = np.sqrt(x**2+y**2)
    theta = R/f
    z = R/np.tan(theta)
    r = np.sqrt(x**2+y**2+z**2)
    # get polar angles from cartesian coordinates
    phi = np.arctan2(x,z)
    theta = np.arcsin(y/r)
    return theta, phi

def polar2cartesian(theta, phi, r=1.):
    ct = np.cos(theta)
    x = r*ct*np.sin(phi)
    z = r*ct*np.cos(phi)
    y = r*np.sin(theta)
    return x, y, z

parser = argparse.ArgumentParser(description='Renders given obj file by rotation a camera around it.')
parser.add_argument('--views', type=int, default=100000,
                    help='number of views to be rendered at each elevation angle (+/- elevation)')
parser.add_argument('obj', type=str,
                    help='Path to the obj file to be rendered.')
parser.add_argument('--output_folder', type=str, default='/tmp',
                    help='The path the output will be dumped to.')
parser.add_argument('--remove_doubles', type=bool, default=True,
                    help='Remove double vertices to improve mesh quality.')
parser.add_argument('--edge_split', type=bool, default=True,
                    help='Adds edge split filter.')
parser.add_argument('--color_depth', type=str, default='8',
                    help='Number of bit per channel used for output. Either 8 or 16.')
parser.add_argument('--format', type=str, default='PNG',
                    help='Format of files generated. Either PNG or OPEN_EXR')

argv = sys.argv[sys.argv.index("--") + 1:]
args = parser.parse_args(argv)

num_lights = 3
lights = []
light_objs = []

# Set up rendering
scene = bpy.context.scene
scene.render.engine = 'CYCLES'
scene.cycles.device = 'GPU'
prefs = bpy.context.preferences
cprefs = prefs.addons['cycles'].preferences
# Attempt to set GPU device types if available
for compute_device_type in ('CUDA', 'OPENCL', 'NONE'):
    try:
        cprefs.compute_device_type = compute_device_type
        break
    except TypeError:
        pass
# Enable all CPU and GPU devices
for device in cprefs.devices:
    device.use = True

scene.use_nodes = True
tree = scene.node_tree
links = tree.links

# Add passes for additionally dumping albedo and normals.
# bpy.context.scene.render.layers["RenderLayer"].use_pass_normal = True
# bpy.context.scene.render.layers["RenderLayer"].use_pass_color = True
scene.render.image_settings.file_format = args.format
scene.render.image_settings.color_depth = args.color_depth

bpy.data.worlds["World"].node_tree.nodes['Background'].inputs['Color'].default_value = [0,0,0,1]

# Set rendering parameters
# bpy.context.scene.world.light_settings.use_environment_light = True
# bpy.context.scene.world.light_settings.environment_energy = 0.75
#bpy.context.object.active_material.use_shadeless = True
# bpy.context.scene.render.use_raytrace = True
# bpy.context.scene.render.use_shadows = True

# # Clear default nodes
# for n in tree.nodes:
#     tree.nodes.remove(n)

# # Create input render layer node.
# render_layers = tree.nodes.new('CompositorNodeRLayers')
# render_layers = tree.nodes['Composite']

# Delete default cube
if bpy.data.objects.get("Cube") is not None:
    bpy.data.objects['Cube'].select_set(True)
    # bpy.context.view_layer.objects.active = bpy.context.view_layer.objects['Cube']
bpy.ops.object.delete()
if bpy.data.objects.get("Light") is not None:
    bpy.data.objects['Light'].select_set(True)
    # bpy.context.view_layer.objects.active = bpy.context.view_layer.objects['Light']
bpy.ops.object.delete()

# Transform model for rendering
# bpy.ops.import_scene.obj(filepath=args.obj)
# bpy.ops.import_scene.fbx(filepath=args.obj)
bpy.ops.import_scene.gltf(filepath=args.obj)
render_object = None
for object in bpy.context.view_layer.objects:
    if object.name in ['Camera']:
        continue
    bpy.context.view_layer.objects.active = object
    if args.remove_doubles:
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.remove_doubles()
        bpy.ops.object.mode_set(mode='OBJECT')
    if args.edge_split:
        bpy.ops.object.modifier_add(type='EDGE_SPLIT')
        bpy.context.object.modifiers["EdgeSplit"].split_angle = 1.32645
        bpy.ops.object.modifier_apply(apply_as='DATA', modifier="EdgeSplit")
    render_object = object
    object.data.use_auto_smooth = False
    bpy.ops.object.shade_smooth()

## Set up environment lighting
# Make empty object at origin for lights to track
o_lamp = bpy.data.objects.new("Empty", None)
o_lamp.location = (0,0,0)

for i in range(num_lights):
    light_name = 'Sun'
    if i > 0:
        light_name += '.00{}'.format(i)
    # Make light just directional, disable shadows.
    bpy.ops.object.light_add(type='SUN')
    lights.append(bpy.data.lights[light_name])
    lights[i].energy = 1.0
    # Possibly disable specular shading:
    # lamp.use_specular = False
    # Make light track origin
    light_objs.append(bpy.data.objects[light_name])
    light_objs[i].location = (3,3,2)
    light_constraint = light_objs[i].constraints.new(type='TRACK_TO')
    light_constraint.track_axis = 'TRACK_NEGATIVE_Z'
    light_constraint.up_axis = 'UP_Y'
    light_constraint.target = o_lamp

# # Make light just directional, disable shadows.
# bpy.ops.object.light_add(type='SUN')
# lamp = bpy.data.lights['Sun']
# lamp.energy = 1.0
# # Possibly disable specular shading:
# # lamp.use_specular = False
# # Make light track origin
# lamp_obj = bpy.data.objects['Sun']
# lamp_obj.location = (3,3,2)
# lamp_constraint = lamp_obj.constraints.new(type='TRACK_TO')
# lamp_constraint.track_axis = 'TRACK_NEGATIVE_Z'
# lamp_constraint.up_axis = 'UP_Y'
# lamp_constraint.target = o_lamp

# # Add another light source so stuff facing away from light is not completely dark
# bpy.ops.object.light_add(type='SUN')
# lamp2 = bpy.data.lights['Sun.001']
# # lamp2.shadow_method = 'NOSHADOW'
# lamp2.energy = 1.0
# # lamp2.use_specular = False
# # Make light point at object
# lamp2_obj = bpy.data.objects['Sun.001']
# lamp2_obj.location = (-3,-3,2)
# lamp2_constraint = lamp2_obj.constraints.new(type='TRACK_TO')
# lamp2_constraint.track_axis = 'TRACK_NEGATIVE_Z'
# lamp2_constraint.up_axis = 'UP_Y'
# lamp2_constraint.target = o_lamp

def parent_obj_to_camera(camobj):
    origin = (0, 0, 0)
    b_empty = bpy.data.objects.new("Empty", None)
    b_empty.location = origin
    camobj.parent = b_empty  # setup parenting
    scn = bpy.context.scene
    scn.collection.objects.link(b_empty)
    bpy.context.view_layer.objects.active = b_empty
    return b_empty

render_resolution = 2448.
scene.render.resolution_x = render_resolution
scene.render.resolution_y = render_resolution
scene.render.resolution_percentage = 100.
scene.render.film_transparent = True
cam = bpy.data.cameras['Camera']
camobj = bpy.data.objects['Camera']
cam.type = 'PANO'
cam.cycles.panorama_type = 'FISHEYE_EQUIDISTANT'
cam.cycles.fisheye_fov = 3.2288591861724854
cam.sensor_fit = 'HORIZONTAL'
cam.sensor_width = 8.4455
cam.sensor_height = 8.4455
# cam.angle = 0.927295218

camobj.location = (0, 0, 1)
cam_constraint = camobj.constraints.new(type='TRACK_TO')
cam_constraint.track_axis = 'TRACK_NEGATIVE_Z'
cam_constraint.up_axis = 'UP_Y'
b_empty = parent_obj_to_camera(camobj)
cam_constraint.target = b_empty

model_identifier = os.path.split(os.path.split(args.obj)[0])[1]
if not os.path.exists(os.path.join(args.output_folder, model_identifier)):
    os.makedirs(os.path.join(args.output_folder, model_identifier))
fp = os.path.join(args.output_folder, model_identifier)
scene.render.image_settings.file_format = 'PNG'  # set output format to .png

b_empty.rotation_mode = 'XYZ'
render_object.rotation_mode = 'QUATERNION'

## Get width, height and the camera
scn = bpy.data.scenes['Scene']
w = scn.render.resolution_x*scn.render.resolution_percentage/100.
h = scn.render.resolution_y*scn.render.resolution_percentage/100.

# Lens model is equidistant fisheye: R = f*theta
f = scene.render.resolution_x / cam.cycles.fisheye_fov

## Get camera intrinsic
K = Matrix().to_3x3()
K[0][0] = f
K[1][1] = f
K[0][2] = w / 2.
K[1][2] = h / 2.
K[2][2] = 1.

R_adj = Matrix().to_4x4()
R_adj[0][0] = 1.
R_adj[1][1] = -1.
R_adj[2][2] = -1.
R_adj[3][3] = 1.

min_dist = 0.1
max_dist = 1.5

sensor_pix_x = 2448
sensor_pix_y = 2048

# crop render to camera sensor
x_frac = sensor_pix_x / render_resolution
x_offset = (1.-x_frac) * render_resolution / 2
x_min = x_offset
x_max = render_resolution - x_offset

y_frac = sensor_pix_y / render_resolution
y_offset = (1.-y_frac) * render_resolution / 2
y_min = y_offset
y_max = render_resolution - y_offset

bpy.data.scenes["Scene"].render.use_border = True
bpy.data.scenes["Scene"].render.use_crop_to_border = True
bpy.data.scenes["Scene"].render.border_min_x = x_min / render_resolution
bpy.data.scenes["Scene"].render.border_min_y = y_min / render_resolution
bpy.data.scenes["Scene"].render.border_max_x = x_max / render_resolution
bpy.data.scenes["Scene"].render.border_max_y = y_max / render_resolution

camobj.location = (0., 0., .0001)
b_empty.rotation_euler = (3.14159,0,0)

# for i in range(0, args.views):
if 0:
    print("Image {}".format(i))

    # Random light configuration
    for l in range(num_lights):
        light_objs[l].location = np.random.uniform(low=-1, high=max_dist+1, size=3)
        lights[l].energy = np.random.uniform(low=1., high=4.)

    # lamp2_obj.location = np.random.uniform(low=-1, high=max_dist+1, size=3)
    # lamp2.energy = np.random.uniform(low=.5, high=2.)

    # Random camera position
    r = np.random.uniform(low=min_dist, high=max_dist)
    px = np.random.uniform(low=-sensor_pix_x/2, high=sensor_pix_x/2)
    py = np.random.uniform(low=-sensor_pix_y/2, high=sensor_pix_y/2)
    theta, phi = fish2polar(px, py, f)
    x, y, z = polar2cartesian(theta, phi, r)
    z = max(0.1, z)

    q = np.random.uniform(low=-1., high=1., size=4)
    q = q / np.linalg.norm(q)

    render_object.rotation_quaternion = q
    render_object.location = (x, y, z)
    o_lamp.location = render_object.location

    bpy.context.view_layer.update()

    # r = r / np.linalg.norm(r)
    # camobj.location = (0, 0, d)
    # b_empty.rotation_quaternion = r

    # Get object pose in proper camera system
    RC = camobj.matrix_world.inverted()
    RO = render_object.matrix_world
    RT = RC@RO
    RT = R_adj@RT
    pos = RT.translation
    quat = RT.to_quaternion()

    # Get camera pose in world
    # RT_inv = camobj.matrix_world
    # pos = RT_inv.translation
    # quat = RT_inv.to_quaternion()

    # Set filepaths for saving
    scene.render.filepath = fp + '/{}'.format(i)

    # Write camera matrix
    mat = {}
    mat['extrinsic'] = np.array(RT)
    mat['K'] = np.array(K)
    mat['pos'] = np.array(pos)
    mat['quat'] = np.array(quat)
    camera_file_path = scene.render.filepath + ".mat"
    scipy.io.savemat(camera_file_path, mat)

    # Render frame
    bpy.ops.render.render(write_still=True)  # render still
