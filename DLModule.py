import sys
from keras.models import Sequential
from keras.layers import Dense, Activation, Bidirectional, Dropout, Conv1D, MaxPooling1D, Flatten, LSTM



class DLClass(object):
    """docstring for DLClass"""
    def __init__(self):
        self.kernel_size = 3
        self.filters = 100
        self.pool_size = 4
        self.strides=1
        self.epochs=10
        self.batch_size=100
        self.model = Sequential()


    def build_model(self,x,y,model_type,lstm_units=100,validation_data=''):
        self.model.add(Conv1D(self.filters,
            self.kernel_size,
            padding='valid',
            activation='relu',
            strides=self.strides,
            input_shape=(x.shape[1], x.shape[2])))
        self.model.add(MaxPooling1D(pool_size=self.pool_size))
        if model_type=='cnn':
            self.model.add(Flatten())
            self.model.add(Dropout(0.5))
        elif model_type=='cblstm':
            self.model.add(Bidirectional(LSTM(lstm_units)))
            self.model.add(Dropout(0.5))
        else:
            sys.exit('Model type must be "cnn" or "blstm"')
        self.model.add(Dense(1))
        self.model.add(Activation('sigmoid'))
        self.model.compile(loss='binary_crossentropy',
            optimizer='adam',
            metrics=['accuracy'])
        print('Train with ',len(x))
        print(self.model.summary())
        self.model.fit(x,y,epochs=self.epochs,batch_size=self.batch_size,validation_data=validation_data)
        