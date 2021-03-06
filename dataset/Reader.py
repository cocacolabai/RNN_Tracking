import os
import sys
import config
import numpy as np
import tensorflow as tf
import cv2
import sys

FLAGS = tf.app.flags.FLAGS

class Reader:
    def __init__(self, data_pattern):
        self.zip_options = tf.python_io.TFRecordOptions(tf.python_io.TFRecordCompressionType.GZIP)
        self.data_pattern = data_pattern
        self.files = np.array(tf.gfile.Glob(self.data_pattern))
        self.init_dataset()

    def get_random_example(self):
        frame_gt_batch, frame_x_batch, ass_matrix_gt_batch, e_vector_gt_batch, file_name = self.read_tfrecord(np.random.choice(self.files))
        return frame_gt_batch, frame_x_batch, ass_matrix_gt_batch, e_vector_gt_batch, file_name

    def read_tfrecord(self, path):
        frame_gt_batch = []
        frame_x_batch = []
        
        ass_matrix_gt_batch = []
        e_vector_gt_batch = []
        
        #index = 0
        #print("path = " + path)
        for string_record in tf.python_io.tf_record_iterator(path=path):
            example = tf.train.Example()
            example.ParseFromString(string_record)
            
            frame_gt, frame_mat, ass_matrix_gt, e_vector_gt = self.feature_decode(example)
            
            frame_gt_batch.append(frame_gt)
            frame_x_batch.append(frame_mat)
            
            ass_matrix_gt_batch.append(ass_matrix_gt)
            e_vector_gt_batch.append(e_vector_gt)
            
            #index += 1
        
        
        #FLAGS.batch_size = index
        #det_x = self.gen_det_x(np.asarray(frame_det_batch)) #reshape the detection input to [batch_size][x,...,y...,w...,h...] batch_size * 4 * 64 tensor
        #sys.exit(0)
        return frame_gt_batch, frame_x_batch, ass_matrix_gt_batch, e_vector_gt_batch, path
        
    def feature_decode(self,example):

        #decode tracking_gt
        frame_gt = example.features.feature['frame_gt'].float_list.value
        
        ass_matrix_gt = example.features.feature['ass_matrix_gt'].float_list.value
        # np.savetxt('numpy_out.txt', np.array(ass_matrix_gt).reshape(257,82), delimiter=',')
        # sys.exit(0)
        
        e_vector_gt = example.features.feature['e_vector_gt'].float_list.value
        
        #decode concated mat
        frame_mat_shape = example.features.feature['frame_concate_mat_shape'].int64_list.value
        frame_mat_string = example.features.feature['frame_concat_mat'].bytes_list.value[0]
        frame_mat = np.fromstring(frame_mat_string, dtype=np.float32).reshape(frame_mat_shape)
        
        # a = np.array(frame_gt).reshape(9,9,35)
        # for i in range(9):
            # for j in range(9):
                # if a[i][j][0] > 0:
                    # print("a[%d][%d]: (%f,%f,%f,%f,%f)" % (i,j,a[i][j][0],a[i][j][1],a[i][j][2],a[i][j][3],a[i][j][4]))
        
        # cv2.imshow("Image", frame_mat[:,:,0:3].copy())
        # cv2.imshow("Mask", frame_mat[:,:,3].copy())
        # cv2.waitKey(0)
        
        return frame_gt, frame_mat, ass_matrix_gt, e_vector_gt
        
    def parse_tfr_filename(self, path):
        filename, ext = os.path.splitext(path)
        path, file = os.path.split(filename)
        return "{}/{}.tfr".format(path, file), np.array([int(file.split('_')[-1])])

    def normalize_images(self, data) -> np.ndarray:
        return data / 255

    def init_dataset(self):
        np.random.shuffle(self.files)
        self.iterator = np.nditer(self.files)
