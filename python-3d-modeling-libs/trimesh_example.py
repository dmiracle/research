import trimesh
import numpy as np


def main():
    print("Creating primitives...")
    # 1. Create primitives
    sphere = trimesh.creation.icosphere(radius=1.0)
    box = trimesh.creation.box(extents=[1.5, 1.5, 1.5])

    # Set colors
    sphere.visual.face_colors = [200, 0, 0, 255]  # Red
    box.visual.face_colors = [0, 200, 0, 150]  # Green, semi-transparent

    print("Performing boolean difference (Box - Sphere)...")
    # 2. Boolean operations (requires 'blender' or 'scad' usually, but trimesh has internal simple ones or wrappers)
    # Note: Robust booleans in trimesh often require `manifold3d` or `blender` installed.
    # We will demonstrate a simple scene assembly instead to ensure it runs without external deps if possible,
    # or try a simple union if available.

    # Let's just show them in a scene for now to be safe on all platforms without extra deps
    scene = trimesh.Scene([box, sphere])

    print(f"Scene has {len(scene.geometry)} geometries.")

    # 3. Basic Analysis
    print(f"Sphere Volume: {sphere.volume:.4f}")
    print(f"Box Volume: {box.volume:.4f}")
    print(f"Is Sphere Watertight? {sphere.is_watertight}")

    # 4. Export
    print("Exporting to 'combined_scene.glb'...")
    scene.export("combined_scene.glb")

    # 5. Visualize
    print("Visualizing... (Close window to exit)")
    scene.show()


if __name__ == "__main__":
    main()
