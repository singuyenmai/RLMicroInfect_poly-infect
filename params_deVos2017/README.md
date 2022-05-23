Data files:

- Interaction matrix growth rate: `GR_3.npy` - ordered according to phylogeny, `i​`
- Interaction matrix maximum reached OD: `MaxOD_3.npy` - ordered according to phylogeny, `i​`
- Growth rates in isolation: `mean_GR_spentHRs.npy` - ordered [1:96]
- Maximum reached OD in isolation: `mean_maxOD_spentHRs.npy` - ordered [1:96] 

Metadata files:

- Full list of 96 strains: `UTI_bacteria.original.tsv`
- List of 72 selected strains in the interaction matrices GR_3 & MaxOD_3: `UTI_bacteria.selected.tsv`, created by running Python script file `make_selected_list.py`
- List of strain numbers ordered according to indices in interaction matrices GR_3 & MaxOD_3: `UTI_bacteria.ordered_selected.txt`

Matrices GR_3 & MaxOD_3:

- Matrix indices ordered by strain number
- Strain number corresponds to the column 'strain_numbered' in file `UTI_bacteria.original.tsv`
- X-axis: acceptor (grown in spent medium of donor)
- Y-axis: donor (made spent medium from)
- Strain number order: `i =[56 2 91 42 59 53 10 62 80 34 76 22 18 19 16 45 68 36 74 79 4 44 23 9 5 21 30 51 87 41 58 92 54 72 83 37 25 69 60 84 78 63 13 82 90 1 7 33 64 14 47 11 66 6 31 71 35 20 3 61 28 81 88 38 46 43 65 55 15 50 75 77]` - stored as lines in file `UTI_bacteria.ordered_selected.txt`