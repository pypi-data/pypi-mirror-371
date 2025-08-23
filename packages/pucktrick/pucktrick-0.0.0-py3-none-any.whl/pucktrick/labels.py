def labels(train_df, original_df=None, strategy=None):

    with open(strategy, 'r') as file:
        strategy = json.load(file)

    strategy = strategy.get("strategy", {})
    target = strategy.get("affected_features")
    selection_criteria = strategy.get("selection_criteria")
    percentage = strategy.get("percentage")
    mode = strategy.get("mode")
    perturbate_config = strategy.get("perturbate_data", {})
    distr1 = perturbate_config.get("distribution")
    value = perturbate_config.get("value", [])
    condition_logic = perturbate_config.get("condition_logic", None)
    params= perturbate_config.get("param", {})
    number=None

    target_col = target[0] if isinstance(target, list) else target
    unique_values = train_df[target_col].dropna().unique()  
    if len(unique_values) == 2:
        var_type = "binary"
    elif len(unique_values) > 2:
        var_type = "categorical"
    else:
        raise ValueError(f"Unable to determine the type of target column '{target}'.")


    if var_type == "binary":
        #print("Target is binary")
        if mode == 'extended':
            noise_df= noiseBinaryExt(original_df, train_df, target_col,distr1, percentage,number,params)
        else:
            noise_df = noiseBinaryNew(train_df, target_col, distr1, percentage,params,number) 

    elif var_type == "categorical":
        if mode == 'extended':
            noise_df = noiseCategoricalIntExtendedExistingValues(original_df, train_df, target_col,distr1, percentage,number,params)

        else:
            noise_df = noiseCategoricalIntNewExistingValues(train_df, target_col, distr1, percentage,number,params) 
    for col in noise_df.select_dtypes(include=['int64']).columns:
        noise_df[col] = noise_df[col].astype('Int64')  

    return noise_df
