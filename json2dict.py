import pickle

from datetime import datetime
from datetime import timedelta

with open("./MyActivity.json", 'r') as fh:
    data1 = fh.read()
with open("./watch-history.json", 'r') as fh:
    data2 = fh.read()
with open("./search-history.json", 'r') as fh:
    data3 = fh.read()

jsoned1 = eval(data1)
jsoned2 = eval(data2)
jsoned3 = eval(data3)

temp = [*jsoned1, *jsoned2, *jsoned3]

jsoned = sorted(temp, key=lambda x: datetime.strptime(
    x['time'][:10], '%Y-%m-%d'))


def strip_it(string):
    if string.startswith("Visited "):
        string = string[8:]
    elif string.startswith("Searched for "):
        string = string[13:]
    elif string.startswith("Watched "):
        string = string[8:]
    if string.startswith("http"):
        string = None
    return string

data_dict = {}
for i, item in enumerate(jsoned):
    item_str = strip_it(item['title'])
    if item_str is None:
        continue
    data_dict[(datetime.strptime(item['time'][:10], '%Y-%m-%d'), i)] = item_str

with open("./data.pkl", 'wb') as fh:
    pickle.dump(data_dict, fh)
