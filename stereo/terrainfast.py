import bpy, bmesh
import random
import os
import time

data_directory = '/home/katie/stereowatergan/input_data/'

start = time.time()
#data_directory = '/home/katie/stereowatergan/data/09172017_hog_reef_north_plot_0_to_15_subset/small/'
bpy.context.scene.render.use_file_extension = True
bpy.data.scenes['Scene'].render.filepath = '/home/katie/Desktop/test.png'
bpy.context.scene.world.light_settings.use_environment_light = True
bpy.context.object.active_material.use_shadeless = True
# delete default cube
#bpy.ops.object.delete(use_global=False)
bpy.ops.object.delete() 
bpy.data.objects['Lamp'].select = True
bpy.ops.object.delete() 

#bpy.context.scene.render.image_settings.color_mode ='RGB'
width = 1360
height = 1024

# setup stereo cameras
R00 = 0.99995995
R01 = -0.00791804
R02 =  0.00417283
R10 = 0.00793539
R11 = 0.99995987
R12 = -0.00415813
R20 = -0.00413974
R21 = 0.00419108
R22 = 0.99998265
trans_x = 0.12862514
trans_y = 0.0010255
trans_z = -0.00051556
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
bpy.data.cameras['Camera'].lens = 27
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
obj_cameraR.location[1] = obj_cameraL.location[1] + trans_y
obj_cameraR.location[2] = obj_cameraL.location[2] + trans_z
obj_cameraR.rotation_euler[0] = 0
obj_cameraR.rotation_euler[1] = 0
obj_cameraR.rotation_euler[2] = 0
#obj_camera.scale[0] = 20
#obj_camera.scale[1] = 20
#obj_camera.scale[2] = 20
# lens (mm)
bpy.data.cameras['Camera.001'].lens = 27
bpy.context.scene.render.resolution_x = width
bpy.context.scene.render.resolution_y = height
obj_cameraR.select = False
cameras = time.time()
print(cameras-start)

count = 0
for file in os.listdir(data_directory):
    start = time.time()
    print(file)
    # insert grid mesh
    xnum = 100
    ynum = 100
   # bpy.ops.mesh.landscape_add(random_seed=1, refresh=True)
    bpy.ops.mesh.primitive_grid_add(x_subdivisions=xnum, y_subdivisions=ynum, radius=1, view_align=False, enter_editmode=False, location=(2.61862, 0.615173, -2.28158), layers=(True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False))
    grid = bpy.data.objects['Grid']
    grid.select = True
    grid.location[0] = 0.0
    grid.location[1] = 0.0
    grid.location[2] = -0.5
    grid.rotation_euler[0] = 0
    grid.rotation_euler[1] = 0
    grid.rotation_euler[2] = 0
    bpy.ops.object.editmode_toggle()

    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.uv.smart_project()
    bpy.ops.object.mode_set(mode='OBJECT')

    # add texture
    myMaterial = bpy.data.materials.new('uwmaterial')
    bpy.context.object.active_material = myMaterial
    bpy.context.object.active_material.use_shadows = False
    bpy.context.object.active_material.use_cast_shadows = False
    bpy.context.object.active_material.use_cast_buffer_shadows = False
    bpy.context.object.active_material.use_cast_approximate = False
    bpy.context.object.active_material.use_ray_shadow_bias = False
    bpy.context.object.active_material.use_shadeless = True
    #myMaterial.diffuse_color = (1.0, 0.0, 0.0)
    myMaterial.diffuse_shader = 'LAMBERT'
    myMaterial.diffuse_intensity = 1.0

    #myMaterial.specular_color = (0.0,1.0,0.0)
    #myMaterial.specular_shader = 'COOKTORR'
    myMaterial.specular_intensity = 0.0
    #myMaterial.specular_hardness = 15

    #bpy.context.object.data.materials.append(myMaterial)

    # texture
    tex=bpy.data.textures.new('ColorTex', type = 'IMAGE')
    #imgpath='/home/droplab/StereoWaterGAN/data/Bermuda.png'
    img = bpy.data.images.load(data_directory+file)
    tex.image = img
    mtex = myMaterial.texture_slots.add()
    mtex.texture = tex
    bpy.context.object.data.uv_textures.new()
    bpy.context.object.data.materials.append(myMaterial)

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

    # proportional editing mode
    #bpy.context.scene.tool_settings.proportional_edit = 'ENABLED'
    #bpy.context.scene.tool_settings.proportional_edit_falloff = 'RANDOM'
    #bpy.ops.object.select_grouped(type='CHILDREN_RECURSIVE')
    #bpy.ops.object.parent_clear(type='CLEAR')
    # select random vertex
    #hcount = 100
    ##for i in range(0, hcount):
    #    vidx = random.randint(0,xnum*ynum-1)
    #    bpy.ops.object.mode_set(mode = 'OBJECT')
    #    obj = bpy.context.active_object
    #    bpy.ops.object.mode_set(mode = 'EDIT') 
    #    bpy.ops.mesh.select_mode(type="VERT")
    #    bpy.ops.mesh.select_all(action = 'DESELECT')
    #    bpy.ops.object.mode_set(mode = 'OBJECT')
    #    obj.data.vertices[vidx].select = True
    #    bpy.ops.object.mode_set(mode = 'EDIT') 

        # make random mountain
 #       tx = 0
#        ty = 0
   #     tz = random.uniform(0.0,0.1)
  #      radius = random.uniform(0.0,1.0)
        
        # maybe better to use bmesh modules here but override works for now
    #    for area in bpy.context.screen.areas: 
    #      if area.type == 'VIEW_3D': 
    #        for region in area.regions: 
    #          if region.type == 'WINDOW': 
    #            override = {'window': bpy.context.window,
     #                       'area': area, 
    #                        'region': region,
    ##                        'scene': bpy.context.scene,
      #                      'screen': bpy.context.screen,
    ##                        'edit_object': bpy.context.edit_object,
      #                      'gpencil_data': bpy.context.gpencil_data,
    #                        'active_object': bpy.context.active_object}
    #    bpy.ops.transform.translate(override, value=(tx, ty, tz), constraint_axis=(False, False, False), constraint_orientation='GLOBAL', mirror=False, proportional='ENABLED', proportional_edit_falloff='SMOOTH', proportional_size=radius, release_confirm=True)

        # smooth if too sharp
#        bpy.ops.mesh.vertices_smooth()
#        obj.data.vertices[vidx].select = False
    # bpy.ops.mesh.subdivide(number_cuts=100, smoothness=0)
    
    bpy.ops.mesh.ant_displace(refresh=True, random_seed = random.randint(0,10000000),height=1.5)
    bpy.ops.object.mode_set(mode = 'EDIT')
    bpy.ops.mesh.vertices_smooth()
    bpy.ops.mesh.vertices_smooth()
    bpy.ops.mesh.vertices_smooth()
    #bpy.ops.mesh.vertices_smooth()
    #bpy.ops.mesh.vertices_smooth()
    
    grid = time.time()
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
    # create a file output node and set the path
    fileOutputL_d = tree.nodes.new(type="CompositorNodeOutputFile")
    fileOutputL_d.base_path = "/home/katie/stereowatergan/output_data"
    fileOutputL_d.file_slots.remove(fileOutputL_d.inputs[0])
    filenamedL = file[:-9]+ '_d%06d_LC0#' % count
    fileOutputL_d.file_slots.new(filenamedL)
    fileOutputL_d.format.file_format = 'HDR'
    #invertL = tree.nodes.new(type="CompositorNodeInvert")
    #links.new(rlL.outputs[2], invertL.inputs[1])
    #links.new(invertL.outputs[0], fileOutputL_d.inputs[0])
    links.new(rlL.outputs[2], fileOutputL_d.inputs[0])

    fileOutputL_i = tree.nodes.new(type="CompositorNodeOutputFile")
    fileOutputL_i.base_path = "/home/katie/stereowatergan/output_data"
    fileOutputL_i.file_slots.remove(fileOutputL_i.inputs[0])
    fileOutputL_i.format.file_format = 'PNG'
    fileOutputL_i.format.color_mode = 'RGB'
    filenameiL = file[:-9]+ '_i%06d_LC0#' % count
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
    fileOutputR_d.base_path = "/home/katie/stereowatergan/output_data"
    fileOutputR_d.file_slots.remove(fileOutputR_d.inputs[0])
    filenamedR = file[:-9]+ '_d%06d_RC0#' % count
    fileOutputR_d.file_slots.new(filenamedR)
    fileOutputR_d.format.file_format = 'HDR'
    links.new(rlR.outputs[2], fileOutputR_d.inputs[0])

    fileOutputR_i = tree.nodes.new(type="CompositorNodeOutputFile")
    fileOutputR_i.base_path = "/home/katie/stereowatergan/output_data"
    fileOutputR_i.file_slots.remove(fileOutputR_i.inputs[0])
    fileOutputR_i.format.file_format = 'PNG'
    fileOutputR_i.format.color_mode = 'RGB'
    filenameiR = file[:-9]+ '_i%06d_RC0#' % count
    fileOutputR_i.file_slots.new(filenameiR)
    links.new(rlR.outputs[0], fileOutputR_i.inputs[0])
    bpy.context.scene.camera = bpy.data.objects['Camera.001']
    #bpy.data.scenes['Scene'].render.filepath = '/home/katie/Desktop/test.png'
    bpy.ops.render.render(write_still = True)
    
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.data.objects['Grid'].select = True
    bpy.data.objects['Camera'].select = False
    bpy.data.objects['Camera.001'].select = False
    bpy.ops.object.delete() 
    count = count + 1
    render = time.time()
    print(render-start)