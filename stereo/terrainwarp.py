import bpy, bmesh
import random
import os
import time
import blam
from mathutils import Matrix, Vector, Euler

# data_directory = '/media/droplab/Data/RSS18/RAW_DATA/HIMB/labsite3/'
# output_path = "/media/droplab/Data/RSS18/RENDERED_DATA/HIMB/labsite3/test/"
# bpy.data.scenes['Scene'].render.filepath = '/home/droplab/Desktop/test.png'

root_dir       = '/home/gidobot/workspace/blender_dev/RenderStereo/'
data_directory = root_dir + 'input_data/'
output_path_distorted   = root_dir + "output_data/distorted/"
output_path_undistorted = root_dir + "output_data/undistorted/"

#data_directory = '/media/storage/NASA_PSTAR/Blender_Projects/THandle/Rendered/Test1/'
bpy.data.scenes['Scene'].render.filepath = '/home/gidobot/Desktop/test.png'

file_distorted   = 'distorted.png'
file_undistorted = 'undistorted.png'

if not os.path.exists(output_path_distorted):
    os.makedirs(output_path_distorted)
if not os.path.exists(output_path_undistorted):
    os.makedirs(output_path_undistorted)

def removeMeshFromMemory(passedMeshName):
    mesh = bpy.data.meshes[passedMeshName]
    mesh.user_clear()
    bpy.data.meshes.remove(mesh)
    return

start = time.time()

def init_env():
    # delete default cube
    #bpy.ops.object.delete(use_global=False)
    bpy.ops.object.delete()
    if bpy.data.objects.get("Lamp") is not None:
        bpy.data.objects['Lamp'].select = True
    bpy.ops.object.delete() 
    if bpy.data.objects.get("Camera") is None:
        bpy.ops.object.camera_add()

    bpy.context.scene.render.use_file_extension = True
    #bpy.context.space_data.show_background_images = True
    bpy.context.scene.world.light_settings.use_environment_light = True
    #bpy.context.object.active_material.use_shadeless = True
    bpy.context.scene.render.use_raytrace = False
    bpy.context.scene.render.use_shadows = False
    bpy.context.scene.render.use_sss = False
    bpy.context.scene.render.resolution_percentage = 100
    bpy.context.scene.render.use_antialiasing = False

    bpy.context.scene.unit_settings.system='METRIC'


    #bpy.context.scene.render.image_settings.color_mode ='RGB'
    width = 1288
    height = 964
    depth = 1.7

    # setup stereo cameras
    R00 = 0.999780186832100
    R01 = 0.0209642830409750
    R02 = 0.000277226530280412
    R10 = -0.0209650122442497
    R11 = 0.999775830571182
    R12 = 0.00295920044982226
    R20 = -0.000215126868762418
    R21 = -0.00296436203619869
    R22 = 0.999995583129320
    trans_x = -197.400763973111/1000
    trans_y = -2.80632320828630/1000
    trans_z = -3.34139599772298/1000

    mat = Matrix(((R00,R01,R02,0),
                  (R10,R11,R12,0),
                  (R20,R21,R22,0),
                  (0,0,0,1)))

    euler = mat.to_euler()


    if bpy.data.objects.get("Camera") is None:
        bpy.ops.object.camera_add()
    bpy.context.scene.camera = bpy.data.objects['Camera']
    #bpy.data.objects['Camera'].data.name = 'Left'
    obj_cameraL = bpy.context.scene.camera
    obj_cameraL.select = True
    obj_cameraL.location[0] = 0
    obj_cameraL.location[1] = 0
    obj_cameraL.location[2] = depth
    obj_cameraL.rotation_euler[0] = 0
    obj_cameraL.rotation_euler[1] = 0
    obj_cameraL.rotation_euler[2] = 0
    # lens (mm)
    bpy.data.objects['Camera'].data.lens = 3.55
    bpy.context.scene.render.resolution_x = width
    bpy.context.scene.render.resolution_y = height
    obj_cameraL.select = False

    #bpy.ops.object.mode_set(mode='OBJECT')
    if bpy.data.objects.get("Camera.001") is None:
        bpy.ops.object.camera_add()
    bpy.context.scene.camera = bpy.data.objects['Camera.001']
    #bpy.data.objects['Camera.001'].data.name = 'Right'
    obj_cameraR = bpy.context.scene.camera
    obj_cameraR.select = True
    obj_cameraR.location[0] = obj_cameraL.location[0] + trans_x
    obj_cameraR.location[1] = obj_cameraL.location[1] + trans_y
    obj_cameraR.location[2] = obj_cameraL.location[2] + trans_z
    obj_cameraR.rotation_euler[0] = euler.x
    obj_cameraR.rotation_euler[1] = euler.y
    obj_cameraR.rotation_euler[2] = euler.z
    #obj_camera.scale[0] = 20
    #obj_camera.scale[1] = 20
    #obj_camera.scale[2] = 20
    # lens (mm)
    bpy.data.objects['Camera.001'].data.lens = 3.55
    bpy.context.scene.render.resolution_x = width
    bpy.context.scene.render.resolution_y = height
    obj_cameraR.select = False

    #projection camera
    if bpy.data.objects.get("Camera.002") is None:
        bpy.ops.object.camera_add()
    bpy.context.scene.camera = bpy.data.objects['Camera.002']
    #bpy.data.objects['Camera.002'].data.name = 'Proj'
    obj_cameraP = bpy.context.scene.camera
    obj_cameraP.select = True
    obj_cameraP.location[0] = obj_cameraL.location[0] + trans_x/2
    obj_cameraP.location[1] = obj_cameraL.location[1] + trans_y/2
    obj_cameraP.location[2] = obj_cameraL.location[2] + trans_z/2
    # lens (mm)
    bpy.data.objects['Camera.002'].data.lens = 2
    bpy.context.scene.render.resolution_x = width
    bpy.context.scene.render.resolution_y = height
    obj_cameraP.select = False

    cameras = time.time()
    print("Cameras")
    print(cameras-start)

    bpy.data.objects['Camera'].data.sensor_width = 4.8
    bpy.data.objects['Camera.001'].data.sensor_width = 4.8
    bpy.data.objects['Camera.002'].data.sensor_width = 4.8

    bpy.data.objects['Camera'].data.sensor_height = 3.6
    bpy.data.objects['Camera.001'].data.sensor_height = 3.6
    bpy.data.objects['Camera.002'].data.sensor_height = 3.6

    bpy.data.objects['Camera'].data.draw_size = 1
    bpy.data.objects['Camera.001'].data.draw_size = 1
    bpy.data.objects['Camera.002'].data.draw_size = 1

    #obj_cameraL.select = True
    #bpy.context.scene.camera = bpy.data.objects['Camera']

count = 0
sort = sorted(os.listdir(data_directory))
#random.shuffle(sort)
for file in sort:
    bpy.ops.wm.revert_mainfile()
    init_env()
    start = time.time()
    print(file)
    img = bpy.data.images.load(data_directory+file)
    rv3d = None
    for area in bpy.context.screen.areas:
      if area.type == 'VIEW_3D':
        space_data = area.spaces.active
        print(area)
        rv3d = space_data.region_3d # Reference 3D view region
        space_data.show_background_images = True # Show BG images
        if count == 0:
          bg = space_data.background_images.new()
        else:
          bg = space_data.background_images[0]
        break
    bg.image = img
    bg.frame_method = 'FIT'
    bg.opacity=1.0

   # bpy.ops.image.open(filepath=(data_directory+filepath), directory=data_directory, files=[{"name":"007480.jpg", "name":"007480.jpg"}], relative_path=True, show_multiview=False)
    # insert grid mesh
    xnum = 200
    ynum = 200
   # bpy.ops.mesh.landscape_add(random_seed=1, refresh=True)
    #bpy.ops.mesh.primitive_grid_add(x_subdivisions=xnum, y_subdivisions=ynum, radius=1, view_align=False, enter_editmode=False, location=(2.61862, 0.615173, -2.28158), layers=(True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False))
    bpy.ops.mesh.landscape_add(subdivision_x = xnum, subdivision_y = ynum, refresh=True, random_seed = random.randint(0,1000000),height=random.uniform(0.5,1.0))
    bpy.context.scene.objects[0].name = 'Landscape'
    grid = bpy.data.objects['Landscape']
    grid.select = True
    grid.location[0] = 0.0
    grid.location[1] = 0.0
    grid.location[2] = 0.0
    grid.rotation_euler[0] = 0
    grid.rotation_euler[1] = 0
    grid.rotation_euler[2] = 0
    
    bpy.context.scene.camera = bpy.data.objects['Camera.002']
    bpy.ops.object.project_bg_onto_mesh()
    #bpy.ops.object.bake_image()
   # bpy.ops.object.editmode_toggle()

#    bpy.ops.object.mode_set(mode='EDIT')
#    bpy.ops.uv.smart_project()
#    bpy.ops.object.mode_set(mode='OBJECT')

    # add texture
#    myMaterial = bpy.data.materials.new('uwmaterial')
 #   bpy.context.object.active_material = myMaterial
    bpy.context.object.active_material.use_shadows = False
    bpy.context.object.active_material.use_raytrace = False
    
    bpy.context.object.active_material.use_cast_shadows = False
    bpy.context.object.active_material.use_cast_buffer_shadows = False
    bpy.context.object.active_material.use_cast_approximate = False
    bpy.context.object.active_material.use_ray_shadow_bias = False
    bpy.context.object.active_material.use_shadeless = True
#    myMaterial.diffuse_color = (1.0, 0.0, 0.0)
    bpy.context.object.active_material.diffuse_shader = 'LAMBERT'
    bpy.context.object.active_material.diffuse_intensity = 1.0

    #myMaterial.specular_color = (0.0,1.0,0.0)
    #myMaterial.specular_shader = 'COOKTORR'
    bpy.context.object.active_material.specular_intensity = 0.0
    #myMaterial.specular_hardness = 15

    #bpy.context.object.data.materials.append(myMaterial)

    # texture
 #   tex=bpy.data.textures.new('ColorTex', type = 'IMAGE')
    #imgpath='/home/droplab/StereoWaterGAN/data/Bermuda.png'
#    img = bpy.data.images.load(data_directory+file)
  #  tex.image = img
 #   mtex = myMaterial.texture_slots.add()
  #  mtex.texture = tex
   # bpy.context.object.data.uv_textures.new()
#    bpy.context.object.data.materials.append(myMaterial)

    #bpy.context.object.data.uv_textures[0].data[0].image = tex.image

    # move grid to origin
    #bpy.context.object.location[0] = 0
    #bpy.context.object.location[1] = 0
    #bpy.context.object.location[2] = 0

    # change grid dimensions to 100x100?

    # scale grid
    bpy.context.object.scale[0] = 1.8
    bpy.context.object.scale[1] = 1.2
    bpy.context.object.scale[2] = 1
    
    grid = time.time()
    print('Mesh done')
    print(grid-start)
    
    # Render images
    bpy.context.scene.use_nodes = True
    tree = bpy.context.scene.node_tree
    links = tree.links
    # clear default nodes
    for n in tree.nodes:
        tree.nodes.remove(n)
    
    # create input render layer node
    bpy.context.scene.camera = bpy.data.objects['Camera']
    #bpy.data.objects['Camera'].data.name = 'Left'
    obj_cameraL = bpy.context.scene.camera
    obj_cameraL.select = True
    rlL = tree.nodes.new('CompositorNodeRLayers')

    # create left camera distortion node with full lens distortion
    bpy.ops.clip.open(directory=root_dir, files=[{"name":file_distorted}])
    bpy.data.movieclips[file_distorted].tracking.camera.sensor_width = 4.8
    bpy.data.movieclips[file_distorted].tracking.camera.pixel_aspect = 1
    bpy.data.movieclips[file_distorted].tracking.camera.principal[0] = 679.920475875245
    bpy.data.movieclips[file_distorted].tracking.camera.principal[1] = 464.764993442538
    scale = bpy.context.scene.render.resolution_percentage / 100
    Lx = bpy.context.scene.render.resolution_x * scale / bpy.data.cameras['Camera'].sensor_width  
    Ly = bpy.context.scene.render.resolution_y * scale / bpy.data.cameras['Camera'].sensor_height
    Lfocalx = 953.801229578324  
    Lfocaly = 954.120828071019  
    Lfmmx = Lfocalx / Lx
    Lfmmy =  Lfocaly / Ly
    bpy.data.movieclips[file_distorted].tracking.camera.units = 'PIXELS'
    bpy.data.movieclips[file_distorted].tracking.camera.focal_length_pixels = (Lfocalx + Lfocaly)/2 #(Lfmmx + Lfmmy)/2
    bpy.data.movieclips[file_distorted].tracking.camera.distortion_model = 'POLYNOMIAL'
    bpy.data.movieclips[file_distorted].tracking.camera.k1 = -0.358124644626306
    bpy.data.movieclips[file_distorted].tracking.camera.k2 = 0.203404497204656
    bpy.data.movieclips[file_distorted].tracking.camera.k3 = -0.0832422205849150
    movieDistortL_d = tree.nodes.new('CompositorNodeMovieDistortion')
    movieDistortL_d.clip = bpy.data.movieclips[file_distorted]
    movieDistortL_d.name = 'MD_d'
    tree.nodes["MD_d"].distortion_type = 'DISTORT'
    movieDistortL_i = tree.nodes.new('CompositorNodeMovieDistortion')
    movieDistortL_i.clip = bpy.data.movieclips[file_distorted]
    movieDistortL_i.name = 'MD_i'
    tree.nodes["MD_i"].distortion_type = 'DISTORT'

    # create left camera distortion node with only principal point
    bpy.ops.clip.open(directory=root_dir, files=[{"name":file_undistorted}])
    bpy.data.movieclips[file_undistorted].tracking.camera.sensor_width = 4.8
    bpy.data.movieclips[file_undistorted].tracking.camera.pixel_aspect = 1
    bpy.data.movieclips[file_undistorted].tracking.camera.principal[0] = 679.920475875245
    bpy.data.movieclips[file_undistorted].tracking.camera.principal[1] = 464.764993442538
    bpy.data.movieclips[file_undistorted].tracking.camera.units = 'PIXELS'
    bpy.data.movieclips[file_undistorted].tracking.camera.focal_length_pixels = (Lfocalx + Lfocaly)/2 #(Lfmmx + Lfmmy)/2
    bpy.data.movieclips[file_undistorted].tracking.camera.distortion_model = 'POLYNOMIAL'
    bpy.data.movieclips[file_undistorted].tracking.camera.k1 = 0
    bpy.data.movieclips[file_undistorted].tracking.camera.k2 = 0
    bpy.data.movieclips[file_undistorted].tracking.camera.k3 = 0
    movieUndistortL_d = tree.nodes.new('CompositorNodeMovieDistortion')
    movieUndistortL_d.clip = bpy.data.movieclips[file_undistorted]
    movieUndistortL_d.name = 'MUD_d'
    tree.nodes["MUD_d"].distortion_type = 'DISTORT'
    movieUndistortL_i = tree.nodes.new('CompositorNodeMovieDistortion')
    movieUndistortL_i.clip = bpy.data.movieclips[file_undistorted]
    movieUndistortL_i.name = 'MUD_i'
    tree.nodes["MUD_i"].distortion_type = 'DISTORT'

    links.new(rlL.outputs[2], movieDistortL_d.inputs[0])
    links.new(rlL.outputs[0], movieDistortL_i.inputs[0])
    links.new(rlL.outputs[2], movieUndistortL_d.inputs[0])
    links.new(rlL.outputs[0], movieUndistortL_i.inputs[0])

    # create a file output nodes and set the path
    fileOutputDistL_d = tree.nodes.new(type="CompositorNodeOutputFile")
    fileOutputDistL_d.base_path = output_path_distorted
    fileOutputDistL_d.file_slots.remove(fileOutputDistL_d.inputs[0])
    filenamedL = file[:-9]+ '_d%06d_RC0#' % count
    fileOutputDistL_d.file_slots.new(filenamedL)
    fileOutputDistL_d.format.file_format = 'HDR'
    links.new(movieDistortL_d.outputs[0], fileOutputDistL_d.inputs[0])
    # links.new(rlL.outputs[2], fileOutputDistL_d.inputs[0])

    fileOutputUndistL_d = tree.nodes.new(type="CompositorNodeOutputFile")
    fileOutputUndistL_d.base_path = output_path_undistorted
    fileOutputUndistL_d.file_slots.remove(fileOutputUndistL_d.inputs[0])
    filenamedL = file[:-9]+ '_d%06d_RC0#' % count
    fileOutputUndistL_d.file_slots.new(filenamedL)
    fileOutputUndistL_d.format.file_format = 'HDR'
    links.new(movieUndistortL_d.outputs[0], fileOutputUndistL_d.inputs[0])
    # links.new(rlL.outputs[2], fileOutputUndistL_d.inputs[0])

    fileOutputDistL_i = tree.nodes.new(type="CompositorNodeOutputFile")
    fileOutputDistL_i.base_path = output_path_distorted
    fileOutputDistL_i.file_slots.remove(fileOutputDistL_i.inputs[0])
    fileOutputDistL_i.format.file_format = 'PNG'
    fileOutputDistL_i.format.color_mode = 'RGB'
    filenameiL = file[:-9]+ '_i%06d_RC0#' % count
    fileOutputDistL_i.file_slots.new(filenameiL)
    links.new(movieDistortL_i.outputs[0], fileOutputDistL_i.inputs[0])
    # links.new(rlL.outputs[0], fileOutputDistL_i.inputs[0])

    fileOutputUndistL_i = tree.nodes.new(type="CompositorNodeOutputFile")
    fileOutputUndistL_i.base_path = output_path_undistorted
    fileOutputUndistL_i.file_slots.remove(fileOutputUndistL_i.inputs[0])
    fileOutputUndistL_i.format.file_format = 'PNG'
    fileOutputUndistL_i.format.color_mode = 'RGB'
    filenameiL = file[:-9]+ '_i%06d_RC0#' % count
    fileOutputUndistL_i.file_slots.new(filenameiL)
    links.new(movieUndistortL_i.outputs[0], fileOutputUndistL_i.inputs[0])
    # links.new(rlL.outputs[0], fileOutputUndistL_i.inputs[0])

    bpy.context.scene.camera = bpy.data.objects['Camera']
    #bpy.data.scenes['Scene'].render.filepath = '/home/droplab/Desktop/test.png'
    bpy.ops.render.render(write_still = True)

    # create a file output node and set the path
    # create input render layer node
    # clear default nodes
    for n in tree.nodes:
        tree.nodes.remove(n)

    # create input render layer node
    bpy.context.scene.camera = bpy.data.objects['Camera.001']
    obj_cameraR = bpy.context.scene.camera
    obj_cameraR.select = True
    rlR = tree.nodes.new('CompositorNodeRLayers')

    # create right camera distortion node with full lens distortion
    bpy.ops.clip.open(directory=root_dir, files=[{"name":file_distorted}])
    bpy.data.movieclips[file_distorted].tracking.camera.sensor_width = 4.8
    bpy.data.movieclips[file_distorted].tracking.camera.pixel_aspect = 1
    bpy.data.movieclips[file_distorted].tracking.camera.principal[0] = 702.5975
    bpy.data.movieclips[file_distorted].tracking.camera.principal[1] = 458.5592
    scale = bpy.context.scene.render.resolution_percentage / 100
    Rx = bpy.context.scene.render.resolution_x * scale / bpy.data.cameras['Camera'].sensor_width  
    Ry = bpy.context.scene.render.resolution_y * scale / bpy.data.cameras['Camera'].sensor_height
    Rfocalx = 948.7867 
    Rfocaly = 948.3590 
    Rfmmx = Rfocalx / Rx
    Rfmmy =  Rfocaly / Ry
    bpy.data.movieclips[file_distorted].tracking.camera.units = 'PIXELS'
    bpy.data.movieclips[file_distorted].tracking.camera.focal_length_pixels = (Rfocalx + Rfocaly)/2 #(Lfmmx + Lfmmy)/2
    bpy.data.movieclips[file_distorted].tracking.camera.distortion_model = 'POLYNOMIAL'
    bpy.data.movieclips[file_distorted].tracking.camera.k1 = -0.343142129
    bpy.data.movieclips[file_distorted].tracking.camera.k2 = 0.1463169
    bpy.data.movieclips[file_distorted].tracking.camera.k3 = -0.01752719
    movieDistortR_d = tree.nodes.new('CompositorNodeMovieDistortion')
    movieDistortR_d.clip = bpy.data.movieclips[file_distorted]
    movieDistortR_d.name = 'MD_d'
    tree.nodes["MD_d"].distortion_type = 'DISTORT'
    movieDistortR_i = tree.nodes.new('CompositorNodeMovieDistortion')
    movieDistortR_i.clip = bpy.data.movieclips[file_distorted]
    movieDistortR_i.name = 'MD_i'
    tree.nodes["MD_i"].distortion_type = 'DISTORT'

    # create right camera distortion node with only principal point
    bpy.ops.clip.open(directory=root_dir, files=[{"name":file_undistorted}])
    bpy.data.movieclips[file_undistorted].tracking.camera.sensor_width = 4.8
    bpy.data.movieclips[file_undistorted].tracking.camera.pixel_aspect = 1
    bpy.data.movieclips[file_undistorted].tracking.camera.principal[0] = 702.5975
    bpy.data.movieclips[file_undistorted].tracking.camera.principal[1] = 458.5592
    bpy.data.movieclips[file_undistorted].tracking.camera.units = 'PIXELS'
    bpy.data.movieclips[file_undistorted].tracking.camera.focal_length_pixels = (Rfocalx + Rfocaly)/2 #(Lfmmx + Lfmmy)/2
    bpy.data.movieclips[file_undistorted].tracking.camera.distortion_model = 'POLYNOMIAL'
    bpy.data.movieclips[file_undistorted].tracking.camera.k1 = 0
    bpy.data.movieclips[file_undistorted].tracking.camera.k2 = 0
    bpy.data.movieclips[file_undistorted].tracking.camera.k3 = 0
    movieUndistortR_d = tree.nodes.new('CompositorNodeMovieDistortion')
    movieUndistortR_d.clip = bpy.data.movieclips[file_undistorted]
    movieUndistortR_d.name = 'MUD_d'
    tree.nodes["MUD_d"].distortion_type = 'DISTORT'
    movieUndistortR_i = tree.nodes.new('CompositorNodeMovieDistortion')
    movieUndistortR_i.clip = bpy.data.movieclips[file_undistorted]
    movieUndistortR_i.name = 'MUD_i'
    tree.nodes["MUD_i"].distortion_type = 'DISTORT'


    links.new(rlR.outputs[2], movieDistortR_d.inputs[0])
    links.new(rlR.outputs[0], movieDistortR_i.inputs[0])
    links.new(rlR.outputs[2], movieUndistortR_d.inputs[0])
    links.new(rlR.outputs[0], movieUndistortR_i.inputs[0])

    # create a file output nodes and set the path
    fileOutputDistR_d = tree.nodes.new(type="CompositorNodeOutputFile")
    fileOutputDistR_d.base_path = output_path_distorted
    fileOutputDistR_d.file_slots.remove(fileOutputDistR_d.inputs[0])
    filenamedR = file[:-9]+ '_d%06d_LC0#' % count
    fileOutputDistR_d.file_slots.new(filenamedR)
    fileOutputDistR_d.format.file_format = 'HDR'
    links.new(movieDistortR_d.outputs[0], fileOutputDistR_d.inputs[0])
    # links.new(rlR.outputs[2], fileOutputDistR_d.inputs[0])

    fileOutputUndistR_d = tree.nodes.new(type="CompositorNodeOutputFile")
    fileOutputUndistR_d.base_path = output_path_undistorted
    fileOutputUndistR_d.file_slots.remove(fileOutputUndistR_d.inputs[0])
    filenamedR = file[:-9]+ '_d%06d_LC0#' % count
    fileOutputUndistR_d.file_slots.new(filenamedR)
    fileOutputUndistR_d.format.file_format = 'HDR'
    links.new(movieUndistortR_d.outputs[0], fileOutputUndistR_d.inputs[0])
    # links.new(rlR.outputs[2], fileOutputUndistR_d.inputs[0])

    fileOutputDistR_i = tree.nodes.new(type="CompositorNodeOutputFile")
    fileOutputDistR_i.base_path = output_path_distorted
    fileOutputDistR_i.file_slots.remove(fileOutputDistR_i.inputs[0])
    fileOutputDistR_i.format.file_format = 'PNG'
    fileOutputDistR_i.format.color_mode = 'RGB'
    filenameiR = file[:-9]+ '_i%06d_LC0#' % count
    fileOutputDistR_i.file_slots.new(filenameiR)
    links.new(movieDistortR_i.outputs[0], fileOutputDistR_i.inputs[0])
    # links.new(rlR.outputs[0], fileOutputDistR_i.inputs[0])

    fileOutputUndistR_i = tree.nodes.new(type="CompositorNodeOutputFile")
    fileOutputUndistR_i.base_path = output_path_undistorted
    fileOutputUndistR_i.file_slots.remove(fileOutputUndistR_i.inputs[0])
    fileOutputUndistR_i.format.file_format = 'PNG'
    fileOutputUndistR_i.format.color_mode = 'RGB'
    filenameiR = file[:-9]+ '_i%06d_LC0#' % count
    fileOutputUndistR_i.file_slots.new(filenameiR)
    links.new(movieUndistortR_i.outputs[0], fileOutputUndistR_i.inputs[0])
    # links.new(rlR.outputs[0], fileOutputUndistR_i.inputs[0])

    bpy.context.scene.camera = bpy.data.objects['Camera.001']
    bpy.ops.render.render(write_still = True)

    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.data.objects['Landscape'].select = True
    bpy.data.objects['Camera'].select = False
    bpy.data.objects['Camera.001'].select = False
    bpy.ops.object.delete()
    removeMeshFromMemory('Landscape')
    count = count + 1
    render = time.time()
    print('Rendered')
    print(render-grid)
