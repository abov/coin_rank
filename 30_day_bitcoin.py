import requests
import json
from ast import literal_eval
import pandas as pd
import datetime
# from datetime import timedelta

# This is an API with the last 30 days by hour of bitcoin prices.
response = requests.get('https://api.coinranking.com/v1/public/coin/1/history/30d') 
a = response.content # .decode('utf-8')

data = literal_eval(a.decode('utf8'))

df = pd.json_normalize(data=data['data'], record_path='history')

# From that, output a JSON file, or display on a browser or endpoint values in this format:
# [
# {
#     "date": "{date}",
#     “price”: ”{value}",
#     "direction": "{up/down/same}",
#     "change": "{amount}",
#     "dayOfWeek": "{name}”,
#     "highSinceStart": "{true/false}”,
#     “lowSinceStart": "{true/false}”
# }
# ]

# - date in format "2019-03-17T00:00:00"
df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
df['date'] = pd.to_datetime(df['timestamp'], format='%Y-%m-%d %H:%M:%S').dt.strftime('%Y-%m-%dT%H:%M:%S')

# - one entry per day at "00:00:00" hours
df = df[df['date'].str.contains(':00:00')]

# - results ordered by oldest date first.
df.sort_values(by='date', ascending=True)

# - "change" is the price difference between current and previous day. “na” for first
df["price"] = df.price.astype(float)
df['change'] = (df['price']-df['price'].shift()) # .fillna('na')

# - "direction" is direction of price change since previous day in the list, first day can be “na” ({up/down/same})
df.loc[df['change']>0, 'direction'] = 'up'
df.loc[df['change']<0, 'direction'] = 'down'
df.loc[df['change']==0, 'direction'] = 'same'
df = df.fillna('na')

# - "high since start” / “low since start” is if this is the highest/lowest price since the oldest date in the list.
df['highSinceStart'] = df['price'] == df['price'].cummax()
df['lowSinceStart'] = df['price'] == df['price'].cummin()

# - "day of week" is name of the day (Saturday, Tuesday, etc)
df['dayOfWeek'] = df['timestamp'].dt.day_name()

df = df.drop(columns=['timestamp']) 

# Example:

# Day1 :
#     price:100
#     Highest:true
#     Lowest:true
# Day2:
#     price:90
#     Highest:false
#     Lowest:true
# Day3:
#     price:101
#     Highest:true
#     Lowest:false
# Etc…

df = df[['date','price','direction','change','dayOfWeek','highSinceStart','lowSinceStart']]
print(df)
df.to_json('sample_file/last_30_days.json', orient="records")

# - code should be written in python and hosted in github
# https://github.com/abov/coin_rank

# Please have this sent back by Sunday 11/15/2020. If you have any questions feel free to reach out.

