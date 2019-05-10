# !/usr/bin/python  
# encoding: utf-8
# Author: zhangtong
# Time: 2019/4/30 11:06
import os
from keras.models import Model, load_model
from keras.callbacks import ModelCheckpoint
from keras.layers import Conv2D, MaxPool2D, Flatten, Dropout, Dense, Input
from keras.optimizers import Adam
from keras.backend.tensorflow_backend import set_session
import tensorflow as tf
import numpy as np

chars = ["京", "沪", "津", "渝", "冀", "晋", "蒙", "辽", "吉", "黑", "苏", "浙", "皖", "闽", "赣", "鲁", "豫", "鄂", "湘", "粤", "桂",
         "琼", "川", "贵", "云", "藏", "陕", "甘", "青", "宁", "新", "0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "A",
         "B", "C", "D", "E", "F", "G", "H", "J", "K", "L", "M", "N", "P", "Q", "R", "S", "T", "U", "V", "W", "X",
         "Y", "Z", "学", "警", "挂"]
M_strIdx = dict(zip(chars, range(len(chars))))


def gen_train(batch_size=32):
    processed_data = np.load('1.npy')
    training_images = processed_data[0]
    training_labels = processed_data[1]
    text_images = processed_data[4]
    text_labels = processed_data[5]
    # l_platestr, l_plateimg = [], []
    start_size = 0
    over_size = start_size+batch_size
    training_len = len(training_images)
    while True:
        if over_size > training_len:
            l_platestr = training_labels[start_size:]
            l_platestr.extend(text_labels[:over_size-training_len])
            l_plateimg = training_images[start_size:]
            l_plateimg.extend(text_images[:over_size - training_len])
            start_size = 0
            over_size = start_size + batch_size
        else:
            l_platestr = training_labels[start_size:over_size]
            l_plateimg = training_images[start_size:over_size]
        training_np = np.array(l_plateimg, dtype=np.uint8)
        ytmp = np.array(list(map(lambda x: [M_strIdx[a] for a in list(x)], l_platestr)), dtype=np.uint8)
        y = np.zeros([ytmp.shape[1], batch_size, len(chars)])
        for batch in range(batch_size):
            for idx, row_i in enumerate(ytmp[batch]):
                y[idx, batch, row_i] = 1
        start_size = over_size
        over_size = start_size + batch_size
        yield training_np, [yy for yy in y]


def gen_val(batch_size=32):
    processed_data = np.load('1.npy')
    val_images = processed_data[2]
    val_labels = processed_data[3]
    start_size = 0
    over_size = start_size+batch_size
    training_len = len(val_images)
    while True:
        if over_size > training_len:
            start_size = 0
            over_size = start_size + batch_size
        l_platestr = val_labels[start_size:over_size]
        l_plateimg = val_images[start_size:over_size]
        val_np = np.array(l_plateimg, dtype=np.uint8)
        ytmp = np.array(list(map(lambda x: [M_strIdx[a] for a in list(x)], l_platestr)), dtype=np.uint8)
        y = np.zeros([ytmp.shape[1], batch_size, len(chars)])
        for batch in range(batch_size):
            for idx, row_i in enumerate(ytmp[batch]):
                y[idx, batch, row_i] = 1
        start_size = over_size
        over_size = start_size + batch_size
        yield val_np, [yy for yy in y]

if __name__ == '__main__':
    if os.path.exists('chepai_best.h5'):
        model = load_model('chepai_best.h5')
    else:
        adam = Adam(lr=0.001)
        input_tensor = Input((42, 132, 3))
        x = input_tensor
        for i in range(3):
            x = Conv2D(32*2**i, (3, 3), activation='relu')(x)
            x = Conv2D(32*2**i, (3, 3), activation='relu')(x)
            x = MaxPool2D(pool_size=(2, 2))(x)
        x = Flatten()(x)
        x = Dropout(0.5)(x)

        n_class = len(chars)
        x = [Dense(n_class, activation='softmax', name='c%d' % (i+1))(x) for i in range(7)]
        model = Model(inputs=input_tensor, outputs=x)
        print(model.summary())
        model.compile(loss='categorical_crossentropy',
                      optimizer=adam,
                      metrics=['accuracy'])

    best_model = ModelCheckpoint("chepai_best.h5", monitor='val_loss', verbose=0, save_best_only=True)

    model.fit_generator(gen_train(32), steps_per_epoch=100, epochs=40000,
                        validation_data=gen_val(32), validation_steps=2,
                        callbacks=[best_model])
