import numpy as np
import pandas as pd
import os
from rdkit.Chem.Descriptors import ExactMolWt
from rdkit.Chem import MolFromSmiles


path = os.path.abspath(os.path.join('..', os.getcwd()))

glucose_data = pd.read_csv(os.path.join(path, 'data/Glucose_MeOH.csv'), delimiter=',',
                             skiprows=[0,1,2,3,4,5,6,7,8, 1039, 1040], usecols=['Mass', 'Kendrick Mass'])
# lines 1039 and 1040 in glucose_data and 1179, 1180 in dextrose_data are "***********"s
# so I had to skip them. First 9 lines contain comments
dextrose_data = pd.read_csv(os.path.join(path, 'data/Dextrose_MeOH.csv'), delimiter=',',
                             skiprows=[0,1,2,3,4,5,6,7,8, 1179, 1180], usecols=['Mass', 'Kendrick Mass'])

simulated_mols = pd.read_csv(os.path.join(path, 'data/generated_mols.txt'), skiprows=1)
simulated_weights = {}

for i in range(len(simulated_mols.index)):
    simulated_weights.update({ExactMolWt(MolFromSmiles(simulated_mols.iloc[i,0])) : 'False'})

# Drop rows containing NaNs
glucose_data.dropna(axis=0, how='any')
dextrose_data.dropna(axis=0, how='any')

# I made a dictionary, whose purpose will become obvious shortly
obs_masses = {}

for row in glucose_data.itertuples(index=True, name='Pandas'):
    # The CSV was a bit weird, ignore the [0], I just had to access a particular element of the tuple
    obs_masses.update({row[0][1]: 'False'}) # [1] refers to the Mass
    # I set the flag to 'False' to mean that it hasn't been found in our simulation
for row in dextrose_data.itertuples(index=True, name='Pandas'):
    obs_masses.update({getattr(row, 'Mass'): 'False'})

# Mass of simulated species calculated by RDKit might differ a bit from experimental obs
# The mass is that of negative ion, so we need to make a correction for an electron
error_margin = 0.01

# Update the flag for those observations which have been found to match our simulations
for obs in obs_masses.keys():
    for sim in simulated_weights.keys():
        if abs(sim - obs) <= error_margin:
            print(f'Observed mass: {obs} matches simulated structure with weight {sim}')
            obs_masses[obs] = True
            simulated_weights[sim] = True
            break

observed_count = 0
for val in obs_masses.values():
    if val == True:
        observed_count += 1
print(f'Out of total {len(obs_masses.keys())}, {observed_count} match simulations')

# Elements which are flagged 'False' aren't in the intersection set of simulation and experiment
matching_sims = 0
for val in simulated_weights.values():
    if val == True:
        matching_sims += 1

print(f'Out of {len(obs_masses.keys())} observed masses {len(obs_masses.keys()) - observed_count} seen in experiment were not in simulations')
print(f'Out of {len(simulated_weights.keys())} unique simulated masses {len(simulated_weights.keys()) - matching_sims} were not seen in experiments')