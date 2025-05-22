
import numpy as np
import pandas as pd

from pandas import Series, DataFrame, Index

#------------------------------------------------------------------------------#

"""

Index Objects:
    
    pandas' objects that hold axis labels

    1. Any array or squence of labels are internally converted to an Index Object, when creating pd.Series or pd.DataFrame

    2. Index Object is immutable (o/w 'TypeError' will occur)
"""

"""

1. Create an pd.Index object:
    
    - Approach 1: 'index' attribute internally converted when creating a pd.Series or a pd.DataFrame

    - Approach 2: Create a pd.Index object directly by pd.Index(1-D array)
        We can pass this pre-defined pd.Index object to the pd.Series or pd.DataFrame as the 'index' attribute

2. 
"""
# 1. Create a pd.Index object

# Approach 1: Auto ('index' attribute internally converted) create an Index Object when constructing a pd.Series OR a pd.DataFrame

obj = pd.Series(np.arange(3), index = ["a", "b", "c"])
index = obj.index

print(f'\nThe pd.Series object is:\n{obj}\nThe associated Index attribute is:\n{index}\n')

# Approach 2:

labels = pd.Index(np.arange(3))

print(f'\nThe defined pd.Index object is:\n{labels}\n')
obj2 = pd.Series([1.5, -2.5, 0], index=labels)
print(f'\nThe resulting pd.Series obj2 is:\n{labels}\n')

# 2. pd.Index operations

# (1) Slicing the Index Object by integer-based indexing

print(f'\nindex[1:] is:\n{index[1:]}\n')

# (2) Index Object are immutable -> TypeError: Index does not support mutable operations
#index[1] = "d" 

# (3) Check 

# Check the type & values of the 'index' attribute of a pd.Series, by the 'is' keyword

print(f'\n{obj2.index is labels}\n')

# Both 'index' and 'columns' attributes of a pd.DataFrame are pd.Index 

populations = {"Ohio": {2000: 1.5, 2001: 1.7, 2002: 3.6}, "Nevada": {2001: 2.4, 2002: 2.9}}
frame3 = pd.DataFrame(data=populations)
print(f'\nThe frame3 is:\n{frame3}\n')

print(f'\nThe frame3.columns is:\n{frame3.columns}\n\nThe frame3.index is:\n{frame3.index}\n')

# Check for pd.DataFrame
print(f'\n{"Ohio" in frame3.columns}\n')
print(f'\n{2003 in frame3.index}\n')

# pd.Index can contain duplicate labels
"""When conducting selections, it returns all occurrences of that label"""

print(f'{pd.Index(["foo", "foo", "bar", "bar"])}')

# 3. pd.Index object Methods for set logic
"""
    1. append()
    2. difference()
    3. intersection()
    4. union()
    5. isin()
    6. delete()
    7. drop()
    8. insert()
    9. is_monotonic
    10.is_unique
    11.unique()

"""