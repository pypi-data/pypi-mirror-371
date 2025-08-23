from pucktrick.utils import *

def missing(train_df,  strategy=None, original_df=None):
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
    params= perturbate_config.get("param", {})

    if affected_features and not isinstance(affected_features, list):
        affected_features = [affected_features]

    if value is None:
        value = [None] * len(affected_features)

    noise_df = train_df.copy()

    if mode == 'extended':
        filters_original = []
        filters_train = []

        for col, val in zip(affected_features, value):
            if val is not None:
                filters_original.append(original_df[col] == val)
                filters_train.append(train_df[col] == val)
            else:
             
                filters_original.append(None)
                filters_train.append(None)

  
        combined_filter_original = None
        combined_filter_train = None

        for filter_original in filters_original:
            if filter_original is not None:
                if combined_filter_original is None:
                    combined_filter_original = filter_original
                else:
                    if condition_logic == "and":
                        combined_filter_original &= filter_original
                    elif condition_logic == "or":
                        combined_filter_original |= filter_original

        for filter_train in filters_train:
            if filter_train is not None:
                if combined_filter_train is None:
                    combined_filter_train = filter_train
                else:
                    if condition_logic == "and":
                        combined_filter_train &= filter_train
                    elif condition_logic == "or":
                        combined_filter_train |= filter_train

        if combined_filter_original is not None:
            origin_column_df = original_df[combined_filter_original]
        else:
            origin_column_df = original_df

        if combined_filter_train is not None:
            target_df = train_df[combined_filter_train]
        else:
            target_df = train_df

        total_rows_to_change = round(len(origin_column_df) * percentage)
        already_null_counts = train_df[affected_features].isnull().all(axis=1).sum()
        new_rows_to_change = total_rows_to_change - already_null_counts

        if new_rows_to_change > 0:
            modifiable_df = target_df[~target_df[affected_features].isnull().all(axis=1)]
            number= new_rows_to_change
            percentage=None
            sampled_indices = sample_indices(distr1, modifiable_df,percentage, number, params)
            sampled_rows = modifiable_df.iloc[sampled_indices].index
            for col in affected_features:
                noise_df.loc[sampled_rows, col] = np.nan

    else:
        filters = []

        for col, val in zip(affected_features, value):
            if val is not None:
                filters.append(train_df[col] == val)
            else:
   
                filters.append(None)
        #print("Filtri:", filters)
        if selection_criteria == "all":
            combined_filter = pd.Series(True, index=train_df.index)
        else:
            combined_filter = None
            for filter_condition in filters:
                if filter_condition is not None:
                    if combined_filter is None:
                       combined_filter = filter_condition
                    else:
                        if condition_logic == "and":
                            combined_filter &= filter_condition
                        elif condition_logic == "or":
                            combined_filter |= filter_condition
            if combined_filter is None:
              combined_filter = pd.Series(True, index=train_df.index)
        print("Righe selezionate:", combined_filter.sum())

    
        if combined_filter is not None:
            column_df = train_df[combined_filter]
        else:
            column_df = train_df

        total_rows_to_change = int(len(column_df) * percentage)
        if total_rows_to_change <= 0:
            return noise_df
        number= total_rows_to_change
        percentage=None
        sampled_indices = sample_indices(distr1, column_df, percentage,number, params)
        sampled_rows = column_df.iloc[sampled_indices].index
        #print(sampled_rows)
        for col in affected_features:
            noise_df.loc[sampled_rows, col] = np.nan

    return noise_df
