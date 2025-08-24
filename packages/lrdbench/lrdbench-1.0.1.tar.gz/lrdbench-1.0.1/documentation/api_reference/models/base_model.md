# BaseModel

## Class Definition

```python
class BaseModel(ABC):
    """Abstract base class for all stochastic models."""
```

## Constructor

```python
def __init__(self, **kwargs):
    """
    Initialize the base model.
    
    Parameters
    ----------
    **kwargs : dict
        Model-specific parameters
        
    Raises
    ------
    ValueError
        If parameters are invalid
    """
```

## Abstract Methods

### generate

```python
@abstractmethod
def generate(self, n: int, seed: Optional[int] = None) -> np.ndarray:
    """
    Generate synthetic time series data.
    
    Parameters
    ----------
    n : int
        Number of samples to generate
    seed : int, optional
        Random seed for reproducibility
        
    Returns
    -------
    np.ndarray
        Generated time series of shape (n,)
        
    Raises
    ------
    ValueError
        If n is not positive
    """
```

### get_parameters

```python
@abstractmethod
def get_parameters(self) -> Dict[str, Any]:
    """
    Get model parameters.
    
    Returns
    -------
    Dict[str, Any]
        Dictionary containing model parameters
    """
```

### get_theoretical_properties

```python
@abstractmethod
def get_theoretical_properties(self) -> Dict[str, Any]:
    """
    Get theoretical properties of the model.
    
    Returns
    -------
    Dict[str, Any]
        Dictionary containing theoretical properties
    """
```

## Concrete Methods

### set_parameters

```python
def set_parameters(self, **kwargs) -> None:
    """
    Set model parameters.
    
    Parameters
    ----------
    **kwargs : dict
        Parameters to set
        
    Raises
    ------
    ValueError
        If parameters are invalid
    """
```

### validate_parameters

```python
def validate_parameters(self) -> None:
    """
    Validate model parameters.
    
    Raises
    ------
    ValueError
        If parameters are invalid
    """
```

### get_model_info

```python
def get_model_info(self) -> Dict[str, Any]:
    """
    Get comprehensive model information.
    
    Returns
    -------
    Dict[str, Any]
        Dictionary containing model information including:
        - model_name: str
        - parameters: Dict[str, Any]
        - theoretical_properties: Dict[str, Any]
        - description: str
    """
```

### __str__

```python
def __str__(self) -> str:
    """
    String representation of the model.
    
    Returns
    -------
    str
        String representation
    """
```

### __repr__

```python
def __repr__(self) -> str:
    """
    Detailed string representation of the model.
    
    Returns
    -------
    str
        Detailed string representation
    """
```

## Properties

### model_name

```python
@property
def model_name(self) -> str:
    """
    Get the model name.
    
    Returns
    -------
    str
        Model name
    """
```

### description

```python
@property
def description(self) -> str:
    """
    Get model description.
    
    Returns
    -------
    str
        Model description
    """
```

## Usage Example

```python
from models.data_models.base_model import BaseModel
import numpy as np
from typing import Dict, Any, Optional

class MyModel(BaseModel):
    def __init__(self, param1: float, param2: float):
        self.param1 = param1
        self.param2 = param2
        self.validate_parameters()
    
    def generate(self, n: int, seed: Optional[int] = None) -> np.ndarray:
        if seed is not None:
            np.random.seed(seed)
        return np.random.randn(n)
    
    def get_parameters(self) -> Dict[str, Any]:
        return {'param1': self.param1, 'param2': self.param2}
    
    def get_theoretical_properties(self) -> Dict[str, Any]:
        return {'mean': 0.0, 'variance': 1.0}
    
    def validate_parameters(self) -> None:
        if self.param1 <= 0:
            raise ValueError("param1 must be positive")
        if self.param2 <= 0:
            raise ValueError("param2 must be positive")

# Usage
model = MyModel(param1=1.0, param2=2.0)
data = model.generate(1000, seed=42)
params = model.get_parameters()
properties = model.get_theoretical_properties()
info = model.get_model_info()
```

## Error Handling

The BaseModel class includes comprehensive error handling:

- **Parameter Validation**: All parameters are validated during initialization
- **Type Checking**: Parameters are checked for correct types
- **Range Validation**: Parameters are checked for valid ranges
- **Informative Errors**: Clear error messages for debugging

## Design Principles

1. **Consistency**: All models follow the same interface
2. **Validation**: Comprehensive parameter validation
3. **Reproducibility**: Seed-based random number generation
4. **Documentation**: Complete docstrings and type hints
5. **Extensibility**: Easy to extend with new models
