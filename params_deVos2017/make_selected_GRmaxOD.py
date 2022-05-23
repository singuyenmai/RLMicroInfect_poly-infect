import numpy as np

# ordered list of strains included in growth and interaction matrices
with open("UTI_bacteria.ordered_selected.txt") as f:
    selected_list = [int(line.rstrip('\n')) - 1 for line in f]

mat_GR = np.load("mean_GR_spentHRs.npy")
mat_maxOD = np.load("mean_maxOD_spentHRs.npy")

mat_GR_selected = mat_GR[:, selected_list]
mat_maxOD_selected = mat_maxOD[:, selected_list]

np.save("mean_GR_spentHRs.selected.npy", mat_GR_selected)
np.save("mean_maxOD_spentHRs.selected.npy", mat_maxOD_selected)