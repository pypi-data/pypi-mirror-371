import unittest
from pucktrick.missing import *
from pucktrick.utils import *
import pandas as pd
import numpy as np
from pandas.testing import assert_frame_equal

class Test_outlies(unittest.TestCase):
  def test_MissingAll(self):
      percentage=0.5
      num_rows = 1000
      fake_df=create_fake_table(num_rows)
      target='f3'
      null_values=fake_df[target].isna().sum()
      strategy =  {'affected_features': 'f3', 'selection_criteria': 'all', 'percentage': 0.5, 'mode': 'new', 'perturbate_data': {'distribution': 'random', 'param': None, 'value': None, 'condition_logic': None}}
      noise_df=missing(fake_df,strategy)
      percentage=0.7
      strategy =  {'affected_features': 'f3', 'selection_criteria': 'all', 'percentage': 0.7, 'mode': 'extended', 'perturbate_data': {'distribution': 'random', 'param': None, 'value': None, 'condition_logic': None}}
      noise_df=missing(noise_df,strategy,fake_df)
      new_null_values=noise_df[target].isna().sum()
      if null_values>0:
        diff=round((new_null_values-null_values)/null_values,2)
        self.assertEqual(diff, percentage)
      else:
          df_len=len(noise_df)
          rows=int(df_len*percentage)
          self.assertEqual(new_null_values, rows)


if __name__ == "__main__":
    unittest.main()
