import bpy, bmesh
import random
import os
import time
import blam

data_directory = '/home/droplab/RSS18/rendering/input_data/'
#data_directory = '/home/katie/rendercheck/'
start = time.time()
#data_directory = '/home/katie/stereowatergan/data/09172017_hog_reef_north_plot_0_to_15_subset/small/'
bpy.context.scene.render.use_file_extension = True
#bpy.context.space_data.show_background_images = True
bpy.data.scenes['Scene'].render.filepath = '/home/droplab/Desktop/test.png'
bpy.context.scene.world.light_settings.use_environment_light = True
#bpy.context.object.active_material.use_shadeless = True
# delete default cube
#bpy.ops.object.delete(use_global=False)
bpy.ops.object.delete() 
bpy.data.objects['Lamp'].select = True
bpy.ops.object.delete() 
bpy.context.scene.render.use_raytrace = False
bpy.context.scene.render.use_shadows = False
bpy.context.scene.render.use_sss = False
bpy.context.scene.render.resolution_percentage = 100
bpy.context.scene.render.use_antialiasing = False


#bpy.context.scene.render.image_settings.color_mode ='RGB'
width = 1360
height = 1024

# setup stereo cameras
#R00 = 0.99995995
#R01 = -0.00791804
#R02 =  0.00417283
#R10 = 0.00793539
#R11 = 0.99995987
#R12 = -0.00415813
#R20 = -0.00413974
#R21 = 0.00419108
#R22 = 0.99998265
#trans_x = 0.12862514
#trans_y = 0.0010255
#trans_z = -0.00051556

trans_x = -0.1286
depth = 2.0

#bpy.ops.object.camera_add()
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
#obj_camera.scale[0] = 20
#obj_camera.scale[1] = 20
#obj_camera.scale[2] = 20
# lens (mm)
bpy.data.cameras['Camera'].lens = 8.24
bpy.context.scene.render.resolution_x = width
bpy.context.scene.render.resolution_y = height
obj_cameraL.select = False

#bpy.ops.object.mode_set(mode='OBJECT')
bpy.ops.object.camera_add()
bpy.context.scene.camera = bpy.data.objects['Camera.001']
#bpy.data.objects['Camera.001'].data.name = 'Right'
obj_cameraR = bpy.context.scene.camera
obj_cameraR.select = True
obj_cameraR.location[0] = obj_cameraL.location[0] + trans_x
obj_cameraR.location[1] = obj_cameraL.location[1]# + trans_y
obj_cameraR.location[2] = obj_cameraL.location[2]# + trans_z
obj_cameraR.rotation_euler[0] = 0
obj_cameraR.rotation_euler[1] = 0
obj_cameraR.rotation_euler[2] = 0
#obj_camera.scale[0] = 20
#obj_camera.scale[1] = 20
#obj_camera.scale[2] = 20
# lens (mm)
bpy.data.cameras['Camera.001'].lens = 8.24
bpy.context.scene.render.resolution_x = width
bpy.context.scene.render.resolution_y = height
obj_cameraR.select = False
cameras = time.time()
print("Cameras")
print(cameras-start)

bpy.data.cameras['Camera'].sensor_width = 8.8
bpy.data.cameras['Camera.001'].sensor_width = 8.8

bpy.data.cameras['Camera'].sensor_height = 6.6
bpy.data.cameras['Camera.001'].sensor_height = 6.6

#obj_cameraL.select = True
#bpy.context.scene.camera = bpy.data.objects['Camera']

count = 0
sort = sorted(os.listdir(data_directory))
for file in sort:
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
    xnum = 100
    ynum = 100
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
    bpy.context.object.scale[0] = (1360/1024)
    bpy.context.object.scale[1] = 1
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
    output_path = "/home/droplab/RSS18/rendering/output_data/"
    # create input render layer node
    bpy.context.scene.camera = bpy.data.objects['Camera']
    #bpy.data.objects['Camera'].data.name = 'Left'
    obj_cameraL = bpy.context.scene.camera
    obj_cameraL.select = True
    rlL = tree.nodes.new('CompositorNodeRLayers')
    # create a file output node and set the path
    fileOutputL_d = tree.nodes.new(type="CompositorNodeOutputFile")
    fileOutputL_d.base_path = output_path
#    fileOutputL_d.base_path = "/home/katie/rendercheck"
    fileOutputL_d.file_slots.remove(fileOutputL_d.inputs[0])
    filenamedL = file[:-9]+ '_d%06d_RC0#' % count
    fileOutputL_d.file_slots.new(filenamedL)
    fileOutputL_d.format.file_format = 'HDR'
    links.new(rlL.outputs[2], fileOutputL_d.inputs[0])

    fileOutputL_i = tree.nodes.new(type="CompositorNodeOutputFile")
    fileOutputL_i.base_path = output_path
    #fileOutputL_i.base_path = "/home/katie/rendercheck"
    fileOutputL_i.file_slots.remove(fileOutputL_i.inputs[0])
    fileOutputL_i.format.file_format = 'PNG'
    fileOutputL_i.format.color_mode = 'RGB'
    filenameiL = file[:-9]+ '_i%06d_RC0#' % count
    fileOutputL_i.file_slots.new(filenameiL)
    links.new(rlL.outputs[0], fileOutputL_i.inputs[0])

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
    # create a file output node and set the path
    fileOutputR_d = tree.nodes.new(type="CompositorNodeOutputFile")
    fileOutputR_d.base_path = output_path
    #fileOutputR_d.base_path = "/home/katie/rendercheck"
    fileOutputR_d.file_slots.remove(fileOutputR_d.inputs[0])
    filenamedR = file[:-9]+ '_d%06d_LC0#' % count
    fileOutputR_d.file_slots.new(filenamedR)
    fileOutputR_d.format.file_format = 'HDR'
    links.new(rlR.outputs[2], fileOutputR_d.inputs[0])

    fileOutputR_i = tree.nodes.new(type="CompositorNodeOutputFile")
    fileOutputR_i.base_path = output_path
    #fileOutputR_i.base_path = "/home/katie/rendercheck"
    fileOutputR_i.file_slots.remove(fileOutputR_i.inputs[0])
    fileOutputR_i.format.file_format = 'PNG'
    fileOutputR_i.format.color_mode = 'RGB'
    filenameiR = file[:-9]+ '_i%06d_LC0#' % count
    fileOutputR_i.file_slots.new(filenameiR)
    links.new(rlR.outputs[0], fileOutputR_i.inputs[0])
    bpy.context.scene.camera = bpy.data.objects['Camera.001']
    #bpy.data.scenes['Scene'].render.filepath = '/home/katie/Desktop/test.png'
    bpy.ops.render.render(write_still = True)
    
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.data.objects['Landscape'].select = True
    bpy.data.objects['Camera'].select = False
    bpy.data.objects['Camera.001'].select = False
    bpy.ops.object.delete() 
    count = count + 1
    render = time.time()
    print('Rendered')
    print(render-grid)
