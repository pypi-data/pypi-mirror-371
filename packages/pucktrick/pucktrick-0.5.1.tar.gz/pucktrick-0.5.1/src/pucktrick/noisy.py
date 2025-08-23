from pucktrick.utils import *

def noise(train_df, strategy, original_df=None):
    if original_df is None:
        original_df = train_df

    affected_features = strategy.get("affected_features")
    selection_criteria = strategy.get("selection_criteria")
    percentage = strategy.get("percentage")
    mode = strategy.get("mode")
    perturbate_config = strategy.get("perturbate_data", {})
    distr1 = perturbate_config.get("distribution")
    value = perturbate_config.get("value", [])
    condition_logic = perturbate_config.get("condition_logic", None)
    params=perturbate_config.get("param", {})

    train1_df = train_df.copy()

    if mode == "extended":
        train_df = original_df
    noisy_df = train_df.copy()
    if affected_features and not isinstance(affected_features, list):
        affected_features = [affected_features]

    if not value:
        filtered_df = noisy_df  
    else:
        row_filters = []
        for feature, value in zip(affected_features, value):
            if value is None:  
                row_filters.append(train_df[feature].notnull())
            else:
                row_filters.append(train_df[feature] == value)

        if condition_logic == "and":
            combined_filter = row_filters[0]
            for f in row_filters[1:]:
                combined_filter &= f
        elif condition_logic == "or":
            combined_filter = row_filters[0]
            for f in row_filters[1:]:
                combined_filter |= f
        elif condition_logic is None:
            combined_filter = row_filters[0]
            for f in row_filters[1:]:
                combined_filter &= f  
        else:
            raise ValueError("condition_logic must be either 'and', 'or', or None.")

        filtered_df = noisy_df[combined_filter]
    
    
    total_rows_to_change = int(len(filtered_df) * percentage)

    if mode == "extended" and original_df is not None:
        train_df = train1_df
        already_modified_mask = (train_df[affected_features[0]] != original_df[affected_features[0]])
        already_modified_count = already_modified_mask.sum()
        rows_to_change = total_rows_to_change - already_modified_count

        if rows_to_change > 0:
            modifiable_indices = filtered_df[~already_modified_mask.reindex(filtered_df.index, fill_value=False)]
            if len(modifiable_indices) == 0:
                print("No modifiable rows available in extended mode.")
                return noisy_df
            number= rows_to_change
            percentage=None
            sampled_indices = sample_indices(distr1, modifiable_indices,percentage, number, params)
            sampled_indices = modifiable_indices.iloc[sampled_indices].index
        else:
            print("No additional rows to change in extended mode.")
            return noisy_df

    else:  
        number= total_rows_to_change
        percentage=None
        sampled_indices = sample_indices(distr1, filtered_df,percentage, number, params)
        sampled_indices = filtered_df.iloc[sampled_indices].index

    if mode == "extended":
        noisy_df = train1_df

    
    for feature in affected_features:
        if pd.api.types.is_string_dtype(noisy_df[feature]):
            unique_values = train_df[feature].dropna().unique()
            for idx in sampled_indices:
                if selection_criteria == "fake_values":  
                   
                    noisy_df.loc[idx, feature] = ''.join(np.random.choice(list('abcdefghijklmnopqrstuvwxyz'), size=5))
                    
                else:
                    
                    while True:
                        new_value = np.random.choice(unique_values)
                        if new_value != noisy_df.loc[idx, feature]:
                            noisy_df.loc[idx, feature] = new_value
                            break

        elif pd.api.types.is_numeric_dtype(noisy_df[feature]):
            min_val = train_df[feature].min()
            max_val = train_df[feature].max()
            for idx in sampled_indices:
                if pd.api.types.is_integer_dtype(noisy_df[feature]):
                    new_value = random.randint(min_val, max_val)
                else:
                    new_value = random.uniform(min_val, max_val)
                noisy_df.loc[idx, feature] = new_value

        elif pd.api.types.is_datetime64_any_dtype(noisy_df[feature]):
            valid_dates = train_df[feature].dropna()
            if valid_dates.empty:
                continue
            min_date = valid_dates.min()
            max_date = valid_dates.max()
            for idx in sampled_indices:
                random_days = random.randint(0, (max_date - min_date).days)
                noisy_df.loc[idx, feature] = min_date + timedelta(days=random_days)

        elif pd.api.types.is_categorical_dtype(noisy_df[feature]):
            
            unique_values = train_df[feature].cat.categories
            for idx in sampled_indices:
                new_value = random.choice(unique_values)
                noisy_df.loc[idx, feature] = new_value

        else:
            raise ValueError(f"Unsupported column type for feature '{feature}'.")
 
    return noisy_df


