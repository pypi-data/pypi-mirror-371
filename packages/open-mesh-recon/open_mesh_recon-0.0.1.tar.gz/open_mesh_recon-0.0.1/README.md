# Welcome to the `Open Mesh` package pypi page

This package includes two classes for this version `(0.0.1)` and it's so easy to use them.

## What does `Open Mesh` do

This package generated for those guys who are trying to use 3D human reconstruction models so easy. 

## How to use `Open Mesh`

Here you can see a step-by-step tutorial of how you can use the package to work with 3D reconstruction models **(for humans)** so easy!

### Step 1: Project structure
In the following content you can see the structure of the project how to use `Open Mesh`

Its recommended to use a virtual environment.

#### Setting up environment
Just run the following commands to install virtualenv and generate a new environment for `Open Mesh`

```bash
pip install virtualenv

virtualenv venv
```

You will have a new folder called `venv` in your directory you were with your terminal

```bash
venv\Scripts\activate # For windows users

source venv/bin/activate # For linux/macos users
```

After this you should see a `(venv)` at the first of your terminal path.

### Step 2: Installation

After the virtual environment generated and activated by the terminal you just need to run:

```bash
pip install open_mesh
```

and then it will start downloading all the requirements and the whole package and then install it.

```
your_project_name/
|
├─── venv/
|
├─── your_main_file.py
|
├─── input_images/
|    |
|    └─── human_image_1.png
|    |
|    └─── human_image_2.png
|    |
|    └─── human_image_3.png
|    |
|    └─── ...
```

### Step 3: Main python script
In the following content you should write your main.py script by the tutorial.

```python
from omesh import MeshFactory, PyLog
```

#### MeshFactory
`MeshFactory` is the core class which includes all the functions to control the whole process.

In the following script you can see all the functions should run in order.

```python
mesh_factory = MeshFactory(mesh_id_min=10, mesh_id_max=20)

mesh_factory.remove_background()

mesh_factory.extract_keypoints()

mesh_factory.run_model()

mesh_factory.save_mesh()

mesh_factory.render_spinning_video()
```
The object of this class has a mesh_id which generated randomly between the range passed as `mesh_id_min` and `mesh_id_max`

The program will automaticly detect the device should be cuda or cpu using `torch.cuda.is_available()` method and the pass it with the `run_model()` function.

The input directory can be changed by editing `input_dir` argument.

```python
# Example:
mf = MeshFactory(input_dir='your_input_directory')
# It is setted to 'input_images' by default which defined in folder structure
```

The last argument of this class is `output_dir` which determines the output directory of the process which setted to `results` by default. You **do not** need to generate the output directory.

#### PyLog
`PyLog` is a simple logging class for better debugging. It includes 4 functions info, warning, error, succeed. 
The functions info, warning and succeed are the same just with different headers. You just need to pass a `message` to all of these functions. The `error` function stops the program directly after the message displayed.

You can see a simple worker for `PyLog` below + the output

```python
log = PyLog()
log.info("This is a simple info")
log.warning("The addon package not installed!")
log.error("Failed to run model!")
log.succeed("Finished Processing")
```

The output might looks like this:
```
 --- INFO ---: This is a simple info
 --- WARNING ---: The addon package not installed!
 --- ERROR ---: Failed to run model!
```

**Tip: Actually the last successful message will not appear beacause the previous error message will stop the program so the rest of the program will not execute.**

```python
log.succeed("Program Executed!")
```

The output of a `succeed` function looks like this:
```
 --- SUCCESSFUL ---: Program Executed!
```

### Step 4: Output
Once you run your main.py file you will be able to see the `results` folder (or the name you specified as 'output_dir'). For each image exists on the input directory there is a removed background image and a 2d keypoints including body landmarks with openpose json format.

You might see the mesh_`mesh id`.obj file + the .mp4 spinning video rendered once the process finished. The program logs for every step and you would see errors if something was not expected.

***Notice: This release `(0.0.1)` is not completed and does not include the implemented functions `run_model`, `save_mesh` and `render_spinning_video`, a pre-release version.***

## Future Versions
In the future releases I might implement the functions not defined. That functions just log their process but do not work.