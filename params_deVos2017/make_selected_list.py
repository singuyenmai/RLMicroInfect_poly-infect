import pandas as pd

origin = pd.read_csv("UTI_bacteria.original.tsv", sep="\t")

# ordered list of strains included in growth and interaction matrices
with open("UTI_bacteria.ordered_selected.txt") as f:
    selected_list = [line.rstrip('\n') for line in f]

# extract the strains
output = origin.loc[origin['strain_numbered'].isin(selected_list), :].copy()

# order the selected strains as in growth and interaction matrices
df_mapping = pd.DataFrame({'strain_numbered': selected_list})
sort_mapping = df_mapping.reset_index().set_index('strain_numbered')

output['strain_index'] = output['strain_numbered'].map(sort_mapping['index'])
output.sort_values('strain_index', inplace=True)

# abbreviations for genus/species names
abb_dict = {"Enterococcus": "Ent", 
            "Escherichia": "Ecoli", 
            "Klebsiella": "KECS", "Enterobacter": "KECS", 
            "Citrobacter": "KECS", "Serratia": "KECS", "Pantoea": "KECS",
            "Proteus": "Pm",
            "Pseudomonas": "Ps", 
            "Staphylococcus": "St",
            "Morganella": "Mm"}

output['abbrev'] = output['species'].map(lambda x: abb_dict[x.split(" ")[0]])

output.to_csv("UTI_bacteria.selected.tsv", sep="\t", index=False)