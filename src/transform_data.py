import pandas as pd
import json
from glob import glob
from sklearn.feature_extraction.text import CountVectorizer

path = '/home/scott/projects/mp2/src/saved/'
room_files = glob(path + 'room_data*')
amenities_files = glob(path + 'amenities_data*')

frames = []
for file in room_files:
    try:
        print(file)
        with open(file, 'r') as f:
            json_dict = json.load(f)
            for key, val in json_dict.items():
                print(key, len(val))
            frame = pd.DataFrame(json_dict)
            frames.append(frame)
    except Exception as e:
        raise e

rooms_frame = pd.concat(frames)

print(rooms_frame.head())
print(rooms_frame.info())

corpus = []
ids = []
elements = []
for file in amenities_files:
    try:
        print(file)
        with open(file, 'r') as f:
            json_dict = json.load(f)
            for key, val in json_dict.items():
                ids.append(key)
                elements.append(val)
                list_of_amenitites = ' '.join([amenity.replace(' ', '_') for amenity in val])
                corpus.append(list_of_amenitites)
    except Exception as e:
        raise e

cv = CountVectorizer()
amenities = cv.fit_transform(corpus)
amenities = pd.DataFrame(amenities.toarray(), columns=cv.get_feature_names(), index=ids)

print(amenities.head())

for idx, row in amenities.reset_index().iterrows():
    print(len(elements[idx]), sum(row[1:]))
    assert row['index'] == ids[idx]
    #assert sum(row[1:]) == len(elements[idx])
