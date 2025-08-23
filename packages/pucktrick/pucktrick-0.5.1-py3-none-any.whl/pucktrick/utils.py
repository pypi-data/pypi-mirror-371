import unittest
from pucktrick.utils import *
import pandas as pd
import numpy as np
from pandas.testing import assert_frame_equal
import random
import json
from datetime import timedelta
from dateutil import parser
import string

def create_fake_table(num_rows=1000):
  # Generate data for each column
  f1 = np.random.uniform(-100, 100, num_rows)  # Continuous values between -100 and 100
  f2 = np.random.randint(-100, 101, num_rows)  # Discrete values between -100 and 100
  f3 = np.random.choice(['apple', 'banana', 'cherry'], num_rows)  # String values
  f4 = np.random.choice(['apple', 'banana', 'cherry'], num_rows)  # String values
  f5 = np.random.choice([0, 1,2,3,4,5], num_rows)  # Binary values (0 or 1)
  delta_days = (pd.to_datetime('2030-12-31') - pd.to_datetime('1970-01-01')).days
  random_days = np.random.randint(0, delta_days, num_rows)
  random_dates = pd.to_datetime('1970-01-01') + pd.to_timedelta(random_days, unit='D')
  date = random_dates  # Restituisce direttamente una Series di tipo datetime.date
  # date between 1970-01-01 and 2030-12-31
  target = np.random.choice([0, 1], num_rows)  # Binary target (0 or 1)

  # Create the DataFrame
  df = pd.DataFrame({
    'f1': f1,
    'f2': f2,
    'f3': f3,
    'f4': f4,
    'f5': f5,
    'date' : date,
    'target': target
  })
  df['date'] = pd.to_datetime(df['date'])
  return df

def generateSubdf(original_df, train_df,column,percentage ):
    rowsToChange=len(original_df[column])*percentage
    dif = original_df[column] != train_df[column]
    diff_number = dif.sum()
    new_rowsToChange=rowsToChange-diff_number
    if new_rowsToChange<=0:
      newPercentage=0
      return train_df,newPercentage
    noise_df= train_df.copy()
    noise_df['id1'] = range(len(noise_df))
    or_df=original_df.copy()
    or_df['id1'] = range(len(or_df))
    mask = or_df[column] == noise_df[column]
    new_df = noise_df[mask]
    new_df = new_df.reset_index(drop=True)
    newPercentage=new_rowsToChange/len(new_df)
    return new_df,newPercentage

def mergeDataframe(noise_df,modified_df):
    merged_df = noise_df.merge(modified_df, on='id1', how='left', suffixes=('_df1', '_df2'))
    new_array = [string for string in noise_df.columns if string != 'id1']
    for col in new_array:
      noise_df[col] = merged_df[col + '_df2'].fillna(merged_df[col + '_df1'])
    noise_df = noise_df.drop('id1', axis=1)
    return noise_df

def generate_random_value(lower, upper):
        return np.random.uniform(lower, upper)

def generate_random_value_discrete(lower, upper):
        return np.random.randint(lower, upper)

def sampleList(percentage, data_length):
    num_samples = int(percentage * data_length) 
    return np.random.choice(data_length, size=num_samples, replace=False)
  
def sample_indices(distribution, data_length, percentage=None, number=None, params=None):
    if percentage is None:
      num_samples = number
    elif number is None:
      num_samples = int(len(data_length) * percentage)  # use data_length directly
    params = params or {}
    #print(percentage)

    if distribution == "random":
        # Change: use len(data_length) to get the size for random sampling
        return np.random.choice(len(data_length), num_samples, replace=False)

    elif distribution == "uniform":
        min_val = params.get("min", 0)
        max_val = params.get("max", len(data_length) - 1)  # data_length
        return np.random.uniform(min_val, max_val, num_samples).astype(int)

    elif distribution == "normal":
        mu = params.get("mu", len(data_length) / 2)  # data_length
        sigma = params.get("sigma", len(data_length) / 6)  # data_length
        samples = np.random.normal(mu, sigma, num_samples)
        samples = np.clip(samples, 0, len(data_length) - 1)  # data_length
        return samples.astype(int)

    elif distribution == "exponential":
        lambd = params.get("lambda", 1.0)
        samples = np.random.exponential(1 / lambd, num_samples)
        samples = (samples / np.max(samples)) * (len(data_length) - 1)  # data_length
        return samples.astype(int)

    else:
        raise ValueError(f"Distribuzione '{distribution}' non supportata.")

def noiseBinaryNew(train_df, target, distribution, percentage , number, params):
    noise_df = train_df.copy()
    #indices_to_modify = sampleList(percentage, len(train_df[target]))
    indices_to_modify= sample_indices(distribution, train_df, percentage, number, params)
    #print(indices_to_modify)
    for i in indices_to_modify:
        noise_df.at[i, target] = 1 - noise_df.at[i, target]  
    return noise_df

def noiseBinaryExt(original_df, train_df, target, distribution,percentage,number,params):
    noise_df = train_df.copy()
    noise_df['id1'] = range(len(noise_df))  
    new_df, newPercentage = generateSubdf(original_df, noise_df, target, percentage)
    if newPercentage == 0:
        return train_df
    modified_df = noiseBinaryNew(new_df, target, distribution, newPercentage,number, params)
    noise_df = mergeDataframe(noise_df, modified_df)
    return noise_df

def noiseCategoricalStringNewExistingValues(train_df, column, distribution, percentage , number, params):
    #extracted_indices = sampleList(percentage, len(train_df[column]))
    extracted_indices = sample_indices(distribution, train_df[column], percentage=None, number=None, params=None)
    noise_df = train_df.copy()
    unique_values = noise_df[column].unique()

    for i in extracted_indices:
        while True:
            new_value = np.random.choice(unique_values)
            if new_value != noise_df.loc[i, column]:
                noise_df.loc[i, column] = new_value
                break
    return noise_df

def noiseCategoricalIntNewExistingValues(train_df, target,  distribution, percentage , number, params):
    noise_df = train_df.copy()
    #indices_to_modify = sampleList(percentage, len(train_df[target]))
    indices_to_modify= sample_indices(distribution, train_df[target], percentage=None, number=None, params=None)
    unique_values = train_df[target].unique()
    for i in indices_to_modify:
        current_value = noise_df.at[i, target]
        new_value = np.random.choice([v for v in unique_values if v != current_value])
        noise_df.at[i, target] = new_value
    return noise_df

def noiseCategoricalIntExtendedExistingValues(original_df, train_df, target, distribution,percentage,number,params):
    noise_df = train_df.copy()
    noise_df['id1'] = range(len(noise_df))  # Aggiunta della colonna 'id1'
    new_df, newPercentage = generateSubdf(original_df, noise_df, target, percentage)
    if newPercentage == 0:
        return train_df
    modified_df = noiseCategoricalIntNewExistingValues(new_df, target, distribution, newPercentage,number, params)
    noise_df = mergeDataframe(noise_df, modified_df)
    return noise_df

def noiseCategoricalStringNewFakeValues(train_df, column, distribution,percentage,number,params):
    #extracted_list = sampleList(percentage, len(train_df))
    extracted_list= sample_indices(distribution, train_df, percentage=None, number=None, params=None) # Cambia qui per selezionare casualmente
    noise_df = train_df.copy()
    for i in extracted_list:  # Usa extracted_list per modificare solo i campioni
        noise_df.loc[i, column] = ''.join(np.random.choice(list('abcdefghijklmnopqrstuvwxyz'), size=5))
    return noise_df

def noiseCategoricalStringExtendedFakeValues(original_df, train_df, column, distribution,percentage,number,params):
    noise_df = train_df.copy()
    noise_df['id1'] = range(len(noise_df))
    new_df, newPercentage = generateSubdf(original_df, noise_df, column, percentage)
    if newPercentage == 0:
        return train_df

    modified_df = noiseCategoricalStringNewFakeValues(new_df, column, distribution,newPercentage,number,params)
    noise_df = mergeDataframe(noise_df, modified_df)

    # Rimuovi la colonna 'id1' temporanea se esiste
    if 'id1' in noise_df.columns:
        noise_df = noise_df.drop('id1', axis=1)

    return noise_df

# Funzione per aggiungere rumore discreto (normal)
def noiseDiscreteNew(train_df, column, distribution,percentage,number,params):
    #extracted_indices = sampleList(percentage, len(train_df[column]))
    extracted_indices= sample_indices(distribution, train_df[column], percentage=None, number=None, params=None)
    noise_df = train_df.copy()
    min_value = noise_df[column].min()
    max_value = noise_df[column].max()

    for i in extracted_indices:
        while True:
            new_value = random.randint(min_value, max_value)
            if new_value != noise_df.loc[i, column]:
                noise_df.loc[i, column] = new_value
                break
    return noise_df

# Funzione per aggiungere rumore continuo (normal)
def noiseContinueNew(train_df, column, distribution,percentage,number,params):
    #extracted_indices = sampleList(percentage, len(train_df[column]))
    extracted_indices= sample_indices(distribution, train_df[column], percentage=None, number=None, params=None)
    noise_df = train_df.copy()
    min_value = noise_df[column].min()
    max_value = noise_df[column].max()

    for i in extracted_indices:
        while True:
            new_value = random.uniform(min_value, max_value)
            if new_value != noise_df.loc[i, column]:
                noise_df.loc[i, column] = new_value
                break
    return noise_df

def outlierContinuosNew3Sigma(train_df, column, distribution,percentage,number,params):
    #extracted_list = sampleList(percentage, len(train_df[column]))
    extracted_list= sample_indices(distribution, train_df[column], percentage=None, number=None, params=None)
    noise_df = train_df.copy()
    mean = np.mean(noise_df[column])
    std_dev = np.std(noise_df[column])
    upper_bound = mean + 3 * std_dev
    lower_bound = mean - 3 * std_dev
    new_lower_limit = mean - 4 * std_dev
    new_upper_limit = mean + 4 * std_dev

    for i in extracted_list:
        if np.random.rand() > 0.5:
            noise_df.loc[i, column] = generate_random_value(upper_bound, new_upper_limit)
        else:
            noise_df.loc[i, column] = generate_random_value(new_lower_limit, lower_bound)

    return noise_df


def outlierDiscreteNew3Sigma(train_df,column,distribution,percentage,number,params):
  #extracted_list=sampleList(percentage,len(train_df[column]))
  extracted_list= sample_indices(distribution, train_df[column], percentage=None, number=None, params=None)
  noise_df= train_df.copy()
  mean = np.mean(noise_df[column])
  std_dev = np.std(noise_df[column])
  upper_bound=round(mean + 3 * std_dev,0)
  lower_bound=round(mean -3 * std_dev,0)
  new_upper_limit = round(mean + 4 * std_dev,0)
  new_lower_limit = round(mean - 4 * std_dev,0)
  if upper_bound==0:
     upper_bound=1
  if new_upper_limit==upper_bound:
     new_upper_limit=5*upper_bound

  if lower_bound==0:
     lower_bound=-1
  if new_lower_limit==lower_bound and lower_bound<0:
     new_lower_limit=5*lower_bound
  elif lower_bound>0:
     new_lower_limit=-5*lower_bound
  if upper_bound>new_upper_limit:
      tmp=new_upper_limit
      new_upper_limit=upper_bound
      upper_bound=tmp
  if new_lower_limit>lower_bound:
     tmp=lower_bound
     lower_bound=new_lower_limit
     new_lower_limit=tmp
  for i in extracted_list:
        if np.random.rand() > 0.5:
            noise_df.loc[i, column] = generate_random_value_discrete(upper_bound, new_upper_limit)
        else:
            noise_df.loc[i, column] = generate_random_value_discrete(new_lower_limit, lower_bound)

  return noise_df

def outlierCategoricalIntegerNew(train_df,column,distribution,percentage,number,params):
  #extracted_list=sampleList(percentage,len(train_df[column]))
  extracted_list= sample_indices(distribution, train_df[column], percentage=None, number=None, params=None)
  noise_df= train_df.copy()
  max_value = noise_df[column].max()
  min_value=noise_df[column].min()
  if min_value==0:
      min_value=-1
      new_minValue=-5
  elif min_value<0:
      new_minValue=5*min_value
  else:
      new_minValue=-5+min_value
  if max_value==0:
      max_value=1
      new_maxValue=5
  else:
      new_maxValue=2*max_value
  for i, value in enumerate(extracted_list):
     if np.random.rand() > 0.5:
      noise_df.loc[i, column] = np.random.randint(max_value, new_maxValue)
     else:
      noise_df.loc[i, column] = np.random.randint(new_minValue, min_value)

  return noise_df

def outlierCategoricalStringNew(train_df,column,distribution,percentage,number,params):
  #extracted_list=sampleList(percentage,len(train_df[column]))
  extracted_list= sample_indices(distribution, train_df[column], percentage=None, number=None, params=None)
  noise_df= train_df.copy()
  for i, value in enumerate(extracted_list):
    noise_df.loc[i, column] = "puck was here"
  return noise_df

# Funzione per identificare le date valide
def identify_valid_dates(df, date_column):
    valid_dates = []
    for date in df[date_column]:
        try:
            # Converte la data in stringa se necessario, prima di passarla a parser.parse
            if isinstance(date, (pd.Timestamp, date)):
                date = str(date)  # Converte in stringa
            parser.parse(date)
            valid_dates.append(True)
        except (ValueError, TypeError):
            valid_dates.append(False)

    df['is_valid_date'] = valid_dates
    return df

# Funzione per standardizzare solo le date riconosciute in un formato coerente
def standardize_dates(df, date_column):
    standardized_dates = []

    for date, is_valid in zip(df[date_column], df['is_valid_date']):
        if is_valid:
            try:
                # Converte la data con `dayfirst=True` e formatta come 'YYYY-MM-DD'
                standardized_date = parser.parse(date, dayfirst=True).date()  # Mantiene solo la parte della data
                standardized_dates.append(standardized_date)
            except (ValueError, TypeError):
                standardized_dates.append(date)  # Mantieni la data originale se c'è un errore
        else:
            standardized_dates.append(date)  # Mantieni la stringa originale per date non valide

    df[date_column] = standardized_dates
    return df

# Funzione per generare una data outlier basata su deviazione standard con un limite massimo
def random_outlier_date(mean_date, std_dev_days, min_date, max_date, factor=3, max_offset_days=36500):
    # Aumenta la variabilità generando un offset più casuale per ciascun outlier
    days_offset = random.choice([-1, 1]) * random.randint(factor, factor * 5) * random.uniform(0.5, 3) * std_dev_days

    # Limita il valore dell'offset per evitare l'errore OutOfBoundsTimedelta
    if abs(days_offset) > max_offset_days:
        days_offset = random.choice([-1, 1]) * random.randint(0, max_offset_days)  # Limita l'offset massimo

    # Calcola la nuova data outlier
    outlier_date = (mean_date + timedelta(days=days_offset)).date()

    return outlier_date

def random_upper_lower(series):
    """Apply random upper/lower casing to each string in the Series."""
    return series.apply(lambda text: ''.join(
        [char.upper() if random.random() > 0.5 else char.lower() for char in text]
    ))

def replace_punctuation(text):
    """Sostituisce ogni segno di punteggiatura (/, ., -) con uno degli altri due in maniera casuale, mantenendo lo stesso sostituto all'interno della stessa stringa."""
    replacements = {
        '/': random.choice(['-', '.']),
        '.': random.choice([',', '/']),
        '-': random.choice(['/', '.'])}
    return ''.join([replacements[char] if char in replacements else char for char in text])

def remove_or_replace(text):
    """Rimuove o sostituisce un carattere casuale, sostituendo lettere con lettere e numeri con numeri."""
    if len(text) < 2:
        return text
    pos = random.randint(0, len(text) - 1)
    char = text[pos]

    if char.isdigit():
        if random.random() > 0.5:
            return text[:pos] + text[pos + 1:]
        else:
            random_digit = str(random.randint(0, 9))
            return text[:pos] + random_digit + text[pos + 1:]
    elif char.isalpha():
        if random.random() > 0.5:
            return text[:pos] + text[pos + 1:]
        else:
            random_letter = random.choice(string.ascii_letters)
            return text[:pos] + random_letter + text[pos + 1:]
    return text

def abbreviate_text(text):
    """Abbrevia il testo mantenendo solo le prime lettere di ogni parola."""
    return ''.join([word[0] for word in text.split()])

def shuffle_words(text):
    """Cambia l'ordine delle parole in una stringa, garantendo un ordine diverso dall'originale."""
    words = text.split()
    while True:
        random.shuffle(words)
        if words != text.split():
            break
    return ' '.join(words)

# Funzione per creare JSON 
def create_json_for_feature(percentage, mode, feature_name=None, selection_criteria="all"):
    config = {
        "strategy": {
            "affected_features": [feature_name] if feature_name else [],
            "selection_criteria": selection_criteria,
            "percentage": percentage,
            "mode": mode,
            "perturbate_data": {
                "distribution": "random",
                "param": None,
                "value": None,
                "condition_logic": None
            }
        }
    }
    return config