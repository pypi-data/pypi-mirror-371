from pucktrick.utils import *

def duplicate(train_df, strategy=None, original_df=None ):
    if original_df is None:
        original_df = train_df

    #with open(strategy, 'r') as file:
    #    strategy = json.load(file)
    #strategy = strategy.get("strategy", {})
    affected_features = strategy.get("affected_features")
    selection_criteria = strategy.get("selection_criteria")
    percentage = strategy.get("percentage")
    mode = strategy.get("mode")
    perturbate_config = strategy.get("perturbate_data", {})
    distr1 = perturbate_config.get("distribution")
    value = perturbate_config.get("value", [])
    condition_logic = perturbate_config.get("condition_logic", None)
    params = perturbate_config.get("param", {})

    if affected_features and not isinstance(affected_features, list):
        affected_features = [affected_features]

    if selection_criteria in [
        "class",
        "upper_lower",
        "replace_punctuation",
        "remove_replace",
        "abbreviate_text",
        "shuffle_words",
    ]:
        # Costruzione dei filtri
        filters = []

        if value is None or not any(value):
            filters = [
                (original_df[col].notnull() if mode == "extended" else train_df[col].notnull())
                for col in affected_features
            ]
        else:
            for col, val in zip(affected_features, value):
                if val is not None:
                    filters.append(
                        (original_df[col] == val) if mode == "extended" else (train_df[col] == val)
                    )
                else:
                    filters.append(
                        (original_df[col].notnull()) if mode == "extended" else (train_df[col].notnull())
                    )

        # Combina i filtri con logica "or" o "and"
        if condition_logic == "and":
            combined_filter = pd.Series(True, index=train_df.index if mode != "extended" else original_df.index)
            for f in filters:
                combined_filter &= f
        elif condition_logic == "or":
            combined_filter = pd.Series(False, index=train_df.index if mode != "extended" else original_df.index)
            for f in filters:
                combined_filter |= f
        elif condition_logic is None:
            # Default: "and" logic
            combined_filter = pd.Series(True, index=train_df.index if mode != "extended" else original_df.index)
            for f in filters:
                combined_filter &= f
        else:
            raise ValueError(f"Unsupported condition_logic '{condition_logic}'")

        # Filtrare le righe
        target_df = original_df if mode == "extended" else train_df
        filtered_df = target_df[combined_filter].reset_index(drop=True)

        rowsToChange = int(len(filtered_df) * percentage)
        if mode == "extended":
            old_duplicated = len(train_df) - len(original_df)
            new_rowsToChange = rowsToChange - old_duplicated
            if new_rowsToChange <= 0:
                return train_df
            percentage = new_rowsToChange / len(filtered_df)

        sampled_indices = sample_indices(distr1, filtered_df, percentage, params,number=None)
        sampled_rows = filtered_df.iloc[sampled_indices].copy()

        for col in affected_features:
            if selection_criteria == "shuffle_words":
                sampled_rows[col] = sampled_rows[col].astype(str).apply(shuffle_words)
            elif selection_criteria == "abbreviate_text":
                sampled_rows[col] = sampled_rows[col].astype(str).apply(abbreviate_text)
            elif selection_criteria == "replace_punctuation":
                sampled_rows[col] = sampled_rows[col].astype(str).apply(replace_punctuation)
            elif selection_criteria == "remove_replace":
                sampled_rows[col] = sampled_rows[col].astype(str).apply(remove_or_replace)
            elif selection_criteria == "upper_lower":
                sampled_rows[col] = random_upper_lower(sampled_rows[col])

        noise_df = pd.concat([train_df, sampled_rows], ignore_index=True)

    elif selection_criteria == 'all':
        if mode == "extended":
            rowsToChange = len(original_df) * percentage
            old_duplicated = original_df.duplicated().sum()
            new_duplicated = train_df.duplicated().sum()
            diff = new_duplicated - old_duplicated
            new_rowsToChange = rowsToChange - diff
            if new_rowsToChange <= 0:
                return train_df
            new_percentage = new_rowsToChange / len(original_df)
            noise_df = train_df.copy()
            sampled_indices = sample_indices(distr1, original_df, new_percentage, params)
            sampled_rows = original_df.iloc[sampled_indices]
            noise_df = pd.concat([noise_df, sampled_rows], ignore_index=True)
        else:
            noise_df = train_df.copy()
            sampled_indices = sample_indices(distr1, train_df, percentage, params)
            sampled_rows = train_df.iloc[sampled_indices]
            noise_df = pd.concat([noise_df, sampled_rows], ignore_index=True)

    else:
        raise ValueError(f"Unsupported selection_criteria '{selection_criteria}'.")

    if "date" in noise_df.columns:
        noise_df["date"] = noise_df["date"].astype(str).str.replace(r"\s00:00:00$", "", regex=True)

    return noise_df

