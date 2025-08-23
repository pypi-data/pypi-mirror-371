import torch
from episode import utils


def divide_B_cat_into_blocks(processed_features):
    """
    
    Args:
    processed_features: an instance of ProcessedFeatures

    Returns:
    dictionary of tensors, each of shape (batch_size, cat_n_unique_dict)
    """
    B_cat = processed_features.B_cat
    cat_n_unique_dict = processed_features.cat_n_unique_dict
    categorical_features_indices = processed_features.categorical_features_indices
    cat_block_dict = {}

    start_index = 0
    for cat_feature_index in categorical_features_indices:
        end_index = start_index + cat_n_unique_dict[cat_feature_index]
        cat_block = B_cat[:,start_index:end_index]
        cat_block_dict[str(cat_feature_index)] = cat_block
        start_index = end_index

    return cat_block_dict


def calculate_cat_shape_functions(processed_features, cat_weights, positive=True):
    """
    
    Args:
    processed_features: an instance of ProcessedFeatures
    cat_weights: a dictionary of tensors, each of shape (cat_n_unique_dict, n_properties)
    positive: boolean, whether the output should be positive or not

    Returns:
    output tensor of shape (batch_size, n_properties, n_cat_features)
    """

    # Divide B_cat into blocks for each variable
    cat_block_dict = divide_B_cat_into_blocks(processed_features)

    # Calculate the shape functions for each variable
    cat_shape_functions = {}
    for cat_feature_index in processed_features.categorical_features_indices:
        cat_block = cat_block_dict[str(cat_feature_index)]
        cat_weight = cat_weights[str(cat_feature_index)]
        if positive:
            cat_shape_functions[str(cat_feature_index)] = torch.nn.functional.softplus(cat_block @ cat_weight) # shape (batch_size, n_properties)
        else:
            cat_shape_functions[str(cat_feature_index)] = cat_block @ cat_weight # shape (batch_size, n_properties)
    
    # Stack the shape functions
    return torch.stack([cat_shape_functions[str(cat_feature_index)] for cat_feature_index in processed_features.categorical_features_indices], dim=2) # shape (batch_size, n_properties, n_cat_features)


def calculate_gams(processed_features, weights, cat_weights, bias, positive=True, sum=False):
    """
    Calculate the GAMS of the model

    Args:
    B: a pair of input tensors of shape (batch_size, n_cont_features, n_basis_functions) and (batch_size, sum(cat_n_unique_dict))
    weights: input tensor of shape (n_basis_functions, n_cont_features, n_properties)
    cat_weights: a dictionary of tensors, each of shape (cat_n_unique_dict, n_properties)
    bias: input tensor of shape (n_properties)

    Returns:
    output tensor of shape (batch_size, n_properties, n_features + 1) if sum is False else (batch_size, n_properties)
    """
    B = processed_features.B
    if positive:
        shape_functions = torch.nn.functional.softplus(torch.einsum('dmb,bmp->dpm', B, weights))
        shape_bias = torch.tile(torch.nn.functional.softplus(bias), (B.shape[0],1)).unsqueeze(-1)
    else:
        shape_functions = torch.einsum('dmb,bmp->dpm', B, weights)
        shape_bias = torch.tile(bias, (B.shape[0],1)).unsqueeze(-1)
    
    if len(processed_features.categorical_features_indices) > 0:
        cat_shape_functions = calculate_cat_shape_functions(processed_features, cat_weights, positive=positive)
        shape_functions_with_bias = torch.concat([shape_functions, cat_shape_functions, shape_bias], dim=2) # shape (batch_size, n_properties, n_features + 1)
    else:
        shape_functions_with_bias = torch.concat([shape_functions, shape_bias], dim=2) # shape (batch_size, n_properties, n_features + 1)
    if sum:
        return torch.sum(shape_functions_with_bias, dim=2)
    else:
        return shape_functions_with_bias
    
def calculate_shape_functions_for_single_feature(b, feature_index, cont_weights, cat_weights, positive=True):
    """
    
    Args:
    b: input tensor of shape (batch_size, n_basis_functions) or (batch_size, cat_n_unique) if categorical
    feature_index: integer, index of the feature from [n_features]
    cont_weights: input tensor of shape (n_basis_functions, n_cont_features, n_properties) or (cat_n_unique, n_properties) if categorical

    Returns:
    output tensor of shape (batch_size, n_properties)
    """
    if str(feature_index) in cat_weights.keys():
        raw_shape_functions = b @ cat_weights[str(feature_index)] # shape (batch_size, n_properties)
    else:
        categorical_features_indices = [int(i) for i in cat_weights.keys()]
        cont_feature_index = utils.from_feature_index_to_cont_feature_index(feature_index, categorical_features_indices)
        raw_shape_functions = b @ cont_weights[:,cont_feature_index,:] # shape (batch_size, n_properties)
    
    if positive:
        return torch.nn.functional.softplus(raw_shape_functions)
    else:
        return raw_shape_functions