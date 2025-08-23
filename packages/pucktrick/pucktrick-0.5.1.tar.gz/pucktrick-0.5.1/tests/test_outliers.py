import unittest
from pucktrick.outliers import *
from pucktrick.utils import *
import pandas as pd
import numpy as np
from pandas.testing import assert_frame_equal

class Test_outlies(unittest.TestCase):
  
  def test_outliers(self):
        percentage=0.5
        num_rows = 1000
        fake_df=create_fake_table(num_rows)
        column='date'
        strategy =  {'affected_features': column, 'selection_criteria': 'all', 'percentage': percentage, 'mode': 'new', 'perturbate_data': {'distribution': 'random', 'param': None, 'value': None, 'condition_logic': None}}
        noise_df=outlier(fake_df,strategy)
        dif = fake_df[column] != noise_df[column]
        diff_number = dif.sum()
        percentage=0.7
        strategy =  {'affected_features': column, 'selection_criteria': 'all', 'percentage':percentage, 'mode': 'extended', 'perturbate_data': {'distribution': 'random', 'param': None, 'value': None, 'condition_logic': None}}
        noise_df=outlier(noise_df,strategy,fake_df)
        dif = fake_df[column] != noise_df[column]
        diff_number = dif.sum()
        diff_p=diff_number/num_rows
        self.assertEqual(diff_p, percentage)
  
    


if __name__ == "__main__":
    unittest.main()
