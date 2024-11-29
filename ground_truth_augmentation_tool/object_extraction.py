import numpy as np
import utils
import tracklets
import open3d as op3d
from visualization import PCViewer
import math

def winkelRechner(x, y):
    winkel_rad = math.atan2(y, x)
    winkel_deg = math.degrees(winkel_rad)
    return winkel_deg


def trianglemeshSpeichern():

    antwort = input("Safe the triangle mesh? (Y/N): ").strip().lower()
    if antwort == "y":
        return True
    elif antwort == "n":
        return False
    else:
        print("Ungültige Eingabe. Bitte antworte mit 'Ja' oder 'Nein'.")
        return trianglemeshSpeichern()

def iterativeClosestPoint(source, target):
    
    target_cloud = op3d.geometry.PointCloud()
    target_cloud.points = op3d.utility.Vector3dVector(target[:, :3])

    max_correspondence_distance = 0.1

    trans_init = np.asarray([[1.0, 0.0, 0.0, 0.0],
                                        [0.0, 1.0, 0.0, 0.0],
                                        [0.0, 0.0, 1.0, 0.0], 
                                        [0.0, 0.0, 0.0, 1.0]], dtype=np.float32)
    
    estimation = op3d.pipelines.registration.TransformationEstimationPointToPoint()

    criteria = op3d.pipelines.registration.ICPConvergenceCriteria(relative_fitness=0.0000001,
                                       relative_rmse=0.0000001,
                                       max_iteration=30)

    registration_icp = op3d.pipelines.registration.registration_icp(source, target_cloud, max_correspondence_distance, 
                                                            trans_init, estimation, criteria)
    
    source.transform(registration_icp.transformation)

    return source


def rotate_points_along_z(points, angle):
              
        cosa = np.cos(angle[0][2])
        sina = np.sin(angle[0][2])

        zeros = np.zeros_like(cosa)
        ones = np.ones_like(cosa)
        rot_matrix = np.stack((
             cosa, sina, zeros,
             -sina, cosa, zeros,
             zeros, zeros, ones
        ), axis=0).reshape(3,3).astype(np.float32)

        points = np.expand_dims(points, axis=0)
        points_rot = np.matmul(points[:, :, 0:3], rot_matrix)

        points_rot = np.concatenate((points_rot, points[:, :, 3:]), axis=-1)

        return points_rot

def rotate_points_along_z_BoundingBox(points, angle):
              
        cosa = np.cos(angle)
        sina = np.sin(angle)

        zeros = np.zeros_like(cosa)
        ones = np.ones_like(cosa)
        rot_matrix = np.stack((
             cosa, sina, zeros,
             -sina, cosa, zeros,
             zeros, zeros, ones
        ), axis=0).reshape(3,3).astype(np.float32)

        points = np.expand_dims(points, axis=0)
        points_rot = np.matmul(points[:, :, 0:3], rot_matrix)

        return points_rot

if __name__=="__main__":

    # Parsing tracklets

    trackletsXML = tracklets.parse_xml("tracklet_labels.xml") #

    boundingBoxCorners = []

    pointcloudsObjects = []

    angles = []

    rotationAngels = []

    for i in range(len(trackletsXML)):

        currentTracklet = trackletsXML[i]
        sizeH = currentTracklet.size[0]
        sizeW = currentTracklet.size[1]
        sizeL = currentTracklet.size[2]

        firstFrame = currentTracklet.first_frame

        currentAngles = []
        currentRotationAngles = []


        pointcloudsObjects.append([currentTracklet.object_type])
        print("Object: " + pointcloudsObjects[i][0] + str(i) + " started.")
        for j in range(len(currentTracklet.trans)):
            
            
            frame = str(firstFrame).zfill(10)
            point_cloud = utils.load_point_cloud_from_file(pc_path='velodyne_points/'+frame+'.bin') #
            firstFrame += 1                

            translation = currentTracklet.trans[j]
            rotation = currentTracklet.rot[j]

            loc = np.reshape(translation, (1, 3))
            l = np.reshape(np.array(sizeL), (1, 1))
            w = np.reshape(np.array(sizeW), (1, 1))
            h = np.reshape(np.array(sizeH), (1, 1))
            rot = np.reshape(rotation, (1, 3))
            loc[:, 2] += h[:, 0] / 2
            current_object = np.concatenate([loc, l, w, h, rot], axis=1)

            #print(current_object)

            currentRotationAngles.append(rot[0][2])

            corners_lidar = utils.boxes_to_corners_3d(current_object)
            #
            #print(corners_lidar)
            currentAngles.append(winkelRechner(loc[0][0], loc[0][1]))
            
            object_points = []

            pcv = PCViewer(point_cloud, current_object)
            pcv.draw() 

            for k in range(len(current_object)):
                flag = utils.in_hull(point_cloud[:, 0:3], corners_lidar[k])
                if np.sum(flag) >= 100:
                    object_points.append(point_cloud[flag])
                
            if len(object_points) == 0:
                continue

            all_object_points = np.concatenate(object_points, axis=0)
            

            newObjectPoints = all_object_points

            newObjectPoints[:, :3] -= translation

            
            newObjectPoints = rotate_points_along_z(newObjectPoints, -rot)
            newObjectPoints = np.squeeze(newObjectPoints)
     

            current_object = np.concatenate([[[0, 0, 0]], l, w, h, [[0, 0, 0]]], axis=1)
            corners_lidar = utils.boxes_to_corners_3d(current_object) 

            pcv = PCViewer(newObjectPoints, current_object)
            pcv.draw()   
            
            pointcloudsObjects[i].append(newObjectPoints)

        angles.append(currentAngles)  
        rotationAngels.append(np.mean(np.degrees(currentRotationAngles)))

        
            
        print("Object: " + pointcloudsObjects[i][0] + str(i) + " ended.")

    #print(rotationAngels)    
    angles = np.array([[np.min(inner_array), np.max(inner_array)] for inner_array in angles])

    for i in range (len(pointcloudsObjects)):

        trackletData = trackletsXML[i]
        sizeH = trackletData.size[0]
        sizeW = trackletData.size[1]
        sizeL = trackletData.size[2]
        l = np.reshape(np.array(sizeL), (1, 1))
        w = np.reshape(np.array(sizeW), (1, 1))
        h = np.reshape(np.array(sizeH), (1, 1))


        if len(pointcloudsObjects[i]) <= 1:
            continue
        currentPointcloud = op3d.geometry.PointCloud()
        currentPointcloud.points = op3d.utility.Vector3dVector(pointcloudsObjects[i][1][:, :3])
        colors = pointcloudsObjects[i][1][:, 3:]
        currentPointcloud.colors = op3d.utility.Vector3dVector(np.column_stack((colors, np.zeros_like(colors), np.zeros_like(colors))))

        for j in range(len(pointcloudsObjects[i])-2):

            currentPointcloud = iterativeClosestPoint(currentPointcloud, pointcloudsObjects[i][j+2])
            helper = np.concatenate((np.array(currentPointcloud.points), pointcloudsObjects[i][j+2][:, :3]), axis=0)
            currentPointcloud.points = op3d.utility.Vector3dVector(helper)
            colorHelper = np.concatenate((np.array(currentPointcloud.colors), np.column_stack((pointcloudsObjects[i][j+2][:, 3:], np.zeros_like(pointcloudsObjects[i][j+2][:, 3:]), np.zeros_like(pointcloudsObjects[i][j+2][:, 3:])))), axis=0)
            currentPointcloud.colors = op3d.utility.Vector3dVector(colorHelper)

            #farben = np.asarray(currentPointcloud.colors)
            #print(farben)

            #punkte = np.asarray(currentPointcloud.points)
            #print(punkte)
            
            #test = np.concatenate((punkte, farben[:, 0].reshape(-1, 1)), axis=1)
            #print(test)

            #if j == 0 or j == 15 or j == 29:
                #pcv = PCViewer(test)
                #pcv.draw() 

        radians = np.radians(rotationAngels[i])

        rotationMatrix = np.array([[np.cos(radians), -np.sin(radians), 0],
                                    [np.sin(radians), np.cos(radians), 0],
                                    [0, 0, 1]])


        cornersCurrentPointcloud = np.concatenate([[[0, 0, 0]], l, w, h, np.reshape(radians, (1, 1))], axis=1)
        #cornersCurrentPointcloud = utils.boxes_to_corners_3d(cornersCurrentPointcloud)

        currentPointcloud.rotate(rotationMatrix, [0, 0, 0])
        #cornersCurrentPointcloud = rotate_points_along_z_BoundingBox([[cornersCurrentPointcloud]], radians).squeeze()

        print(cornersCurrentPointcloud)

        print("Object: " + pointcloudsObjects[i][0] + str(i) + " done.")

        currentPointcloud.estimate_normals()
        currentPointcloud.orient_normals_consistent_tangent_plane(100)

        if pointcloudsObjects[i][0] == "Car" or pointcloudsObjects[i][0] == "Van":

            mesh, densities = op3d.geometry.TriangleMesh.create_from_point_cloud_poisson(currentPointcloud, depth=9)
            densities = np.asarray(densities)
            vertices_to_remove = densities < np.quantile(densities, 0.02)
            mesh.remove_vertices_by_mask(vertices_to_remove)
            mesh = mesh.filter_smooth_simple(10)
        else:
            distances = currentPointcloud.compute_nearest_neighbor_distance()
            avg_dist = np.mean(distances)
            radius = 1.5 * avg_dist
            mesh = op3d.geometry.TriangleMesh.create_from_point_cloud_ball_pivoting(currentPointcloud, op3d.utility.DoubleVector([radius, radius * 2]))

        op3d.visualization.draw_geometries([mesh], mesh_show_back_face=True)

        print(cornersCurrentPointcloud)

        pcv = PCViewer(np.asarray(currentPointcloud.points), cornersCurrentPointcloud)
        pcv.draw()

        if trianglemeshSpeichern() == False:
            continue

        op3d.io.write_triangle_mesh("extractedObjects" + pointcloudsObjects[i][0] + "/objectMin"+ str(angles[i][1]) +str(i) + "Max" + str(angles[i][0]) + pointcloudsObjects[i][0] + ".ply", mesh)
        filename = "objectMin"+ str(angles[i][1]) +str(i) + "Max" + str(angles[i][0]) + pointcloudsObjects[i][0] + ".txt"
        np.savetxt("BoundingBoxes/"+filename, cornersCurrentPointcloud)
