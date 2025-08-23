import pandas as pd
from typing import Sequence
import numpy as np
import pandas as pd
from episode import utils


class FeatureDataset:
    def __init__(
            self, 
            V: np.ndarray,
            feature_names: Sequence[str],
            categorical_features_indices: Sequence[int],
            categories: dict[int,Sequence[str]]
            ):
        self.array = V
        self.feature_names = feature_names
        self.categorical_features_indices = categorical_features_indices
        self.categories = categories
        assert set(self.categories.keys()) == set(self.categorical_features_indices), \
            "Categories must match the categorical feature indices."
        self.n_features = V.shape[1]
        self.n_samples = V.shape[0]

    def filter_by_mask(self, mask: np.ndarray | list[bool]) -> 'FeatureDataset':
        V_copy= self.array.copy()
        V_filtered = V_copy[mask]

        return FeatureDataset(
            V_filtered,
            self.feature_names,
            self.categorical_features_indices,
            self.categories
        )
       

class FeatureTransformer:

    def __init__(self):
       self.is_fitted = False

    def _is_categorical_type(self, type: str) -> bool:
        return type in ['object', 'category', 'string', 'bool', 'int']

    def fit_df(self, V_df: pd.DataFrame):
        V_df = V_df.copy()
        self.categories = {}
        self.feature_names = V_df.columns.tolist()
        self.categorical_features_indices = [
            i for i, col in enumerate(self.feature_names) if self._is_categorical_type(V_df[col].dtype.name)
        ]
        for i in self.categorical_features_indices:
            V_df.iloc[:, i] = V_df.iloc[:, i].astype('category')
            self.categories[i] = list(V_df.iloc[:, i].cat.categories)
        self.is_fitted = True

        
    def transform_df(self, V_df: pd.DataFrame) -> FeatureDataset:
        if not self.is_fitted:
            raise RuntimeError("Transformer must be fitted before transforming data.")
        V_df = V_df.copy()
        for i in self.categorical_features_indices:
            V_df.iloc[:, i] = V_df.iloc[:, i].astype('category')
            V_df.iloc[:,i] = V_df.iloc[:,i].cat.set_categories(self.categories[i]) # type: ignore
            column_name = self.feature_names[i]
            V_df[column_name] = V_df[column_name].cat.codes
            V_df[column_name] = V_df[column_name].astype('float32')
        
        V = V_df.to_numpy(dtype='float32')
        return FeatureDataset(
            V, 
            self.feature_names, 
            self.categorical_features_indices, 
            self.categories)
    
    def fit_numpy(
        self, 
        V: np.ndarray, 
        categorical_features_indices: Sequence[int], 
        feature_names: Sequence[str] | None = None, 
        categories: dict[int,Sequence[str]] | None = None):
        if categories is None:
            self.categories = {}
            for i in categorical_features_indices:
                self.categories[i] = np.unique(V[:, i]).tolist()
        else:
            for i in categorical_features_indices:
                assert len(categories[i]) >= len(np.unique(V[:, i])), \
                    f"Categories for feature index {i} must cover all unique values in the data."
            self.categories = categories
        if feature_names is None:
            self.feature_names = [f"feature_{i}" for i in range(V.shape[1])]
        else:
            self.feature_names = feature_names
        self.categorical_features_indices = categorical_features_indices
        self.is_fitted = True

    def transform_numpy(self, V: np.ndarray) -> FeatureDataset:
        if not self.is_fitted:
            raise RuntimeError("Transformer must be fitted before transforming data.")
        V = V.copy()
        for i in self.categorical_features_indices:
            # Convert to integer codes based on categories
            assert set(np.unique(V[:, i])).issubset(set(self.categories[i])), \
                f"Categories for feature index {i} must cover all unique values in the data."
            category_to_code = {cat: float(code) for code, cat in enumerate(self.categories[i])}
            V[:, i] = np.vectorize(category_to_code.get)(V[:, i], -1)
            
        return FeatureDataset(
            V,
            self.feature_names,
            self.categorical_features_indices,
            self.categories
        )
    
    def fit_transform_df(self, V_df: pd.DataFrame) -> FeatureDataset:
        self.fit_df(V_df)
        return self.transform_df(V_df)
    
    def fit_transform_numpy(
        self, V: np.ndarray, 
        categorical_features_indices: Sequence[int], 
        feature_names: Sequence[str] | None = None, 
        categories: dict[int,Sequence[str]] | None = None
        ) -> FeatureDataset:
        self.fit_numpy(V, categorical_features_indices, feature_names, categories)
        return self.transform_numpy(V)