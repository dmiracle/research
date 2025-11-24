import open3d as o3d
import numpy as np

def main():
    print("Generating random point cloud...")
    # 1. Create a random point cloud
    pcd = o3d.geometry.PointCloud()
    # Generate 1000 random points
    points = np.random.rand(1000, 3)
    pcd.points = o3d.utility.Vector3dVector(points)

    # Add colors (random RGB)
    colors = np.random.rand(1000, 3)
    pcd.colors = o3d.utility.Vector3dVector(colors)

    print(f"Created point cloud with {len(pcd.points)} points.")

    # 2. Voxel downsampling (simple processing)
    print("Downsampling...")
    downpcd = pcd.voxel_down_sample(voxel_size=0.05)
    print(f"Downsampled point cloud has {len(downpcd.points)} points.")

    # 3. Estimate normals
    print("Estimating normals...")
    downpcd.estimate_normals(search_param=o3d.geometry.KDTreeSearchParamHybrid(radius=0.1, max_nn=30))

    # 4. Visualization
    print("Visualizing... (Close window to exit)")
    # Draw geometries
    # We'll show the coordinate frame as well
    mesh_frame = o3d.geometry.TriangleMesh.create_coordinate_frame(size=0.6, origin=[0, 0, 0])
    o3d.visualization.draw_geometries([downpcd, mesh_frame], 
                                      window_name="Open3D Example",
                                      width=800,
                                      height=600)

if __name__ == "__main__":
    main()
