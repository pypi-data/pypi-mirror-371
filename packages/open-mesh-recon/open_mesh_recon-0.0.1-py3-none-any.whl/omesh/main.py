import mesh_generation as mg

mesh_factory = mg.MeshFactory(mesh_id_min=10, mesh_id_max=20) # For device you can just provide 'cpu' or 'cuda'. Else it will auto-detect.

mesh_factory.remove_background()

mesh_factory.extract_keypoints()

mesh_factory.run_model()

mesh_factory.save_mesh()

mesh_factory.render_spinning_video()