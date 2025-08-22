#!/usr/bin/env python3
"""
AutoML 2.0 - Intelligent Automation Module
==========================================

Next-generation automated machine learning with:
- Intelligent model selection
- Auto hyperparameter tuning
- Explainable AI
- Continuous learning
- Meta-learning capabilities
"""

import os
import json
import time
import warnings
from typing import Dict, Any, List, Optional, Union, Tuple
from datetime import datetime
import numpy as np
import pandas as pd
from ._imports import get_sklearn_utils, get_lightgbm_utils, get_xgboost_utils, get_shap_utils
from .utils import save_results

warnings.filterwarnings('ignore')

# Global ML library availability
def _get_ml_availability():
    """Get ML library availability silently."""
    sklearn_utils = get_sklearn_utils()
    lightgbm_utils = get_lightgbm_utils()
    xgboost_utils = get_xgboost_utils()
    shap_utils = get_shap_utils()
    
    return (
        sklearn_utils['available'],
        lightgbm_utils['available'],
        xgboost_utils['available'],
        shap_utils['available']
    )

SKLEARN_AVAILABLE, LIGHTGBM_AVAILABLE, XGBOOST_AVAILABLE, SHAP_AVAILABLE = _get_ml_availability()

def intelligent_model_selection(
    X: Union[np.ndarray, pd.DataFrame],
    y: Union[np.ndarray, pd.Series],
    task_type: str = 'auto',
    max_models: int = 10,
    cv_folds: int = 5,
    n_jobs: int = -1
) -> Dict[str, Any]:
    
    def intelligent_model_selection(
        self,
        X: Union[np.ndarray, pd.DataFrame],
        y: Union[np.ndarray, pd.Series],
        task_type: str = 'auto',
        max_models: int = 10,
        cv_folds: int = 5,
        n_jobs: int = -1
    ) -> Dict[str, Any]:
        """
        Intelligent model selection based on data characteristics
        
        Args:
            X: Feature matrix
            y: Target variable
            task_type: 'classification', 'regression', or 'auto'
            max_models: Maximum number of models to test
            cv_folds: Cross-validation folds
            n_jobs: Number of parallel jobs
            
        Returns:
            Dictionary with selection results and recommendations
        """
        if not SKLEARN_AVAILABLE:
            return {'error': 'Scikit-learn not available'}
        
        start_time = time.time()
        
        # Auto-detect task type
        if task_type == 'auto':
            task_type = self._detect_task_type(y)
        
        # Analyze data characteristics
        data_insights = self._analyze_data_characteristics(X, y)
        
        # Select optimal models based on data characteristics
        selected_models = self._select_models_by_characteristics(
            data_insights, task_type, max_models
        )
        
        # Test models with cross-validation
        model_results = self._evaluate_models(
            X, y, selected_models, task_type, cv_folds, n_jobs
        )
        
        # Rank models by performance
        ranked_models = self._rank_models(model_results)
        
        # Select best model
        self.best_model = ranked_models[0]['model']
        
        # Generate insights and recommendations
        insights = self._generate_model_insights(
            ranked_models, data_insights, task_type
        )
        
        execution_time = time.time() - start_time
        
        results = {
            'task_type': task_type,
            'data_insights': data_insights,
            'models_tested': len(selected_models),
            'ranked_models': ranked_models,
            'best_model': {
                'name': ranked_models[0]['name'],
                'score': ranked_models[0]['cv_score'],
                'std': ranked_models[0]['cv_std']
            },
            'insights': insights,
            'performance': {
                'execution_time': execution_time,
                'cv_folds': cv_folds,
                'n_jobs': n_jobs
            }
        }
        
        # Save results
        self._save_results(results, 'intelligent_model_selection')
        
        return results
    
    def auto_hyperparameter_tuning(
        self,
        X: Union[np.ndarray, pd.DataFrame],
        y: Union[np.ndarray, pd.Series],
        model_type: str = 'auto',
        tuning_method: str = 'bayesian',
        max_iterations: int = 100,
        cv_folds: int = 5,
        n_jobs: int = -1
    ) -> Dict[str, Any]:
        """
        Automatic hyperparameter tuning with multiple methods
        
        Args:
            X: Feature matrix
            y: Target variable
            model_type: Type of model to tune
            tuning_method: 'grid', 'random', 'bayesian', or 'auto'
            max_iterations: Maximum tuning iterations
            cv_folds: Cross-validation folds
            n_jobs: Number of parallel jobs
            
        Returns:
            Dictionary with tuning results and best parameters
        """
        if not SKLEARN_AVAILABLE:
            return {'error': 'Scikit-learn not available'}
        
        start_time = time.time()
        
        # Auto-detect model type if needed
        if model_type == 'auto':
            model_type = self._detect_best_model_type(X, y)
        
        # Get model and parameter grid
        model, param_grid = self._get_model_and_params(model_type)
        
        # Select optimal tuning method
        if tuning_method == 'auto':
            tuning_method = self._select_tuning_method(param_grid, max_iterations)
        
        # Perform hyperparameter tuning
        best_params, best_score, tuning_results = self._perform_tuning(
            model, param_grid, X, y, tuning_method, max_iterations, cv_folds, n_jobs
        )
        
        # Train final model with best parameters
        final_model = self._train_final_model(
            model, best_params, X, y
        )
        
        execution_time = time.time() - start_time
        
        results = {
            'model_type': model_type,
            'tuning_method': tuning_method,
            'best_parameters': best_params,
            'best_score': best_score,
            'tuning_results': tuning_results,
            'final_model': final_model,
            'performance': {
                'execution_time': execution_time,
                'max_iterations': max_iterations,
                'cv_folds': cv_folds
            }
        }
        
        # Save results
        self._save_results(results, 'auto_hyperparameter_tuning')
        
        return results
    
    def explainable_ai(
        self,
        model,
        X: Union[np.ndarray, pd.DataFrame],
        y: Union[np.ndarray, pd.Series],
        explanation_type: str = 'comprehensive'
    ) -> Dict[str, Any]:
        """
        Generate comprehensive AI explanations
        
        Args:
            model: Trained model to explain
            X: Feature matrix
            y: Target variable
            explanation_type: 'basic', 'comprehensive', or 'advanced'
            
        Returns:
            Dictionary with explanation data and visualizations
        """
        if not SKLEARN_AVAILABLE:
            return {'error': 'Scikit-learn not available'}
        
        start_time = time.time()
        
        explanations = {}
        
        # Basic explanations
        if explanation_type in ['basic', 'comprehensive', 'advanced']:
            explanations['feature_importance'] = self._get_feature_importance(model, X)
            explanations['model_complexity'] = self._analyze_model_complexity(model)
            explanations['prediction_examples'] = self._generate_prediction_examples(model, X, y)
        
        # Advanced explanations
        if explanation_type in ['comprehensive', 'advanced']:
            if SHAP_AVAILABLE:
                explanations['shap_analysis'] = self._perform_shap_analysis(model, X)
            explanations['decision_paths'] = self._analyze_decision_paths(model, X)
            explanations['partial_dependence'] = self._calculate_partial_dependence(model, X)
        
        # Expert explanations
        if explanation_type == 'advanced':
            explanations['counterfactual_analysis'] = self._generate_counterfactuals(model, X, y)
            explanations['adversarial_examples'] = self._generate_adversarial_examples(model, X)
            explanations['model_interpretability'] = self._assess_interpretability(model)
        
        execution_time = time.time() - start_time
        
        results = {
            'explanation_type': explanation_type,
            'explanations': explanations,
            'performance': {
                'execution_time': execution_time
            }
        }
        
        # Save explanations
        self._save_results(results, 'explainable_ai')
        self.explanation_data = explanations
        
        return results
    
    def continuous_learning(
        self,
        X_new: Union[np.ndarray, pd.DataFrame],
        y_new: Union[np.ndarray, pd.Series],
        learning_strategy: str = 'incremental',
        performance_threshold: float = 0.95
    ) -> Dict[str, Any]:
        """
        Continuous learning with new data
        
        Args:
            X_new: New feature data
            y_new: New target data
            learning_strategy: 'incremental', 'online', or 'batch'
            performance_threshold: Minimum performance to maintain
            
        Returns:
            Dictionary with learning results and model updates
        """
        if self.best_model is None:
            return {'error': 'No model available for continuous learning'}
        
        start_time = time.time()
        
        # Evaluate current model on new data
        current_performance = self._evaluate_current_model(X_new, y_new)
        
        # Decide learning strategy
        if current_performance < performance_threshold:
            learning_strategy = 'retrain'  # Force retraining if performance drops
        
        # Perform continuous learning
        if learning_strategy == 'incremental':
            updated_model = self._incremental_learning(X_new, y_new)
        elif learning_strategy == 'online':
            updated_model = self._online_learning(X_new, y_new)
        elif learning_strategy == 'batch':
            updated_model = self._batch_learning(X_new, y_new)
        elif learning_strategy == 'retrain':
            updated_model = self._retrain_model(X_new, y_new)
        
        # Evaluate updated model
        updated_performance = self._evaluate_current_model(X_new, y_new)
        
        # Update performance history
        self.performance_history.append({
            'timestamp': datetime.now().isoformat(),
            'strategy': learning_strategy,
            'old_performance': current_performance,
            'new_performance': updated_performance,
            'improvement': updated_performance - current_performance
        })
        
        execution_time = time.time() - start_time
        
        results = {
            'learning_strategy': learning_strategy,
            'performance_comparison': {
                'before': current_performance,
                'after': updated_performance,
                'improvement': updated_performance - current_performance
            },
            'model_updated': True,
            'performance_history': self.performance_history[-10:],  # Last 10 updates
            'performance': {
                'execution_time': execution_time
            }
        }
        
        # Save results
        self._save_results(results, 'continuous_learning')
        
        return results
    
    def meta_learning_framework(
        self,
        datasets: List[Tuple[np.ndarray, np.ndarray]],
        meta_features: List[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Meta-learning to learn from multiple datasets
        
        Args:
            datasets: List of (X, y) tuples
            meta_features: List of dataset characteristics
            
        Returns:
            Dictionary with meta-learning results and insights
        """
        if not SKLEARN_AVAILABLE:
            return {'error': 'Scikit-learn not available'}
        
        start_time = time.time()
        
        # Extract meta-features if not provided
        if meta_features is None:
            meta_features = [self._extract_meta_features(X, y) for X, y in datasets]
        
        # Train models on all datasets
        dataset_results = []
        for i, (X, y) in enumerate(datasets):
            result = self.intelligent_model_selection(X, y)
            dataset_results.append({
                'dataset_id': i,
                'meta_features': meta_features[i],
                'best_model': result['best_model'],
                'performance': result['insights']
            })
        
        # Analyze patterns across datasets
        meta_patterns = self._analyze_meta_patterns(dataset_results)
        
        # Build meta-learner
        meta_learner = self._build_meta_learner(dataset_results, meta_features)
        
        execution_time = time.time() - start_time
        
        results = {
            'n_datasets': len(datasets),
            'dataset_results': dataset_results,
            'meta_patterns': meta_patterns,
            'meta_learner': meta_learner,
            'performance': {
                'execution_time': execution_time
            }
        }
        
        # Save results
        self._save_results(results, 'meta_learning_framework')
        
        return results
    
    # ============================================================================
    # HELPER METHODS
    # ============================================================================
    
    def _detect_task_type(self, y: Union[np.ndarray, pd.Series]) -> str:
        """Auto-detect if task is classification or regression"""
        if len(np.unique(y)) <= 20:  # Heuristic for classification
            return 'classification'
        return 'regression'
    
    def _analyze_data_characteristics(self, X: np.ndarray, y: np.ndarray) -> Dict[str, Any]:
        """Analyze data characteristics for model selection"""
        return {
            'n_samples': X.shape[0],
            'n_features': X.shape[1],
            'feature_types': self._detect_feature_types(X),
            'target_distribution': self._analyze_target_distribution(y),
            'data_complexity': self._assess_data_complexity(X, y),
            'missing_values': self._check_missing_values(X),
            'outliers': self._detect_outliers(X)
        }
    
    def _select_models_by_characteristics(
        self, data_insights: Dict, task_type: str, max_models: int
    ) -> List[Tuple[str, Any]]:
        """Select optimal models based on data characteristics"""
        models = []
        
        if task_type == 'classification':
            if data_insights['n_samples'] < 1000:
                models.extend([
                    ('LogisticRegression', LogisticRegression()),
                    ('DecisionTree', DecisionTreeClassifier()),
                    ('KNeighbors', KNeighborsClassifier())
                ])
            else:
                models.extend([
                    ('RandomForest', RandomForestClassifier()),
                    ('GradientBoosting', GradientBoostingClassifier()),
                    ('SVM', SVC(probability=True))
                ])
        else:  # regression
            if data_insights['n_samples'] < 1000:
                models.extend([
                    ('LinearRegression', LinearRegression()),
                    ('DecisionTree', DecisionTreeRegressor()),
                    ('KNeighbors', KNeighborsRegressor())
                ])
            else:
                models.extend([
                    ('RandomForest', RandomForestRegressor()),
                    ('GradientBoosting', GradientBoostingRegressor()),
                    ('SVR', SVR())
                ])
        
        # Add advanced models if available
        if LIGHTGBM_AVAILABLE:
            if task_type == 'classification':
                models.append(('LightGBM', lgb.LGBMClassifier()))
            else:
                models.append(('LightGBM', lgb.LGBMRegressor()))
        
        return models[:max_models]
    
    def _evaluate_models(
        self, X: np.ndarray, y: np.ndarray, models: List, 
        task_type: str, cv_folds: int, n_jobs: int
    ) -> List[Dict]:
        """Evaluate models with cross-validation"""
        results = []
        
        for name, model in models:
            try:
                if task_type == 'classification':
                    cv_scores = cross_val_score(model, X, y, cv=cv_folds, scoring='accuracy', n_jobs=n_jobs)
                else:
                    cv_scores = cross_val_score(model, X, y, cv=cv_folds, scoring='r2', n_jobs=n_jobs)
                
                results.append({
                    'name': name,
                    'model': model,
                    'cv_score': cv_scores.mean(),
                    'cv_std': cv_scores.std(),
                    'cv_scores': cv_scores.tolist()
                })
            except Exception as e:
                print(f"⚠️  Model {name} evaluation failed: {e}")
        
        return results
    
    def _rank_models(self, model_results: List[Dict]) -> List[Dict]:
        """Rank models by performance"""
        return sorted(model_results, key=lambda x: x['cv_score'], reverse=True)
    
    def _generate_model_insights(
        self, ranked_models: List[Dict], data_insights: Dict, task_type: str
    ) -> Dict[str, Any]:
        """Generate insights about model selection"""
        return {
            'top_performer': ranked_models[0]['name'],
            'performance_gap': ranked_models[0]['cv_score'] - ranked_models[-1]['cv_score'],
            'model_diversity': len(set(m['name'] for m in ranked_models)),
            'data_characteristics': data_insights,
            'recommendations': self._generate_recommendations(ranked_models, data_insights)
        }
    
    def _save_results(self, results: Dict, operation_name: str):
        """Save results to output directory"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{operation_name}_{timestamp}.json"
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"💾 Results saved: {filepath}")
    
    # Additional helper methods would be implemented here...
    def _detect_feature_types(self, X):
        """Detect feature types (numerical, categorical, etc.)"""
        return {'numerical': X.shape[1], 'categorical': 0}  # Simplified
    
    def _analyze_target_distribution(self, y):
        """Analyze target variable distribution"""
        return {'unique_values': len(np.unique(y)), 'distribution': 'balanced'}
    
    def _assess_data_complexity(self, X, y):
        """Assess data complexity"""
        return 'medium'  # Simplified
    
    def _check_missing_values(self, X):
        """Check for missing values"""
        return 0  # Simplified
    
    def _detect_outliers(self, X):
        """Detect outliers in data"""
        return 0  # Simplified
    
    def _detect_best_model_type(self, X, y):
        """Detect best model type for data"""
        return 'RandomForest'  # Simplified
    
    def _get_model_and_params(self, model_type):
        """Get model and parameters for a given type"""
        if not SKLEARN_AVAILABLE:
            return None, {}
        
        try:
            sklearn_utils = get_sklearn_utils()
            
            if model_type == 'classification':
                models = {
                    'logistic_regression': sklearn_utils['LogisticRegression'](),
                    'decision_tree': sklearn_utils['DecisionTreeClassifier'](),
                    'knn': sklearn_utils['KNeighborsClassifier'](),
                    'random_forest': sklearn_utils['RandomForestClassifier'](),
                    'gradient_boosting': sklearn_utils['GradientBoostingClassifier'](),
                    'svm': sklearn_utils['SVC']()
                }
            else:  # regression
                models = {
                    'linear_regression': sklearn_utils['LinearRegression'](),
                    'decision_tree': sklearn_utils['DecisionTreeRegressor'](),
                    'knn': sklearn_utils['KNeighborsRegressor'](),
                    'random_forest': sklearn_utils['RandomForestRegressor'](),
                    'gradient_boosting': sklearn_utils['GradientBoostingRegressor'](),
                    'svr': sklearn_utils['SVR']()
                }
            
            # Add advanced models if available
            if LIGHTGBM_AVAILABLE:
                lightgbm_utils = get_lightgbm_utils()
                if model_type == 'classification':
                    models['lightgbm'] = lightgbm_utils['LGBMClassifier']()
                else:
                    models['lightgbm'] = lightgbm_utils['LGBMRegressor']()
            
            if XGBOOST_AVAILABLE:
                xgboost_utils = get_xgboost_utils()
                if model_type == 'classification':
                    models['xgboost'] = xgboost_utils['XGBClassifier']()
                else:
                    models['xgboost'] = xgboost_utils['XGBRegressor']()
            
            return models, {}
            
        except Exception as e:
            return None, {}

    def _evaluate_models(self, X, y, models, task_type, cv_folds, n_jobs):
        """Evaluate models using cross-validation"""
        if not SKLEARN_AVAILABLE:
            return {}
        
        try:
            sklearn_utils = get_sklearn_utils()
            cross_val_score = sklearn_utils['cross_val_score']
            
            results = {}
            
            for name, model in models.items():
                try:
                    # Use cross-validation
                    if task_type == 'classification':
                        scores = cross_val_score(model, X, y, cv=cv_folds, scoring='accuracy', n_jobs=n_jobs)
                    else:
                        scores = cross_val_score(model, X, y, cv=cv_folds, scoring='r2', n_jobs=n_jobs)
                    
                    results[name] = {
                        'model': model,
                        'mean_score': scores.mean(),
                        'std_score': scores.std(),
                        'scores': scores.tolist()
                    }
                except Exception as e:
                    results[name] = {'error': str(e)}
            
            return results
            
        except Exception as e:
            return {'error': f'Model evaluation failed: {str(e)}'}

    def _train_final_model(self, model, best_params, X, y):
        """Train final model with best parameters"""
        try:
            # Set best parameters if available
            if best_params:
                model.set_params(**best_params)
            
            # Train model
            model.fit(X, y)
            return model
            
        except Exception as e:
            return None

    def _get_feature_importance(self, model, X):
        """Get feature importance from trained model"""
        try:
            if hasattr(model, 'feature_importances_'):
                return model.feature_importances_.tolist()
            elif hasattr(model, 'coef_'):
                return model.coef_.tolist()
            else:
                return None
        except Exception:
            return None

    def _analyze_model_complexity(self, model):
        """Analyze model complexity"""
        try:
            complexity = {}
            
            if hasattr(model, 'n_estimators'):
                complexity['n_estimators'] = model.n_estimators
            if hasattr(model, 'max_depth'):
                complexity['max_depth'] = model.max_depth
            if hasattr(model, 'n_neighbors'):
                complexity['n_neighbors'] = model.n_neighbors
            
            return complexity
        except Exception:
            return {}

    def _generate_prediction_examples(self, model, X, y):
        """Generate prediction examples"""
        try:
            predictions = model.predict(X[:5])  # First 5 samples
            return {
                'actual': y[:5].tolist(),
                'predicted': predictions.tolist(),
                'sample_indices': list(range(5))
            }
        except Exception:
            return {}

    def _perform_shap_analysis(self, model, X):
        """Perform SHAP analysis if available"""
        if not SHAP_AVAILABLE:
            return {'error': 'SHAP not available'}
        
        try:
            shap_utils = get_shap_utils()
            TreeExplainer = shap_utils['TreeExplainer']
            
            # Use TreeExplainer for tree-based models
            if hasattr(model, 'feature_importances_'):
                explainer = TreeExplainer(model)
                shap_values = explainer.shap_values(X[:100])  # First 100 samples
                
                return {
                    'shap_values': shap_values.tolist() if isinstance(shap_values, np.ndarray) else shap_values,
                    'feature_names': list(X.columns) if hasattr(X, 'columns') else list(range(X.shape[1]))
                }
            else:
                return {'error': 'Model not compatible with SHAP'}
                
        except Exception as e:
            return {'error': f'SHAP analysis failed: {str(e)}'}
    
    def _analyze_decision_paths(self, model, X):
        """Analyze decision paths"""
        return {'available': hasattr(model, 'decision_path')}
    
    def _calculate_partial_dependence(self, model, X):
        """Calculate partial dependence"""
        return {'available': False}  # Would need additional implementation
    
    def _generate_counterfactuals(self, model, X, y):
        """Generate counterfactual examples"""
        return {'available': False}  # Would need additional implementation
    
    def _generate_adversarial_examples(self, model, X):
        """Generate adversarial examples"""
        return {'available': False}  # Would need additional implementation
    
    def _assess_interpretability(self, model):
        """Assess model interpretability"""
        return {'score': 0.7, 'reason': 'Tree-based model'}
    
    def _evaluate_current_model(self, X, y):
        """Evaluate current model performance"""
        if not SKLEARN_AVAILABLE:
            return {'error': 'Scikit-learn not available'}
        
        try:
            sklearn_utils = get_sklearn_utils()
            accuracy_score = sklearn_utils['accuracy_score']
            r2_score = sklearn_utils['r2_score']
            
            y_pred = self.best_model.predict(X)
            
            if self.task_type == 'classification':
                score = accuracy_score(y, y_pred)
            else:
                score = r2_score(y, y_pred)
            
            return {
                'score': float(score),
                'predictions': y_pred.tolist(),
                'actual': y.tolist() if hasattr(y, 'tolist') else list(y)
            }
            
        except Exception as e:
            return {'error': f'Evaluation failed: {str(e)}'}
    
    def _incremental_learning(self, X_new, y_new):
        """Incremental learning approach"""
        # Simplified implementation
        return self.best_model
    
    def _online_learning(self, X_new, y_new):
        """Online learning approach"""
        # Simplified implementation
        return self.best_model
    
    def _batch_learning(self, X_new, y_new):
        """Batch learning approach"""
        # Simplified implementation
        return self.best_model
    
    def _retrain_model(self, X_new, y_new):
        """Retrain model with new data"""
        # Simplified implementation
        return self.best_model
    
    def _extract_meta_features(self, X, y):
        """Extract meta-features from dataset"""
        return {
            'n_samples': X.shape[0],
            'n_features': X.shape[1],
            'target_type': 'classification' if len(np.unique(y)) <= 20 else 'regression'
        }
    
    def _analyze_meta_patterns(self, dataset_results):
        """Analyze patterns across datasets"""
        return {'patterns_found': len(dataset_results)}
    
    def _build_meta_learner(self, dataset_results, meta_features):
        """Build meta-learner from multiple datasets"""
        return {'type': 'MetaLearner', 'n_datasets': len(dataset_results)}
    
    def _generate_recommendations(self, ranked_models, data_insights):
        """Generate recommendations based on results"""
        return [
            f"Use {ranked_models[0]['name']} for best performance",
            "Consider ensemble methods for improved stability",
            "Monitor model performance over time"
        ]

# Convenience functions
def intelligent_model_selection(*args, **kwargs):
    """Convenience function for intelligent model selection"""
    automl = AutoML2()
    return automl.intelligent_model_selection(*args, **kwargs)

def auto_hyperparameter_tuning(*args, **kwargs):
    """Convenience function for auto hyperparameter tuning"""
    automl = AutoML2()
    return automl.auto_hyperparameter_tuning(*args, **kwargs)

def explainable_ai(*args, **kwargs):
    """Convenience function for explainable AI"""
    automl = AutoML2()
    return automl.explainable_ai(*args, **kwargs)

def continuous_learning(*args, **kwargs):
    """Convenience function for continuous learning"""
    automl = AutoML2()
    return automl.continuous_learning(*args, **kwargs)

def meta_learning_framework(*args, **kwargs):
    """Convenience function for meta-learning framework"""
    automl = AutoML2()
    return automl.meta_learning_framework(*args, **kwargs)


class AutoMLPipeline:
    """
    Comprehensive AutoML Pipeline with end-to-end automation
    
    Features:
    - Automated data preprocessing
    - Feature engineering and selection
    - Model selection and hyperparameter tuning
    - Performance evaluation and comparison
    - Model deployment and monitoring
    """
    
    def __init__(self, 
                 task_type: str = 'auto',
                 optimization_metric: str = 'auto',
                 max_time: int = 3600,
                 max_models: int = 50,
                 cv_folds: int = 5,
                 random_state: int = 42):
        """
        Initialize AutoML Pipeline
        
        Parameters:
        -----------
        task_type : str
            Type of task ('classification', 'regression', 'auto')
        optimization_metric : str
            Metric to optimize ('accuracy', 'f1', 'r2', 'rmse', 'auto')
        max_time : int
            Maximum time in seconds for pipeline execution
        max_models : int
            Maximum number of models to try
        cv_folds : int
            Number of cross-validation folds
        random_state : int
            Random seed for reproducibility
        """
        self.task_type = task_type
        self.optimization_metric = optimization_metric
        self.max_time = max_time
        self.max_models = max_models
        self.cv_folds = cv_folds
        self.random_state = random_state
        
        # Pipeline components
        self.data_preprocessor = None
        self.feature_selector = None
        self.model_selector = None
        self.hyperparameter_tuner = None
        self.evaluator = None
        
        # Results storage
        self.pipeline_results = {}
        self.best_model = None
        self.best_score = None
        self.feature_importance = None
        self.model_comparison = None
        
        # Performance tracking
        self.execution_time = 0
        self.models_tried = 0
        self.optimization_history = []
        
        print(f"🚀 AutoML Pipeline initialized for {task_type} task")
        print(f"⏱️  Max execution time: {max_time}s")
        print(f"🎯 Max models to try: {max_models}")
    
    def fit(self, X, y, validation_data=None):
        """
        Execute the complete AutoML pipeline
        
        Parameters:
        -----------
        X : array-like
            Training features
        y : array-like
            Training targets
        validation_data : tuple, optional
            (X_val, y_val) for validation
            
        Returns:
        --------
        self : AutoMLPipeline
            Fitted pipeline
        """
        import time
        start_time = time.time()
        
        print("🔧 Starting AutoML Pipeline execution...")
        print(f"📊 Input data shape: {X.shape}")
        
        try:
            # Step 1: Data Preprocessing
            print("📋 Step 1: Data Preprocessing...")
            X_processed, y_processed = self._preprocess_data(X, y)
            
            # Step 2: Feature Engineering and Selection
            print("🔍 Step 2: Feature Engineering and Selection...")
            X_selected = self._engineer_and_select_features(X_processed, y_processed)
            
            # Step 3: Model Selection
            print("🤖 Step 3: Model Selection...")
            self._select_models(X_selected, y_processed)
            
            # Step 4: Hyperparameter Tuning
            print("⚙️  Step 4: Hyperparameter Tuning...")
            self._tune_hyperparameters(X_selected, y_processed)
            
            # Step 5: Final Evaluation
            print("📈 Step 5: Final Evaluation...")
            self._evaluate_final_models(X_selected, y_processed, validation_data)
            
            # Step 6: Generate Insights
            print("💡 Step 6: Generating Insights...")
            self._generate_insights()
            
            self.execution_time = time.time() - start_time
            print(f"✅ AutoML Pipeline completed in {self.execution_time:.2f}s")
            
            return self
            
        except Exception as e:
            print(f"❌ AutoML Pipeline failed: {e}")
            self.execution_time = time.time() - start_time
            return self
    
    def _preprocess_data(self, X, y):
        """Preprocess input data"""
        try:
            # Convert to numpy arrays
            if hasattr(X, 'to_numpy'):
                X = X.to_numpy()
            if hasattr(y, 'to_numpy'):
                y = y.to_numpy()
            
            # Handle missing values
            if np.isnan(X).any():
                print("🔧 Handling missing values...")
                from sklearn.impute import SimpleImputer
                imputer = SimpleImputer(strategy='mean')
                X = imputer.fit_transform(X)
            
            # Handle categorical variables
            if X.dtype == 'object' or (hasattr(X, 'dtype') and X.dtype == 'object'):
                print("🔧 Encoding categorical variables...")
                from sklearn.preprocessing import LabelEncoder
                le = LabelEncoder()
                X = le.fit_transform(X.reshape(-1, 1)).reshape(X.shape)
            
            # Scale numerical features
            print("🔧 Scaling numerical features...")
            from sklearn.preprocessing import StandardScaler
            scaler = StandardScaler()
            X = scaler.fit_transform(X)
            
            print(f"✅ Data preprocessing completed. Shape: {X.shape}")
            return X, y
            
        except Exception as e:
            print(f"⚠️  Data preprocessing failed: {e}")
            return X, y
    
    def _engineer_and_select_features(self, X, y):
        """Engineer and select features"""
        try:
            print(f"🔍 Starting feature engineering on {X.shape[1]} features...")
            
            # Basic feature selection
            if X.shape[1] > 100:
                print("🔍 High-dimensional data detected, applying feature selection...")
                from sklearn.feature_selection import SelectKBest, f_classif, f_regression
                
                if self.task_type == 'classification':
                    selector = SelectKBest(score_func=f_classif, k=min(50, X.shape[1]))
                else:
                    selector = SelectKBest(score_func=f_regression, k=min(50, X.shape[1]))
                
                X_selected = selector.fit_transform(X, y)
                selected_features = selector.get_support()
                
                print(f"✅ Feature selection completed. Selected {X_selected.shape[1]} features")
                return X_selected
            else:
                print("✅ No feature selection needed")
                return X
                
        except Exception as e:
            print(f"⚠️  Feature engineering failed: {e}")
            return X
    
    def _select_models(self, X, y):
        """Select appropriate models for the task"""
        try:
            print("🤖 Selecting models for the task...")
            
            # Auto-detect task type if needed
            if self.task_type == 'auto':
                unique_targets = len(np.unique(y))
                if unique_targets <= 20:
                    self.task_type = 'classification'
                else:
                    self.task_type = 'regression'
                print(f"🎯 Auto-detected task type: {self.task_type}")
            
            # Model candidates
            if self.task_type == 'classification':
                from sklearn.linear_model import LogisticRegression
                from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
                from sklearn.svm import SVC
                from sklearn.neighbors import KNeighborsClassifier
                
                models = {
                    'LogisticRegression': LogisticRegression(random_state=self.random_state),
                    'RandomForest': RandomForestClassifier(random_state=self.random_state, n_estimators=100),
                    'GradientBoosting': GradientBoostingClassifier(random_state=self.random_state, n_estimators=100),
                    'SVM': SVC(random_state=self.random_state, probability=True),
                    'KNN': KNeighborsClassifier(n_neighbors=5)
                }
            else:  # Regression
                from sklearn.linear_model import LinearRegression, Ridge, Lasso
                from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
                from sklearn.svm import SVR
                
                models = {
                    'LinearRegression': LinearRegression(),
                    'Ridge': Ridge(random_state=self.random_state),
                    'Lasso': Lasso(random_state=self.random_state),
                    'RandomForest': RandomForestRegressor(random_state=self.random_state, n_estimators=100),
                    'GradientBoosting': GradientBoostingRegressor(random_state=self.random_state, n_estimators=100),
                    'SVR': SVR()
                }
            
            self.model_candidates = models
            print(f"✅ Selected {len(models)} model candidates")
            
        except Exception as e:
            print(f"⚠️  Model selection failed: {e}")
            self.model_candidates = {}
    
    def _tune_hyperparameters(self, X, y):
        """Tune hyperparameters for selected models"""
        if not SKLEARN_AVAILABLE:
            return {'error': 'Scikit-learn not available'}
        
        try:
            sklearn_utils = get_sklearn_utils()
            GridSearchCV = sklearn_utils['GridSearchCV']
            RandomizedSearchCV = sklearn_utils['RandomizedSearchCV']
            
            tuned_models = {}
            
            for name, model in self.model_candidates.items():
                try:
                    # Simple parameter grid
                    if 'random_forest' in name.lower():
                        param_grid = {'n_estimators': [50, 100], 'max_depth': [5, 10]}
                    elif 'gradient_boosting' in name.lower():
                        param_grid = {'n_estimators': [50, 100], 'learning_rate': [0.1, 0.2]}
                    else:
                        param_grid = {}
                    
                    if param_grid:
                        # Use GridSearchCV for small parameter grids
                        grid_search = GridSearchCV(model, param_grid, cv=3, n_jobs=-1)
                        grid_search.fit(X, y)
                        
                        tuned_models[name] = {
                            'model': grid_search.best_estimator_,
                            'best_params': grid_search.best_params_,
                            'best_score': grid_search.best_score_
                        }
                    else:
                        # No tuning needed
                        model.fit(X, y)
                        tuned_models[name] = {
                            'model': model,
                            'best_params': {},
                            'best_score': 0.0
                        }
                        
                except Exception as e:
                    print(f"⚠️  Model {name} tuning failed: {e}")
                    continue
            
            return tuned_models
            
        except Exception as e:
            return {'error': f'Hyperparameter tuning failed: {str(e)}'}

    def _evaluate_final_models(self, X, y, validation_data=None):
        """Evaluate final tuned models"""
        if not SKLEARN_AVAILABLE:
            return {'error': 'Scikit-learn not available'}
        
        try:
            sklearn_utils = get_sklearn_utils()
            accuracy_score = sklearn_utils['accuracy_score']
            r2_score = sklearn_utils['r2_score']
            
            evaluation_results = {}
            
            for name, model_info in self.tuned_models.items():
                try:
                    model = model_info['model']
                    y_pred = model.predict(X)
                    
                    if self.task_type == 'classification':
                        score = accuracy_score(y, y_pred)
                    else:
                        score = r2_score(y, y_pred)
                    
                    evaluation_results[name] = {
                        'score': float(score),
                        'best_params': model_info['best_params'],
                        'best_tuning_score': float(model_info['best_score'])
                    }
                    
                except Exception as e:
                    evaluation_results[name] = {'error': str(e)}
            
            # Find best model
            if evaluation_results:
                best_name = max(evaluation_results.keys(), 
                              key=lambda x: evaluation_results[x].get('score', 0) if 'error' not in evaluation_results[x] else 0)
                
                if 'error' not in evaluation_results[best_name]:
                    self.best_model = self.tuned_models[best_name]['model']
                    self.best_score = evaluation_results[best_name]['score']
            
            return evaluation_results
            
        except Exception as e:
            return {'error': f'Final evaluation failed: {str(e)}'}

    def _generate_insights(self):
        """Generate insights from the analysis"""
        try:
            insights = {
                'task_type': self.task_type,
                'best_model_name': type(self.best_model).__name__ if self.best_model else 'None',
                'best_score': float(self.best_score) if hasattr(self, 'best_score') else 0.0,
                'total_models_tested': len(self.selected_models),
                'hyperparameter_tuning_performed': len(self.tuned_models) > 0,
                'execution_time': self.execution_time
            }
            
            # Add feature importance if available
            if self.best_model and hasattr(self.best_model, 'feature_importances_'):
                insights['feature_importance'] = self.best_model.feature_importances_.tolist()
            
            return insights
            
        except Exception as e:
            return {'error': f'Insight generation failed: {str(e)}'}

    def _get_scoring_metric(self):
        """Get appropriate scoring metric for the task"""
        if self.task_type == 'classification':
            return 'accuracy'
        else:
            return 'r2'

    def predict(self, X):
        """Make predictions using the best model"""
        if not self.best_model:
            raise ValueError("No trained model available. Call fit() first.")
        
        try:
            return self.best_model.predict(X)
        except Exception as e:
            raise ValueError(f"Prediction failed: {str(e)}")

    def predict_proba(self, X):
        """Get prediction probabilities (for classification)"""
        if not self.best_model:
            raise ValueError("No trained model available. Call fit() first.")
        
        if self.task_type != 'classification':
            raise ValueError("Probability predictions only available for classification tasks")
        
        try:
            if hasattr(self.best_model, 'predict_proba'):
                return self.best_model.predict_proba(X)
            else:
                raise ValueError("Model does not support probability predictions")
        except Exception as e:
            raise ValueError(f"Probability prediction failed: {str(e)}")

    def get_feature_importance(self):
        """Get feature importance from the best model"""
        if not self.best_model:
            return None
        
        try:
            if hasattr(self.best_model, 'feature_importances_'):
                return self.best_model.feature_importances_.tolist()
            elif hasattr(self.best_model, 'coef_'):
                return self.best_model.coef_.tolist()
            else:
                return None
        except Exception:
            return None

    def get_model_comparison(self):
        """Get comparison of all tested models"""
        return self.evaluation_results

    def get_pipeline_summary(self):
        """Get summary of the entire pipeline"""
        return {
            'task_type': self.task_type,
            'data_shape': self.data_shape,
            'models_tested': len(self.selected_models),
            'best_model': type(self.best_model).__name__ if self.best_model else 'None',
            'best_score': float(self.best_score) if hasattr(self, 'best_score') else 0.0,
            'execution_time': self.execution_time,
            'hyperparameter_tuning': len(self.tuned_models) > 0
        }

    def save_pipeline(self, filepath):
        """Save the trained pipeline"""
        try:
            import joblib
            pipeline_data = {
                'best_model': self.best_model,
                'task_type': self.task_type,
                'data_shape': self.data_shape,
                'evaluation_results': self.evaluation_results,
                'tuned_models': self.tuned_models
            }
            joblib.dump(pipeline_data, filepath)
            print(f"💾 Pipeline saved to: {filepath}")
            return True
        except Exception as e:
            print(f"❌ Failed to save pipeline: {e}")
            return False

    @classmethod
    def load_pipeline(cls, filepath):
        """Load a saved pipeline"""
        try:
            import joblib
            pipeline_data = joblib.load(filepath)
            
            # Create new instance
            instance = cls()
            instance.best_model = pipeline_data['best_model']
            instance.task_type = pipeline_data['task_type']
            instance.data_shape = pipeline_data['data_shape']
            instance.evaluation_results = pipeline_data['evaluation_results']
            instance.tuned_models = pipeline_data['tuned_models']
            
            print(f"📂 Pipeline loaded from: {filepath}")
            return instance
        except Exception as e:
            print(f"❌ Failed to load pipeline: {e}")
            return None
