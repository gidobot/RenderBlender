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

parser = argparse.ArgumentParser(description='Renders given obj file with random orientation, centered perspective image.')
parser.add_argument('--views', type=int, default=10,
                    help='number of views to be rendered')
parser.add_argument('--persp_dim', type=int, default=400,
                    help='perspective focal length in pixels')
parser.add_argument('--flength', type=float, default=350,
                    help='dimension of square perspective image')
parser.add_argument('obj', type=str,
                    help='Path to the obj file to be rendered.')
parser.add_argument('--output_folder', type=str, default='/tmp/render_blender',
                    help='The path the output will be dumped to.')
parser.add_argument('--remove_doubles', type=bool, default=True,
                    help='Remove double vertices to improve mesh quality.')
parser.add_argument('--edge_split', type=bool, default=True,
                    help='Adds edge split filter.')
parser.add_argument('--color_depth', type=str, default='8',
                    help='Number of bit per channel used for output. Either 8 or 16.')
parser.add_argument('--depth_scale', type=float, default=10,
                    help='Scaling that is applied to depth. Depends on size of mesh. Try out various values until you get a good result. Ignored if format is OPEN_EXR.')
parser.add_argument('--format', type=str, default='PNG',
                    help='Format of files generated. Either PNG or OPEN_EXR')

argv = sys.argv[sys.argv.index("--") + 1:]
args = parser.parse_args(argv)

object_offset = [0, .076731, 0]

# Set up rendering of depth map.
bpy.context.scene.use_nodes = True
tree = bpy.context.scene.node_tree
links = tree.links

# Add passes for additionally dumping albedo and normals.
bpy.context.scene.render.layers["RenderLayer"].use_pass_normal = True # for Blender version < 2.8
bpy.context.scene.render.layers["RenderLayer"].use_pass_color = True  # for Blender version < 2.8
# bpy.context.view_layer.use_pass_normal = True # for Blender version >= 2.8
# bpy.context.view_layer.use_pass_diffuse_color = True  # for Blender version >= 2.8
bpy.context.scene.render.image_settings.file_format = args.format
bpy.context.scene.render.image_settings.color_depth = args.color_depth

# Set rendering parameters
bpy.context.scene.world.light_settings.use_environment_light = True
bpy.context.scene.world.light_settings.environment_energy = 0.75
#bpy.context.object.active_material.use_shadeless = True
bpy.context.scene.render.use_raytrace = True
bpy.context.scene.render.use_shadows = True

# Clear default nodes
for n in tree.nodes:
    tree.nodes.remove(n)

# Create input render layer node.
render_layers = tree.nodes.new('CompositorNodeRLayers')

depth_file_output = tree.nodes.new(type="CompositorNodeOutputFile")
depth_file_output.label = 'Depth Output'
if args.format == 'OPEN_EXR':
  links.new(render_layers.outputs['Depth'], depth_file_output.inputs[0])
else:
  # Remap as other types can not represent the full range of depth.
  map = tree.nodes.new(type="CompositorNodeMapValue")
  # Size is chosen kind of arbitrarily, try out until you're satisfied with resulting depth map.
  map.offset = [-1]
  map.size = [args.depth_scale]
  map.use_min = True
  map.min = [0]
  links.new(render_layers.outputs['Depth'], map.inputs[0])

  links.new(map.outputs[0], depth_file_output.inputs[0])

scale_normal = tree.nodes.new(type="CompositorNodeMixRGB")
scale_normal.blend_type = 'MULTIPLY'
# scale_normal.use_alpha = True
scale_normal.inputs[2].default_value = (0.5, 0.5, 0.5, 1)
links.new(render_layers.outputs['Normal'], scale_normal.inputs[1])

bias_normal = tree.nodes.new(type="CompositorNodeMixRGB")
bias_normal.blend_type = 'ADD'
# bias_normal.use_alpha = True
bias_normal.inputs[2].default_value = (0.5, 0.5, 0.5, 0)
links.new(scale_normal.outputs[0], bias_normal.inputs[1])

normal_file_output = tree.nodes.new(type="CompositorNodeOutputFile")
normal_file_output.label = 'Normal Output'
links.new(bias_normal.outputs[0], normal_file_output.inputs[0])

albedo_file_output = tree.nodes.new(type="CompositorNodeOutputFile")
albedo_file_output.label = 'Albedo Output'
links.new(render_layers.outputs['Color'], albedo_file_output.inputs[0])

# Delete default cube
if bpy.data.objects.get("Cube") is not None:
    bpy.data.objects['Cube'].select = True
bpy.ops.object.delete()
if bpy.data.objects.get("Lamp") is not None:
    bpy.data.objects['Lamp'].select = True
bpy.ops.object.delete()

# Transform model for rendering
bpy.ops.import_scene.obj(filepath=args.obj)
for object in bpy.context.scene.objects:
    if object.name in ['Camera']:
        continue
    bpy.context.scene.objects.active = object
    if args.remove_doubles:
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.remove_doubles()
        bpy.ops.object.mode_set(mode='OBJECT')
    if args.edge_split:
        bpy.ops.object.modifier_add(type='EDGE_SPLIT')
        bpy.context.object.modifiers["EdgeSplit"].split_angle = 1.32645
        bpy.ops.object.modifier_apply(apply_as='DATA', modifier="EdgeSplit")
    object.location = object_offset


## Set up environment lighting
# Make empty object at origin for lights to track
o_lamp = bpy.data.objects.new("Empty", None)
o_lamp.location = (0,0,0)

# Make light just directional, disable shadows.
bpy.ops.object.lamp_add(type='SUN')
lamp = bpy.data.lamps['Sun']
# lamp.shadow_method = 'NOSHADOW'
lamp.energy = 0.75
# Possibly disable specular shading:
# lamp.use_specular = False
# Make light track origin
lamp_obj = bpy.data.objects['Sun']
lamp_obj.location = (3,3,2)
lamp_constraint = lamp_obj.constraints.new(type='TRACK_TO')
lamp_constraint.track_axis = 'TRACK_NEGATIVE_Z'
lamp_constraint.up_axis = 'UP_Y'
lamp_constraint.target = o_lamp

# Add another light source so stuff facing away from light is not completely dark
bpy.ops.object.lamp_add(type='SUN')
lamp2 = bpy.data.lamps['Sun.001']
# lamp2.shadow_method = 'NOSHADOW'
lamp2.energy = 0.75
# lamp2.use_specular = False
# Make light point at object
lamp2_obj = bpy.data.objects['Sun.001']
lamp2_obj.location = (-3,-3,2)
lamp2_constraint = lamp2_obj.constraints.new(type='TRACK_TO')
lamp2_constraint.track_axis = 'TRACK_NEGATIVE_Z'
lamp2_constraint.up_axis = 'UP_Y'
lamp2_constraint.target = o_lamp

def parent_obj_to_camera(b_camera):
    origin = (0, 0, 0)
    b_empty = bpy.data.objects.new("Empty", None)
    b_empty.location = origin
    b_camera.parent = b_empty  # setup parenting

    scn = bpy.context.scene
    scn.objects.link(b_empty)
    scn.objects.active = b_empty
    return b_empty

scene = bpy.context.scene
scene.render.resolution_x = args.persp_dim
scene.render.resolution_y = args.persp_dim
scene.render.resolution_percentage = 100
scene.render.alpha_mode = 'TRANSPARENT'
cam = bpy.data.cameras['Camera']
camobj = bpy.data.objects['Camera']
cam.angle = 2*np.arctan(args.persp_dim/(2*args.flength))         # TODO: rather than scale object to unit cube, adjust render distance
camobj.location = (1, 0, 0) # so object appearance is consistent with real camera
cam_constraint = camobj.constraints.new(type='TRACK_TO')
cam_constraint.track_axis = 'TRACK_NEGATIVE_Z'
cam_constraint.up_axis = 'UP_Y'
b_empty = parent_obj_to_camera(camobj)
cam_constraint.target = b_empty

model_identifier = os.path.split(os.path.split(args.obj)[0])[1]
if not os.path.exists(os.path.join(args.output_folder, model_identifier)):
    os.makedirs(os.path.join(args.output_folder, model_identifier))
# fp = os.path.join(args.output_folder, model_identifier, model_identifier)
fp = os.path.join(args.output_folder, model_identifier)
# scene.render.use_file_extension = False
scene.render.image_settings.file_format = 'PNG'  # set output format to .png

b_empty.rotation_mode = 'QUATERNION'

# for output_node in [depth_file_output, normal_file_output, albedo_file_output]:
#     output_node.base_path = ''
# for output_node in [albedo_file_output]:
#     output_node.base_path = ''

obj_adj = Matrix().to_4x4()
obj_adj[0][0] = 1.
obj_adj[1][1] = 1.
obj_adj[2][2] = 1. 
obj_adj[3][3] = 1.
obj_adj[0][3] = object_offset[0]
obj_adj[1][3] = object_offset[1]
obj_adj[2][3] = object_offset[2]

rot = Matrix().to_4x4()
rot[0][0] = 1.
rot[1][1] = -1.
rot[2][2] = -1. 
rot[3][3] = 1.

## Get width, height and the camera
scn = bpy.data.scenes['Scene']
w = scn.render.resolution_x*scn.render.resolution_percentage/100.
h = scn.render.resolution_y*scn.render.resolution_percentage/100.

## Get camera intrinsic
K = Matrix().to_3x3()
K[0][0] = w/2 / tan(cam.angle/2)
ratio = w/h
K[1][1] = h/2. / tan(cam.angle/2) * ratio
K[0][2] = w / 2.
K[1][2] = h / 2.
K[2][2] = 1.

for i in range(0, args.views):
    print("image {}".format(i))

    # randomize lamps
    rnd_loc = np.random.uniform(low=0, high=3.0, size=3)
    lamp_obj.location = tuple(rnd_loc)
    rnd_loc = np.random.uniform(low=0, high=3.0, size=3)
    lamp2_obj.location = tuple(rnd_loc)

    ## Render for positive elevation
    # b_empty.rotation_euler[1] = radians(args.elevation)
    d = np.random.uniform(low=0.2, high=2.0)
    camobj.location = (d, 0, 0)

    q = np.random.uniform(low=-1.0, high=1.0, size=4)
    q = q/np.linalg.norm(q)

    b_empty.rotation_quaternion = q

    scene.update()

    # Get camera extrinsic
    # RT = camobj.matrix_world.inverted()
    # rotate 180 degrees about x axis to correct blender coordinates
    
    # import pdb; pdb.set_trace()

    RT = rot*camobj.matrix_world.inverted()*obj_adj
    pos = RT.translation
    quat = RT.to_quaternion()

    # Get camera pose in world
    # RT_inv = camobj.matrix_world
    # pos = RT_inv.translation
    # quat = RT_inv.to_quaternion()

    # Set filepaths for saving
    scene.render.filepath = fp + '/{}'.format(i)
    # depth_file_output.file_slots[0].path = scene.render.filepath + "_#_depth.png"
    # normal_file_output.file_slots[0].path = scene.render.filepath + "_#_normal.png"
    # albedo_file_output.file_slots[0].path = scene.render.filepath + "_#_.png"

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