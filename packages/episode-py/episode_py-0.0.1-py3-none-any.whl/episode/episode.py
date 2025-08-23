import numpy as np
import pandas as pd
from episode.dataset import FeatureDataset
from episode.types import NpArrayOrList
from episode.semantic_predictor import SemanticPredictor, NDSemanticPredictor
from episode.trajectory_predictor import TrajectoryPredictorBase



class NDEPISODE:

    def __init__(
        self,
        M: int,
        nd_semantic_predictor: NDSemanticPredictor,
        trajectory_predictor: TrajectoryPredictorBase,
        ):
        self.M = M
        self.trajectory_predictor = trajectory_predictor
        self.nd_semantic_predictor = nd_semantic_predictor
        self.per_dim = [
            EPISODE(
                semantic_predictor=nd_semantic_predictor.per_dim[m],
                trajectory_predictor=trajectory_predictor
            ) for m in range(M)]
     
    def fit(self,V: FeatureDataset,T: NpArrayOrList ,Y: NpArrayOrList):
        for m, episode in enumerate(self.per_dim):
            Y_m = [y[:,m] for y in Y]
            T_m = T
            V_m = V
            episode.fit(V_m,T_m,Y_m)

    def predict(self,V: FeatureDataset,T: NpArrayOrList) -> NpArrayOrList:
        Y_pred_per_dim = []
        for m, episode in enumerate(self.per_dim):
            Y_pred_m = episode.predict(V,T)
            Y_pred_per_dim.append(Y_pred_m)
        Y_pred = []
        for i in range(len(T)):
            Y_pred.append(np.stack([Y_pred_per_dim[m][i] for m in range(len(self.per_dim))], axis=1))
        if isinstance(T, np.ndarray):
            Y_pred = np.stack(Y_pred, axis=0)
        return Y_pred
        
    
class EPISODE:

    def __init__(
        self,
        semantic_predictor: SemanticPredictor,
        trajectory_predictor: TrajectoryPredictorBase,
        ):
        self.semantic_predictor = semantic_predictor
        self.trajectory_predictor = trajectory_predictor

    def fit(self,V: FeatureDataset, T: NpArrayOrList, Y: NpArrayOrList):
      
        self.semantic_predictor.fit(V,T,Y)

    def predict(self,V: FeatureDataset,T: NpArrayOrList) -> NpArrayOrList:

        semantic_representation = self.semantic_predictor.predict(V)
        Y_pred = self.trajectory_predictor.predict(semantic_representation, T)
        
        return Y_pred  # type: ignore
    

