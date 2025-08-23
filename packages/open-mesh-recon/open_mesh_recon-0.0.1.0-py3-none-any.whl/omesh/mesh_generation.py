from .log import PyLog
l = PyLog()
l.info("Initializing ...")

from rembg import remove as remove_rembg
import os, sys, trimesh, pyrender, imageio
import numpy as np

from pathlib import Path

import torch

import json
import mediapipe as mp
import cv2 as cv

from random import randint as rand
import subprocess

class MeshFactory:
    def __init__(self, mesh_id_min=0, mesh_id_max=9, input_dir='input_images', output_dir='results'):
        print(" --- Mesh Factory --- ")

        self.logger = l

        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'

        self.logger.info(f"Using device: {self.device}")

        mesh_id = rand(mesh_id_min, mesh_id_max)

        if not os.path.exists(input_dir):
            self.logger.error(f"Could find any folder in the provided path {input_dir}")
        
        self.input_dir = input_dir

        self.root_path = os.path.join(output_dir, str(mesh_id))

        os.makedirs(output_dir, exist_ok=True)
        os.makedirs(self.root_path, exist_ok=True)

        self.mesh_id = mesh_id

        self.no_bg_dir = os.path.join(self.root_path, 'nobg')

        os.makedirs(self.no_bg_dir, exist_ok=True)

        self.output_video = os.path.join(self.root_path, 'rotating_video.mp4')

        self.video_size = 900
        self.frames = 240
        self.fps = 30
        
        if not os.listdir(self.input_dir):
            self.logger.error(f"No input images provided in {self.input_dir}")

        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(static_image_mode=True, min_detection_confidence=0.7)

        self.mesh_path = os.path.join(self.root_path, 'mesh.obj')

        self.mesh = None # Initialize mesh attribute

        self.logger.succeed("Initialization finished")

    def remove_background(self):
        self.logger.info("Removing Background ...")

        for filename in os.listdir(self.input_dir):
            image_path = os.path.join(self.input_dir, filename)
            with open(image_path, 'rb') as f:
                image = f.read()
            
            output = remove_rembg(image)

            with open(os.path.join(self.no_bg_dir, filename), 'wb') as o:
                o.write(output)

        self.logger.succeed("Background Removal finished")
    
    def extract_keypoints(self):
        self.logger.info("Extracting 2D keypoints ...")
        for filename in os.listdir(self.input_dir):
            image_path = os.path.join(self.input_dir, filename)
            image = cv.imread(image_path)
            h, w = image.shape[:2]
            image_rgb = cv.cvtColor(image, cv.COLOR_BGR2RGB)
            results = self.pose.process(image_rgb)
            if not results.pose_landmarks:
                self.logger.error(f"Could not find any landmarks in the provided image: {image_path}")
            
            landmarks = results.pose_landmarks.landmark
            keypoints = []
            for lm in landmarks:
                x, y, vis = lm.x * w, lm.y * h, lm.visibility
                keypoints.extend([x, y, vis])

            openpose_json = {
                'version': 1.3,
                'people': [
                    {
                        'person_id': [-1],
                        'pose_keypoints_2d': keypoints,
                        'face_keypoints_2d': [],
                        'hand_left_keypoints_2d': [],
                        'hand_right_keypoints_2d': [],
                        "pose_keypoints_3d": [],
                        "face_keypoints_3d": [],
                        "hand_left_keypoints_3d": [],
                        "hand_right_keypoints_3d": []
                    }
                ]
            }

            file_no_ext = filename.split('.')[0]
            with open(os.path.join(self.no_bg_dir, f'{file_no_ext}_keypoints.json'), 'w') as json_out:
                json.dump(openpose_json, json_out)

        self.logger.succeed("Extracted keypoints and saved them on 'keypoints.json' files")

    def run_model(self):
        self.logger.info(f"Running 3D reconstruction model (ECON) ...")
        # This function assumes that the ECON environment is set up and the 'apps.infer' script is accessible.
        # You would typically clone the ECON repository and install its dependencies separately.
        # Example command for ECON, you might need to adjust paths and arguments:
        # For running ECON, you generally need:
        # 1. The ECON repository cloned.
        # 2. Its environment set up (e.g., conda env create -f environment.yaml).
        # 3. Pretrained checkpoints downloaded.
        # The input for ECON is usually a directory containing RGB images and optionally masks/keypoints.
        # In your case, 'self.no_bg_dir' contains the background-removed images and keypoints.
        # You would map these to ECON's expected input format.
        
        # Placeholder command - replace with actual ECON execution
        # The output mesh will be saved by ECON to a specified output directory.
        # For demonstration, we'll assume a dummy mesh is created.
        try:
            # Example: Run ECON's inference script. This needs to be adapted to your ECON setup.
            # command = [
            #     "python", "-m", "apps.infer",
            #     "-cfg", "/path/to/ECON/configs/econ.yaml", # Path to ECON's config file
            #     "-in_dir", self.no_bg_dir, # Your preprocessed input images
            #     "-out_dir", self.root_path # Output directory for ECON (where it saves the mesh)
            # ]
            # subprocess.run(command, check=True)

            # For now, create a dummy mesh for demonstration purposes
            self.logger.info("Creating a dummy mesh for demonstration as ECON is not integrated directly.")
            self.mesh = trimesh.creation.icosphere(subdivisions=2, radius=1.0)
            self.logger.succeed(f"Dummy mesh created.")

        except Exception as e:
            self.logger.error(f"Error running 3D reconstruction model: {e}")
            self.logger.error("Please ensure ECON is correctly set up and its executable path is correct if you intend to use it via subprocess.")
            sys.exit(1)

        self.logger.succeed(f"Model run process finished.")

    def save_mesh(self):
        self.logger.info(f"Saving generated mesh ...")
        if self.mesh is not None:
            self.mesh.export(self.mesh_path)
            self.logger.succeed(f"Saved the generated mesh in {self.mesh_path}")
        else:
            self.logger.error("No mesh to save. Run the model first.")
            sys.exit(1)

    def render_spinning_video(self):
        self.logger.info(f"Rendering the video ...")
        if self.mesh is None:
            self.logger.error("No mesh found to render. Run the model and save the mesh first.")
            sys.exit(1)

        # Create a scene
        scene = pyrender.Scene(bg_color=[0.0, 0.0, 0.0, 0.0], ambient_light=[0.3, 0.3, 0.3])

        # Add the mesh to the scene
        mesh_node = pyrender.Mesh.from_trimesh(self.mesh)
        scene.add(mesh_node)

        # Set up camera - orthographic for consistent scale
        camera = pyrender.OrthographicCamera(xmag=1.0, ymag=1.0)
        camera_pose = np.array([
            [1.0, 0.0, 0.0, 0.0],
            [0.0, 1.0, 0.0, 0.0],
            [0.0, 0.0, 1.0, 2.0], # Move camera back to view the mesh
            [0.0, 0.0, 0.0, 1.0]
        ])
        scene.add(camera, pose=camera_pose)

        # Set up light
        light = pyrender.DirectionalLight(color=[1.0, 1.0, 1.0], intensity=10.0)
        light_pose = np.eye(4)
        light_pose[:3, 3] = np.array([0, -1, 1])
        scene.add(light, pose=light_pose)

        # Create a renderer
        r = pyrender.OffscreenRenderer(self.video_size, self.video_size)

        frames = []
        for i in range(self.frames):
            # Rotate the mesh around the Y-axis
            angle = 2 * np.pi * i / self.frames
            rotation_y = trimesh.transformations.rotation_matrix(angle, [0, 1, 0])
            
            # Apply rotation to the mesh node
            # Note: pyrender operates on nodes, so we update the pose of the mesh_node
            scene.set_pose(mesh_node, rotation_y)

            color, depth = r.render(scene)
            frames.append(color)
        
        r.delete() # Clean up the renderer

        imageio.mimwrite(self.output_video, frames, fps=self.fps, macro_block_size=8)

        self.logger.succeed(f"Spinning video saved in {self.output_video}")

if __name__ == "__main__":
    print("Note: This file is not a runable file that has output. Just use the 'MeshFactory' class in another script or run the 'main.py' script and be careful the folder 'input_images' should exist including just images.")
