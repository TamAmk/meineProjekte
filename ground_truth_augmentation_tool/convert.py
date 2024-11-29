import open3d as op3d
import pickle as pck
import os

    

if __name__=="__main__":
    
    folder = "extractedObjectsCar/"

    meshes = os.listdir(folder)

    for mesh in meshes:
        mesh_path = os.path.join(folder, mesh)

        readMesh = op3d.io.read_triangle_mesh(mesh_path)

        tensorMesh = op3d.t.geometry.TriangleMesh.from_legacy(readMesh)

        with open("extractedObjectsCarAsPickle/"+mesh+'.pkl', 'wb') as datei:
            pck.dump(tensorMesh, datei)

            