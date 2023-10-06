# Script to render underwater fisheye simulation data of objects using the underwater_fisheye_env.blend environment.
#
# Example:
# blender --background underwater_fisheye_env.blend --python render_blender_underwater_fisheye.py -- --output_folder /tmp --views 10 /path/to/my.glb
#

import argparse, sys, os
import scipy.io
import bpy
import glob
import numpy as np
from os import path as osp
from mathutils import *
from math import *
import random


BASE_DIR = os.path.dirname(bpy.data.filepath)
COCO_PATH = os.path.join(BASE_DIR, 'COCO')
assert osp.exists(COCO_PATH), \
    'COCO path does not exist: {}'.format(COCO_PATH)
COCO_FILE_LIST = os.listdir(COCO_PATH)


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
parser.add_argument('--views', type=int, default=5,
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
parser.add_argument('--lights', type=int, default=3,
                    help='number of spotlights to randomly place in scene')

argv = sys.argv[sys.argv.index("--") + 1:]
args = parser.parse_args(argv)

num_lights = args.lights
lights_data = []
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
cprefs.get_devices()
for device in cprefs.devices:
    device.use = True

tree = scene.node_tree

scene.render.image_settings.file_format = args.format
scene.render.image_settings.color_depth = args.color_depth

bpy.data.worlds["World"].node_tree.nodes['Background'].inputs['Color'].default_value = [0,0,0,1]

# Transform model for rendering
bpy.ops.import_scene.gltf(filepath=args.obj)
render_object = None
for object in bpy.context.view_layer.objects:
    if object.name in ['Camera', 'ObjectParent', 'ObjectTracker', 'Seafloor', 'Water', 'CameraTracker', 'SeafloorParent', 'SeafloorTracker']:
        continue
    bpy.context.view_layer.objects.active = object
    if args.remove_doubles:
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.remove_doubles()
        bpy.ops.object.mode_set(mode='OBJECT')
    if args.edge_split:
        bpy.ops.object.modifier_add(type='EDGE_SPLIT')
        bpy.context.object.modifiers["EdgeSplit"].split_angle = 1.32645
        # bpy.ops.object.modifier_apply(apply_as='DATA', modifier="EdgeSplit")
        bpy.ops.object.modifier_apply(modifier="EdgeSplit")
    render_object = object
    object.data.use_auto_smooth = False
    bpy.ops.object.shade_smooth()

## Set up environment lighting
for i in range(num_lights):
    light_name = 'Spot'+'{}'.format(i)
    # create light datablock, set attributes
    lights.append(bpy.data.lights.new(name=light_name, type='SPOT'))
    lights[i].energy = 1600
    lights[i].shadow_soft_size = 0.1
    lights[i].spot_size = 90.*np.pi/180.
    lights[i].spot_blend = 1
    # create new object with our light datablock
    light_objs.append(bpy.data.objects.new(name=light_name, object_data=lights[i]))
    # link light object
    bpy.context.collection.objects.link(light_objs[i])
    # Make light track object
    light_objs[i].location = (0,0,-2)
    light_constraint = light_objs[i].constraints.new(type='TRACK_TO')
    light_constraint.track_axis = 'TRACK_NEGATIVE_Z'
    light_constraint.up_axis = 'UP_Y'
    light_constraint.target = render_object

# Camera parameters match real camera except no distortion
render_resolution = 2448
scene.render.resolution_x = render_resolution
scene.render.resolution_y = render_resolution
scene.render.resolution_percentage = 100
scene.render.film_transparent = True
cam = bpy.data.cameras['Camera']
camobj = bpy.data.objects['Camera']
cam.type = 'PANO'
cam.cycles.panorama_type = 'FISHEYE_EQUIDISTANT'
# cam.cycles.fisheye_fov = 3.2288591861724854 # 185 deg
cam.cycles.fisheye_fov = 3.160749 # 181.1 deg

cam.sensor_fit = 'HORIZONTAL'
cam.sensor_width = 8.4455
cam.sensor_height = 8.4455
cam.shift_x = (1224. - 1267.71)/2448.
cam.shift_y = (1024. - 1022.30)/2448.

# Image save path
model_identifier = os.path.split(os.path.split(args.obj)[0])[1]
if not os.path.exists(os.path.join(args.output_folder, model_identifier)):
    os.makedirs(os.path.join(args.output_folder, model_identifier))
fp = os.path.join(args.output_folder, model_identifier)
scene.render.image_settings.file_format = 'PNG'  # set output format to .png

render_object.rotation_mode = 'XYZ'
# render_object.rotation_mode = 'QUATERNION'

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

min_dist = 0.2
max_dist = 1.2

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

object_parent = bpy.data.objects['ObjectParent']
object_tracker = bpy.data.objects['ObjectTracker']
render_object.rotation_euler = [0,0,0]
render_object.parent = object_parent

seafloor_tracker = bpy.data.objects['SeafloorTracker']

# find start index for continuing data generation
index_list = [int(os.path.splitext(os.path.split(x)[1])[0]) for x in glob.glob(fp+'/*.png')]
if index_list == []:
    min_idx = 0
else:
    min_idx = max(index_list) + 1

for i in range(min_idx, args.views):
# if 1:
    try:
        print("Image {}".format(i))

        # Random light configuration
        for l in range(num_lights):
            light_objs[l].location = np.concatenate([np.random.uniform(low=-2, high=2, size=2), np.random.uniform(low=-2, high=0, size=1)])
            lights[l].energy = np.random.uniform(low=100., high=1600.)

        # Random object position
        r = np.random.uniform(low=min_dist, high=max_dist)
        px = np.random.uniform(low=-sensor_pix_x/2, high=sensor_pix_x/2)
        py = np.random.uniform(low=-sensor_pix_y/2, high=sensor_pix_y/2)
        theta, phi = fish2polar(px, py, f)
        x, y, z = polar2cartesian(theta, phi, r)
        z = max(0.1, z)

        # q = np.random.uniform(low=-1., high=1., size=4)
        # q = q / np.linalg.norm(q)

        # render_object.rotation_quaternion = q
        # render_object.location = (x, y, z)

        # use parent and tracker constraints to define limited object orientation on hemisphere
        object_parent.location = (x, y, z)
        phi = np.random.uniform(low=0., high=2.*np.pi)
        theta = np.random.uniform(low=np.pi/2., high=np.pi)
        object_tracker.location = (np.sin(theta)*np.cos(phi)-x, np.sin(theta)*np.sin(phi)-y, cos(theta)-z)
        render_object.rotation_euler[1] = np.random.uniform(low=0., high=2.*np.pi)

        bpy.context.view_layer.update()

        # Get object pose in proper camera system
        RC = camobj.matrix_world.inverted()
        RO = render_object.matrix_world
        RT = RC@RO
        RT = R_adj@RT
        pos = RT.translation
        quat = RT.to_quaternion()

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

        # Randomly sample seafloor background and planar tilt
        bpy.data.images['seafloor'].filepath = osp.join(COCO_PATH,random.choice(COCO_FILE_LIST))
        [w,h] = bpy.data.images['seafloor'].size[:]
        aspect = w/h
        min_dim = 8.
        if aspect >=1:
            plane_w = aspect*min_dim
            plane_h = min_dim
        else:
            plane_w = min_dim
            plane_h = min_dim/aspect

        bpy.data.objects['Seafloor'].dimensions = [plane_w, plane_h, 0.]
        seafloor_tracker.location = np.random.uniform(low=-1., high=1., size=3)

        # Randomize water properties
        bpy.data.materials['Water'].node_tree.nodes["Value"].outputs[0].default_value = np.random.uniform(low=0.2, high=0.4)
        bpy.data.materials['Water'].node_tree.nodes["Volume Scatter"].inputs[2].default_value = np.random.uniform(low=0.4, high=0.9)

        # Render frame
        # blur_size = np.random.randint(low=2, high=8)
        blur_size = 0
        tree.nodes['Blur'].size_x = blur_size
        tree.nodes['Blur'].size_y = blur_size
        bpy.ops.render.render(write_still=True)  # render still
    except Exception as e:
        print(str(e))
        i -= 1
        continue
