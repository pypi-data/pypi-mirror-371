"""
Machine Learning Quality Predictor for Rust Crates

Uses ML models to predict:
- Code quality scores
- Security risk levels
- Maintenance activity
- Popularity trends
- Dependency health
"""

import json
import logging
import pickle
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, classification_report


@dataclass
class QualityPrediction:
    """Prediction results for crate quality."""

    crate_name: str
    quality_score: float
    security_risk: str
    maintenance_score: float
    popularity_trend: str
    dependency_health: float
    confidence: float
    features_used: List[str]
    model_version: str


class CrateQualityPredictor:
    """ML-based quality predictor for Rust crates."""

    def __init__(self, model_dir: str = "./models"):
        self.model_dir = Path(model_dir)
        self.model_dir.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger(__name__)

        # Models
        self.quality_model: Optional[RandomForestRegressor] = None
        self.security_model: Optional[RandomForestClassifier] = None
        self.maintenance_model: Optional[RandomForestRegressor] = None
        self.popularity_model: Optional[RandomForestClassifier] = None
        self.dependency_model: Optional[RandomForestRegressor] = None

        # Feature processing
        self.text_vectorizer: Optional[TfidfVectorizer] = None
        self.scaler: Optional[StandardScaler] = None

        # Model metadata
        self.model_version = "1.0.0"
        self.feature_names: List[str] = []

        self._load_models()

    def _load_models(self) -> None:
        """Load trained models from disk."""
        try:
            model_files = {
                "quality": "quality_model.pkl",
                "security": "security_model.pkl",
                "maintenance": "maintenance_model.pkl",
                "popularity": "popularity_model.pkl",
                "dependency": "dependency_model.pkl",
                "vectorizer": "text_vectorizer.pkl",
                "scaler": "feature_scaler.pkl",
                "metadata": "model_metadata.json",
            }

            # Load metadata
            metadata_file = self.model_dir / model_files["metadata"]
            if metadata_file.exists():
                with open(metadata_file, "r") as f:
                    metadata = json.load(f)
                    self.model_version = metadata.get("version", "1.0.0")
                    self.feature_names = metadata.get("feature_names", [])

            # Load models
            for model_name, filename in model_files.items():
                if model_name in ["metadata"]:
                    continue

                model_file = self.model_dir / filename
                if model_file.exists():
                    with open(model_file, "rb") as f:
                        model = pickle.load(f)

                    if model_name == "quality":
                        self.quality_model = model
                    elif model_name == "security":
                        self.security_model = model
                    elif model_name == "maintenance":
                        self.maintenance_model = model
                    elif model_name == "popularity":
                        self.popularity_model = model
                    elif model_name == "dependency":
                        self.dependency_model = model
                    elif model_name == "vectorizer":
                        self.text_vectorizer = model
                    elif model_name == "scaler":
                        self.scaler = model

            self.logger.info(
                f"Loaded {len([m for m in [self.quality_model, self.security_model, 
                                                       self.maintenance_model, self.popularity_model, 
                                                       self.dependency_model] if m is not None])} models"
            )

        except Exception as e:
            self.logger.warning(f"Failed to load models: {e}")

    def _extract_features(self, crate_data: Dict[str, Any]) -> np.ndarray:
        """Extract features from crate data."""
        features = []

        # Basic metrics
        features.extend(
            [
                crate_data.get("downloads", 0),
                crate_data.get("github_stars", 0),
                len(crate_data.get("dependencies", [])),
                len(crate_data.get("dev_dependencies", [])),
                len(crate_data.get("features", [])),
                crate_data.get("version_count", 1),
                crate_data.get("days_since_updated", 0),
                crate_data.get("contributor_count", 1),
            ]
        )

        # Text features
        text_features = []
        for text_field in ["description", "readme", "keywords"]:
            text = crate_data.get(text_field, "")
            if isinstance(text, list):
                text = " ".join(text)
            text_features.append(text or "")

        # Vectorize text if vectorizer is available
        if self.text_vectorizer and text_features:
            try:
                text_vectors = self.text_vectorizer.transform(text_features)
                features.extend(text_vectors.toarray().flatten())
            except Exception as e:
                self.logger.warning(f"Text vectorization failed: {e}")
                features.extend([0] * 100)  # Default vector size

        # Analysis results
        analysis = crate_data.get("enhanced_analysis", {})
        if analysis:
            features.extend(
                [
                    analysis.get("insights", {}).get("overall_quality_score", 0.5),
                    analysis.get("insights", {}).get("security_risk_level_score", 0.5),
                    len(analysis.get("clippy", {}).get("warnings", [])),
                    len(analysis.get("clippy", {}).get("errors", [])),
                    analysis.get("geiger", {}).get("safety_score", 1.0),
                    analysis.get("geiger", {}).get("total_unsafe_items", 0),
                ]
            )

        # Convert to numpy array
        feature_array = np.array(features, dtype=np.float32)

        # Scale features if scaler is available
        if self.scaler:
            try:
                feature_array = self.scaler.transform(
                    feature_array.reshape(1, -1)
                ).flatten()
            except Exception as e:
                self.logger.warning(f"Feature scaling failed: {e}")

        return feature_array

    def predict_quality(self, crate_data: Dict[str, Any]) -> QualityPrediction:
        """Predict quality metrics for a crate."""
        try:
            features = self._extract_features(crate_data)

            # Make predictions
            quality_score = 0.5
            if self.quality_model:
                quality_score = float(self.quality_model.predict([features])[0])
                quality_score = max(0.0, min(1.0, quality_score))

            security_risk = "medium"
            if self.security_model:
                risk_pred = self.security_model.predict([features])[0]
                security_risk = ["low", "medium", "high"][risk_pred]

            maintenance_score = 0.5
            if self.maintenance_model:
                maintenance_score = float(self.maintenance_model.predict([features])[0])
                maintenance_score = max(0.0, min(1.0, maintenance_score))

            popularity_trend = "stable"
            if self.popularity_model:
                trend_pred = self.popularity_model.predict([features])[0]
                popularity_trend = ["declining", "stable", "growing"][trend_pred]

            dependency_health = 0.5
            if self.dependency_model:
                dependency_health = float(self.dependency_model.predict([features])[0])
                dependency_health = max(0.0, min(1.0, dependency_health))

            # Calculate confidence based on model availability
            models_available = sum(
                [
                    self.quality_model is not None,
                    self.security_model is not None,
                    self.maintenance_model is not None,
                    self.popularity_model is not None,
                    self.dependency_model is not None,
                ]
            )
            confidence = min(1.0, models_available / 5.0)

            return QualityPrediction(
                crate_name=crate_data.get("name", "unknown"),
                quality_score=quality_score,
                security_risk=security_risk,
                maintenance_score=maintenance_score,
                popularity_trend=popularity_trend,
                dependency_health=dependency_health,
                confidence=confidence,
                features_used=self.feature_names,
                model_version=self.model_version,
            )

        except Exception as e:
            self.logger.error(f"Prediction failed: {e}")
            return QualityPrediction(
                crate_name=crate_data.get("name", "unknown"),
                quality_score=0.5,
                security_risk="unknown",
                maintenance_score=0.5,
                popularity_trend="unknown",
                dependency_health=0.5,
                confidence=0.0,
                features_used=[],
                model_version=self.model_version,
            )

    def train_models(self, training_data: List[Dict[str, Any]]) -> None:
        """Train models on historical crate data."""
        if not training_data:
            self.logger.warning("No training data provided")
            return

        try:
            # Prepare training data
            X = []
            y_quality = []
            y_security = []
            y_maintenance = []
            y_popularity = []
            y_dependency = []

            for crate in training_data:
                features = self._extract_features(crate)
                X.append(features)

                # Extract labels
                y_quality.append(crate.get("quality_score", 0.5))
                y_security.append(
                    crate.get("security_risk_level", 1)
                )  # 0=low, 1=medium, 2=high
                y_maintenance.append(crate.get("maintenance_score", 0.5))
                y_popularity.append(
                    crate.get("popularity_trend", 1)
                )  # 0=declining, 1=stable, 2=growing
                y_dependency.append(crate.get("dependency_health", 0.5))

            X = np.array(X)
            y_quality = np.array(y_quality)
            y_security = np.array(y_security)
            y_maintenance = np.array(y_maintenance)
            y_popularity = np.array(y_popularity)
            y_dependency = np.array(y_dependency)

            # Split data
            X_train, X_test, y_quality_train, y_quality_test = train_test_split(
                X, y_quality, test_size=0.2, random_state=42
            )

            # Train quality model
            self.quality_model = RandomForestRegressor(
                n_estimators=100, random_state=42
            )
            self.quality_model.fit(X_train, y_quality_train)

            # Train security model
            self.security_model = RandomForestClassifier(
                n_estimators=100, random_state=42
            )
            self.security_model.fit(X_train, y_security)

            # Train maintenance model
            self.maintenance_model = RandomForestRegressor(
                n_estimators=100, random_state=42
            )
            self.maintenance_model.fit(X_train, y_maintenance)

            # Train popularity model
            self.popularity_model = RandomForestClassifier(
                n_estimators=100, random_state=42
            )
            self.popularity_model.fit(X_train, y_popularity)

            # Train dependency model
            self.dependency_model = RandomForestRegressor(
                n_estimators=100, random_state=42
            )
            self.dependency_model.fit(X_train, y_dependency)

            # Save models
            self._save_models()

            # Evaluate models
            self._evaluate_models(
                X_test,
                y_quality_test,
                y_security,
                y_maintenance,
                y_popularity,
                y_dependency,
            )

        except Exception as e:
            self.logger.error(f"Model training failed: {e}")

    def _save_models(self) -> None:
        """Save trained models to disk."""
        try:
            models = {
                "quality_model.pkl": self.quality_model,
                "security_model.pkl": self.security_model,
                "maintenance_model.pkl": self.maintenance_model,
                "popularity_model.pkl": self.popularity_model,
                "dependency_model.pkl": self.dependency_model,
                "text_vectorizer.pkl": self.text_vectorizer,
                "feature_scaler.pkl": self.scaler,
            }

            for filename, model in models.items():
                if model is not None:
                    model_file = self.model_dir / filename
                    with open(model_file, "wb") as f:
                        pickle.dump(model, f)

            # Save metadata
            metadata = {
                "version": self.model_version,
                "feature_names": self.feature_names,
                "model_count": len([m for m in models.values() if m is not None]),
            }

            metadata_file = self.model_dir / "model_metadata.json"
            with open(metadata_file, "w") as f:
                json.dump(metadata, f, indent=2)

            self.logger.info("Models saved successfully")

        except Exception as e:
            self.logger.error(f"Failed to save models: {e}")

    def _evaluate_models(
        self,
        X_test: np.ndarray,
        y_quality_test: np.ndarray,
        y_security: np.ndarray,
        y_maintenance: np.ndarray,
        y_popularity: np.ndarray,
        y_dependency: np.ndarray,
    ) -> None:
        """Evaluate model performance."""
        try:
            if self.quality_model is not None:
                y_pred = self.quality_model.predict(X_test)
                mse = mean_squared_error(y_quality_test, y_pred)
                self.logger.info(f"Quality model MSE: {mse:.4f}")

            if self.security_model is not None:
                y_pred = self.security_model.predict(X_test)
                report = classification_report(
                    y_security, y_pred, target_names=["low", "medium", "high"]
                )
                self.logger.info(f"Security model report:\n{report}")

        except Exception as e:
            self.logger.warning(f"Model evaluation failed: {e}")


# Global predictor instance
_global_predictor: Optional[CrateQualityPredictor] = None


def get_predictor() -> CrateQualityPredictor:
    """Get global predictor instance."""
    global _global_predictor
    if _global_predictor is None:
        _global_predictor = CrateQualityPredictor()
    return _global_predictor


def set_predictor(predictor: CrateQualityPredictor) -> None:
    """Set global predictor instance."""
    global _global_predictor
    _global_predictor = predictor
