"""
Machine Learning Integration Module for hpfracc

This module provides comprehensive ML integration for fractional calculus,
including neural networks, attention mechanisms, loss functions, optimizers,
and a complete development-to-production workflow.

Features:
- Fractional Neural Networks with various architectures
- Fractional Attention Mechanisms
- Fractional Loss Functions
- Fractional Optimizers
- Model Registry and Versioning
- Development vs. Production Workflow
- Quality Gates and Validation
- Model Monitoring and Rollback
- Fractional Neural Network Layers
- PyTorch Autograd Integration for Fractional Derivatives
"""

from .core import (
    FractionalNeuralNetwork,
    FractionalAttention,
    FractionalLossFunction,
    FractionalAutoML,
    MLConfig,
)

from .registry import (
    ModelRegistry,
    ModelVersion,
    ModelMetadata,
    DeploymentStatus,
)

from .workflow import (
    DevelopmentWorkflow,
    ProductionWorkflow,
    ModelValidator,
    QualityGate,
    QualityMetric,
    QualityThreshold,
)

from .layers import (
    FractionalConv1D,
    FractionalConv2D,
    FractionalLSTM,
    FractionalTransformer,
    FractionalPooling,
    FractionalBatchNorm1d,
    LayerConfig,
)

from .losses import (
    FractionalMSELoss,
    FractionalCrossEntropyLoss,
    FractionalHuberLoss,
    FractionalSmoothL1Loss,
    FractionalKLDivLoss,
    FractionalBCELoss,
    FractionalNLLLoss,
    FractionalPoissonNLLLoss,
    FractionalCosineEmbeddingLoss,
    FractionalMarginRankingLoss,
    FractionalMultiMarginLoss,
    FractionalTripletMarginLoss,
    FractionalCTCLoss,
    FractionalCustomLoss,
    FractionalCombinedLoss,
)

from .optimizers import (
    FractionalAdam,
    FractionalSGD,
    FractionalRMSprop,
    FractionalAdagrad,
    FractionalAdamW,
)

from .fractional_autograd import (
    FractionalDerivativeFunction,
    FractionalDerivativeLayer,
    fractional_derivative,
    rl_derivative,
    caputo_derivative,
    gl_derivative,
)

__all__ = [
    # Core ML components
    "FractionalNeuralNetwork",
    "FractionalAttention", 
    "FractionalLossFunction",
    "FractionalAutoML",
    "MLConfig",
    
    # Model management
    "ModelRegistry",
    "ModelVersion",
    "ModelMetadata",
    "DeploymentStatus",
    
    # Workflow management
    "DevelopmentWorkflow",
    "ProductionWorkflow",
    "ModelValidator",
    "QualityGate",
    "QualityMetric",
    "QualityThreshold",
    
    # Neural network layers
    "FractionalConv1D",
    "FractionalConv2D",
    "FractionalLSTM",
    "FractionalTransformer",
    "FractionalPooling",
    "FractionalBatchNorm1d",
    "LayerConfig",
    
    # Loss functions
    "FractionalMSELoss",
    "FractionalCrossEntropyLoss",
    "FractionalHuberLoss",
    "FractionalSmoothL1Loss",
    "FractionalKLDivLoss",
    "FractionalBCELoss",
    "FractionalNLLLoss",
    "FractionalPoissonNLLLoss",
    "FractionalCosineEmbeddingLoss",
    "FractionalMarginRankingLoss",
    "FractionalMultiMarginLoss",
    "FractionalTripletMarginLoss",
    "FractionalCTCLoss",
    "FractionalCustomLoss",
    "FractionalCombinedLoss",
    
    # Optimizers
    "FractionalAdam",
    "FractionalSGD",
    "FractionalRMSprop",
    "FractionalAdagrad",
    "FractionalAdamW",
    
    # Autograd integration
    "FractionalDerivativeFunction",
    "FractionalDerivativeLayer",
    "fractional_derivative",
    "rl_derivative",
    "caputo_derivative",
    "gl_derivative",
]

__version__ = "0.1.0"
__author__ = "Davian R. Chin"
__email__ = "d.r.chin@pgr.reading.ac.uk"
__institution__ = "Department of Biomedical Engineering, University of Reading"
