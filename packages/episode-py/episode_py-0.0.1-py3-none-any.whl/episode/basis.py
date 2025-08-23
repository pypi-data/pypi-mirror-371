from abc import ABC, abstractmethod
import numpy as np
from scipy.interpolate import BSpline

class BasisFunctions(ABC):

    def __init__(self, n_basis):
        self.n_basis = n_basis

    @abstractmethod
    def compute(self, X, X_ranges) -> np.ndarray:
        pass

class BSplineBasisFunctions(BasisFunctions):

    def __init__(self,n_basis, k=3, include_bias=True, include_linear=False):
        super().__init__(n_basis)
        self.k = k
        self.include_bias = include_bias
        self.include_linear = include_linear
    
    def compute(self,X,X_ranges):

        categorical_features_indices = [i for i in range(X.shape[1]) if not isinstance(X_ranges[i],tuple)]

        if self.include_bias:
            n_b_basis = self.n_basis - 1
        else:
            n_b_basis = self.n_basis

        if self.include_linear:
            n_b_basis = n_b_basis - 1

        def singleton_vector(n,k):
            vector = np.zeros(n)
            vector[k] = 1
            return vector
        
        n_features = X.shape[1]
        B_list = []

        for feature_index in range(n_features):

            if feature_index in categorical_features_indices:
                continue

            x_range = X_ranges[feature_index]

            shape_knots = np.r_[[x_range[0]]*self.k,np.linspace(x_range[0], x_range[1], n_b_basis-self.k+1),[x_range[1]]*self.k]
       
            bsplines = [BSpline(shape_knots,singleton_vector(n_b_basis,k_index),k=self.k,extrapolate=False) for k_index in range(n_b_basis)]
            
            X_i = X[:,feature_index].flatten()
            # bspline_basis_per_sample = [BSpline(shape_knots,singleton_vector(n_b_basis,k_index),k=self.k,extrapolate=False)(X.flatten()) for k_index in range(n_b_basis)]
            bspline_basis_per_sample = [bspline(X_i) for bspline in bsplines]
            # fill na values with 0
            final_list = []
            for i, values in enumerate(bspline_basis_per_sample):
                below = X_i <= x_range[0]
                above = X_i >= x_range[1]
                values[below] = bsplines[i](x_range[0])
                values[above] = bsplines[i](x_range[1])
                # print(X.flatten())
                # print(values)
                if np.any(np.isnan(values)):
                    print(f'Nan values found for basis function {i}')
                    print(f'X: {X_i}')
                    print(f'Values: {values}')
                final_list.append(values)

            if self.include_bias:
                # add the constant basis function
                final_list.append(np.ones_like(X_i))
            
            if self.include_linear:
                # add the linear basis function
                values = X_i
                below = X_i <= x_range[0]
                above = X_i >= x_range[1]
                values[below] = x_range[0]
                values[above] = x_range[1]
                final_list.append(values)


            B_i = np.stack(final_list, axis=1) # shape (n_samples, n_basis)
            B_list.append(B_i)

        B = np.stack(B_list, axis=1) # shape (n_samples, n_cont_features, n_basis)
        return B
    
class OneHotBasisFunctions():

    def __init__(self):
        pass
    
    def compute(self,V,V_ranges):
        """
        Compute the one-hot encoded basis functions for the given input and ranges.
        Parameters:
        ----------
        V: a numpy array of shape (n_samples, n_features)
        V_ranges: a list of tuples or sets representing ranges of the features
        Returns:
        -------
        B: a numpy array of shape (n_samples, sum(n_unique_values))
        n_unique_values_dict: a dictionary mapping feature indices to the number of unique values in each feature
        """
        categorical_features_indices = [i for i in range(len(V_ranges)) if not isinstance(V_ranges[i],tuple)]
        B_list = []
        n_unique_values_dict = {}
        for feature_index in categorical_features_indices:
            
            V_i = V[:,feature_index].flatten()
            unique_values = np.unique(V_i)

            # Check whether all unique values are in the appropriate range
            unique_values_set = set(unique_values)
            V_i_range = V_ranges[feature_index]
            if not unique_values_set.issubset(V_i_range):
                raise ValueError(f'Unique values {unique_values} for feature {feature_index} are not in the range {V_i_range}. \
                                 They were either not availalbe during training or do not belong to the appropriate leaves')
            
            V_i_range_list = sorted(list(V_i_range))
    
            n_unique_values = len(V_i_range_list)

            B_i = np.zeros((V_i.shape[0],n_unique_values))
            for i, value in enumerate(V_i_range_list):
                B_i[V_i == value,i] = 1
            B_list.append(B_i)

            n_unique_values_dict[feature_index] = n_unique_values
        
        B = np.concatenate(B_list, axis=1) # shape (n_samples, sum(n_unique_values))
        return B, n_unique_values_dict

    def compute_single(self,V,V_ranges,feature_index):
        """
        Args: 
        V: a numpy array of shape (n_samples, n_features)
        V_ranges: a list of tuples or sets representing ranges of the features
        feature_index: index of the feature to compute the one-hot encoding for
        Returns:
        -------
        B: a numpy array of shape (n_samples, n_unique_values)
        """
        categorical_features_indices = [i for i in range(len(V_ranges)) if not isinstance(V_ranges[i],tuple)]
        
        if feature_index not in categorical_features_indices:
            raise ValueError(f'Feature {feature_index} is not a categorical feature')
        
        B_list = []
        V_i = V[:,feature_index].flatten()
        unique_values = np.unique(V_i)

        # Check whether all unique values are in the appropriate range
        unique_values_set = set(unique_values)
        V_i_range = V_ranges[feature_index]
        if not unique_values_set.issubset(V_i_range):
            raise ValueError(f'Unique values {unique_values} for feature {feature_index} are not in the range {V_i_range}. \
                                They were either not availalbe during training or do not belong to the appropriate leaves')
        
        V_i_range_list = sorted(list(V_i_range))

        n_unique_values = len(V_i_range_list)

        B_i = np.zeros((V_i.shape[0],n_unique_values))
        for i, value in enumerate(V_i_range_list):
            B_i[V_i == value,i] = 1

        return B_i    