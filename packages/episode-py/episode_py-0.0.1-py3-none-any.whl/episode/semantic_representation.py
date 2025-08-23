from typing import Tuple, Union, Sequence, Self
import numpy as np
import torch
from episode.infinite_motifs import get_default_motif_class

class Composition:
    def __init__(self, motifs: Tuple[str, ...]):
        self.motifs = motifs

        if self.is_bounded():
            self.bounded_part = self.motifs
        else:
            self.bounded_part = tuple(list(self.motifs)[:-1])
    
    def __hash__(self):
        return hash(self.motifs)
    
    def __eq__(self, other):
        if not isinstance(other, Composition):
            return False
        return self.motifs == other.motifs
    
    def is_bounded(self):
        return self.motifs[-1][2] == 'b'
    
    def get_unbounded_motif(self) -> str | None:
        if not self.is_bounded():
            return self.motifs[-1]
        else:
            return None
    
    def type_of_transition_point(self, index: int) -> str:
        if index == 0:
            return 'start'
        elif index == len(self.motifs):
            return 'end'
        else:
            if (self.motifs[index-1][:2] == "++") and (self.motifs[index][:2] == "+-"):
                return 'inflection'
            elif (self.motifs[index-1][:2] == "+-") and (self.motifs[index][:2] == "++"):
                return 'inflection'
            elif (self.motifs[index-1][:2] == "+-") and (self.motifs[index][:2] == "--"):
                return 'max'
            elif (self.motifs[index-1][:2] == "-+") and (self.motifs[index][:2] == "++"):
                return 'min'
            elif (self.motifs[index-1][:2] == "-+") and (self.motifs[index][:2] == "--"):
                return 'inflection'
            elif (self.motifs[index-1][:2] == "--") and (self.motifs[index][:2] == "-+"):
                return 'inflection'
            else:
                raise ValueError('Unknown transition point type')
            

    def get_first_derivative_at_end_status(self) -> str:

        n_motifs = len(self)

        if not self.is_bounded():
            if n_motifs == 1:
                # If there is only one infinite motif, then the first derivative at end is specified by the parameter/weights
                return "weights"
            else:
                # If there is a bounded motif before the infinite motif
                index_last_finite_tp = n_motifs - 1
                type_of_last_finite_tp = self.type_of_transition_point(index_last_finite_tp)

                if type_of_last_finite_tp == 'max' or type_of_last_finite_tp == 'min':
                    # It has to be zero
                    return "zero"
                elif type_of_last_finite_tp == 'inflection':
                    # It is determined by the cubic because the second derivative is fixed at 0
                    return "cubic"
                else:
                    raise ValueError(f"Unknown type of last finite transition point: {type_of_last_finite_tp}")
        else:
            # If the composition is finite, then the first derivative at end is specified by the parameter/weights
            # unless the composition has only one motif
            if n_motifs == 1:
                return "cubic"
            else:
                return "weights"
    
    def get_second_derivative_at_end_status(self) -> str:
        
        n_motifs = len(self)

        if not self.is_bounded():
            if n_motifs == 1:
                # If there is only one infinite motif, then the second derivative at end is specified by the parameter/weights
                # unless the unbounded motif does not allow for anyhting but zero
                if get_default_motif_class(self.motifs[-1]).second_derivative_vanishes():
                    return "zero"
                else:
                    return "weights"
            else:
                # If there is a bounded motif before the infinite motif
                index_last_finite_tp = n_motifs - 1
                type_of_last_finite_tp = self.type_of_transition_point(index_last_finite_tp)

                if type_of_last_finite_tp == 'max' or type_of_last_finite_tp == 'min':
                    # Determined by the cubic because the first derivative is fixed at 0
                    return "cubic"
                elif type_of_last_finite_tp == 'inflection':
                    # It has to be zero
                    return "zero"
                else:
                    raise ValueError(f"Unknown type of last finite transition point: {type_of_last_finite_tp}")
        else:
            # If the composition if finite then the second derivative at end is specified by the cubic
            # As it is the first derivative at end that determins the cubic
            return "cubic"
    
    def get_first_derivative_at_start_status(self) -> str:

        n_motifs = len(self)

        if not self.is_bounded():
            if n_motifs == 1:
                # If there is only one infinite motif, then the first derivative at start is none because it coincides with the end
                return "none"
            else:
                # If there is a bounded motif before the infinite motif then the first derivative at start is specified by the parameter/weights
                return "weights"
        else:
            # If the composition is finite, then the first derivative at start is specified by the parameter/weights
            return "weights"
        
    def get_number_of_properties_for_unbounded_motif(self) -> int:
        if not self.is_bounded():
            return get_default_motif_class(self.motifs[-1]).num_network_properties()
        return 0
    
    def get_first_derivative_range_coefficients(self, motif_index: int, which_point: str) -> Tuple[float, float]:
        motif = self.motifs[motif_index]
                                    
        if which_point == 'left':
            if motif == '++b':
                if self.type_of_transition_point(motif_index+1) == 'end':
                    return (0,1)
                elif self.type_of_transition_point(motif_index+1) == 'inflection':
                    return (0,1)
            elif motif == "+-b":
                if self.type_of_transition_point(motif_index+1) == 'end':
                    return (1,2)
                elif self.type_of_transition_point(motif_index+1) == 'max':
                    return (1.5,3)
                elif self.type_of_transition_point(motif_index+1) == 'inflection':
                    return (1,3)
            elif motif == "-+b":
                if self.type_of_transition_point(motif_index+1) == 'end':
                    return (1,2)
                elif self.type_of_transition_point(motif_index+1) == 'min':
                    return (1.5,3)
                elif self.type_of_transition_point(motif_index+1) == 'inflection':
                    return (1,3)
            elif motif == "--b":
                if self.type_of_transition_point(motif_index+1) == 'end':
                    return (0,1)
                elif self.type_of_transition_point(motif_index+1) == 'inflection':
                    return (0,1)
        
        elif which_point == 'right':
            if motif == '++b':
                if self.type_of_transition_point(motif_index) == 'inflection':
                    return (1,3)
                elif self.type_of_transition_point(motif_index) == 'min':
                    return (1.5,3)
            elif motif == "+-b":
                if self.type_of_transition_point(motif_index) == 'inflection':
                    return (0,1)
            elif motif == "-+b":
                if self.type_of_transition_point(motif_index) == 'inflection':
                    return (0,1)
            elif motif == "--b":
                if self.type_of_transition_point(motif_index) == 'inflection':
                    return (1,3)
                elif self.type_of_transition_point(motif_index) == 'max':
                    return (1.5,3)
            
        raise ValueError(f"Unknown motif: {motif} or point: {which_point}")

    def __len__(self) -> int:
        return len(self.motifs)
    
    def __str__(self) -> str:
        formatted_motifs = []
        for motif in self.motifs:
            # Replace 'c' with 'b' and 'f', 'p' with 'u'
            motif_string = str(motif).replace('c','b').replace('f','u').replace('p','u')
            motif_string = "s_{"+str(motif_string)+"}"
            formatted_motifs.append(motif_string)
        return fr"$({', '.join(formatted_motifs)})$"
        
    
    @staticmethod
    def create_composition(motifs: Tuple[str, ...] | Sequence[str]) -> 'Composition':
        """Create a Composition object from a sequence of motifs.
        
        Parameters
        ----------
        motifs : Tuple[str, ...] | Sequence[str]
            A sequence of motif strings.
        
        Returns
        -------
        Composition
            A Composition object representing the motifs.
        """
        if isinstance(motifs, Sequence):
            motifs = tuple(motifs)
        return Composition(motifs)
    
    @staticmethod
    def create_composition_library(list_of_motifs: Sequence[Tuple[str, ...]] | Sequence[Sequence[str]]) -> Sequence['Composition']:
        """Create a library of Composition objects from a list of motifs.

        Parameters
        ----------
        list_of_motifs : Sequence[Tuple[str, ...]] | Sequence[Sequence[str]]
            A sequence of sequences of motif strings.
        Returns
        -------
        Sequence[Composition]
            A list of Composition objects representing the motifs.
        """
        compositions = []
        for motifs in list_of_motifs:
            compositions.append(Composition.create_composition(motifs))
        return compositions
    
    @staticmethod
    def create_full_composition_library(max_length,is_infinite, simplified=False):

        motif_succession_rules = {
            '+-':['--','++'],
            '-+':['--','++'],
            '--':['-+'],
            '++':['+-']
        }

        motif_infinite_types = {
            '++':['f'],
            '+-':['p','h'],
            '-+':['f','h'],
            '--':['f']
        }

        all_compositions = []
        # dfs graph search algorithm
        def dfs(current_composition):

            if len(current_composition) > 0: # We do not add empty composition
                if is_infinite and current_composition[-1][2] != 'b':
                    all_compositions.append(current_composition)
                    return # The last motif is infinite, we cannot add more motifs
                elif not is_infinite:
                    all_compositions.append(current_composition)
                # If the is_infinite but the last motif is finite, it's not a valid composition, so we do not add it to the list

            if len(current_composition) == max_length:
                return

            def expand(new_motif):
                if is_infinite:
                    # We can make it a final motif by adding an infinite extension
                    for infinite_extension in motif_infinite_types[new_motif]:
                        dfs(current_composition.copy() + [new_motif + infinite_extension])
                    # We can also add a finite extension if there is still space
                    if len(current_composition) < max_length-1:
                        dfs(current_composition.copy() + [new_motif + 'b'])
                else:
                    dfs(current_composition.copy() + [new_motif + 'b'])

            if len(current_composition) == 0:
                for new_motif in ['+-','--','-+','++']:
                    expand(new_motif)
            else:
                for new_motif in motif_succession_rules[current_composition[-1][0:2]]:
                    expand(new_motif)
            
        dfs([])

        def is_simple(composition):
            for i in range(2,len(composition)):
                if composition[i][:2] == composition[i-2][:2]:
                    return False
            return True

        if simplified:
            all_compositions = [composition for composition in all_compositions if is_simple(composition)]

        return Composition.create_composition_library(all_compositions)

class Properties:

    def __init__(self,
                  engine: str,
                  composition: Composition,
                  transition_points: Union[np.ndarray, torch.Tensor],
                  first_derivative_start: Union[np.ndarray, torch.Tensor],
                  first_derivative_end: Union[np.ndarray, torch.Tensor],
                  second_derivative_end: Union[np.ndarray, torch.Tensor],
                  unbounded_motif_properties: Union[None, np.ndarray, torch.Tensor] = None,
                  unbounded_motif_properties_raw: bool = False):
        """Initialize the Properties class.

        Parameters
        ----------
        engine : str
            The computational engine to use ('pytorch' or 'numpy').
        composition : Composition
            Composition object containing motif information.
        transition_points : Union[np.ndarray, torch.Tensor]
            Array or tensor of transition points of shape (n_samples, n_transition_points,2).
        first_derivative_start : Union[np.ndarray, torch.Tensor]
            Array or tensor of first derivative start points of shape (n_samples, 1).
        first_derivative_end : Union[np.ndarray, torch.Tensor]
            Array or tensor of first derivative end points of shape (n_samples, 1).
        second_derivative_end : Union[np.ndarray, torch.Tensor]
            Array or tensor of second derivative end points of shape (n_samples, 1).
        unbounded_motif_properties : Union[None, np.ndarray, torch.Tensor], optional
            Properties for unbounded motifs, if applicable. Defaults to None.
        Raises
        ------
        ValueError
            If the engine is not 'pytorch' or 'numpy'.
        """
        self.engine = engine
        self.composition = composition
        if engine not in ['pytorch', 'numpy']:
            raise ValueError("Engine must be either 'pytorch' or 'numpy'.")
        self.transition_points = transition_points
        self.first_derivative_start = first_derivative_start
        self.first_derivative_end = first_derivative_end
        self.second_derivative_end = second_derivative_end
        self.unbounded_motif_properties = unbounded_motif_properties
        self.unbounded_motif_properties_raw = unbounded_motif_properties_raw

    def is_unbounded_motif_properties_raw(self) -> bool:
        return self.unbounded_motif_properties_raw
    
    def __len__(self):
        return len(self.transition_points)
    
    def __repr__(self):
        return (f"Properties(engine={self.engine}, "
                f"composition={self.composition}, "
                f"transition_points_shape={self.transition_points.shape}, "
                f"first_derivative_start_shape={self.first_derivative_start.shape}, "
                f"first_derivative_end_shape={self.first_derivative_end.shape}, "
                f"second_derivative_end_shape={self.second_derivative_end.shape}, "
                f"unbounded_motif_properties_shape={self.unbounded_motif_properties.shape if self.unbounded_motif_properties is not None else None})")

class SemanticRepresentation:
    def __init__(self, compositions: Sequence[Composition], predicted_composition_indices: np.ndarray, engine: str = 'numpy'):
        """Initialize the SemanticRepresentation class.

        Parameters
        ----------
        compositions : Sequence[Composition]
            A sequence of Composition objects.
        predicted_composition_indices : np.ndarray
            An array of predicted composition indices.
            Should be of shape (n_samples,) and contain integers representing indices of compositions.
        engine : str, optional
            The computational engine to use ('pytorch' or 'numpy'), by default 'numpy'
        """
      
        self.compositions = compositions
        self.predicted_composition_indices = predicted_composition_indices
        self.engine = engine
        self.properties_dict = {}
    def add_properties(self, properties: Properties):

        if properties.composition in self.properties_dict.keys():
            raise ValueError(f"Properties for composition {properties.composition} already exist in the semantic representation.")
        
        composition_index = self.compositions.index(properties.composition)
        assert np.sum(self.predicted_composition_indices == composition_index) == len(properties), \
            f"Number of samples in properties ({len(properties)}) does not match the number of samples with composition index {composition_index} ({np.sum(self.predicted_composition_indices == composition_index)})"
        self.properties_dict[properties.composition] = (composition_index, properties)

    def get_present_compositions(self) -> Sequence[Composition]:
        """Get a list of compositions that have associated properties.

        Returns
        -------
        Sequence[Composition]
            A sequence of compositions with properties.
        """
        unique_composition_ids = np.unique(self.predicted_composition_indices)
        return [self.compositions[i] for i in unique_composition_ids if self.compositions[i] in self.properties_dict]

    def get_properties_by_composition(self, composition: Composition) -> Tuple[Properties,np.ndarray]:
        """Get properties for a specific composition.

        Parameters
        ----------
        composition : Composition
            The composition for which to retrieve properties.
        Returns
        -------
        Properties 
            The properties associated with the specified composition.
        """
        if composition not in self.get_present_compositions():
            raise ValueError(f"No samples with composition: {composition}")
        if composition not in self.properties_dict:
            raise ValueError(f"No properties specified for composition: {composition}")
        
        mask = self.predicted_composition_indices == self.properties_dict[composition][0]

        return self.properties_dict[composition][1], mask


# class SemanticRepresentation:

#     def __init__(self, engine: str):
#         self.engine = engine
#         if engine not in ['pytorch', 'numpy']:
#             raise ValueError("Engine must be either 'pytorch' or 'numpy'.")
#         self.subsets = []
#         self.slices = []
    
#     def add_properties(self, properties: Properties):
#         self.subsets.append(properties)
#         if len(self.slices) == 0:
#             start = 0
#         else:
#             start = self.slices[-1][1]
#         end = start + len(properties)
#         self.slices.append((start, end, properties.composition))

#     def get_present_compositions(self):
#         return list(set(s[2] for s in self.slices))

#     def get_properties_by_composition(self, composition: Composition):
#         """Get properties for a specific composition. If there are multiple 
#         subsets with same composition, create a new Properties object that
#         combines their properties. Also return a list of indices which is a contatenation
#         of indices defined by the slices of the subsets with the same composition.

#         Parameters
#         ----------
#         composition : Composition
#             The composition for which to retrieve properties.

#         Returns
#         -------
#         Properties
#             A Properties object containing the combined properties for the specified composition.
#         list[int]
#             A list of indices corresponding to the slices of the subsets with the same composition.
#         """

#         properties_to_concat = []
#         indices = []
#         for i, s in enumerate(self.slices):
#             if s[2] == composition:
#                 properties_to_concat.append(self.subsets[i])
#                 indices.append((s[0], s[1]))

#         if not properties_to_concat:
#             raise ValueError(f"No properties found for composition: {composition}")
        
#         # Combine properties
#         if self.engine == 'pytorch':
#             combined_transition_points = torch.cat([p.transition_points for p in properties_to_concat], dim=0)
#             combined_first_derivative_start = torch.cat([p.first_derivative_start for p in properties_to_concat], dim=0)
#             combined_first_derivative_end = torch.cat([p.first_derivative_end for p in properties_to_concat], dim=0)
#             combined_second_derivative_end = torch.cat([p.second_derivative_end for p in properties_to_concat], dim=0)
#         elif self.engine == 'numpy':
#             combined_transition_points = np.concatenate([p.transition_points for p in properties_to_concat], axis=0)
#             combined_first_derivative_start = np.concatenate([p.first_derivative_start for p in properties_to_concat], axis=0)
#             combined_first_derivative_end = np.concatenate([p.first_derivative_end for p in properties_to_concat], axis=0)
#             combined_second_derivative_end = np.concatenate([p.second_derivative_end for p in properties_to_concat], axis=0)
#         else:
#             raise ValueError("Unsupported engine type. Must be 'pytorch' or 'numpy'.")
        
#         combined_properties = Properties(
#             engine=self.engine,
#             composition=composition,
#             transition_points=combined_transition_points,
#             first_derivative_start=combined_first_derivative_start,
#             first_derivative_end=combined_first_derivative_end,
#             second_derivative_end=combined_second_derivative_end
#             )
#         return combined_properties, indices

#     def __len__(self):
#         return self.slices[-1][1] if self.slices else 0

