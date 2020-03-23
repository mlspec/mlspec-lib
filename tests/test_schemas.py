from unittest import TestCase
from mlspeclib import mlspeclib, core, helpers

# use_data = pd.read_csv('mlpsec/data/iris.csv')

'''
def test_encode_and_bind():
    s = utilities.encode_and_bind(use_data, 'sepal_length')
    assert isinstance(s, pd.DataFrame)
    
def test_remove_features():
    s = utilities.remove_features(use_data, ['sepal_length','sepal_width'])
    assert s.shape[1] == 3
    
def test_apply_function_to_column():
    s = utilities.apply_function_to_column(use_data, ['sepal_length'], 'times_4', 'x*4')
    assert s['sepal_length'].sum() * 4 == 3506.0

def test_get_closest_string(): 
    s = utilities.get_closest_string(['hey there','we we are','howdy doody'], 'doody')
    assert s == 'howdy doody'

'''