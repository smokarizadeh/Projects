import numpy as np
import pandas as pd
import xgboost as xgb
import matplotlib.pyplot as plt
# calculate the volume of the structure

train  = pd.read_csv('train.csv')
train2 = pd.read_csv('train_data_features2.csv')
test = pd.read_csv('test.csv')
test2 = pd.read_csv('test_data_features2.csv')

train2['id'] = train2['5']

def get_vol(a, b, c, alpha, beta, gamma):
    """
    Args:
        a (float) - lattice vector 1
        b (float) - lattice vector 2
        c (float) - lattice vector 3
        alpha (float) - lattice angle 1 [radians]
        beta (float) - lattice angle 2 [radians]
        gamma (float) - lattice angle 3 [radians]
    Returns:
        volume (float) of the parallelepiped unit cell
    """
    return a*b*c*np.sqrt(1 + 2*np.cos(alpha)*np.cos(beta)*np.cos(gamma)
                           - np.cos(alpha)**2
                           - np.cos(beta)**2
                           - np.cos(gamma)**2)

# convert lattice angles from degrees to radians for volume calculation
lattice_angles = ['lattice_angle_alpha_degree', 'lattice_angle_beta_degree',
                  'lattice_angle_gamma_degree']
for lang in lattice_angles:
    train[lang+'_r'] = np.pi * train[lang] / 180
    test[lang+'_r'] = np.pi * test[lang] / 180
    
    
# compute the cell volumes 
train['vol'] = get_vol(train['lattice_vector_1_ang'],
                        train['lattice_vector_2_ang'],
                        train['lattice_vector_3_ang'],
                        train['lattice_angle_alpha_degree_r'],
                        train['lattice_angle_beta_degree_r'],
                        train['lattice_angle_gamma_degree_r'])
test['vol'] = get_vol(test['lattice_vector_1_ang'],
                        test['lattice_vector_2_ang'],
                        test['lattice_vector_3_ang'],
                        test['lattice_angle_alpha_degree_r'],
                        test['lattice_angle_beta_degree_r'],
                        test['lattice_angle_gamma_degree_r'])
for lang in lattice_angles:
    del train[lang+'_r']
    del test[lang+'_r']
del train2['5']
test2['id'] = test2['5']
del test2['5']
train = pd.merge(train,train2,on='id')
test = pd.merge(test,test2,on='id')
extra_feature = [x for x in train.keys() if '(' in x and 'Bond' not in x]
for i in extra_feature:
    train['N'+i] = train[i]/train['vol']
    test['N'+i] = test[i]/test['vol']
# bond angles
train_angle = np.load('train_bond_angles.npy').item()
test_angle = np.load('test_bond_angles.npy').item()
def more_less_than(x,a,b):
    return np.mean((x > a) * (x < b))
for i in [('Al', 'Ga'), ('Al', 'In'), ('Ga', 'In'),
          ('Al', 'Al'), ('Ga', 'Ga'), ('In', 'In'),
          ('O', 'O')]:
    temp = []
    all_angle = []
    all_list = []
    train[str(i)+'_A_mean'] = 0
    train[str(i)+'_A_std'] = 0
    train['array_'+str(i)] = 0
    for j in train_angle.keys():
        temp += [[np.mean(train_angle[j][i]),np.std(train_angle[j][i])],]
        all_angle += train_angle[j][i]
        all_list += [np.array(train_angle[j][i]),]
    all_angle = [ x for x in all_angle if x  <= 500 and x >=-500];
    plt.hist(all_angle,bins = 100);plt.savefig(str(i)+'.png');plt.close()
    train = train.set_value(train.index,[str(i)+'_A_mean',str(i)+'_A_std'],temp)
    train = train.set_value(train.index,'array_'+str(i),all_list)
    
    temp = []
    all_list = []
    test[str(i)+'_A_mean'] = 0
    test[str(i)+'_A_std'] = 0
    test['array_'+str(i)] = 0
    for j in test_angle.keys():
        temp += [[np.mean(test_angle[j][i]),np.std(test_angle[j][i])],]
        all_list += [np.array(test_angle[j][i]),]
    test = test.set_value(test.index,[str(i)+'_A_mean',str(i)+'_A_std'],temp)    
    test = test.set_value(test.index,'array_'+str(i),all_list)
    for ii in range(75,180,10):
        train[str(i)+'_%s_%s'%(ii,ii+10)] = train['array_'+str(i)].apply(lambda x : more_less_than(x,ii,ii+10))
        test[str(i)+'_%s_%s' %(ii,ii+10)] = test['array_'+str(i)].apply(lambda x : more_less_than(x,ii,ii+10))
        if np.mean(train[str(i)+'_%s_%s'%(ii,ii+10)]) == 0:
            del train[str(i)+'_%s_%s'%(ii,ii+10)]
            del test[str(i)+'_%s_%s'%(ii,ii+10)]
            print str(i)+'_%s_%s'%(ii,ii+10)

train_bond = np.load('train_bond_distribution.npy').item()
test_bond = np.load('test_bond_distribution.npy').item()
for i in [('Al', 'O'),('Ga', 'O'),('In', 'O')]:
    temp = []
    train['array_'+str(i)] = 0
    for j in train_bond.keys():
        temp += [np.array(train_bond[j][i]),]
    train = train.set_value(train.index, 'array_'+str(i),temp)
    temp = []
    test['array_'+str(i)] = 0
    for j in test_bond.keys():
        temp += [np.array(test_bond[j][i]),]
    test = test.set_value(test.index, 'array_'+str(i),temp)
    for ii in np.linspace(1.5,2.7,13):
        train[str(i)+'_%s_%s'%(ii,ii+0.1)] = train['array_'+str(i)].apply(lambda x : more_less_than(x,ii,ii+0.1))
        test[str(i)+'_%s_%s'%(ii,ii+0.1)] = test['array_'+str(i)].apply(lambda x : more_less_than(x,ii,ii+0.1))
        if np.mean(train[str(i)+'_%s_%s'%(ii,ii+0.1)] ) == 0:
            del train[str(i)+'_%s_%s'%(ii,ii+0.1)]
            del test[str(i)+'_%s_%s'%(ii,ii+0.1)]
            print str(i)+'_%s_%s'%(ii,ii+0.1)
target1 = 'formation_energy_ev_natom'
target2 = 'bandgap_energy_ev'
cols = [x for x in train.keys() if (x not in ['id',target1,target2] and 'array' not in x)]
train[target1] = np.log1p(train[target1])
train[target2] = np.log1p(train[target2])
for alpha in [0.001,0.003]:
    alpha = alpha/100
    train['predict1'] = 0
    test['predict1'] = 0
    train['predict2'] = 0
    test['predict2'] = 0
    from sklearn.cross_validation import train_test_split
    from sklearn.preprocessing import StandardScaler
    from sklearn import linear_model
    dictt_EN = {'O' : 3.44, 'In': 1.78, 'Al' : 1.61, 'Ga' : 1.81}
    dictt_cols1 = pd.DataFrame(cols + ['z1','z2'],columns=[1])
    dictt_cols2 = pd.DataFrame(cols + ['z1','z2'],columns=[1])

    for i in train.keys()[::-1]:
        train = train.fillna(0)
        test = test.fillna(0)
    train_ori = train.copy(deep = True)
    seeds = [1,5516,643,5235,2352,12,5674,19239,41241,1231,151,34,1235,2663,75765,2314,24,534,745,1215,643,754,8568,96][:]
    print seeds,len(seeds)
    for seed in seeds:
        train = train.sample(2400,random_state=seed).reset_index(drop=True)
        for i in range(0,10):
            test_id = [x for x in range(0,2400) if x%10 == i] 
            train_id = [x for x in range(0,2400) if x%10 != i] 
            scaler = StandardScaler()
            regr = linear_model.LinearRegression()#Lasso(alpha=alpha)
            scaler = scaler.fit(train.iloc[train_id][cols].values)
            X_train, y_train1,y_train2 = train.iloc[train_id][cols], train.iloc[train_id][target1],\
                                         train.iloc[train_id][target2]
            X_test, y_test1,y_test2 = train.iloc[test_id][cols], train.iloc[test_id][target1],\
                                      train.iloc[test_id][target2]
            regr = regr.fit(scaler.transform(X_train.values),y_train1.values)
            train = train.set_value(test_id,'predict1',train.iloc[test_id]['predict1']+regr.predict(scaler.transform(X_test.values))/len(seeds))
            test = test.set_value(test.index, 'predict1', test['predict1']+regr.predict(scaler.transform(test[cols].values))/(10*len(seeds)))
            regr = linear_model.Lasso(alpha=alpha)
            regr = regr.fit(scaler.transform(X_train.values),y_train2.values)
            train = train.set_value(test_id,'predict2',train.iloc[test_id]['predict2']+regr.predict(scaler.transform(X_test.values))/len(seeds))
            test = test.set_value(test.index, 'predict2', test['predict2']+regr.predict(scaler.transform(test[cols].values))/(10*len(seeds)))
    #print train[['predict1','predict2',target1,target2]].corr()
    a,b = np.mean((train['predict1']-train[target1])**2)**.5, np.mean((train['predict2']-train[target2])**2)**.5
    print a
    print b
    print alpha,(a+b)/2
if True:
    name1 = 'predict1_%s'%np.round((a+b)/2,5)
    name2 = 'predict2_%s'%np.round((a+b)/2,5)
    test[name1] = test['predict1']
    test[name2] = test['predict2']
    train[name1] = train['predict1']
    train[name2] = train['predict2']
    train[['id',name1,name2,target1,target2]].to_csv('modelL_train_%s.csv'%np.round((a+b)/2,5),index=0)
    test[['id',name1,name2]].to_csv('modelL_test_%s.csv'%np.round((a+b)/2,5),index=0)
die
dictt_cols1 = dictt_cols1.fillna(0)
dictt_cols2 = dictt_cols2.fillna(0)
for i in range(2,1+len(dictt_cols1.keys())):
    dictt_cols1[i] = 100*dictt_cols1[i] / np.sum(dictt_cols1[i])
    dictt_cols2[i] = 100*dictt_cols2[i] / np.sum(dictt_cols2[i])
#print np.sum(dictt_cols1[range(2,len(dictt_cols1.keys()))].values,1)
#print np.sum(dictt_cols2[range(2,len(dictt_cols1.keys()))].values,1)
dictt_cols1['avg'] =  np.sum(dictt_cols1[range(2,len(dictt_cols1.keys()))].values,1)
dictt_cols2['avg'] =  np.sum(dictt_cols2[range(2,len(dictt_cols1.keys()))].values,1)
print dictt_cols2[[1,'avg']].sort_values('avg').iloc[-20:]
print dictt_cols1[[1,'avg']].sort_values('avg').iloc[-20:]
a,b = np.mean((train['predict1']-train[target1])**2)**.5, np.mean((train['predict2']-train[target2])**2)**.5
print a
print b
print (a+b)/2
test[target1] = np.exp(test[target1])-1
test[target2] = np.exp(test[target2])-1
train[target1] = np.exp(train[target1])-1
train[target2] = np.exp(train[target2])-1
train['predict1'] = np.exp(train['predict1'])-1
train['predict2'] = np.exp(train['predict2'])-1
test[['id',target1,target2]].to_csv('test_v2%s.csv'%np.round((a+b)/2,4),index=0)
if True:
    train.to_csv('train_v2%s.csv'%np.round((a+b)/2,4),index=0)
    test.to_csv('test_v2%s.csv'%np.round((a+b)/2,4),index=0)
if True:
    name1 = 'predict1_%s'%np.round((a+b)/2,5)
    name2 = 'predict2_%s'%np.round((a+b)/2,5)
    test[name1] = np.log1p(test[target1])
    test[name2] = np.log1p(test[target2])
    train[name1] = np.log1p(train['predict1'])
    train[name2] = np.log1p(train['predict2'])
    train[['id',name1,name2,target1,target2]].to_csv('model_train_%s.csv'%np.round((a+b)/2,5),index=0)
    test[['id',name1,name2]].to_csv('model_test_%s.csv'%np.round((a+b)/2,5),index=0)
list(set(list(dictt_cols1[[1,'avg']].sort_values('avg').iloc[-70:][1]) + list(dictt_cols2[[1,'avg']].sort_values('avg').iloc[-70:][1])))
import matplotlib.pyplot as plt
##for i in cols:
##	f, ax = plt.subplots(1,2,figsize=(10,5));
##	ax[0].plot(train[i],train[target1],'ro')
##	ax[1].plot(train[i],train[target2],'ro')
##	ax[0].set_title(i+'_'+target1)
##	ax[1].set_title(i+'_'+target2)
##	ax[0].set_xlabel(train[[i,target1]].corr()[i])
##	ax[1].set_xlabel(train[[i,target2]].corr()[i])
##	plt.savefig(i+'.png',dpi=300,bbox_inches='tight');plt.close();
'''
benchmark *5
0.03250080113
0.0880216978405
0.0602612494852
with engeinner features *5
0.028781766046
0.0849339614409
0.0568578637434

engineer_features from paper*5
0.026665032169
0.0816681029669
0.054166567568

# engineer_features from paper*5 + bond angles
0.0245717966321
0.0791911408058
0.051881468719
'''

'''
https://media.nature.com/original/nature-assets/npjcompumats/2016/npjcompumats201628/extref/npjcompumats201628-s1.pdf
Average atomic mass
Average column on periodic table
Average  row  on  the  periodic  table
Average atomic radius
verage electronegativity
fraction of valence electrons
'''