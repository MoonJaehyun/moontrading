import os
import cv2
import numpy as np
import pandas as pd
import mplfinance as mpf
from pykrx import stock
from keras.preprocessing.image import ImageDataGenerator
from keras.models import Sequential
from keras.layers import Conv2D, MaxPooling2D, Activation, Dropout, Flatten, Dense

def split_data(data, train_ratio=0.8):
    train_idx = int(len(data) * train_ratio)
    train_data = data[:train_idx]
    test_data = data[train_idx:]
    return train_data, test_data


f = stock.get_stock_major_changes("005930")
row_titles = f.index
r = row_titles[0]
date = r.strftime('%Y%m%d')


df_cap = stock.get_market_cap("20200101", "20230519", "005930", "m")
min_cap = df_cap['시가총액'].min()
listed_shares = df_cap['상장주식수'][0] 
min_value = min_cap / listed_shares


df = stock.get_market_ohlcv(date, "20230519", "005930")
df_selected = df[['시가', '고가', '종가', '저가']]


df_selected = df_selected[df_selected >= min_value].dropna()

high_prices = df_selected['고가']
low_prices = df_selected['저가']
open_prices = df_selected['시가']
close_prices = df_selected['종가']


train_open, test_open = split_data(open_prices)
train_high, test_high = split_data(high_prices)
train_low, test_low = split_data(low_prices)
train_close, test_close = split_data(close_prices)


train_data = {'Open': train_open,
              'High': train_high,
              'Low': train_low,
              'Close': train_close}
test_data = {'Open': test_open,
             'High': test_high,
             'Low': test_low,
             'Close': test_close}

df_train = pd.DataFrame(train_data)
df_test = pd.DataFrame(test_data)


mc = mpf.make_marketcolors(up='r', down='b', edge='inherit', wick='inherit', volume='inherit', ohlc='i')
s = mpf.make_mpf_style(marketcolors=mc)
fig, axes = mpf.plot(df_train, type='candle', style=s, title='Samsung Stock Price Train', returnfig=True)


train_image_path = 'samsung_train.png'
fig.savefig(train_image_path)


img = cv2.imread(train_image_path)
img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
img = cv2.resize(img, (150, 150))
img = img.reshape((1,) + img.shape)
img = img / 255.0


model = Sequential()
model.add(Conv2D(32, (3, 3), input_shape=(150, 150, 3)))
model.add(Activation('relu'))
model.add(MaxPooling2D(pool_size=(2, 2)))
model.add(Conv2D(32, (3, 3)))
model.add(Activation('relu'))
model.add(MaxPooling2D(pool_size=(2, 2)))
model.add(Conv2D(64, (3, 3)))
model.add(Activation('relu'))
model.add(MaxPooling2D(pool_size=(2, 2)))
model.add(Flatten())
model.add(Dense(64))
model.add(Activation('relu'))
model.add(Dropout(0.5))
model.add(Dense(1))
model.add(Activation('sigmoid'))

model.compile(loss='binary_crossentropy',
              optimizer='rmsprop',
              metrics=['accuracy'])


model.fit(img, np.array([0]), batch_size=1, epochs=50)


fig, axes = mpf.plot(df_test, type='candle', style=s, title='Samsung Stock Price Test', returnfig=True)


test_image_path = 'samsung_test.png'
fig.savefig(test_image_path)


new_img = cv2.imread(test_image_path)
new_img = cv2.cvtColor(new_img, cv2.COLOR_BGR2RGB)
new_img = cv2.resize(new_img, (150, 150))
new_img = new_img.reshape((1,) + new_img.shape)
new_img = new_img / 255.0


prediction = model.predict(new_img)


if prediction > 0.5:
    print("The model predicts the stock price on 20230518 will rise.")
else:
    print("The model predicts the stock price on 20230518 will fall.")


actual_change = test_close[-1] - test_open[-1]
if actual_change > 0 and prediction > 0.5:
    print("The model correctly predicted the stock price would rise.")
elif actual_change <= 0 and prediction <= 0.5:
    print("The model correctly predicted the stock price would fall.")
else:
    print("The model failed to predict the correct direction of the stock price.")
