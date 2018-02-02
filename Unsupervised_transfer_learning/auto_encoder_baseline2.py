import tensorflow as tf
import numpy as np
import keras as keras
from keras.layers import Conv2D, Input , AveragePooling2D,UpSampling2D
import matplotlib.pyplot as plt
# images are 96 * 96

'''
Stacked Convolutional Auto-Encoders for
Hierarchical Feature Extraction
http://people.idsia.ch/~ciresan/data/icann2011.pdf

'''

data = np.load('Unlabelled_10%_images.npy')[::10]
Inp0 = Input(shape=(96,96,3),name = 'Input_layer')
layer0  = keras.layers.Lambda( lambda x : x/128-1) (Inp0) #convert to 0-1
layer1 = Conv2D(32,(3,3),padding='same',
                             activation = 'relu')(layer0)
layer1 = AveragePooling2D(pool_size=(2, 2),name = 'AvgPool01_layera')(layer1)
layer1 = Conv2D(64,(3,3),padding='same',
                             activation = 'relu')(layer1)
layer1 = AveragePooling2D(pool_size=(2, 2),name = 'AvgPool01_layerB')(layer1)
layer1 = Conv2D(128,(3,3),padding='same',
                             activation = 'relu')(layer1)
layer1 = AveragePooling2D(pool_size=(2, 2),name = 'AvgPool01_layerC')(layer1)
layer1 = Conv2D(128,(3,3),padding='same',
                             activation = 'relu')(layer1)
layer1 = AveragePooling2D(pool_size=(2, 2),name = 'AvgPool01_layerD')(layer1)
layer1 = Conv2D(256,(3,3),padding='same',
                             activation = 'relu')(layer1)
layer1 = AveragePooling2D(pool_size=(2, 2),name = 'AvgPool01_layerE')(layer1)
dense1 = keras.layers.GlobalAveragePooling2D()(layer1)
dense2 = keras.layers.Dense(256)(dense1)
a,b,c = map(int,(layer1.shape[-1],layer1.shape[-2],layer1.shape[-3]))
#ense2 = keras.layers.Dense(a,name='dense1')(dense2)
#dense2 = keras.layers.Dense(a*b,name='dense2')(dense2)
dense2 = keras.layers.Dense(a*b*c/2,name='dense3')(dense2)
dense2 = keras.layers.Reshape((c,b,a/2))(dense2)
layer2 = Conv2D(128,(3,3),padding='same',
                             activation = 'relu')(dense2)
layer2 = UpSampling2D(data_format="channels_last")(layer2)
layer2 = Conv2D(128,(3,3),padding='same',
                             activation = 'relu')(layer2)
layer2 = UpSampling2D(data_format="channels_last")(layer2)
layer2 = Conv2D(64,(3,3),padding='same',
                             activation = 'relu')(layer2)
layer2 = UpSampling2D(data_format="channels_last")(layer2)
layer2 = Conv2D(64,(3,3),padding='same',
                             activation = 'relu')(layer2)
layer2 = UpSampling2D(data_format="channels_last")(layer2)
layer2 = Conv2D(32,(3,3),padding='same',
                             activation = 'relu')(layer2)
layer2 = UpSampling2D(data_format="channels_last")(layer2)
layer2 = Conv2D(32,(3,3),padding='same',
                             activation = 'relu')(layer2)
layer3 = Conv2D(3,(1,1),padding='same',
                             activation =  None)(layer2)
layer4  = keras.layers.Lambda( lambda x : (tf.tanh(x)+1)*128) (layer3) #convert back to u8bit
model = keras.models.Model(Inp0, layer4)

# initiate RMSprop optimizer
opt = keras.optimizers.rmsprop(lr=0.0001, decay=1e-4) #decays by two orders of magnitude

# Let's train the model using RMSprop

from keras import backend as K
def mean_squared_error2(y_true, y_pred):
    return K.mean(K.square(y_pred - y_true), axis=(-1,-2,-3))
# Let's train the model using RMSprop
model.compile(loss=mean_squared_error2,
              optimizer=opt)
model.summary()
try:
    model.load_weights("model2.h5");
except :
    'Model training from scratch'
train_id = [x for x in range(len(data)) if x%10 != 0]
test_id = [x for x in range(len(data)) if x%10 == 0]
die
print (len(train_id),len(test_id))
model.fit(data[train_id],data[train_id],256,50,verbose=2,validation_data = (data[test_id],data[test_id]))
model.save_weights("model2.h5")
model.fit(data[train_id],data[train_id],256,50,verbose=2,validation_data = (data[test_id],data[test_id]))
model.save_weights("model2.h5")
model.fit(data[train_id],data[train_id],256,50,verbose=2,validation_data = (data[test_id],data[test_id]))
model.save_weights("model2.h5")
