from abc import abstractmethod
from episode.semantic_representation import SemanticRepresentation, Properties, Composition
from typing import Sequence, Union
import numpy as np
import torch
import episode.utils as utils
from episode import cubic
from episode.infinite_motifs import get_default_motif_class
from numba import jit
from episode.types import NpArrayOrTensor, ArrayOrList
from array_api_compat import array_namespace, is_numpy_namespace


class TrajectoryPredictorBase:

    def __init__(self):
        pass

    def predict(self, 
                semantic_rep: SemanticRepresentation, 
                timepoints: ArrayOrList
                ) -> ArrayOrList:
        
        compositions = semantic_rep.get_present_compositions()
        
        if isinstance(timepoints, Sequence):
            xp = array_namespace(timepoints[0])
            result = [xp.array([])] * len(timepoints)
            for composition in compositions:
                properties, mask = semantic_rep.get_properties_by_composition(composition)
                masked_t = utils.filter_by_mask(timepoints, mask)
                predictions = self._predict_from_properties(properties, masked_t)
                utils._assign_to_mask(mask, result, predictions)
        else:
            xp = array_namespace(timepoints)
            result = xp.zeros_like(timepoints)
            for composition in compositions:
                properties, mask = semantic_rep.get_properties_by_composition(composition)
                masked_t = utils.filter_by_mask(timepoints, mask)
                predictions = self._predict_from_properties(properties, masked_t)
                result[mask] = predictions
        
        return result

    @abstractmethod
    def _predict_from_properties(self, properties: Properties, timepoints: ArrayOrList) -> ArrayOrList:
        pass


class C0TrajectoryPredictor(TrajectoryPredictorBase):

    def __init__(self):
        super().__init__()
        self.cached_coefficients_bounded_part: NpArrayOrTensor | None = None

    def _predict_from_properties(self, properties: Properties, timepoints: ArrayOrList) -> ArrayOrList:

        transition_points = properties.transition_points
        first_derivative_start = properties.first_derivative_start
        first_derivative_end = properties.first_derivative_end
        second_derivative_end = properties.second_derivative_end
        composition = properties.composition

        coefficients_bounded_part = self._get_coefficients_bounded_composition(
            composition,
            transition_points,
            first_derivative_start,
            first_derivative_end,
            second_derivative_end
        )  # shape (n_samples, n_bounded_motifs, 4)

        xp = array_namespace(coefficients_bounded_part, timepoints)

        if isinstance(timepoints, Sequence):
            timepoints, mask = utils.pad_and_mask(timepoints)
        else:
            mask = None

        T = timepoints
        Y = xp.zeros_like(T)

        knots = properties.transition_points[:, :, 0]
        last_transition_point = properties.transition_points[:,-1,:]

        # If unbounded motif then add infinite knots at the end
        if not properties.composition.is_bounded():
            knots = xp.concatenate([knots, xp.full((knots.shape[0], 1), xp.inf)], axis=1)

        for i in range(len(properties.composition)):

            if utils.is_bounded_motif(properties.composition.motifs[i]):
                coefficients = coefficients_bounded_part[:, i, :]
                values = cubic.evaluate_cubic(coefficients,T)
            else:
                x0 = last_transition_point[:,[0]]
                y0 = last_transition_point[:,[1]]
                t_end = last_transition_point[:,0]

                y1 = properties.first_derivative_end.flatten()
                y2 = properties.second_derivative_end.flatten()

                if xp.isnan(y1).any():
                    # when there is no first derivative, estimate from the last cubic
                    y1 = xp.where(xp.isnan(y1), cubic.first_derivative_at_end_from_cubic(coefficients_bounded_part, t_end), y1)
                if xp.isnan(y2).any():
                    # when there is no second derivative, estimate from the last cubic
                    y2 = xp.where(xp.isnan(y2), cubic.second_derivative_at_end_from_cubic(coefficients_bounded_part, t_end), y2)

                infinite_motif_properties = properties.unbounded_motif_properties
                # infinite motif
                motif_class = get_default_motif_class(properties.composition.motifs[i])
                T_to_use = xp.where(T < x0, x0, T) # make sure we don't evaluate the infinite motif before the last transition point - this might cause errors
                
                if properties.is_unbounded_motif_properties_raw():
                    values = motif_class.evaluate_from_network(T_to_use,infinite_motif_properties, x0, y0, y1.reshape(-1, 1), y2.reshape(-1, 1))
                else:
                    values = motif_class.evaluate_from_properties(T_to_use,infinite_motif_properties, x0, y0, y1.reshape(-1, 1), y2.reshape(-1, 1))
                
            Y += xp.where(
                (T >= knots[:, [i]]) & (T < knots[:, [i + 1]]),
                values,
                0)
        
        if properties.composition.is_bounded():
            # Due the sharp inequalities earlier, we need to add the last piece separately
            coefficients = coefficients_bounded_part[:, i, :]
            values = cubic.evaluate_cubic(coefficients,T)
            Y += xp.where(T == knots[:,[-1]], values, 0)

            
        if mask is not None:
            # Apply mask and return a list of arrays
            result = []
            for i in range(len(Y)):
                result.append(Y[i, mask[i]])
        else:
            result = Y

        return result
    
    def _get_first_derivative_at_end_from_cubic(self, composition: Composition, transition_points: NpArrayOrTensor, first_derivative_start) -> NpArrayOrTensor:

        assert composition.get_first_derivative_at_end_status() == 'cubic', "This method is only applicable for compositions with cubic first derivative at the end."

        xp = array_namespace(transition_points, first_derivative_start)
        n_samples = transition_points.shape[0]
        first_derivative_end = xp.full((n_samples, 1), xp.nan)
        second_derivative_end = xp.full((n_samples, 1), xp.nan)

        coefficients_bounded_part = self._get_coefficients_bounded_composition(
            composition,
            transition_points,
            first_derivative_start,
            first_derivative_end,
            second_derivative_end
        )
        last_transition_point = transition_points[:,-1,:]
        t_end = last_transition_point[:,0]
        first_derivative_end = cubic.first_derivative_at_end_from_cubic(coefficients_bounded_part, t_end).reshape(-1, 1)

        return first_derivative_end

    def _get_second_derivative_at_end_from_cubic(self, composition: Composition, transition_points: NpArrayOrTensor, first_derivative_start) -> NpArrayOrTensor:

        assert composition.get_second_derivative_at_end_status() == 'cubic', "This method is only applicable for compositions with cubic second derivative at the end."
        
        xp = array_namespace(transition_points, first_derivative_start)
        n_samples = transition_points.shape[0]
        first_derivative_end = xp.full((n_samples, 1), xp.nan)
        second_derivative_end = xp.full((n_samples, 1), xp.nan)

        coefficients_bounded_part = self._get_coefficients_bounded_composition(
            composition,
            transition_points,
            first_derivative_start,
            first_derivative_end,
            second_derivative_end
        )
        last_transition_point = transition_points[:,-1,:]
        t_end = last_transition_point[:,0]

        second_derivative_end = cubic.second_derivative_at_end_from_cubic(coefficients_bounded_part, t_end).reshape(-1, 1)

        return second_derivative_end

    def _get_coefficients_bounded_composition(
            self,
            composition: Composition,
            transition_points: NpArrayOrTensor, 
            first_derivative_start: NpArrayOrTensor,
            first_derivative_end: NpArrayOrTensor,
            second_derivative_end: NpArrayOrTensor
            ) -> NpArrayOrTensor:



        xp = array_namespace(transition_points, first_derivative_start, first_derivative_end, second_derivative_end)

       
        n_samples, n_transition_points, _ = transition_points.shape
        bounded = composition.is_bounded()

        if bounded:
            assert n_transition_points == len(composition) + 1
        else:
            assert n_transition_points == len(composition)
        
        b = np.zeros((n_samples,3))
        coefficients_list = []

        for motif_index, motif in enumerate(composition.bounded_part):
            coordinate_1 = transition_points[:,motif_index,:]
            coordinate_2 = transition_points[:,motif_index+1,:]

            A_row_0 = cubic.create_row(coordinate_1,0)
            A_row_1 = cubic.create_row(coordinate_2,0)
            b_0 = coordinate_1[:,1]
            b_1 = coordinate_2[:,1]

            type_1 = composition.type_of_transition_point(motif_index)
            type_2 = composition.type_of_transition_point(motif_index+1)
            if type_1 == 'max' or type_1 == 'min':
                A_row_2 = cubic.create_row(coordinate_1,1)
                b_2 = xp.zeros(n_samples)
            elif type_1 == 'inflection':
                A_row_2 = cubic.create_row(coordinate_1,2)
                b_2 = xp.zeros(n_samples)
            elif type_1 == 'start' and composition.get_first_derivative_at_start_status() == "weights":
                A_row_2 = cubic.create_row(coordinate_1,1)
                b_2 = first_derivative_start[:,0] # needs to satisfy requirements
                # calculated_first_derivative_ratio = sigmoid(first_derivative_at_start)
                # slope_min, slope_max = self.get_first_derivative_range(motif_index, coordinate_1, coordinate_2, "left")
                # b_2 = slope_min + calculated_first_derivative_ratio * (slope_max - slope_min)
                if type_2 == 'end':
                    # in that case we reduce the cubic to a quadratic, assign [1,0,0,0] to all samples using np.tile
                    A_row_3 = xp.tile(xp.array([1, 0, 0, 0]), (n_samples, 1))
                    b_3 = xp.zeros(n_samples)
            else:
                raise ValueError("Invalid combination of transition point types.")
            
            if type_2 == 'max' or type_2 == 'min':
                A_row_3 = cubic.create_row(coordinate_2,1)
                b_3 = xp.zeros(n_samples)
            elif type_2 == 'inflection':
                A_row_3 = cubic.create_row(coordinate_2,2)
                b_3 = xp.zeros(n_samples)
            elif (type_2 == 'end' and composition.get_first_derivative_at_end_status() == 'weights') and type_1 != 'start':
                # TODO: I am not sure if this can ever happen. Think about this
                A_row_3 = cubic.create_row(coordinate_2,1)
                b_3 = first_derivative_end[:,0] # needs to satisfy requirements
                # calculated_first_derivative_ratio = sigmoid(first_derivative_at_end)
                # slope_min, slope_max = self.get_first_derivative_range(motif_index, coordinate_1, coordinate_2, "right")
                # b_3 = slope_min + calculated_first_derivative_ratio * (slope_max - slope_min)
            else:
                raise ValueError("Invalid combination of transition point types.")

            A = xp.stack([A_row_0, A_row_1, A_row_2, A_row_3], axis=1)
            b = xp.stack([b_0, b_1, b_2, b_3], axis=1)

            # Calculate the determinant of A to check if it's well-conditioned
            determinants = xp.linalg.det(A)
            bad_indices = (xp.abs(determinants) < 1e-9) | (xp.abs(determinants) > 1e9)

            coefficients = xp.zeros((n_samples, 4))

            # For bad indices, just connect with a line
            slope = (coordinate_2[bad_indices,1] - coordinate_1[bad_indices,1])/(coordinate_2[bad_indices,0]-coordinate_1[bad_indices,0])
            line_b = coordinate_1[bad_indices,1] - slope * coordinate_1[bad_indices,0]
            singular_coefficients = xp.stack([xp.zeros_like(line_b),xp.zeros_like(line_b),slope,line_b],axis=1)

            if is_numpy_namespace(xp):
                solver = utils.linalg_solve_multiple_numpy
            else:
                solver = torch.linalg.solve

            try:
                non_singular_coefficients = solver(A[~bad_indices,:,:], b[~bad_indices,:])
            except:
                # Just connect all with a line if solving fails
                slope = (coordinate_2[:,1] - coordinate_1[:,1])/(coordinate_2[:,0]-coordinate_1[:,0])
                line_b = coordinate_1[:,1] - slope * coordinate_1[:,0]
                non_singular_coefficients = xp.stack([xp.zeros_like(line_b),xp.zeros_like(line_b),slope,line_b],axis=1)

            coefficients[bad_indices,:] = singular_coefficients
            coefficients[~bad_indices,:] = non_singular_coefficients

            coefficients_list.append(coefficients)
        
        if len(coefficients_list) == 0:
            all_coefficients = xp.zeros((0, 0, 4))
        else:
            all_coefficients = xp.stack(coefficients_list, axis=1) # shape (n_samples, n_motifs, 4)

        self.cached_coefficients_bounded_part = all_coefficients

        return all_coefficients





        



