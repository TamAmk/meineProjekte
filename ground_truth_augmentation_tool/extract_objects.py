from visualization import PCViewer
import numpy as np
import utils

if __name__ == "__main__":
    frame = '000000'
    point_cloud = utils.load_point_cloud_from_file(pc_path='pointclouds/'+frame+'.bin')
    labels = utils.gt_boxes_from_label(label_file='labels/'+frame+'.txt', calib='calib/'+frame+'.txt')
    num_objects = len(labels)

    pcv = PCViewer(point_cloud, labels)
    pcv.draw()

    corners_lidar = utils.boxes_to_corners_3d(labels)
    num_points_in_gt = -np.ones(num_objects, dtype=np.int32)

    object_points = []

    for k in range(num_objects):
        flag = utils.in_hull(point_cloud[:, 0:3], corners_lidar[k])
        object_points.append(point_cloud[flag])

    all_object_points = np.concatenate(object_points, axis=0)

    pcv = PCViewer(all_object_points, labels)
    pcv.draw()