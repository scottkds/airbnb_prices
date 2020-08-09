#!/usr/bin/env python
# coding: utf-8

# In[22]:


# Imports
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import json
import re
import matplotlib.pyplot as plt
import seaborn as sns

# Scikit-learn
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.linear_model import LinearRegression, LassoCV, RidgeCV, Lasso, Ridge
from sklearn.preprocessing import StandardScaler, PolynomialFeatures, FunctionTransformer, normalize
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.pipeline import make_pipeline
from sklearn.metrics import mean_squared_error, r2_score

# Others
from sklearn_pandas import DataFrameMapper
import statsmodels.api as sm


# In[28]:


# Globals
SEED = 42


# In[2]:


# Read in room data
rooms = pd.read_csv('../data/room_data.csv')
rooms = rooms.drop_duplicates()
rooms['isSuperhost'] = rooms['isSuperhost'].astype(int)
rooms['avgRating'] = rooms['avgRating'].fillna(rooms['avgRating'].mean())
rooms = rooms.set_index('id')
rooms.info()


# In[3]:


# Check our dataframe contents.
rooms.head()


# In[4]:


# Read in amenities data from a json object.
with open('../data/amenities_strings.json', 'r') as f:
    amenities_dict = json.load(f)


# In[5]:


# Convert each entry in the amenities_dict to a document. Replace spaces with underscores
# any other non-alphanumeric character with and underscore.
corpus = []
key_list = []
for key, word_list in amenities_dict.items():
    
    try:
        integer_key = int(key)
        key_list.append(integer_key)
    except Exception as e:
        raise e
    cleaned_word_list = [re.sub(r'(\s+|\W+)', '_', doc) for doc in word_list]
    document = ' '.join(cleaned_word_list)
    corpus.append(document)


# In[6]:


# Fit a CountVectorizer
cv = CountVectorizer()
amenities_vec = cv.fit_transform(corpus)
cv.get_feature_names()[:5]


# In[7]:


# Convert transformed CountVecortizer data to a DataFrame with room ids as
# the index.
amenities_vec = amenities_vec.toarray()
amenities = pd.DataFrame(amenities_vec, index=key_list)
amenities.head()


# In[8]:


# Validate that the length of the imput list of amenities is equal to the sum
# of the amenities in the row for the equivalent id.
for key, val in amenities_dict.items():
    assert len(val) == sum(amenities.loc[int(key)])


# In[19]:


# Compare correlation values for price and log of the price with the features before
# and after taking the log of the feaures.
# price_r and log_price_r os the correlation to normal features.
# price_l and log_price_l is for the correlation with the log of the features. 
fields_to_compare = ['price', 'log_price',  'bedrooms', 'beds', 'bathrooms','personCapacity',
                     'reviewsCount', 'isSuperhost', 'avgRating', 'cleaning_fee']
log_rooms = rooms[fields_to_compare].copy()
features_to_log = ['bedrooms', 'beds', 'bathrooms', 'personCapacity', 'cleaning_fee']
for feature in features_to_log:
    log_rooms[feature] = np.log1p(log_rooms[feature])
r = rooms[fields_to_compare].corr()
l = log_rooms.corr()
features = ['price', 'log_price']
r[features].merge(l[features], left_index=True, right_index=True, suffixes=('_r', '_l'))


# **Based on the correlation values above price will be fit with the following features:**  
# log of bedrooms  
# log of beds  
# log of bathrooms  
# log of personCapacity  
# reviewsCount - low correlation so likely noise  
# isSuperhost - low correlation so likely noise  
# avgRating - low correlation so likely noise  
# cleaning_fee  

# In[ ]:


X_train, X_test, y_train, y_test = train_test_split(rooms)


# In[23]:


rooms.head()


# In[27]:


# Create DataFrames for train_test_split.
# One unchanged from original data as a control.
# One with the log of the selected features.
logs = ['bedrooms', 'beds', 'bathrooms', 'personCapacity']
X_r = rooms.drop(['price', 'log_price', 'lat', 'lng'], axis=1)
y_r = rooms['price']
X_l = rooms.drop(['price', 'log_price', 'lat', 'lng'], axis=1)
for item in logs:
    X_l[item] = np.log1p(X_l[item])
y_l = rooms['price']


# In[35]:


Xr_train, Xr_test, yr_train, yr_test = train_test_split(X_r, y_r, test_size=0.2, random_state=SEED, stratify=np.floor(np.log2(y_r)))
Xl_train, Xl_test, yl_train, yl_test = train_test_split(X_l, y_l, test_size=0.2, random_state=SEED, stratify=np.floor(np.log2(y_l)))


# In[33]:





# In[ ]:




