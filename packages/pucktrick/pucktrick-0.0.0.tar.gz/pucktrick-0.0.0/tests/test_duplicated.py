import unittest
from pucktrick.duplicated import *
from pucktrick.utils import *
import pandas as pd
import numpy as np
from pandas.testing import assert_frame_equal


class Test_outlies(unittest.TestCase):
 
 def test_duplicateClassExtended(self):
      percentage=0.5
      num_rows = 1000
      fake_df=create_fake_table(num_rows)
      target='f3'
      value='banana'
      old_len=len(fake_df[fake_df[target]==value])
      new_percentage=0.7
      config=create_json_for_feature( new_percentage, "new")
      strategy = config.get("strategy", {})
     
      noise_df=duplicate(fake_df,strategy)
      new_len=len(noise_df[noise_df[target]==value])
      diff=round((new_len-old_len)/old_len,1)
      self.assertEqual(diff, new_percentage)
  
 def test_duplicateAllExtended(self):
      percentage=0.5
      num_rows = 1000
      fake_df=create_fake_table(num_rows)
      config=create_json_for_feature( percentage, "new")
      strategy = config.get("strategy", {})
      noise_df=duplicate(fake_df,strategy)
      new_percentage=0.7
      config=create_json_for_feature( new_percentage, "extended")
      strategy = config.get("strategy", {})
      
      noise_df=duplicate(noise_df,strategy,fake_df)
      new_len=len(noise_df)
      diff=(new_len-num_rows)/num_rows
      self.assertEqual(diff, new_percentage)

if __name__ == "__main__":
    unittest.main()
