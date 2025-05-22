
import numpy as np
import pandas as pd
from pandas import Series, DataFrame
#------------------------------------------------------------------------------#
"""

    Data Structures in pandas: 

    1. pandas.Series
        Series is a one-dim array-like object, containing a squence of values & an associated array of data labels (index)
        - pd.Series(array, index): an object with two attributes 'array' (values) and 'index' (labels)

    2. pandas.DataFrame

"""

#------------------------------------------------------------------------------#

"""1. Creating a pd.Series """

# (1) Approach 1: Declare the 'array' attribute only, with default 'index' starting from 0

obj = pd.Series([4, 7, -5, 3])

print(f"The pandas Series is: \n{obj} \n")

""" attributes:
    - 'array': values
    - 'index': labels
        - 'name': attribute of the attribute 'index', name of the 'index' array
    - 'name': name of this pd.Series object
"""
#display 'array' (values) and 'index' (labels) attribute of the pd.Series
print(f"The array attribute is: \n{obj.array} \n")
print(f"The index part is: \n{obj.index} \n")

# (2) Approach 2: Declare both the 'array' and 'index' attributes

obj2 = pd.Series([4, 7, -5, 3], index = ["d", "b", "a", "c"], name = "numbers")

print(f"The pandas Series is: \n{obj2} \n")

# (3) Approach 3: Creating a pd.Series by passing a pre-defined Python dictionary
#pd.Series can be seen as a set of key-value pairs, I.e. dictionary-like, keys are 'index', values are 'array'

sdata = {"Ohio": 35000, "Texas": 71000, "Oregon": 16000, "Utah": 5000}
obj3 = pd.Series(sdata)

#use dot notation to assign values to 'name'
obj3.name = "population1"
obj3.index.name = "states"

print(f"obj3 is: \n{obj3}\n")

# (4) Approach 4: Overriding exists if passing 'array' is a dictionary containing keys as 'index', and passing 'index' is different w/ keys. I.e., declared 'index' twice when creating

states = ["California", "Ohio", "Oregon", "Texas"]
obj4 = pd.Series(sdata, states, name = "population2")

obj4.index.name = "states"
print(f"obj4 is: \n{obj4}\n")

"""Note: there'll exist NaN if new index name is declared """

#------------------------------------------------------------------------------#

"""2. Indexing"""

# (1) Access one or multiple values by indexing
print(f'obj2["d"] is: \n{obj2["d"]}\n')
print(f'obj2[["c", "a", "d"]] is: \n{obj2[["c", "a", "d"]]}\n')

# (2) Alter 'array'(labels) values by indexing
obj2["d"] = 6
print(f'After altering obj2["d"] = 6, the pandas Series is: \n{obj2} \n')

# (3) Alter 'index' values by assignment
obj.index = ["Bob", "Steve", "Jeff", "Ryan"]
print(f'After altering obj.index, the pandas Series is: \n{obj} \n')

#------------------------------------------------------------------------------#

"""3.  NumPy-like Operations """

# (1) Filtering with a Boolean array
print(f'\n{obj2[obj2 > 0]}\n')
print(f'\n{obj2[obj2 > 3]}\n')

# (2) Scalar Multiplication
print(f'\n{obj2 * 2}\n')

# (3) Using NumPy Functions on pd.Series object
print(f'\n{np.exp(obj2)}\n')
print(obj2)

# (4) Checking existence of an index within a pd.Series
print("b" in obj2)
print("e" in obj2)

#------------------------------------------------------------------------------#

"""4. pd.Series Object Methods""" 

# (1) to_dict() method: Convert the pd.Series to a dictionary

print(obj3.to_dict())

# (2) isna() method: detect missing value NaN, same as the isna(obj) function

print(obj4.isna())

#------------------------------------------------------------------------------#

"""5. pandas functions """

# (1) isna(obj) & notna(obj): detect missing values NaN
""" returns the pd.Series with boolean values as the 'array' attribute values """

print(pd.isna(obj4))
      
print(pd.notna(obj4))

# (2)

#------------------------------------------------------------------------------#

"""6. Arithmetic operations """

# (1) data alignment feature
""" automatical data alignment feature: similar to join operation
    auto conducting calculations at the right position by aligning 'index' labels"""

obj3 + obj4
