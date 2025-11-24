import bpy
import random


def clear_scene():
    """Clears all objects from the scene."""
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()


def create_tower(height=10, radius=2):
    """Creates a simple procedural tower of cubes."""
    for i in range(height):
        # Calculate size based on height (tapering)
        size = radius * (1 - (i / height) * 0.5)

        # Add a cube
        bpy.ops.mesh.primitive_cube_add(size=size, location=(0, 0, i * 1.0))

        # Random rotation for visual interest
        obj = bpy.context.active_object
        obj.rotation_euler[2] = random.uniform(0, 3.14)


def main():
    print("Starting Blender script...")
    clear_scene()

    print("Creating procedural tower...")
    create_tower(height=15, radius=3)

    # Join all objects into one
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.join()

    output_file = "procedural_tower.obj"
    print(f"Exporting to {output_file}...")
    # Export
    # Note: The command might vary slightly depending on Blender version (2.8+ vs 4.0+)
    # This uses the standard operator for recent versions
    try:
        bpy.ops.wm.obj_export(filepath=output_file)
    except AttributeError:
        # Fallback for older versions
        bpy.ops.export_scene.obj(filepath=output_file)

    print("Done!")


if __name__ == "__main__":
    main()
