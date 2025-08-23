import torch
import numpy as np
from episode import utils
from episode import torch_utils
from episode import constants
from episode.infinite_motifs import get_default_motif_class
from episode.semantic_representation import Properties, Composition
from episode.trajectory_predictor import C0TrajectoryPredictor
from episode.constants import MIN_TRANSITION_POINT_SEP
from episode.config import TorchTrainerConfig

def torch_inverse_softplus(x):
    # Above 20, the softplus is approximately equal to the input
    return torch.where(x < 20, torch.log(torch.exp(x) - 1), x)


class ProcessedFeatures:
    def __init__(self, B, B_cat, categorical_features_indices, cat_n_unique_dict, X0 : torch.Tensor | None = None, x0_index : int | float | None = None):
        """
        Processed features for the model.

        Args:
        B: input tensor of shape (batch_size, n_cont_features, n_basis_functions)
        B_cat: input tensor of shape (batch_size, sum(cat_n_unique_dict))
        categorical_features_indices: list of indices for categorical features
        cat_n_unique_dict: dictionary with the number of unique values for each categorical feature
        X0: initial condition tensor of shape (batch_size,1) or None
        x0_index: index of the initial condition in the feature vector, or a float value to set the initial condition directly
        """
        self.B = B
        self.B_cat = B_cat
        self.categorical_features_indices = categorical_features_indices
        self.cat_n_unique_dict = cat_n_unique_dict
        self.X0 = X0
        self.batch_size = B.shape[0]
        self.x0_index = x0_index


class FullModel(torch.nn.Module):
    def __init__(self, config: TorchTrainerConfig):
        super(FullModel, self).__init__()
        self.config = config.__dict__
        self.property_module = PropertyModule(self.config)
        self.trajectory_predictor = C0TrajectoryPredictor()
        self.cached_properties: Properties | None = None

    def predict_from_cached_properties(self, T: torch.Tensor) -> torch.Tensor:
        """Predict the trajectory from cached properties.

        Parameters
        ----------
        T : torch.Tensor
            Time tensor of shape (batch_size, n_max_timesteps).

        Returns
        -------
        torch.Tensor
            Output tensor of shape (batch_size, n_output_features).
        """
        if self.cached_properties is None:
            raise ValueError("Cached properties are not set. Call predict first.")
        
        Y_pred = self.trajectory_predictor._predict_from_properties(self.cached_properties, T)
        assert isinstance(Y_pred, torch.Tensor), "The output of the trajectory predictor should be a torch.Tensor"
        return Y_pred
    
    def predict_properties(self, processed_features: ProcessedFeatures) -> Properties:
        """Predict the properties based on the processed features.

        Parameters
        ----------
        processed_features : ProcessedFeatures
            Processed features containing B, B_cat, categorical features indices, and categorical unique counts.

        Returns
        -------
        Properties
            Predicted properties of the trajectories.
        """
        self.cached_properties = self.property_module.predict(processed_features)
        return self.cached_properties

    def forward(self, processed_features: ProcessedFeatures, T: torch.Tensor) -> torch.Tensor:
        """Forward pass of the model.
        Parameters
        ----------
        processed_features : ProcessedFeatures
            Processed features containing B, B_cat, categorical features indices, and categorical unique counts.
        T : torch.Tensor
            Time tensor of shape (batch_size, n_max_timesteps).

        Returns
        -------
        torch.Tensor
            Output tensor of shape (batch_size, n_output_features)
        """
        # Get the output from the property module
        properties = self.predict_properties(processed_features)

        # Get the output from the trajectory predictor
        Y_pred = self.trajectory_predictor._predict_from_properties(properties, T)

        assert isinstance(Y_pred, torch.Tensor), "The output of the trajectory predictor should be a torch.Tensor"

        return Y_pred
    
    def loss_last_transition_point(self) -> torch.Tensor:
        if self.cached_properties is None:
            raise ValueError("Cached properties are not set. Call predict of forward first.")
        finite_coordinates = self.cached_properties.transition_points
        
        if not self.cached_properties.composition.is_bounded():
            return self.config['last_loss_coeff'] * torch.nn.functional.relu(finite_coordinates[:,-1,0] - self.config['t_range'][1]).mean()
        else:
            return self.config['last_loss_coeff'] * torch.nn.functional.relu(finite_coordinates[:,-2,0] - (self.config['t_range'][1] - MIN_TRANSITION_POINT_SEP)).mean()
        

    def loss_discontinuity_of_derivatives(self) -> torch.Tensor:

        coefficients = self.trajectory_predictor.cached_coefficients_bounded_part
        assert coefficients is not None, "Coefficients must be set before calculating the loss of discontinuity of derivatives"
        assert isinstance(coefficients, torch.Tensor), "Coefficients should be a torch.Tensor"
        assert self.cached_properties is not None, "Finite coordinates must be set before calculating the loss of discontinuity of derivatives"
        finite_coordinates = self.cached_properties.transition_points
        assert finite_coordinates is not None, "Finite coordinates must be set before calculating the loss of discontinuity of derivatives"
        assert isinstance(finite_coordinates, torch.Tensor), "Finite coordinates should be a torch.Tensor"

        composition: Composition = self.config['composition']

        def derivative_difference_loss():

            global_first_derivative_discontinuity = 0
            global_second_derivative_discontinuity = 0
            
            for i in range(len(composition.bounded_part)-1):
                if composition.type_of_transition_point(i+1) == 'min' or composition.type_of_transition_point(i+1) == 'max':
                    pass
                else:
                    first_derivatives_left = 3*coefficients[:,i,0] * finite_coordinates[:,i+1,0]**2 + 2 * coefficients[:,i,1] * finite_coordinates[:,i+1,0] + coefficients[:,i,2]
                    first_derivatives_right = 3*coefficients[:,i+1,0] * finite_coordinates[:,i+1,0]**2 + 2 * coefficients[:,i+1,1] * finite_coordinates[:,i+1,0] + coefficients[:,i+1,2]

                    first_derivative_discontinuity = first_derivatives_left - first_derivatives_right

                    first_norm = torch.max(torch.abs(first_derivatives_left), torch.abs(first_derivatives_right))
                    mask = first_norm > 1e-3

                    first_derivative_discontinuity[mask] =  first_derivative_discontinuity[mask]/first_norm[mask]
                    first_derivative_discontinuity[~mask] = first_derivative_discontinuity[~mask]

                    global_first_derivative_discontinuity += torch.mean(first_derivative_discontinuity ** 2)
                if composition.type_of_transition_point(i+1) == 'inflection':
                    pass
                else:
                    second_derivatives_left = 6*coefficients[:,i,0] * finite_coordinates[:,i+1,0] + 2 * coefficients[:,i,1]
                    second_derivatives_right = 6*coefficients[:,i+1,0] * finite_coordinates[:,i+1,0] + 2 * coefficients[:,i+1,1]

                    second_derivative_discontinuity = second_derivatives_left - second_derivatives_right

                    second_norm = torch.max(torch.abs(second_derivatives_left), torch.abs(second_derivatives_right))
                    mask = second_norm > 1e-3

                    second_derivative_discontinuity[mask] =  second_derivative_discontinuity[mask]/second_norm[mask]
                    second_derivative_discontinuity[~mask] = second_derivative_discontinuity[~mask]*1e3

                    global_second_derivative_discontinuity += torch.mean(second_derivative_discontinuity ** 2)

            # calculate the loss
            return global_first_derivative_discontinuity + global_second_derivative_discontinuity

        def last_derivative_loss():
             # calculate the first derivative at the transition points
            first_derivative_last = 3*coefficients[:,-1,0] * finite_coordinates[:,-1,0]**2 + 2 * coefficients[:,-1,1] * finite_coordinates[:,-1,0] + coefficients[:,-1,2]
            return torch.mean(first_derivative_last ** 2)


        if finite_coordinates.shape[1] <= 1:
            return torch.tensor(0.0, device=self.config['device'])  # No transition points, no discontinuity loss
        elif finite_coordinates.shape[1] <=2:
            return last_derivative_loss() * self.config['dis_loss_coeff_2']
        else:
            return derivative_difference_loss() * self.config['dis_loss_coeff_1'] + last_derivative_loss() * self.config['dis_loss_coeff_2']
        
    # def loss(self, processed_features: ProcessedFeatures, T: torch.Tensor, Y: torch.Tensor, mask: torch.Tensor, with_derivative_loss: bool = True, dtw: bool = False) -> torch.Tensor:

    #     Y_pred = self.forward(processed_features, T)

    #     # if dtw:
    #         # TODO:
    #         # criterion = SoftDTW(gamma=1.0, normalize=True)
    #         # TY = torch.stack([T, Y], dim=2)
    #         # TY_pred = torch.stack([T, Y_pred], dim=2)
    #         # loss = criterion(TY_pred, TY).mean()
    #     # else:
    #     diff_squared = (Y_pred - Y) ** 2
    #     diff_squared = diff_squared * mask  # Apply mask to the squared differences
    #     loss_per_sample = torch.sum(diff_squared, dim=1) / mask.sum(dim=1)  # shape (batch_size,)
    #     loss = torch.mean(loss_per_sample)
    #     total_loss = loss
    #     # TODO: Add the derivative loss if required
    #     # if with_derivative_loss:
    #     #     derivative_loss = self.loss_discontinuity_of_derivatives(all_coefficients, finite_coordinates)
    #     #     total_loss += derivative_loss
    #     #     total_loss += self.loss_last_transition_point(finite_coordinates)
    #     #     if self.soft_constraint is not None:
    #     #         derivatives = {}
    #     #         derivatives[('start',1)] = self._boundary_derivative('start',1,B,finite_coordinates,all_coefficients)
    #     #         derivatives[('end',1)] = self._boundary_derivative('end',1,B,finite_coordinates,all_coefficients)
    #     #         derivatives[('end',2)] = self._boundary_derivative('end',2,B,finite_coordinates,all_coefficients)
    #     #         raw_properties = self._infinite_properties_from_weights(B)
    #     #         print_properties = self._extract_print_properties_infinite_motif(raw_properties,finite_coordinates,derivatives[('end',1)],derivatives[('end',2)])
    #     #         total_loss += self.loss_from_soft_constraint(finite_coordinates, derivatives, print_properties)
       
    #     return total_loss



class PropertyModule(torch.nn.Module):
    def __init__(self, config):
        super(PropertyModule, self).__init__()
        self.config = config
        self.composition = config['composition']
        self.n_basis_functions = config['n_basis_functions']
        self.n_features = config['n_features']
        self.seed = config['seed']
        self.n_coordinates = 2*len(self.composition)
        self.x0_included = config['x0_included']
        self.x0_index = config['x0_index']
        self.categorical_features_indices = config['categorical_features_indices']
        self.cat_n_unique_dict = config['cat_n_unique_dict']
        self.n_cat_features = len(self.categorical_features_indices)
        self.n_cont_features = self.n_features - self.n_cat_features
        self.device = utils.get_torch_device(config['device'])

        self.transition_point_module = TransitionPointModule(config)
        self.derivative_module = DerivativeModule(config)
        if not self.composition.is_bounded():
            self.final_motif_property_module = FinalMotifPropertyModule(config, self.transition_point_module, self.derivative_module)
        else:
            self.final_motif_property_module = None
        
    def predict(self, processed_features: ProcessedFeatures) -> Properties:
        """Predict the properties based on the processed features.

        Parameters
        ----------
        processed_features : ProcessedFeatures
            Processed features containing B, B_cat, categorical features indices, and categorical unique counts.
        Returns
        -------
        Properties
            Predicted properties of the trajectories
        """
        transition_points = self.transition_point_module.predict(processed_features)
        first_derivative_at_start, first_derivative_at_end, second_derivative_at_end = self.derivative_module.predict(processed_features, transition_points)
        if self.final_motif_property_module is not None:
            final_motif_properties = self.final_motif_property_module.predict(processed_features, transition_points, first_derivative_at_end, second_derivative_at_end)
        else:
            final_motif_properties = None
        return Properties(
            "pytorch",
            composition=self.composition,
            transition_points=transition_points,
            first_derivative_start=first_derivative_at_start.reshape(-1,1),
            first_derivative_end=first_derivative_at_end.reshape(-1,1),
            second_derivative_end=second_derivative_at_end.reshape(-1,1),
            unbounded_motif_properties=final_motif_properties,
            unbounded_motif_properties_raw=True
        )


class TransitionPointModule(torch.nn.Module):


    def __init__(self, config):
        super(TransitionPointModule, self).__init__()
        self.config = config
        self.composition = config['composition']
        self.n_basis_functions = config['n_basis_functions']
        self.n_features = config['n_features']
        self.seed = config['seed']
        self.n_coordinates = 2*len(self.composition)
        self.x0_included = config['x0_included']
        self.x0_index = config['x0_index']
        self.categorical_features_indices = config['categorical_features_indices']
        self.cat_n_unique_dict = config['cat_n_unique_dict']
        self.n_cat_features = len(self.categorical_features_indices)
        self.n_cont_features = self.n_features - self.n_cat_features
        self.device = utils.get_torch_device(config['device'])

        self.t_range = torch.Tensor([config['t_range'][0],config['t_range'][1]]).to(self.device)

        # t-coordinates of transition points
        t_span = self.t_range[1] - self.t_range[0]
        avg_interval = t_span / len(self.composition.bounded_part)
        avg_interval_per_feature = avg_interval / (self.n_features + 1)
        inverse_interval_per_feature = torch_inverse_softplus(avg_interval_per_feature).item()

        horizontal_weights = torch.randn(self.n_basis_functions, self.n_cont_features, len(self.composition.bounded_part)) + inverse_interval_per_feature
        self.horizontal_weights = torch.nn.Parameter(horizontal_weights)
        self.cat_horizontal_weights = torch.nn.ParameterDict({
            str(i): torch.nn.Parameter(torch.randn(self.cat_n_unique_dict[i], len(self.composition.bounded_part)) + inverse_interval_per_feature) for i in self.categorical_features_indices
        })
        self.horizontal_bias = torch.nn.Parameter(torch.randn(len(self.composition.bounded_part)) + inverse_interval_per_feature)

        # x-coordinates of transition points
        self.vertical_weights = torch.nn.Parameter(torch.randn(self.n_basis_functions, self.n_cont_features, len(self.composition.bounded_part)))
        self.cat_vertical_weights = torch.nn.ParameterDict({
            str(i): torch.nn.Parameter(torch.randn(self.cat_n_unique_dict[i], len(self.composition.bounded_part))) for i in self.categorical_features_indices
        })
        self.vertical_bias = torch.nn.Parameter(torch.randn(len(self.composition.bounded_part)))

        # TODO: This is only needed if there is no initial condition. Otherwise, it is redundant
        self.initial_condition_weights = torch.nn.Parameter(torch.randn(self.n_basis_functions, self.n_cont_features, 1))
        self.cat_initial_condition_weights = torch.nn.ParameterDict({
            str(i): torch.nn.Parameter(torch.randn(self.cat_n_unique_dict[i], 1)) for i in self.categorical_features_indices
        })
        self.initial_condition_bias = torch.nn.Parameter(torch.randn(1))


    def predict(self, features: ProcessedFeatures) -> torch.Tensor:
        """Predict the transition points based on the processed features.

        Parameters
        ----------
        features : ProcessedFeatures
            Processed features containing B, B_cat, categorical features indices, and categorical unique counts.

        Returns
        -------
        torch.Tensor
            Predicted transition points of shape (batch_size, n_transition_points, 2).
        """

        calculated_values_horizontal = torch_utils.calculate_gams(features,self.horizontal_weights,self.cat_horizontal_weights,self.horizontal_bias)
        calculated_values_vertical = torch_utils.calculate_gams(features,self.vertical_weights,self.cat_vertical_weights,self.vertical_bias)

        batch_size = features.batch_size
        X0 = features.X0

        if features.x0_index is not None:
            if isinstance(features.x0_index, int):
                calculated_initial_condition = torch.zeros(batch_size, 1, self.n_features + 1).to(self.device)
                assert X0 is not None
                calculated_initial_condition[:,0,features.x0_index] = X0.flatten()
            elif isinstance(features.x0_index, float):
                calculated_initial_condition = torch.zeros(batch_size, 1, self.n_features + 1).to(self.device)
                calculated_initial_condition[:,0,-1] = features.x0_index # We set the bias to the x0_index value
            else:
                raise ValueError('Invalid x0_index')
        else:
            calculated_initial_condition = torch_utils.calculate_gams(features,self.initial_condition_weights,self.cat_initial_condition_weights,self.initial_condition_bias, positive=False)

           
        all_coordinate_values = torch.zeros(batch_size, len(self.composition.bounded_part)+1,2).to(self.device)
        
        cumulative_horizontal_shape_functions = torch.zeros(batch_size, 1, self.n_features + 1).to(self.device) 
        cumulative_horizontal_shape_functions[:,0,-1] = self.t_range[0]

        cumulative_vertical_shape_functions = calculated_initial_condition # shape (batch_size, 1, n_features + 1)

        # j = 0
        all_coordinate_values[:,0,0] = torch.sum(cumulative_horizontal_shape_functions, dim=2)[:,0]
        all_coordinate_values[:,0,1] = torch.sum(cumulative_vertical_shape_functions, dim=2)[:,0]

        for j in range(1, len(self.composition.bounded_part)+1):
            sign = 1 if self.composition.bounded_part[j-1][0] == '+' else -1
            cumulative_horizontal_shape_functions += calculated_values_horizontal[:,[j-1],:]
            cumulative_vertical_shape_functions += sign * calculated_values_vertical[:,[j-1],:]

            all_coordinate_values[:,j,0] = torch.sum(cumulative_horizontal_shape_functions, dim=2)[:,0] + constants.MIN_TRANSITION_POINT_SEP * j
            all_coordinate_values[:,j,1] = torch.sum(cumulative_vertical_shape_functions, dim=2)[:,0] #TODO: Maybe add minimum separation as in model_numpy.py

        if self.composition.is_bounded():
            all_coordinate_values[:,-1,0] = torch.maximum(all_coordinate_values[:,-2,0] + constants.MIN_TRANSITION_POINT_SEP, self.t_range[1])
        return all_coordinate_values

    def _predict_shape_function(self, ind, coordinate, feature_index, b, X0 : torch.Tensor | None = None):
        """
        Extract the shape function of a transition point

        Args:
        ind: integer, index of the transition point
        coordinate: string, either 't' or 'x'
        feature_index: integer, index of the feature from [n_features]
        b: input tensor of shape (batch_size, n_basis_functions) or (batch_size, cat_n_unique) if categorical
        X0 (optional): input tensor of shape (batch_size, 1)

        Returns:
        output tensor of shape (batch_size,)
        """

        if coordinate == 't':
            if self.composition.is_bounded():
                if ind == len(self.composition.bounded_part): # the last transition point
                    shape_function = torch.zeros(b.shape[0]).to(self.device) # Because we absorb it into the bias
                    return shape_function
            raw_shape_functions = torch_utils.calculate_shape_functions_for_single_feature(b, feature_index, self.horizontal_weights, self.cat_horizontal_weights, positive=True)
            shape_function = torch.sum(raw_shape_functions[:,:ind], dim=1)
            return shape_function
        elif coordinate == 'x':
            raw_shape_functions = torch_utils.calculate_shape_functions_for_single_feature(b, feature_index, self.vertical_weights, self.cat_vertical_weights, positive=True)
            if self.x0_included:
                if isinstance(self.x0_index, int):
                    if feature_index == self.x0_index:
                        assert X0 is not None
                        initial_condition_shape_function = X0
                    else:
                        initial_condition_shape_function = torch.zeros(b.shape[0], 1).to(self.device)
                elif isinstance(self.x0_index, float):
                    initial_condition_shape_function = torch.zeros(b.shape[0], 1).to(self.device)
                else:
                    raise ValueError('Invalid x0_index')
            else:
                initial_condition_shape_function = torch_utils.calculate_shape_functions_for_single_feature(b, feature_index, self.initial_condition_weights, self.cat_initial_condition_weights, positive=False)
            
            cumulative_vertical_shape_functions = initial_condition_shape_function # shape (batch_size, 1)

            for j in range(1,ind+1):
                sign = 1 if self.composition.bounded_part[j-1][0] == '+' else -1
                cumulative_vertical_shape_functions = cumulative_vertical_shape_functions + sign * raw_shape_functions[:,[j-1]]

            return cumulative_vertical_shape_functions.flatten()
        else:
            raise ValueError(f"Unknown coordinate: {coordinate}")
    
        
    def _predict_bias(self, ind, coordinate):
        """
        Extract the bias of a transition point

        Args:
        ind: integer, index of the transition point
        coordinate: string, either 't' or 'x'

        Returns:
        output tensor of shape (1,)
        """
        if coordinate == 't':
            if self.composition.is_bounded():
                if ind == len(self.composition.bounded_part): # the last transition point
                    return self.t_range[1]
            raw_bias = torch.nn.functional.softplus(self.horizontal_bias)
            return torch.sum(raw_bias[:ind]) + self.t_range[0] + constants.MIN_TRANSITION_POINT_SEP * ind
        elif coordinate == 'x':
            raw_bias = torch.nn.functional.softplus(self.vertical_bias)

            if self.x0_included:
                if isinstance(self.x0_index, int):
                    initial_condition_bias = torch.tensor([0.0]).to(self.device)
                elif isinstance(self.x0_index, float):
                    initial_condition_bias = torch.ones(1).to(self.device) * self.x0_index
            else:
                initial_condition_bias = self.initial_condition_bias
            
            cumulative_vertical_bias = initial_condition_bias # type: ignore

            for j in range(1,ind+1):
                sign = 1 if self.composition.bounded_part[j-1][0] == '+' else -1
                cumulative_vertical_bias += sign * raw_bias[j-1]
            return cumulative_vertical_bias
        else:
            raise ValueError(f"Unknown coordinate: {coordinate}")

class DerivativeModule(torch.nn.Module):
    def __init__(self, config):
        super(DerivativeModule, self).__init__()
        self.config = config
        self.composition = config['composition']
        self.n_basis_functions = config['n_basis_functions']
        self.n_features = config['n_features']
        self.seed = config['seed']
        self.n_coordinates = 2*len(self.composition)
        self.x0_included = config['x0_included']
        self.x0_index = config['x0_index']
        self.categorical_features_indices = config['categorical_features_indices']
        self.cat_n_unique_dict = config['cat_n_unique_dict']
        self.n_cat_features = len(self.categorical_features_indices)
        self.n_cont_features = self.n_features - self.n_cat_features
        self.device = utils.get_torch_device(config['device'])

        self.t_range = torch.Tensor([config['t_range'][0],config['t_range'][1]]).to(self.device)

        self.first_derivative_at_start_status = self.composition.get_first_derivative_at_start_status()
        self.first_derivative_at_end_status = self.composition.get_first_derivative_at_end_status()
        self.second_derivative_at_end_status = self.composition.get_second_derivative_at_end_status()

        if self.first_derivative_at_start_status == "weights":
            self.first_derivative_at_start = torch.nn.Parameter(torch.randn(self.n_basis_functions, self.n_cont_features, 1))
            self.cat_first_derivative_at_start = torch.nn.ParameterDict({
                str(i): torch.nn.Parameter(torch.randn(self.cat_n_unique_dict[i], 1)) for i in self.categorical_features_indices
            })
            self.first_derivative_at_start_bias = torch.nn.Parameter(torch.randn(1))

        if self.first_derivative_at_end_status == "weights":
            self.first_derivative_at_end = torch.nn.Parameter(torch.randn(self.n_basis_functions, self.n_cont_features, 1))
            self.cat_first_derivative_at_end = torch.nn.ParameterDict({
                str(i): torch.nn.Parameter(torch.randn(self.cat_n_unique_dict[i], 1)) for i in self.categorical_features_indices
            })
            self.first_derivative_at_end_bias = torch.nn.Parameter(torch.randn(1))

        if self.second_derivative_at_end_status == "weights":
            self.second_derivative_at_end = torch.nn.Parameter(torch.randn(self.n_basis_functions, self.n_cont_features, 1))
            self.cat_second_derivative_at_end = torch.nn.ParameterDict({
                str(i): torch.nn.Parameter(torch.randn(self.cat_n_unique_dict[i], 1)) for i in self.categorical_features_indices
            })
            self.second_derivative_at_end_bias = torch.nn.Parameter(torch.randn(1))

    def predict(self, features: ProcessedFeatures, finite_coordinates: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        """Predict the derivatives based on the processed features and finite coordinates.
        Parameters
        ----------
        features : ProcessedFeatures
            Processed features containing B, B_cat, categorical features indices, and categorical unique counts.
        finite_coordinates : torch.Tensor
            Finite coordinates tensor of shape (batch_size, n_coordinates, 2).
        
        Returns
        -------
        tuple
            A tuple containing three tensors: the predicted first derivative at the start, 
            the predicted first derivative at the end, and the predicted second derivative at the end.
            Each tensor has shape (batch_size,).
        """
        first_derivative_at_start = self.predict_first_derivative_at_start(features, finite_coordinates)
        first_derivative_at_end = self.predict_first_derivative_at_end(features, finite_coordinates)
        second_derivative_at_end = self.predict_second_derivative_at_end(features)
        return (first_derivative_at_start, first_derivative_at_end, second_derivative_at_end)

    def predict_first_derivative_at_start(self, features: ProcessedFeatures, transition_points: torch.Tensor) -> torch.Tensor:
        """Predict the first derivative at the start of the transition.

        Parameters
        ----------
        features : ProcessedFeatures
            Processed features containing B, B_cat, categorical features indices, and categorical unique counts.
        transition_points : torch.Tensor
            Transition points tensor of shape (batch_size, n_transition_points, 2).

        Returns
        -------
        torch.Tensor
            Predicted first derivative at the start of the transition.
            Shape: (batch_size,)

        Raises
        ------
        ValueError
            If the first_derivative_at_start_status is unknown.
        """
        if self.first_derivative_at_start_status == "weights":
            return self._first_derivative_at_start_from_weights(features,transition_points)
        elif self.first_derivative_at_start_status == "none":
            return torch.full((features.batch_size,), torch.nan).to(self.device)
        else:
            raise ValueError(f"Unknown first_derivative_at_start_status: {self.first_derivative_at_start_status}")
    
    def predict_first_derivative_at_end(self, features: ProcessedFeatures, transition_points: torch.Tensor) -> torch.Tensor:
        """Predict the first derivative at the end of the transition.
        Parameters
        ----------
        features : ProcessedFeatures
            Processed features containing B, B_cat, categorical features indices, and categorical unique counts.
        transition_points : torch.Tensor
            Transition points tensor of shape (batch_size, n_transition_points, 2).
        Returns
        -------
        torch.Tensor
            Predicted first derivative at the end of the transition.
            Shape: (batch_size,)
        Raises
        ------
        ValueError
            If the first_derivative_at_end_status is unknown.
        """
        if self.first_derivative_at_end_status == "weights":
            return self._first_derivative_at_end_from_weights(features,transition_points)
        elif self.first_derivative_at_end_status == "zero":
            return torch.zeros(features.batch_size,).to(self.device)
        elif self.first_derivative_at_end_status == "cubic":
            return torch.full((features.batch_size,), torch.nan).to(self.device)
        else:
            raise ValueError(f"Unknown first_derivative_at_end_status: {self.first_derivative_at_end_status}")
        
    def predict_second_derivative_at_end(self, features: ProcessedFeatures) -> torch.Tensor:
        """Predict the second derivative at the end of the transition.
        Parameters
        ----------
        features : ProcessedFeatures
            Processed features containing B, B_cat, categorical features indices, and categorical unique counts.
        Returns
        -------
        torch.Tensor
            Predicted second derivative at the end of the transition.
            Shape: (batch_size,)
        Raises
        ------
        ValueError
            If the second_derivative_at_end_status is unknown.
        """
        if self.second_derivative_at_end_status == "weights":
            return self._second_derivative_at_end_from_weights(features)
        elif self.second_derivative_at_end_status == "zero":
            return torch.zeros(features.batch_size,).to(self.device)
        elif self.second_derivative_at_end_status == "cubic":
            return torch.full((features.batch_size,), torch.nan).to(self.device)
        else:
            raise ValueError(f"Unknown second_derivative_at_end_status: {self.second_derivative_at_end_status}")

    def _first_derivative_at_start_from_weights(self,features : ProcessedFeatures,finite_coordinates: torch.Tensor) -> torch.Tensor:
        """
        Calculate the first derivative at the start from B and the finite coordinates

        Args:
        features: an instance of ProcessedFeatures
        finite_coordinates: input tensor of shape (batch_size, n_all_coordinates, 2)

        Returns:
        output tensor of shape (batch_size,)
        """
        calculated_first_derivative = self._predict_gam('start', 1, features)
        result = utils.transform_first_derivative("start",self.composition, calculated_first_derivative, finite_coordinates)
        assert isinstance(result, torch.Tensor), "The result should be a torch.Tensor"
        return result
    

    def _first_derivative_at_end_from_weights(self, features: ProcessedFeatures, finite_coordinates: torch.Tensor) -> torch.Tensor:
        """
        Calculate the first derivative at the end from B

        Args:
        features: an instance of ProcessedFeatures

        Returns:
        output tensor of shape (batch_size,)
        """
        if not self.composition.is_bounded():
            result = self._predict_gam('end', 1, features)
        else:
            calculated_first_derivative = self._predict_gam('end', 1, features)
            result = utils.transform_first_derivative("end", self.composition, calculated_first_derivative, finite_coordinates)
        assert isinstance(result, torch.Tensor), "The result should be a torch.Tensor"
        return result

    def _second_derivative_at_end_from_weights(self,processed_features: ProcessedFeatures) -> torch.Tensor:
        """
        Calculate the second derivative at the end from B

        Args:
        features: an instance of ProcessedFeatures

        Returns:
        output tensor of shape (batch_size,)
        """
        return self._predict_gam('end', 2, processed_features)

    def _predict_gam(self, boundary, order, processed_features: ProcessedFeatures) -> torch.Tensor:
        """Predict the GAM (Generalized Additive Model) output for a given boundary and order.

        Parameters
        ----------
        boundary : str
            The boundary type, either 'start' or 'end'.
        order : int
            The order of the derivative, either 1 or 2.
        processed_features : ProcessedFeatures
            An instance of ProcessedFeatures containing the input features.

        Returns
        -------
        torch.Tensor
            The predicted GAM output.
            Shape: (batch_size,)
        """
        if boundary == 'start':
            if order == 1:
                if self.first_derivative_at_start_status == "weights":
                    # Needs to be transformed to the correct range
                    return torch_utils.calculate_gams(processed_features,self.first_derivative_at_start,self.cat_first_derivative_at_start,self.first_derivative_at_start_bias,positive=False,sum=True).flatten()
                else:
                    raise ValueError('First derivative at the start is not implemented as a trainable GAM')
            else:
                raise ValueError('Second derivative at the start is not implemented')
        elif boundary == 'end':
            if order == 1:
                if self.first_derivative_at_end_status == "weights":
                    if not self.composition.is_bounded():
                        # This is only triggered if there is only one motif in the infinite composition. 
                        # Otherwise, the first derivative at the end is calculated from the cubic coefficients or is set to zero.
                        sign = 1 if self.composition.motifs[-1][0] == '+' else -1
                        return sign * torch_utils.calculate_gams(processed_features,self.first_derivative_at_end,self.cat_first_derivative_at_end,self.first_derivative_at_end_bias,positive=True,sum=True).flatten()
                    else:
                        # Needs to be transformed to the correct range
                        return torch_utils.calculate_gams(processed_features,self.first_derivative_at_end,self.cat_first_derivative_at_end,self.first_derivative_at_end_bias,positive=False,sum=True).flatten()
                else:
                    raise ValueError('First derivative at the end is not implemented as a trainable GAM')
            elif order == 2:
                if self.second_derivative_at_end_status == "weights":
                    sign = 1 if self.composition.motifs[-1][1] == '+' else -1
                    return sign * torch_utils.calculate_gams(processed_features,self.second_derivative_at_end,self.cat_second_derivative_at_end,self.second_derivative_at_end_bias,positive=True,sum=True).flatten()
                else:
                    raise ValueError('Second derivative at the end is not implemented as a trainable GAM')
        raise ValueError(f"Unknown boundary: {boundary} or order: {order}")


    def _predict_shape_function(self, boundary, order, feature_index, b, X0 : torch.Tensor | None = None):
        """
        Extract the shape function of a derivative

        Args:
        boundary: string, either 'start' or 'end'
        order: integer, either 1 or 2
        feature_index: integer, index of the feature
        b: input tensor of shape (batch_size, n_basis_functions) or (batch_size, cat_n_unique) if categorical
        X0 (optional): input tensor of shape (batch_size, 1)

        Returns:
        output tensor of shape (batch_size,)
        """
        if boundary == 'start':
            if order == 1:
                if self.first_derivative_at_start_status == "weights":
                    return torch_utils.calculate_shape_functions_for_single_feature(b, feature_index, self.first_derivative_at_start, self.cat_first_derivative_at_start, positive=False)[:,0]
                else:
                    raise ValueError('First derivative at the start is not implemented as a trainable GAM')
            else:
                raise ValueError('Second derivative at the start is not implemented')
        elif boundary == 'end':
            if order == 1:
                if self.first_derivative_at_end_status == "weights":
                    if not self.composition.is_bounded():
                        sign = 1 if self.composition.motifs[-1][0] == '+' else -1
                        return sign * torch_utils.calculate_shape_functions_for_single_feature(b, feature_index, self.first_derivative_at_end, self.cat_first_derivative_at_end, positive=True)[:,0]
                    else:
                        # This would need to be passed by a sigmoid later
                        return torch_utils.calculate_shape_functions_for_single_feature(b, feature_index, self.first_derivative_at_end, self.cat_first_derivative_at_end, positive=True)[:,0]
                else:
                    raise ValueError('First derivative at the end is not implemented as a trainable GAM')
            elif order == 2:
                if self.second_derivative_at_end_status == "weights":
                    sign = 1 if self.composition.motifs[-1][1] == '+' else -1
                    return sign * torch_utils.calculate_shape_functions_for_single_feature(b, feature_index, self.second_derivative_at_end, self.cat_second_derivative_at_end, positive=True)[:,0]
                else:
                    raise ValueError('Second derivative at the end is not implemented as a trainable GAM')
        raise ValueError(f"Unknown boundary: {boundary} or order: {order}")
        
    def _predict_bias(self, boundary, order):
        """
        Extract the bias of a derivative

        Args:
        boundary: string, either 'start' or 'end'
        order: integer, either 1 or 2

        Returns:
        output tensor of shape (1,)
        """
        if boundary == 'start':
            if order == 1:
                if self.first_derivative_at_start_status == "weights":
                    return self.first_derivative_at_start_bias
                else:
                    return torch.zeros(1).to(self.device)
            else:
                raise ValueError('Second derivative at the start is not implemented')
        elif boundary == 'end':
            if order == 1:
                if self.first_derivative_at_end_status == "weights":
                    sign = 1 if self.composition.motifs[-1][0] == '+' else -1
                    return sign * torch.nn.functional.softplus(self.first_derivative_at_end_bias)
                else:
                    return torch.zeros(1).to(self.device)
            elif order == 2:
                if self.second_derivative_at_end_status == "weights":
                    sign = 1 if self.composition.motifs[-1][1] == '+' else -1
                    return sign * torch.nn.functional.softplus(self.second_derivative_at_end_bias)
                else:
                    return torch.zeros(1).to(self.device)
                
        raise ValueError(f"Unknown boundary: {boundary} or order: {order}")
    
class FinalMotifPropertyModule(torch.nn.Module):

    def __init__(self, config, transition_point_module: TransitionPointModule, derivative_module: DerivativeModule):
        super(FinalMotifPropertyModule, self).__init__()
        self.config = config
        self.composition = config['composition']
        self.n_basis_functions = config['n_basis_functions']
        self.n_features = config['n_features']
        self.seed = config['seed']
        self.n_coordinates = 2*len(self.composition)
        self.x0_included = config['x0_included']
        self.x0_index = config['x0_index']
        self.categorical_features_indices = config['categorical_features_indices']
        self.cat_n_unique_dict = config['cat_n_unique_dict']
        self.n_cat_features = len(self.categorical_features_indices)
        self.n_cont_features = self.n_features - self.n_cat_features
        self.device = utils.get_torch_device(config['device'])
        self.transition_point_module = transition_point_module
        self.derivative_module = derivative_module
        num_properties = self.composition.get_number_of_properties_for_unbounded_motif()
        if num_properties == 0:
            raise ValueError('No properties to predict for the final motif')
        self.infinite_motif_properties_weights = torch.nn.Parameter(torch.randn(self.n_basis_functions, self.n_cont_features, num_properties))
        self.cat_infinite_motif_properties_weights = torch.nn.ParameterDict({
            str(i): torch.nn.Parameter(torch.randn(self.cat_n_unique_dict[i], num_properties)) for i in self.categorical_features_indices
        })
        self.infinite_motif_properties_bias = torch.nn.Parameter(torch.randn(num_properties))
        self.scalers = {}
        self.scalers['infinite_motif_properties'] = torch.nn.Parameter(torch.randn(num_properties))
        self.scalers = torch.nn.ParameterDict(self.scalers)

    def predict(self, processed_features: ProcessedFeatures, transition_points: torch.Tensor, first_derivative_at_end : torch.Tensor, second_derivative_at_end : torch.Tensor) -> torch.Tensor:
        """Predict the generalized additive model (GAM) for the given processed features.

        Parameters
        ----------
        processed_features : ProcessedFeatures
            An instance of ProcessedFeatures containing the input features.
        transition_points : torch.Tensor
            Transition points tensor of shape (batch_size, n_transition_points, 2).

        Returns
        -------
        torch.Tensor
            The predicted GAM values.
            Shape: (batch_size, num_properties)
        """
        raw_properties = torch_utils.calculate_gams(processed_features,self.infinite_motif_properties_weights,self.cat_infinite_motif_properties_weights,self.infinite_motif_properties_bias,positive=True,sum=True) * torch.nn.functional.softplus(self.scalers['infinite_motif_properties'])
        # motif_class = get_default_motif_class(self.composition.motifs[-1])
        # x0 = transition_points[:,-1,0].reshape(-1,1)  # Last transition point t-coordinate
        # y0 = transition_points[:,-1,1].reshape(-1,1)
        # y1 = first_derivative_at_end.reshape(-1,1)
        # y2 = second_derivative_at_end.reshape(-1,1)
        # result = motif_class.extract_properties_from_network(raw_properties, x0, y0, y1, y2)
        return raw_properties

    
    def _predict_shape_function(self, property_index, feature_index, b, X0=None):
        """
        Extract the shape function of an infinite property

        Args:
        property_index: integer, index of the property
        feature_index: integer, index of the feature
        b: input tensor of shape (batch_size, n_basis_functions) or (batch_size, cat_n_unique) if categorical
        X0 (optional): input tensor of shape (batch_size, 1)

        Returns:
        output tensor of shape (batch_size,)
        """
        raw_shape_functions = torch_utils.calculate_shape_functions_for_single_feature(b, feature_index, self.infinite_motif_properties_weights, self.cat_infinite_motif_properties_weights, positive=True) * torch.nn.functional.softplus(self.scalers['infinite_motif_properties'])

        last_transition_point_index = len(self.composition.bounded_part)
        x0_shape_functions = self.transition_point_module._predict_shape_function(last_transition_point_index, "t", feature_index, b, X0=X0).reshape(-1,1)
        y0_shape_functions = self.transition_point_module._predict_shape_function(last_transition_point_index, "x", feature_index, b, X0=X0).reshape(-1,1)
        motif_class = get_default_motif_class(self.composition.motifs[-1])
        return motif_class.get_property_shapes(raw_shape_functions, x0_shape_functions, y0_shape_functions)[:,property_index]
    
    def _predict_bias(self, property_index):
        """
        Extract the bias of an infinite property

        Args:
        property_index: integer, index of the property

        Returns:
        output tensor of shape (1,)
        """
        raw_bias = torch.nn.functional.softplus(self.infinite_motif_properties_bias) * torch.nn.functional.softplus(self.scalers['infinite_motif_properties'])
        raw_bias = raw_bias.reshape(1,-1)
        last_transition_point_index = len(self.composition.bounded_part)
        x0_bias = self.transition_point_module._predict_bias(last_transition_point_index, 't').reshape(1,1)
        y0_bias = self.transition_point_module._predict_bias(last_transition_point_index, 'x').reshape(1,1)
        motif_class = get_default_motif_class(self.composition.motifs[-1])
        return motif_class.get_property_shapes(raw_bias, x0_bias, y0_bias)[0,property_index]