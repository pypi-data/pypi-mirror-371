"""
Clustering Models for Universal Scikit-learn Tools.

This module provides clustering model implementations including:
- K-Means clustering
- DBSCAN clustering
- Agglomerative clustering
- Spectral clustering
- Mean shift clustering
- OPTICS clustering
"""

import importlib
from typing import Dict, Any
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from .base_model import BaseSklearnModel


class ClusteringModels(BaseSklearnModel):
    """
    Clustering models implementation.
    
    This class provides functionality for training and evaluating various
    clustering models from scikit-learn.
    """
    
    def _get_model_mapping(self) -> Dict[str, Any]:
        """Define the model mapping for clustering algorithms."""
        return {
            "kmeans": {
                "module": "sklearn.cluster",
                "class": "KMeans",
                "type": "clustering",
                "metrics": ["silhouette", "calinski_harabasz", "davies_bouldin"],
                "description": "K-Means clustering"
            },
            "dbscan": {
                "module": "sklearn.cluster",
                "class": "DBSCAN",
                "type": "clustering",
                "metrics": ["silhouette", "calinski_harabasz", "davies_bouldin"],
                "description": "DBSCAN clustering"
            },
            "agglomerative_clustering": {
                "module": "sklearn.cluster",
                "class": "AgglomerativeClustering",
                "type": "clustering",
                "metrics": ["silhouette", "calinski_harabasz", "davies_bouldin"],
                "description": "Agglomerative clustering"
            },
            "spectral_clustering": {
                "module": "sklearn.cluster",
                "class": "SpectralClustering",
                "type": "clustering",
                "metrics": ["silhouette", "calinski_harabasz", "davies_bouldin"],
                "description": "Spectral clustering"
            },
            "mean_shift": {
                "module": "sklearn.cluster",
                "class": "MeanShift",
                "type": "clustering",
                "metrics": ["silhouette", "calinski_harabasz", "davies_bouldin"],
                "description": "Mean shift clustering"
            },
            "optics": {
                "module": "sklearn.cluster",
                "class": "OPTICS",
                "type": "clustering",
                "metrics": ["silhouette", "calinski_harabasz", "davies_bouldin"],
                "description": "OPTICS clustering"
            }
        }
    
    def _get_available_models(self) -> Dict[str, Any]:
        """Define available clustering models grouped by type."""
        return {
            "partitioning": {
                "kmeans": {
                    "description": "K-Means clustering",
                    "class": "KMeans",
                    "module": "sklearn.cluster",
                    "metrics": ["silhouette", "calinski_harabasz", "davies_bouldin"]
                }
            },
            "density_based": {
                "dbscan": {
                    "description": "DBSCAN clustering",
                    "class": "DBSCAN",
                    "module": "sklearn.cluster",
                    "metrics": ["silhouette", "calinski_harabasz", "davies_bouldin"]
                },
                "optics": {
                    "description": "OPTICS clustering",
                    "class": "OPTICS",
                    "module": "sklearn.cluster",
                    "metrics": ["silhouette", "calinski_harabasz", "davies_bouldin"]
                }
            },
            "hierarchical": {
                "agglomerative_clustering": {
                    "description": "Agglomerative clustering",
                    "class": "AgglomerativeClustering",
                    "module": "sklearn.cluster",
                    "metrics": ["silhouette", "calinski_harabasz", "davies_bouldin"]
                }
            },
            "spectral": {
                "spectral_clustering": {
                    "description": "Spectral clustering",
                    "class": "SpectralClustering",
                    "module": "sklearn.cluster",
                    "metrics": ["silhouette", "calinski_harabasz", "davies_bouldin"]
                }
            },
            "other": {
                "mean_shift": {
                    "description": "Mean shift clustering",
                    "class": "MeanShift",
                    "module": "sklearn.cluster",
                    "metrics": ["silhouette", "calinski_harabasz", "davies_bouldin"]
                }
            }
        }
    
    def fit_model(self, model_name: str, data: pd.DataFrame, **kwargs) -> Dict[str, Any]:
        """Fit a clustering model."""
        try:
            # Validate model name
            if model_name not in self.model_mapping:
                return self.create_error_result(
                    model_name,
                    f"Model '{model_name}' not found. Available models: {list(self.model_mapping.keys())}"
                )
            
            # Extract parameters
            random_state = kwargs.get('random_state', 42)
            
            # Remove non-model parameters
            model_params = {k: v for k, v in kwargs.items() 
                          if k not in ['random_state']}
            
            # Prepare data
            data_prep = self.prepare_data_for_unsupervised_learning(data)
            
            if "error" in data_prep:
                return self.create_error_result(model_name, data_prep["error"])
            
            X = data_prep["X"]
            
            # Scale features for clustering
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)
            
            # Import and instantiate model
            mapping = self.model_mapping[model_name]
            module = importlib.import_module(mapping["module"])
            model_class = getattr(module, mapping["class"])
            
            # Add random_state if the model supports it
            if hasattr(model_class, 'random_state'):
                model_params['random_state'] = random_state
            
            model = model_class(**model_params)
            
            # Fit the model and get clusters
            if hasattr(model, 'fit_predict'):
                clusters = model.fit_predict(X_scaled)
            else:
                model.fit(X_scaled)
                clusters = model.predict(X_scaled)
            
            # Calculate clustering metrics
            metrics = self.calculate_clustering_metrics(X_scaled, clusters)
            
            # Get cluster information
            n_clusters = len(np.unique(clusters))
            cluster_centers = None
            if hasattr(model, 'cluster_centers_'):
                cluster_centers = model.cluster_centers_.tolist()
            
            # Get cluster sizes
            cluster_sizes = {}
            for cluster_id in np.unique(clusters):
                if cluster_id != -1:  # Skip noise points (for DBSCAN, OPTICS)
                    cluster_sizes[f"cluster_{cluster_id}"] = int(np.sum(clusters == cluster_id))
            
            return self.create_result_dict(
                model_name=model_name,
                model=model,
                data_shape=X.shape,
                metrics=metrics,
                clusters=clusters.tolist() if hasattr(clusters, 'tolist') else clusters,
                n_clusters=n_clusters,
                cluster_centers=cluster_centers,
                cluster_sizes=cluster_sizes,
                label_encoders=data_prep["label_encoders"]
            )
            
        except Exception as e:
            return self.create_error_result(model_name, f"Failed to train {model_name}: {str(e)}")
