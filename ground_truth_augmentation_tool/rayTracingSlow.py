import open3d as op3d
import matplotlib.pyplot as plt
import numpy as np
import utils
import math
from visualization import PCViewer

#Rays müssen gleichzeitig gemacht werden
#intensität kann über primitivUVs interpoliert werden



if __name__=="__main__":

    #Load Pointcloud with intensities

    pointcloudLoaded = utils.load_point_cloud_from_file(pc_path='velodyne_points/0000000000.bin')
    # pointcloud =  op3d.geometry.PointCloud()
    # pointcloud.points = op3d.utility.Vector3dVector(pointcloudLoaded[:, :3])
    # colors = np.column_stack((pointcloudLoaded[:, 3:], np.zeros_like(pointcloudLoaded[:, 3:]), np.zeros_like(pointcloudLoaded[:, 3:])))
    # pointcloud.colors = op3d.utility.Vector3dVector(colors)

    #Load mesh

    mesh = op3d.io.read_triangle_mesh("extractedObjects/object0Car.ply").translate([0, 5, 0]) # Lost
    mesh = op3d.t.geometry.TriangleMesh.from_legacy(mesh)

    scene = op3d.t.geometry.RaycastingScene()
    scene.add_triangles(mesh)
    
    origin = np.array([0, 0, 0])

    def euklidischeDistanz(point):
        return math.sqrt((point[0] - 0)**2 + (point[1] - 0)**2 + (point[2] - 0)**2)    


    # Raycasting and transforming points
    for x in range(len(pointcloudLoaded)):
        
        destination = np.array(pointcloudLoaded[x][:3])

        ray = op3d.core.Tensor(np.concatenate((origin, destination)).reshape(1, -1), dtype=op3d.core.Dtype.Float32)

        ans = scene.cast_rays(ray)


        if(ans['t_hit'].numpy() == '[inf]'):
            continue

        if(euklidischeDistanz(destination) - ans['t_hit'].numpy() < 0.1):
            continue
        
        else:
            hit = ans['t_hit'].isfinite()
            point = ray[hit][:,:3] + ray[hit][:,3:]*ans['t_hit'][hit].reshape((-1,1))
            
            point = point.numpy().reshape(-1)
            
            pointcloudLoaded[x] = np.concatenate((point, pointcloudLoaded[x][3:]))
    
    
    #pointcloud =  op3d.geometry.PointCloud()
    #pointcloud.points = op3d.utility.Vector3dVector(pointcloudLoaded[:, :3])
    #colors = np.column_stack((pointcloudLoaded[:, 3:], np.zeros_like(pointcloudLoaded[:, 3:]), np.zeros_like(pointcloudLoaded[:, 3:])))
    #pointcloud.colors = op3d.utility.Vector3dVector(colors)

    pcv = PCViewer(pointcloudLoaded)
    pcv.draw()
