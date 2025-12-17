"""
Preprocessing Technique Registry

This package contains the technique registry for algorithm-aware preprocessing.
Each module exports a TECHNIQUES dictionary mapping technique names to functions.

Modules:
- clean_data: Outlier handling techniques (8 techniques)
- handle_missing: Missing value imputation techniques (7 techniques)
- encode_features: Categorical encoding techniques (7 techniques)
- scale_features: Feature scaling techniques (7 techniques)

Total: 28 preprocessing techniques
"""

__all__ = ["clean_data", "handle_missing", "encode_features", "scale_features"]
