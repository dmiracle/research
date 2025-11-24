# Best Python 3D Modeling Libraries (2024-2025)

This document summarizes the top 3 Python libraries for 3D modeling, processing, and visualization, based on features, performance, and ease of use.

## Top 3 Libraries

| Library | Best For | License | Key Features |
| :--- | :--- | :--- | :--- |
| **Open3D** | 3D Data Processing & ML | MIT | Point cloud processing, scene reconstruction, 3D ML support (PyTorch/TensorFlow), visualization. |
| **Trimesh** | Mesh Manipulation | MIT | Loading/exporting many formats, mesh analysis, boolean operations, lightweight. |
| **Blender (bpy)** | Full 3D Creation | GPL | Complete 3D suite (modeling, sculpting, animation, rendering), procedural generation. |

---

## 1. Open3D

**Open3D** is a modern library for 3D data processing. It is highly optimized and supports rapid development.

### Installation
```bash
pip install open3d
```

### Basic Usage (Read and Visualize a Point Cloud)
```python
import open3d as o3d
import numpy as np

# Create a point cloud
pcd = o3d.geometry.PointCloud()
pcd.points = o3d.utility.Vector3dVector(np.random.rand(100, 3))

# Visualize
o3d.visualization.draw_geometries([pcd])
```

---

## 2. Trimesh

**Trimesh** is pure Python (with numpy) and is excellent for loading and manipulating triangular meshes. It's great for "glue" code in 3D pipelines.

### Installation
```bash
pip install trimesh
```

### Basic Usage (Load and Show Mesh)
```python
import trimesh

# Load a mesh (example: a primitive)
mesh = trimesh.creation.box()

# Show the mesh
mesh.show()

# Get some stats
print(f"Vertices: {len(mesh.vertices)}, Faces: {len(mesh.faces)}")
```

---

## 3. Blender Python API (bpy)

**Blender** is the industry-standard open-source 3D suite. Its Python API (`bpy`) allows you to automate almost everything in Blender.
*Note: Typically run inside Blender, but can be built as a module.*

### Installation
Usually comes with Blender. To use it, run your script with Blender:
```bash
blender --background --python my_script.py
```

### Basic Usage (Create a Cube)
```python
import bpy

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create a cube
bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 0))

# Export to OBJ
bpy.ops.wm.obj_export(filepath="my_cube.obj")
```

## Honorable Mentions
- **PyVista**: Excellent high-level interface for VTK, great for scientific visualization.
- **CadQuery**: Best for parametric/CAD modeling (code-based CAD).
- **MeshLib**: High-performance mesh processing.
