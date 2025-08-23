from episode.composition_map import CompositionMapBase, NDCompositionMapBase
from episode.semantic_representation import SemanticRepresentation, Composition
from episode.property_map import SinglePropertyMap, PropertyMapBase, NDPropertyMapBase
from episode import utils
import numpy as np
import matplotlib.pyplot as plt
from episode.dataset import FeatureDataset
from episode.types import NpArrayOrList


class NDSemanticPredictor:

    def __init__(self, nd_composition_map: NDCompositionMapBase, nd_property_map: NDPropertyMapBase):
        self.nd_composition_map = nd_composition_map
        self.nd_property_map = nd_property_map
        self.per_dim = [SemanticPredictor(
            composition_map=nd_composition_map.per_dim[m],
            property_map=nd_property_map.per_dim[m]
        ) for m in range(nd_composition_map.M)]


class SemanticPredictor:

    def __init__(self, composition_map: CompositionMapBase, property_map: PropertyMapBase):
        """
        Args:
        compostion_map: a CompositionMap object
        property_maps: a dictionary with keys (composition: tuple of strings) and values of type SinglePropertyMap
        t_range: a tuple of floats representing the range of the time variable
        """
        self.composition_map = composition_map
        self.property_map = property_map
        self.all_compositions = self.composition_map.composition_library

    def predict(self,V: FeatureDataset):
        """
        Predict the semantic representation

        Args:
        V: a numpy array of shape (batch_size, n_features)

        Returns:
        a list of SemanticRepresentation objects
        """
        composition_indices = self.composition_map.predict_composition_indices(V)
        unique_composition_indices = np.unique(composition_indices)

        semantic_representation = SemanticRepresentation(self.all_compositions, composition_indices)

        for composition_index in unique_composition_indices:
            mask = composition_indices == composition_index
            V_filtered = V.filter_by_mask(mask)
            composition = self.all_compositions[composition_index]
            properties = self.property_map.predict(composition,V_filtered)
            semantic_representation.add_properties(properties)
        
        return semantic_representation
    
    def fit(self,V: FeatureDataset,T: NpArrayOrList,Y: NpArrayOrList):
        """
        Fit the semantic predictor to the data

        Parameters:
        ----------
        V: FeatureDataset
            The input feature dataset.
        T: NpArrayOrList
            The target values.
        Y: NpArrayOrList
            The additional target values.

        """
        self.composition_map.fit(V, T, Y)
        self.property_map.fit(V, T, Y, self.composition_map)
