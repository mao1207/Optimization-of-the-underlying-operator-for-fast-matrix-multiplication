from __future__ import print_function
import keras
from keras.datasets import cifar10
from keras.preprocessing.image import ImageDataGenerator
from keras.models import Sequential
from keras.layers import Dense, Dropout, Activation, Flatten
from keras.layers import Conv2D, MaxPooling2D, BatchNormalization
from keras import optimizers
import numpy as np
from keras.layers.core import Lambda
from keras import backend as K
from keras import regularizers

import time
from scipy.special import softmax

from ctypes import *

from tkinter import _flatten
from math import *

csum = cdll.LoadLibrary('./avg_final.so')
func = cdll.LoadLibrary('./find_final.so')

class cifar10vgg:
    def __init__(self, train=True):
        self.num_classes = 10
        self.weight_decay = 0.0005
        self.x_shape = [32, 32, 3]

        self.model = self.build_model()
        if train:
            self.model = self.train(self.model)
        else:
            self.model.load_weights('cifar10vgg.h5')
            self.last_dense = None
            self.prepare_last_dense()

    def build_model(self):
        # Build the network of vgg for 10 classes with massive dropout and weight decay as described in the paper.

        model = Sequential()
        weight_decay = self.weight_decay

        model.add(Conv2D(64, (3, 3), padding='same',
                         input_shape=self.x_shape, kernel_regularizer=regularizers.l2(weight_decay)))
        model.add(Activation('relu'))
        model.add(BatchNormalization())
        model.add(Dropout(0.3))

        model.add(Conv2D(64, (3, 3), padding='same', kernel_regularizer=regularizers.l2(weight_decay)))
        model.add(Activation('relu'))
        model.add(BatchNormalization())

        model.add(MaxPooling2D(pool_size=(2, 2)))

        model.add(Conv2D(128, (3, 3), padding='same', kernel_regularizer=regularizers.l2(weight_decay)))
        model.add(Activation('relu'))
        model.add(BatchNormalization())
        model.add(Dropout(0.4))

        model.add(Conv2D(128, (3, 3), padding='same', kernel_regularizer=regularizers.l2(weight_decay)))
        model.add(Activation('relu'))
        model.add(BatchNormalization())

        model.add(MaxPooling2D(pool_size=(2, 2)))

        model.add(Conv2D(256, (3, 3), padding='same', kernel_regularizer=regularizers.l2(weight_decay)))
        model.add(Activation('relu'))
        model.add(BatchNormalization())
        model.add(Dropout(0.4))

        model.add(Conv2D(256, (3, 3), padding='same', kernel_regularizer=regularizers.l2(weight_decay)))
        model.add(Activation('relu'))
        model.add(BatchNormalization())
        model.add(Dropout(0.4))

        model.add(Conv2D(256, (3, 3), padding='same', kernel_regularizer=regularizers.l2(weight_decay)))
        model.add(Activation('relu'))
        model.add(BatchNormalization())

        model.add(MaxPooling2D(pool_size=(2, 2)))

        model.add(Conv2D(512, (3, 3), padding='same', kernel_regularizer=regularizers.l2(weight_decay)))
        model.add(Activation('relu'))
        model.add(BatchNormalization())
        model.add(Dropout(0.4))

        model.add(Conv2D(512, (3, 3), padding='same', kernel_regularizer=regularizers.l2(weight_decay)))
        model.add(Activation('relu'))
        model.add(BatchNormalization())
        model.add(Dropout(0.4))

        model.add(Conv2D(512, (3, 3), padding='same', kernel_regularizer=regularizers.l2(weight_decay)))
        model.add(Activation('relu'))
        model.add(BatchNormalization())

        model.add(MaxPooling2D(pool_size=(2, 2)))

        model.add(Conv2D(512, (3, 3), padding='same', kernel_regularizer=regularizers.l2(weight_decay)))
        model.add(Activation('relu'))
        model.add(BatchNormalization())
        model.add(Dropout(0.4))

        model.add(Conv2D(512, (3, 3), padding='same', kernel_regularizer=regularizers.l2(weight_decay)))
        model.add(Activation('relu'))
        model.add(BatchNormalization())
        model.add(Dropout(0.4))

        model.add(Conv2D(512, (3, 3), padding='same', kernel_regularizer=regularizers.l2(weight_decay)))
        model.add(Activation('relu'))
        model.add(BatchNormalization())

        model.add(MaxPooling2D(pool_size=(2, 2)))
        model.add(Dropout(0.5))

        model.add(Flatten())
        model.add(Dense(512, kernel_regularizer=regularizers.l2(weight_decay)))
        model.add(Activation('relu'))
        model.add(BatchNormalization())

        model.add(Dropout(0.5))
        model.add(Dense(self.num_classes))
        model.add(Activation('softmax'))
        return model

    def normalize(self, X_train, X_test):
        # this function normalize inputs for zero mean and unit variance
        # it is used when training a model.
        # Input: training set and test set
        # Output: normalized training set and test set according to the trianing set statistics.
        mean = np.mean(X_train, axis=(0, 1, 2, 3))
        std = np.std(X_train, axis=(0, 1, 2, 3))
        X_train = (X_train - mean) / (std + 1e-7)
        X_test = (X_test - mean) / (std + 1e-7)
        return X_train, X_test

    def normalize_production(self, x):
        # this function is used to normalize instances in production according to saved training set statistics
        # Input: X - a training set
        # Output X - a normalized training set according to normalization constants.

        # these values produced during first training and are general for the standard cifar10 training set normalization
        mean = 120.707
        std = 64.15
        return (x - mean) / (std + 1e-7)

    def predict(self, x, normalize=True, batch_size=50):
        if normalize:
            x = self.normalize_production(x)
        return self.model.predict(x, batch_size)

    def train(self, model):

        # training parameters
        batch_size = 128
        maxepoches = 250
        learning_rate = 0.1
        lr_decay = 1e-6
        lr_drop = 20
        # The data, shuffled and split between train and test sets:
        (x_train, y_train), (x_test, y_test) = cifar10.load_data()
        x_train = x_train.astype('float32')
        x_test = x_test.astype('float32')
        x_train, x_test = self.normalize(x_train, x_test)

        y_train = keras.utils.to_categorical(y_train, self.num_classes)
        y_test = keras.utils.to_categorical(y_test, self.num_classes)

        def lr_scheduler(epoch):
            return learning_rate * (0.5 ** (epoch // lr_drop))

        reduce_lr = keras.callbacks.LearningRateScheduler(lr_scheduler)

        # data augmentation
        datagen = ImageDataGenerator(
            featurewise_center=False,  # set input mean to 0 over the dataset
            samplewise_center=False,  # set each sample mean to 0
            featurewise_std_normalization=False,  # divide inputs by std of the dataset
            samplewise_std_normalization=False,  # divide each input by its std
            zca_whitening=False,  # apply ZCA whitening
            rotation_range=15,  # randomly rotate images in the range (degrees, 0 to 180)
            width_shift_range=0.1,  # randomly shift images horizontally (fraction of total width)
            height_shift_range=0.1,  # randomly shift images vertically (fraction of total height)
            horizontal_flip=True,  # randomly flip images
            vertical_flip=False)  # randomly flip images
        # (std, mean, and principal components if ZCA whitening is applied).
        datagen.fit(x_train)

        # optimization details
        sgd = optimizers.SGD(lr=learning_rate, decay=lr_decay, momentum=0.9, nesterov=True)
        model.compile(loss='categorical_crossentropy', optimizer=sgd, metrics=['accuracy'])

        # training process in a for loop with learning rate drop every 25 epoches.

        historytemp = model.fit_generator(datagen.flow(x_train, y_train,
                                                       batch_size=batch_size),
                                          steps_per_epoch=x_train.shape[0] // batch_size,
                                          epochs=maxepoches,
                                          validation_data=(x_test, y_test), callbacks=[reduce_lr], verbose=2)
        model.save_weights('cifar10vgg.h5')
        return model

    def get_layer_output(self, inputs, layer_index=-1):
        layer_model = keras.models.Model(inputs=self.model.input, outputs=self.model.layers[layer_index].get_output_at(0))
        return layer_model.predict(inputs)

    def last_dense_weights(self):
        return self.model.layers[-2].get_weights()

    def prepare_last_dense(self):
        layer_input = keras.layers.Input(shape=(self.model.layers[-2].get_input_shape_at(0)[-1],))
        layer_output = self.model.layers[-2](layer_input)
        self.last_dense = keras.models.Model(inputs=layer_input, outputs=layer_output)

    def simulate_last_dense(self, inputs):
        # layer_input = keras.layers.Input(shape=(self.model.layers[-2].get_input_shape_at(0)[-1],))
        # layer_output = self.model.layers[-2](layer_input)
        # last_dense = keras.models.Model(inputs=layer_input, outputs=layer_output)
        # return last_dense.predict(inputs)
        return self.last_dense.predict(inputs)

    def loop_simulate_last_dense(self, inputs, weights, bias):
        result = np.empty(shape=(inputs.shape[0], weights.shape[-1]))
        for i, vec in enumerate(inputs):
            result[i] = np.dot(vec, weights) + bias
        return result


class HashingTree:
    def __init__(self):
        self.table = np.load('lookup_table_4.npy')
        self.tree_parameters = np.load('hashing_model_4_indices.npy', allow_pickle=True).item()
        self.num_space = len(self.tree_parameters)
        self.num_level = len(self.tree_parameters[0][1])

    def transform(self,number_list):
        minimum = min(number_list)
        l=floor(log(255/(max(number_list)-minimum),2))
        a=pow(2,l)
        result=[]
        for i in range(len(number_list)):
            result.append(int(a*(number_list[i]-minimum)))
        return np.array(result,dtype='uint8')

    def __encoding(self, matrix, tree_threshold, tree_comp_indices):
        indices = []
        i = 0
        for vec in matrix:
            number_list=list(tree_threshold)
            number_list.append(vec[tree_comp_indices[0]])
            number_list.append(vec[tree_comp_indices[1]])
            number_list.append(vec[tree_comp_indices[2]])
            number_list.append(vec[tree_comp_indices[3]])
            number_list=self.transform(number_list)
            number_list_ptr=cast(number_list.ctypes.data, POINTER(c_uint8))
            indices.append(func.Multiple_find(number_list_ptr))
            i += 1
        return indices

    def calc(self, inputs):
        result = []
        if len(inputs.shape) == 1:
            inputs = inputs[np.newaxis, :]
        for i in range(self.num_space):
            tree_threshold, tree_comp_indices, j_indices = self.tree_parameters[i]
            tree_threshold = _flatten(tree_threshold)
            index = self.__encoding(inputs[:, j_indices], tree_threshold, tree_comp_indices)
            #table=[x for y in self.table[i, index] for x in y]
            table=self.table[i, index]
            result.append(table)
        result=np.array(result)
        return result.sum(axis=0)


class ProductQuantization:
    def __init__(self):
        self.table = np.load('q_lookup_table.npy')
        self.pq_parameters = np.load('pq_model.npy', allow_pickle=True).item()
        self.num_space = len(self.pq_parameters)
        self.cls = self.pq_parameters[0][0].shape[0]

    def __encoding(self, matrix, prototypes):
        indices = []
        for vec in matrix:
            i = 0
            min_dist = np.inf
            for k in range(self.cls):
                dist = np.linalg.norm(vec - prototypes[k])
                if dist < min_dist:
                    min_dist = dist
                    i = k
            indices.append(i)
        return indices

    def calc(self, inputs):
        result = []
        if len(inputs.shape) == 1:
            inputs = inputs[np.newaxis, :]
        for i in range(self.num_space):
            prototypes, j_indices = self.pq_parameters[i]
            index = self.__encoding(inputs[:, j_indices], prototypes)
            result.append(self.table[i, index])
        return np.stack(result, axis=0).sum(axis=0)


if __name__ == '__main__':
    (x_train, y_train), (x_test, y_test) = cifar10.load_data()
    # x_train = x_train.astype('float32')
    x_test = x_test.astype('float32')
    #
    # y_train = keras.utils.to_categorical(y_train, 10)
    y_test = keras.utils.to_categorical(y_test, 10)

    model = cifar10vgg(train=False)
    train_matrices = model.get_layer_output(model.normalize_production(x_train), -3)
    test_matrices = model.get_layer_output(model.normalize_production(x_test), -3)
    last_weight, last_bias = model.last_dense_weights()

    hashing_tree = HashingTree()
    product_quantization = ProductQuantization()
    #
    # # the following code is some experiments
    #
    spend_time1=0
    residuals1=[]
    for i in range(100):
        start_time1 = time.time()
        model_result=softmax(model.simulate_last_dense(test_matrices[100*i:(100*i+1)]),axis=-1)
        end_time1 = time.time()
        spend_time1+=end_time1 - start_time1
        residuals1.append(np.argmax(model_result, 1) != np.argmax(y_test[100*i:(100*i+1)], 1))
    loss1 = sum(residuals1) / len(residuals1)
    print("the validation 0/1 loss of model is: %f\n time is %.3f" % (loss1, spend_time1))

    spend_time2=0
    residuals2=[]
    for i in range(100):
        start_time2 = time.time()
        hashing_result=hashing_tree.calc(test_matrices[100*i:(100*i+1)])
        end_time2 = time.time()
        spend_time2+=end_time2 - start_time2
        residuals2.append(np.argmax(hashing_result, 1) != np.argmax(y_test[100*i:(100*i+1)], 1))
    loss2 = sum(residuals2) / len(residuals2)
    print("the validation 0/1 loss of hashing is: %f\n time is %.3f" % (loss2, spend_time2))
    
    
    spend_time3=0
    residuals3=[]
    for i in range(100):
        start_time3 = time.time()
        pq_result = softmax(product_quantization.calc(test_matrices[100*i:(100*i+1)]), axis=-1)
        end_time3 = time.time()
        spend_time3+=end_time3 - start_time3
        residuals3.append(np.argmax(pq_result, 1) != np.argmax(y_test[100*i:(100*i+1)], 1))
        
    loss3 = sum(residuals3) / len(residuals3)
    print("the validation 0/1 loss of product quantization is: %f\n time is %.3f" % (loss3, spend_time3))
    
    spend_time4=0
    residuals4=[]
    for i in range(100):
        start_time4 = time.time()
        loop_multiply_result = softmax(model.loop_simulate_last_dense(test_matrices[100*i:(100*i+1)], *model.last_dense_weights()), axis=-1)
        end_time4 = time.time()
        spend_time4+=end_time4 - start_time4
        residuals4.append(np.argmax(loop_multiply_result, 1) != np.argmax(y_test[100*i:(100*i+1)], 1))
    
    loss4 = sum(residuals4) / len(residuals4)
    print("the validation 0/1 loss of loop multiply is: %f\n time is %.3f" % (loss4, spend_time4))

    '''
    np.save('train_matrices.npy', train_matrices)
    np.save('test_matrices.npy', test_matrices)

    # print(train_matrices.shape, test_matrices.shape)

    np.save('weight.npy', last_weight)
    np.save('bias.npy', last_bias)

    # print('layer in {}:\n{}\n'.format(-3, test_matrices.shape))
    # print('layer in {}:\n{}\n{}\n'.format(-1, last_weight.shape, last_bias.shape))
    # manual_result = np.dot(test_matrices, last_weight) + last_bias
    # softmax_result = softmax(manual_result, axis=-1)
    # model_result = model.predict(x_test, True)
    # print(softmax_result.shape)
    # print(model_result.shape)
    # print(softmax_result == model_result)
    # print((np.argmax(softmax_result, 1) != np.argmax(y_test, 1)) == (np.argmax(model_result, 1) != np.argmax(y_test, 1)))

    # predicted_x = model.predict(x_test)
    # residuals = np.argmax(predicted_x, 1) != np.argmax(y_test, 1)
    #
    # loss = sum(residuals) / len(residuals)
    # print("the validation 0/1 loss is: ", loss)
    '''
