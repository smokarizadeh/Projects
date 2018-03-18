import pandas as pd
from rdkit import Chem
#from rdkit.Chem import Tools
from rdkit.Chem import AllChem
from rdkit.Chem import Descriptors
import numpy as np
#import matplotlib.pyplot as plt
import os


result = {}
counter = 0
dictt = { 1.0 : 0 , 1.5 : 1 , 2.0:2}
all = []
all2 = []
atom2Id = {}
train = pd.read_csv('GDB13_Subset-ABCDEFGH.smi',header=None,skiprows=0)
for iii in range(len(train)):
        counter += 1
        smile = train.iloc[iii][0]
        try:
            #print (counter)
            mol = Chem.MolFromSmiles(smile)
            mol = Chem.AddHs(mol)
            adj = Chem.GetAdjacencyMatrix(mol)*1.0
            #mol = AllChem.MMFFGetMoleculeProperties(mol)
            #AllChem.Compute2DCoords(mol)
            #AllChem.EmbedMolecule(mol,AllChem.ETKDG())
            #open('temp_%s.sdf'%(counter-1),'w').write(Chem.MolToMolBlock(mol));plt.show()
            #Chem.MolFromMolBlock(mol)
            #bond_order = np.zeros(shape = adj.shape + (3,))
##            atoms = list(
##                        map(lambda x: mol.GetMMFFAtomType(x),
##                            range(len(adj))
##                             )
##                        )
            atoms = [ mol.GetAtomWithIdx(i).GetAtomicNum() for i in range(len(adj))]
            bonds = np.argwhere(np.triu(adj)==1)
            #associated_words = list(map(lambda x : tuple(sorted(map(lambda x : atoms[x],x))) , bonds))
            atoms2 = []
            for i in range(len(adj)):
                neighbours_i =     np.concatenate(np.argwhere(adj[i]==1))
                bond_i = list(map(lambda x : mol.GetBondBetweenAtoms(i,int(x)).GetBondTypeAsDouble()  ,neighbours_i))
                neighbours_i = list(map(lambda x : atoms[x],neighbours_i))
                #for bond_,atom_ in zip(bond_i, neighbours_i):
                temp = [atoms[i],]
                for j in np.argsort(neighbours_i):
                        bond_ = bond_i[j]
                        atom_ = neighbours_i[j]
                        temp += [bond_,atom_]
                atoms2 += [tuple(temp),]
            atomsIndex = []
            for i in range(len(adj)):
                neighbours_i =     np.concatenate(np.argwhere(adj[i]==1))
                bond_i = list(map(lambda x : mol.GetBondBetweenAtoms(i,int(x)).GetBondTypeAsDouble()  ,neighbours_i))
                neighbours_i_old = list(map(lambda x : atoms[x],neighbours_i))
                neighbours_i = list(map(lambda x : atoms2[x],neighbours_i))
                #for bond_,atom_ in zip(bond_i, neighbours_i):
                temp = [atoms2[i],]
                for j in np.argsort(neighbours_i_old):
                        bond_ = bond_i[j]
                        atom_ = neighbours_i[j]
                        temp += [bond_,atom_]
                try:
                        x = atom2Id[tuple(temp)]
                except :
                        atom2Id[tuple(temp)] = len(atom2Id)
                atomsIndex += [atom2Id[tuple(temp)],]
            #associated_words = [ [mol.GetAtomWithIdx(i).GetAtomicNum(),]+\
            #                     sorted([(x.GetAtomicNum(),x.GetBonds()) for x in mol.GetAtomWithIdx(i).GetNeighbors()],reverse=True) \
            #                     for i in range(len(adj))]
            associated_words = list(map(lambda x : tuple(sorted(map(lambda x : atomsIndex[x],x))) , bonds))    
            #bond_pairs = 
            all2 += associated_words
##            for i in range(len(adj)):
##                for j in range(len(adj)):
##                    if adj[i,j] == 1:
##                        bond_type = mol.GetBondBetweenAtoms(i,j).GetBondTypeAsDouble()
##                        if bond_type in dictt:
##                            index = dictt[bond_type]
##                            bond_order[i,j,index] = 1
##                            bond_order[j,i,index] =  bond_order[i,j,index]
##            temp = np.concatenate([np.stack([adj,dist],-1),bond_order],-1)

        except :
            print ('errror',counter,smile);
            print (len(all2),len(tuple(set(all2))),len(atom2Id))
np.save('atom2Id.npy', atom2Id)
np.save('bonds2.npy.zip',all2)