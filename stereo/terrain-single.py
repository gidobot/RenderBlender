import bpy, bmesh
import random
import os

data_directory = '/home/droplab/StereoWaterGAN/data/09172017_hog_reef_north_plot_0_to_15_subset/small/'

# delete default cube
#bpy.ops.object.delete(use_global=False)
bpy.ops.object.delete() 

for file in os.listdir(data_directory):
    print(file)
    # insert grid mesh
    xnum = 100
    ynum = 100
    bpy.ops.mesh.primitive_grid_add(x_subdivisions=xnum, y_subdivisions=ynum, radius=1, view_align=False, enter_editmode=False, location=(2.61862, 0.615173, -2.28158), layers=(True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False))
    bpy.ops.object.editmode_toggle()

    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.uv.smart_project()
    bpy.ops.object.mode_set(mode='OBJECT')

    # add texture
    myMaterial = bpy.data.materials.new('uwmaterial')
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
    bpy.context.object.location[0] = 0
    bpy.context.object.location[1] = 0
    bpy.context.object.location[2] = 0

    # change grid dimensions to 100x100?

    # scale grid
    bpy.context.object.scale[0] = 1
    bpy.context.object.scale[1] = 1
    bpy.context.object.scale[2] = 1

    # proportional editing mode
    bpy.context.scene.tool_settings.proportional_edit = 'ENABLED'
    bpy.context.scene.tool_settings.proportional_edit_falloff = 'RANDOM'

    # select random vertex
    hcount = 100
    for i in range(0, hcount):
        vidx = random.randint(0,xnum*ynum-1)
        bpy.ops.object.mode_set(mode = 'OBJECT')
        obj = bpy.context.active_object
        bpy.ops.object.mode_set(mode = 'EDIT') 
        bpy.ops.mesh.select_mode(type="VERT")
        bpy.ops.mesh.select_all(action = 'DESELECT')
        bpy.ops.object.mode_set(mode = 'OBJECT')
        obj.data.vertices[vidx].select = True
        bpy.ops.object.mode_set(mode = 'EDIT') 

        # make random mountain
        tx = 0
        ty = 0
        tz = random.uniform(0.0,0.1)
        radius = random.uniform(0.0,1.0)
        bpy.ops.transform.translate(value=(tx, ty, tz), constraint_axis=(False, False, False), constraint_orientation='GLOBAL', mirror=False, proportional='ENABLED', proportional_edit_falloff='SMOOTH', proportional_size=radius, release_confirm=True)

        # smooth if too sharp
        bpy.ops.mesh.vertices_smooth()
        obj.data.vertices[vidx].select = False


    # RENDERING
    #bpy.context.scene.render.image_settings.color_mode ='RGB'
    width = 603
    height = 453
    # setup stereo cameras
    R00 = 0.9999937114001909
    R01 = 0.001844845370574911
    R02 = 0.003028812577618397
    R10 = -0.001848473069533369
    R11 = 0.9999975771188431
    R12 = 0.001195367623232744
    R20 = -0.003026599970739602
    R21 = -0.001200958784526568
    R22 = 0.9999946986812555
    trans_x = 0.0815123106302772
    trans_y = 0.0009179626345281808
    trans_z = 0.003191009813981309

    depth = 2.0

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
    bpy.context.scene.render.resolution_x = width
    bpy.context.scene.render.resolution_y = height

    bpy.ops.object.mode_set(mode='OBJECT')
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
    bpy.context.scene.render.resolution_x = width
    bpy.context.scene.render.resolution_y = height

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
    fileOutputL_d.base_path = "/home/droplab/Desktop"
    fileOutputL_d.file_slots.remove(fileOutputL_d.inputs[0])
    fileOutputL_d.file_slots.new("depth_######_L")
    fileOutputL_d.format.file_format = 'HDR'
    #invertL = tree.nodes.new(type="CompositorNodeInvert")
    #links.new(rlL.outputs[2], invertL.inputs[1])
    #links.new(invertL.outputs[0], fileOutputL_d.inputs[0])
    links.new(rlL.outputs[2], fileOutputL_d.inputs[0])

    fileOutputL_i = tree.nodes.new(type="CompositorNodeOutputFile")
    fileOutputL_i.base_path = "/home/droplab/Desktop"
    fileOutputL_i.file_slots.remove(fileOutputL_i.inputs[0])
    fileOutputL_i.format.file_format = 'PNG'
    fileOutputL_i.file_slots.new("image_######_L")
    links.new(rlL.outputs[0], fileOutputL_i.inputs[0])

    bpy.context.scene.camera = bpy.data.objects['Camera']
    #bpy.data.scenes['Scene'].render.filepath = '/home/droplab/Desktop/test.png'
    bpy.ops.render.render(write_still=True)

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
    fileOutputR_d.base_path = "/home/droplab/Desktop"
    fileOutputR_d.file_slots.remove(fileOutputR_d.inputs[0])
    fileOutputR_d.file_slots.new("depth_######_R")
    fileOutputR_d.format.file_format = 'HDR'
    links.new(rlR.outputs[2], fileOutputR_d.inputs[0])

    fileOutputR_i = tree.nodes.new(type="CompositorNodeOutputFile")
    fileOutputR_i.base_path = "/home/droplab/Desktop"
    fileOutputR_i.file_slots.remove(fileOutputR_i.inputs[0])
    fileOutputR_i.format.file_format = 'PNG'
    fileOutputR_i.file_slots.new("image_######_R")
    links.new(rlR.outputs[0], fileOutputR_i.inputs[0])
    bpy.context.scene.camera = bpy.data.objects['Camera.001']
    #bpy.data.scenes['Scene'].render.filepath = '/home/droplab/Desktop/test.png'
    bpy.ops.render.render(write_still=True)
    bpy.ops.object.delete() 