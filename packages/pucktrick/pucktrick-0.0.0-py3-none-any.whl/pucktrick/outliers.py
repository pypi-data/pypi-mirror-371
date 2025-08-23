from pucktrick.utils import *

def is_int_categorical(series: pd.Series,
                       max_unique: int = 10,
                       max_domain_size: int = 20,
                       max_unique_ratio: float = 0.05,
                       require_nonnegative: bool = True) -> bool:
    """
    Heuristic: decide if an integer-typed column is actually categorical (coded as ints).
    """
    if not pd.api.types.is_integer_dtype(series):
        return False
    
    s = series.dropna()
    if s.empty:
        return False
    
    nunq = s.nunique()
    if nunq <= max_unique:
        return True
    
    if nunq <= max_domain_size and nunq / len(s) <= max_unique_ratio:
        return True
    
    vals = np.sort(s.unique())
    if require_nonnegative and vals[0] < 0:
        return False
    
    # consecutive small domain?
    if len(vals) <= max_domain_size and np.all(np.diff(vals) == 1):
        return True
    
    return False

def outlier(train_df, strategy, original_df=None):

    if original_df is None:
        original_df = train_df.copy()  

    affected_features = strategy.get("affected_features")
    selection_criteria = strategy.get("selection_criteria")
    percentage = strategy.get("percentage")
    mode = strategy.get("mode")
    perturbate_config = strategy.get("perturbate_data", {})
    distr1 = perturbate_config.get("distribution")
    values = perturbate_config.get("value", [])
    condition_logic = perturbate_config.get("condition_logic", None)
    params=perturbate_config.get("param", {})
    train1_df=train_df.copy()
    noisy_df = train_df.copy()
    if mode == "extended":
        train_df = original_df

    if affected_features and not isinstance(affected_features, list):
        affected_features = [affected_features]
    if not values:
        filtered_df = noisy_df
    else:
        row_filters = []
        for feature, value in zip(affected_features, values):
            if value is None:
                row_filters.append(train_df[feature].notnull())
            else:
                row_filters.append(train_df[feature] == value)

        if condition_logic == "and":
            combined_filter = row_filters[0]
            for f in row_filters[1:]:
                combined_filter &= f
        else:
            combined_filter = row_filters[0]
            for f in row_filters[1:]:
                combined_filter |= f

        filtered_df = noisy_df[combined_filter]
    total_rows_to_change = int(len(filtered_df) * percentage)
    
    if mode == "extended" and original_df is not None:
        already_modified_mask = train1_df[affected_features].ne(original_df[affected_features]).any(axis=1)
        already_modified_count = already_modified_mask.sum()
        rows_to_change = total_rows_to_change - already_modified_count 
        modifiable_indices = filtered_df[~already_modified_mask.reindex(filtered_df.index, fill_value=False)]
        if rows_to_change <= 0 or len(modifiable_indices) == 0:
            print("⚠️ Modalità 'extended': nessuna nuova riga da sporcare. (Tutte le righe disponibili sono già modificate)")
            return noisy_df

        number=rows_to_change
        percentage=None
        sampled_indices = sample_indices(distr1, modifiable_indices,percentage, number, params)
        sampled_indices = modifiable_indices.iloc[sampled_indices].index
    else:
        number=total_rows_to_change
        percentage=None
        sampled_indices = sample_indices(distr1, filtered_df,percentage, number, params)
        sampled_indices = filtered_df.iloc[sampled_indices].index
    
    for feature in affected_features:
        if pd.api.types.is_string_dtype(noisy_df[feature]):
            for i in sampled_indices:
                noisy_df.loc[i, feature] = "puck was here"

        elif pd.api.types.is_integer_dtype(noisy_df[feature]):
            if is_int_categorical(noisy_df[feature]):
                current_max = noisy_df[feature].max(skipna=True)
                current_max=current_max+1
                for i in sampled_indices:
                    noisy_df.loc[i, feature] = current_max
            else:
                mean = np.mean(noisy_df[feature])
                std_dev = np.std(noisy_df[feature])
                new_upper = round(mean + 4 * std_dev, 0)
                new_lower = round(mean - 4 * std_dev, 0)

                for i in sampled_indices:
                    if np.random.rand() > 0.5:
                        noisy_df.loc[i, feature] = random.randint(int(mean + 3 * std_dev), int(new_upper))
                    else:
                        noisy_df.loc[i, feature] = random.randint(int(new_lower), int(mean - 3 * std_dev))

        elif pd.api.types.is_datetime64_any_dtype(noisy_df[feature]):
            valid_dates = train_df[feature].dropna()
            if valid_dates.empty:
                continue
            min_date = valid_dates.min()
            max_date = valid_dates.max()

            for i in sampled_indices:
                random_days = random.randint(0, (max_date - min_date).days)
                noisy_df.loc[i, feature] = min_date + timedelta(days=random_days)

        elif pd.api.types.is_float_dtype(noisy_df[feature]):
            mean = np.mean(noisy_df[feature])
            std_dev = np.std(noisy_df[feature])
            new_upper = mean + 4 * std_dev
            new_lower = mean - 4 * std_dev

            for i in sampled_indices:
                if np.random.rand() > 0.5:
                    noisy_df.loc[i, feature] = np.random.uniform(mean + 3 * std_dev, new_upper)
                else:
                    noisy_df.loc[i, feature] = np.random.uniform(new_lower, mean - 3 * std_dev)

        else:
            raise ValueError(f"Unsupported column type for feature '{feature}'.")

    return noisy_df


    
    

