# Render Blender

Render Blender is a set of scripts for rendering visual datasets in Blender.

Some scripts are compatable with Blender 2.79 and others have been updated for Blender 2.80+. Compatabilities are noted in the script descriptions below.

## Repo Structure

The repo is organized into folders for the different rendering applications. These folders are outlined below.

### scripts

`blender_render.py` - renders evenly distributed viewpoints of an object by rotating a camera around the object at defined elevation angles. Also generates depth maps. *Compatible with Blender 2.79*

`blender_render_dataset.py` - renders random orientations of an object centered in a perspective image. *Compatible with Blender 2.79*

### stereo

This is an experimental project for rendering stereo datasets of randomly generated surface structure texture mapped with underwater monocular images. This project may be updated in the future, but is currently provided "as is", though may be documented in the future. *Compatible with Blender 2.79*

### uwhandles

This is a project for rendering fisheye images of objects in a virtual underwater environment to supplement the [UWHandles](https://github.com/gidobot/UWHandles/blob/master/README.md) dataset. The script is intended for rendering the *.glb* models provided with the dataset. Documentation for the project will be extended in the future.

`render_blender_underwater_fisheye.py` - main script. *Compatable with Blender 2.80+*

Example invocation  
`~/blender-2.82/blender --background underwater_fisheye_env.blend --python render_blender_underwater_fisheye.py -- --output_folder /tmp/rendered textured_real.glb`

## Example Script Usage

Some examples are provided here with *render_blender.py* to show how the scripts can be used for single instance and batch data generation.

To render a single *.obj* file, run  
`blender --background --python render_blender.py -- --output_folder /tmp path_to_model.obj`

To render a batch of data with different models, you can e. g. use the unix tool find  
`find . -name *.obj -exec blender --background --python render_blender.py -- --output_folder /tmp {} \;`

To speed up the process, you can also use xargs to have multiple blender instances run in parallel using the *-P* argument  
`find . -name *.obj -print0 | xargs -0 -n1 -P3 -I {} blender --background --python render_blender.py -- --output_folder /tmp {}`

### Example command for rendering YCB-Video dataset models using parallel instances

This invocation was used to generate the rendered model input images for [SilhoNet](https://github.com/gidobot/SilhoNet)  
`find $YCB_DIR/models -name "*.obj" -print0 | xargs -0 -n1 -P3 -I {} blender --background --python render_blender.py -- --output_folder $YCB_DIR/models/rendered {}`  
where $YCB_DIR is the root directory of the YCB-Video dataset

