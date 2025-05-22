
import numpy as np
import pandas as pd

from pandas import Series, DataFrame

#------------------------------------------------------------------------------#

"""
1. Creating pd.DataFrame(data=, columns=[], index=[]) object:
    - 'data': a dictionary of equal-length lists or NumPy arrays
        - each key-value pair is a column, according the insertion order
        - index (row names) will be auto assigned w/o assignment, column names are keys of the passed dictionary
    - 'columns': a list of column names, with datatype 'Index' object
    - 'index': a list of column names, with datatype 'Index' object
"""

# (1) Create by passing a pre-defined data dictionary (key-value pairs)
"""keys as col_names 'columns', auto assign row_names 'index' starting from 0
"""

data = {"state": ["Ohio", "Ohio", "Ohio", "Nevada", "Nevada", "Nevada"],
        "year": [2000, 2001, 2002, 2001, 2002, 2003],
        "pop": [1.5, 1.7, 3.6, 2.4, 2.9, 3.2]}
frame = pd.DataFrame(data)

print(f'\n{frame}\n')

# (2) Create by passing both 'data' and 'columns' attributes, overriding occurs

frame2 = pd.DataFrame(data=data, columns=["year", "state", "pop", "debt"])

print(f'\n{frame2}\n')
"""new columns that never have been created will contain missing values NaN"""

# (3) Create by passing a dictionary of dictionaries
"""outer dictionary keys as col_names 'columns',
   inner dictionary keys as row_names 'index' 
"""

populations = {"Ohio": {2000: 1.5, 2001: 1.7, 2002: 3.6},
               "Nevada": {2001: 2.4, 2002: 2.9}}
frame3 = pd.DataFrame(data = populations)

print(f'The frame3 is:\n{frame3}\n')

# (4) Create by passing 'data', 'columns', and 'index' attributes. Overriding occurs

frame4 = pd.DataFrame(data = populations, index = [2001, 2002, 2003])

print(f'The frame4 is:\n{frame4}\n')

#Display the 'columns' attribute
print(f'The frame4.columns attribute is:\n{frame4.columns}\ntype of frame4.columns is:\n{type(frame4.columns)}\n')
#Display the 'index' attribute
print(f'The frame4.index attribute is:\n{frame4.index}\ntype of frame4.columns is:\n{type(frame4.index)}\n')


#------------------------------------------------------------------------------#

"""
2. Operations

    (1) Display rows of pd.DataFrame object:
        - pd.DataFrame.head(number) method:
            Display the first number of rows
        - pd.DataFrame.tail(number) method:
            Display the last number of rows
    
    (2) Selection (Slicing): 

        - Retrieve columns of pd.DataFrame object:
            * Approach 1: By indexing
                pd.DataFrame[col_name]
            * Approach 2: By dot attribute notation
                pd.DataFrame.col_name
        
        - Retrieve rows or specific elements:
            * Approach 1:'loc' attribute (label-based indexing)
                pd.DataFrame.loc[row_name, col_name]
            * Approach 2:'iloc' attribute (integer-based indexing)
                pd.DataFrame.iloc[row_num, col_num]
                Note: [row_num, col_num] is a position
            * Approach 3: directly use indexing on the pd.DataFrame
                - Retrieve rows: pd.DataFrame[:], column slicing, returns a pd.DataFrame type subset
                - Retrieve columns: pd.DataFrame[col_name], label-indexing, returns a pd.Series; OR pd.DataFrame.iloc[:, :]
                - Retrieve subset: pd.DataFrame.iloc[:, :], [row_slicing, column_slicing], returns a pd.DataFrame type subset
                - Retrieve an element: pd.DataFrame[col_name][row_name]

    (3) Altering columns: insert new values, replace values, delete values
        
        - Assign new values:
            Approach 1: indexing (for both existing and non-existing columns)
            (alter the object itself and returns a view, rather than a copy)
                * by passing a list of values, directly (the same length)
                * by passing a pre-defined 1-D NumPy ndarray (a list of values of the same length)
                * by passing a pre-defined pandas.Series object (a list of values of the same length)
                * Assign boolean values by passing a condition statement: 
            Approach 2: Dot attribute notation (only for existing columns)
        
        - delete columns:
            del method
    
    (4) Transpose: swap rows and columns of existing pd.DataFrame
        
        by pd.DataFrame.T method
    
"""

# (1) Display rows: pd.DataFrame.head(number), and pd.DataFrame.tail(number) methods

print(f'\n{frame.head(3)}\n')

print(f'\n{frame.tail(2)}\n')

# (2) Selection (Slicing), subset

""" Retrieve columns:
    returns in the form of a pd.Series object, which name is the col_name
"""

# Approach 1: Indexing by col_name
print(f'\n{frame2["state"]}\n') # KeyError if retrieve a col that does not exist (DNE)

# Approach 2: Dot Attribute Notation
print(f'\n{frame2.state}\n') # works only when no symbols/whitespaces

""" Retrieve rows:
    returns in the form of a pd.Series object, by special location attribute 'loc' and 'iloc' of the pd.DataFrame object.
"""
# Approach 1:'loc' attribute (label-based indexing)
# Approach 2:'iloc' attribute (integer-based indexing)

print(f'\n{frame2.loc[1]}\n')
print(f'\n{frame2.iloc[1]}\n')

print(f'\n{frame2.iloc[1, 2]}\n') # integer-based indexing
print(f'\n{frame2.loc[1, "pop"]}\n') # label-based indexing

""" Retrieve subset of the pd.DataFrame: Slicing for multiple times
    - returns interested part (rows, cols, or subset of the original DataFrame).
    - directly by label-based indexing on the pd.DataFrame
"""

print(f'\nThe interested frame3 is:\n{frame3[:]}\n')  

# pd.Series-like: Retrieve a part of a column (get a column vector first (pd.Series), then slicing it by integer-indexing)
print(f'\nThe interested column slice of frame3 is:\n{frame3["Ohio"][:-1]}\n') #returns a pd.Series, containing a column "ohio" from row 0 to -1

# pd.Series-like: Retrieve a subset of the pd.DataFrame, returns a pd.DataFrame type (integer-indexing slicing)
print(f'\nThe interested subset of frame3 is:\n{frame3[:-1][:-1]}\nThe type of this subset is:\n{type(frame3[:-1][:-1])}') 

# Retrieve a subset of the pd.DataFrame, returns a pd.DataFrame type (integer-indexing slicing)
print(f'\nThe interested row slice of frame3 is:\n{frame3.iloc[1][:-1]}\nThe type of this subset is:\n{type(frame3.iloc[1][:-1])}')  

# Retrieve a subset of the pd.DataFrame, returns a pd.DataFrame type (integer-indexing slicing)
print(f'\nThe interested subset of frame3 is:\n{frame3.iloc[:-1, :-1]}\nThe type of this subset is:\n{type(frame3[:][:-1])}')  

# Retrieve an element (label-indexing)
print(f'\nThe interested element of frame3 is:\n{frame3["Ohio"][2002]}\nThe type of this returned element is:\n{type(frame3["Ohio"][2002])}') #returns an element at position [Ohio, 2002]


# (3) Altering columns values by assignment

#--Assign new values
frame2["debt"] = 16.5 #assign 16.5 to the entire col 'debt'
print(f'\n{frame2}\n')

#--Assign new values by numpy.arange() method: returns a 1-D ndarray
dt = np.arange(start=0., stop=6., step=1)
print(f'the numpy array dt is: \n{dt}\ntype is: \n{type(dt)}\nshape is: \n{dt.shape}\n')

frame2["debt"] = np.arange(start=0., stop=6., step=1) #numpy object method arange
print(f'\n{frame2}\n') 

#--Assign new values by passing a pre-defined pandas.Series object
val = pd.Series([-1.2, -1.5, -1.7], index=["two", "four", "five"]) #new index never present, will insert NaN values
frame2["debt"] = val

print(f'\n{frame2}\n') 

val = pd.Series([-1.2, -1.5, -1.7]) 
frame2["debt"] = val

print(f'\n{frame2}\n') 

#--Assign boolean values by passing a condition statement:
frame2["eastern"] = frame2["state"] == 'Ohio' 

print(f'\n{frame2}\n') 
"""This create a new col, since we declared a new col. 
    cannot use the dot attribute notation to create a new col, since this new col DNE for now"""

print(frame2.index[1])
print(type(frame2.index))

# (3) Delete a column: del method

del frame2["eastern"]

print(f'\n{frame2}\n') 

# (4) Transpose the pd.DataFrame by pd.DataFrame.T method

print(f'The transpose of frame3 is:\n{frame3.T}\n')
"""This alter the different columns data type to pure Python objects, losing previoous data type info"""

# (5) Tranform the pd.DataFrame to a 2-dim NumPy ndarray by the to_numpy() method
print(f'The original frame3 is:\n{frame3}\n')
print(f'After transformation:\n{frame3.to_numpy()}\n')

print(f'The original frame2 is:\n{frame2}\n')
print(f'After transformation:\n{frame2.to_numpy()}\n')

#------------------------------------------------------------------------------#

"""
3. 'name' attribute

    - The pd.DataFrame itself does not have a name attribute
    - 'name' attribute of 'index' attribute: pd.DataFrame.index.name
    - 'name' attribute of 'columns' attribute: pd.DataFrame.columns.name
"""

# 
frame3.index.name = "year"
frame3.columns.name = "state"

print(f'The resulting frame3 is:\n{frame3}\n')

