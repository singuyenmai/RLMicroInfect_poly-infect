import scipy.io as sio
import numpy as np
import sys

input_file = sys.argv[1]
filename = input_file.rsplit("/", 1)[1]
filename = filename.rsplit(".", 1)[0]

data = sio.loadmat(input_file)
mat_key = list(data.keys())[-1]
data_mat = data[mat_key]

np.save(filename + ".npy", data_mat)