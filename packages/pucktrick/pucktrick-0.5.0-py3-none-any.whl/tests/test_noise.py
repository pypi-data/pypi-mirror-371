import unittest
from pucktrick.noisy import *
from pucktrick.utils import * 
import pandas as pd
from pandas.testing import assert_frame_equal
class TestCategorical(unittest.TestCase):
    def test_saluta(self):
        percentage=0.5
        num_rows = 1000
        fake_df=create_fake_table()
        column='f3'
        strategy =  {'affected_features': 'f3', 'selection_criteria': 'all', 'percentage': 0.5, 'mode': 'new', 'perturbate_data': {'distribution': 'random', 'param': None, 'value': None, 'condition_logic': None}}
        noise_df=noise(fake_df,strategy)
        dif = fake_df[column] != noise_df[column]
        diff_number = dif.sum()
        percentage=0.7
        strategy =  {'affected_features': 'f3', 'selection_criteria': 'all', 'percentage': 0.7, 'mode': 'extended', 'perturbate_data': {'distribution': 'random', 'param': None, 'value': None, 'condition_logic': None}}
        noise_df=noise(noise_df,strategy,fake_df)
        dif = fake_df[column] != noise_df[column]
        diff_number = dif.sum()
        diff_p=diff_number/num_rows
    
        # Verifica che il numero di modifiche sia corretto
        self.assertEqual(diff_p, percentage)
    


if __name__ == "__main__":
    unittest.main()
