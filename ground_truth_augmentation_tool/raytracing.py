import open3d as op3d
import numpy as np
import utils
import random
import os
from visualization import PCViewer
import re
import matplotlib.pyplot as plt
from scipy.stats import norm
import pickle


def platzierungWinkelbereich(minWinkel, maxWinkel):

    mittelWinkel = random.uniform(minWinkel, maxWinkel)
    radius = random.uniform(4, 6)
    mittelWinkel = np.deg2rad(mittelWinkel)

    x = radius * np.cos(mittelWinkel)
    y = radius * np.sin(mittelWinkel)

    return x, y

def rayTracing(pointcloud, amountObjects, amountTries, objectClass):
    #Load Pointcloud

    pointcloudLoaded = utils.load_point_cloud_from_file(pc_path='velodyne_points/'+pointcloud)

    boxes = []

    #Load mesh and placing (x Achse vor(+) und zurück(-), y Achse links(+) rechts(-), z Achse hoch(+) runter(-))

    for y in range(0, amountObjects):

        folderPath = "extractedObjects" + objectClass
        meshes = os.listdir(folderPath)

        randomMesh = random.choice(meshes)

        folderPathPickle = "extractedObjectsCarAsPickle/"
        pickleMeshes = os.listdir(folderPathPickle)
        randomPickleMesh = random.choice(pickleMeshes)

        with open(folderPathPickle+randomPickleMesh, 'rb') as datei:
            loadedTensorMesh = pickle.load(datei)


        boundingBoxData = randomMesh.replace(".ply", ".txt")



        with open("BoundingBoxes/"+boundingBoxData, 'r') as file:
            content = file.read()
            boundingBox = content.split()

        boundingBox = np.asarray([float(element) for element in boundingBox]).reshape(1, -1)

        print(boundingBox)

        boxPoints = utils.boxes_to_corners_3d(boundingBox).squeeze()

        print(boxPoints)


        mesh = op3d.io.read_triangle_mesh(folderPath+"/"+randomMesh)
        min_value = float(re.search(r"Min(-?[\d.]+)", randomMesh).group(1))
        max_value = float(re.search(r"Max(-?[\d.]+)", randomMesh).group(1))

        boxHeightCenter = np.abs(np.min(boxPoints[:, 2]) - np.max(boxPoints[:, 2])) / 2
        highestPoint = np.max(pointcloudLoaded[:, 2])
        lowestPoint = np.min(pointcloudLoaded[:, 2])

        #Hier wird ein Platz für das Mesh gesucht, falls einer gefunden wird, wird dieser dahin platziert

        for x in range(0, amountTries):

            raytrace = False

            meshX, meshY = platzierungWinkelbereich(min_value, max_value)

            array = np.array([meshX, meshY, -boxHeightCenter])
            mesh.translate(array)
            loadedTensorMesh.translate(array)
            boxPoints += array 
            #print(boxPoints) 
            #print(np.asarray(mesh.get_center()))
            #meshBoundingBox = mesh.get_axis_aligned_bounding_box()
            #boxPoints = np.asarray(meshBoundingBox.get_box_points())


            boxPointsMittelwertZKoordinate = np.mean(boxPoints[:, 2])
            boxPoints[boxPoints[:, 2] >= boxPointsMittelwertZKoordinate, 2] = highestPoint
            boxPoints[boxPoints[:, 2] <= boxPointsMittelwertZKoordinate, 2 ] = lowestPoint   

            

            flag = utils.in_hull(pointcloudLoaded[:, :3], boxPoints)
            


            zAchsenWerte = pointcloudLoaded[:, 2][flag]

            mittelwertZAchse = np.mean(zAchsenWerte)
            standardAbweichung = np.std(zAchsenWerte)

            #Plot für Debugging Zwecke

            #plt.hist(zAchsenWerte, bins=30)
            #xmin, xmax = plt.xlim()
            #x = np.linspace(xmin, xmax, 100)
            #p = norm.pdf(x, mittelwertZAchse, standardAbweichung)

            #plt.plot(x, p, 'k', linewidth=2)
            #title = "Fit results: Mittelwert = %.2f,  Standardabweichung = %.2f" % (mittelwertZAchse, standardAbweichung)
            #plt.title(title)
            
            #plt.show()


            if not np.any(flag) or 100 < np.sum(zAchsenWerte > mittelwertZAchse + 0.1) or standardAbweichung > 0.1:
                mesh.translate(-array)
                loadedTensorMesh.translate(-array)
                continue
            else:
                raytrace = True
                boundingBox[:, :3] = array
                break

        
        # Falls ein Platz gefunden wurde für das Mesh findet hier das Raytracing statt
        
        if(raytrace):

            boxes.append(boundingBox.squeeze()) 
            
            #mesh = op3d.t.geometry.TriangleMesh.from_legacy(mesh)

            scene = op3d.t.geometry.RaycastingScene()
            scene.add_triangles(loadedTensorMesh)

            origin = np.zeros((len(pointcloudLoaded), 3))

            destination = np.asarray(pointcloudLoaded[:, :3])

            rayVectors = np.concatenate((origin, destination), axis=1)
            
            
            ray = op3d.core.Tensor(rayVectors, dtype=op3d.core.Dtype.Float32)

            ans = scene.cast_rays(ray)

            #mesh = op3d.t.geometry.TriangleMesh.to_legacy(mesh)

            ray = ray.numpy()
            hit = ans['t_hit'].numpy() < 1

            primitiveIDs = ans['primitive_ids'].numpy()[hit]

            triangleIDs = np.asarray(mesh.triangles)[primitiveIDs]

            colors = np.asarray(mesh.vertex_colors)[triangleIDs.flatten(), 0].reshape((-1, 3))

            primitiveUVs = ans['primitive_uvs'].numpy()[hit]
            
            primitiveUVs = np.concatenate((primitiveUVs, 1 - primitiveUVs.sum(axis=1, keepdims=True)), axis=1)

            colors = colors * primitiveUVs

            colors = np.sum(colors, axis=1)
            
            pointcloudLoaded[hit, :3] = pointcloudLoaded[hit, :3] * np.repeat(ans['t_hit'].numpy()[hit].reshape(-1, 1), 3, axis=1)
            pointcloudLoaded[hit, 3:] = colors.reshape(-1, 1)

    #print(boxes)

    if not(len(boxes) == 0):
        pcv = PCViewer(pointcloudLoaded, np.asarray(boxes))
        pcv.draw()
    else:
        pcv = PCViewer(pointcloudLoaded)
        pcv.draw()


if __name__=="__main__":

    rayTracing("0000000000.bin", 5, 20, "Car")





    

    

