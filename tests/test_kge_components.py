"""
Tests for KGE components function.
"""

import numpy as np
import pytest
from hydrometrics import kge_components


class TestKGEComponents:
    """Tests for kge_components function."""

    def test_version_2012_scalar(self):
        """Test KGE 2012 version with scalar input (axis=None)."""
        obs = np.array([1, 2, 3, 4, 5, 6])
        sim = np.array([1.1, 2.1, 3.1, 4.1, 5.1, 6.1])
        
        result = kge_components(obs, sim, axis=None, version="2012")
        
        # Should return a MetricResult with dict value
        assert hasattr(result, 'value')
        assert isinstance(result.value, dict)
        
        # Check keys
        assert set(result.value.keys()) == {"r", "alpha", "beta", "gamma"}
        
        # All values should be scalars
        for k, v in result.value.items():
            assert np.isscalar(v), f"{k} should be scalar, got {type(v)}"

    def test_version_2009_scalar(self):
        """Test KGE 2009 version with scalar input (axis=None)."""
        obs = np.array([1, 2, 3, 4, 5, 6])
        sim = np.array([1.1, 2.1, 3.1, 4.1, 5.1, 6.1])
        
        result = kge_components(obs, sim, axis=None, version="2009")
        
        assert hasattr(result, 'value')
        assert isinstance(result.value, dict)
        
        # 2009 version should not have gamma
        assert set(result.value.keys()) == {"r", "alpha", "beta"}

    def test_axis_0_returns_arrays(self):
        """Test axis=0 with reduction='none' returns arrays for each component."""
        obs = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]], dtype=float)
        sim = np.array([[1.1, 2.1, 3.1], [4.1, 5.1, 6.1], [7.1, 8.1, 9.1]], dtype=float)

        # With an axis and no explicit reduction, returns arrays (D10)
        result = kge_components(obs, sim, axis=0, version="2012")
        for k, v in result.value.items():
            assert np.shape(v) == (3,), f"{k} should be an array with default reduction, got {type(v)}"

        # An explicit reduction="mean" returns scalars
        result = kge_components(obs, sim, axis=0, reduction="mean", version="2012")
        for k, v in result.value.items():
            assert np.isscalar(v), f"{k} should be scalar with reduction='mean', got {type(v)}"

        # With reduction="none", returns arrays
        result = kge_components(obs, sim, axis=0, reduction="none", version="2012")
        assert hasattr(result, 'value')
        assert isinstance(result.value, dict)

        # Check keys
        assert set(result.value.keys()) == {"r", "alpha", "beta", "gamma"}

        # All values should be arrays of shape (3,)
        for k, v in result.value.items():
            assert isinstance(v, np.ndarray), f"{k} should be array, got {type(v)}"
            assert v.shape == (3,), f"{k} should have shape (3,), got {v.shape}"

    def test_axis_1_returns_arrays(self):
        """Test axis=1 with reduction='none' returns arrays for each component."""
        obs = np.array([[1, 2, 3], [4, 5, 6]], dtype=float)
        sim = np.array([[1.1, 2.1, 3.1], [4.1, 5.1, 6.1]], dtype=float)

        # With an axis and no explicit reduction, returns arrays (D10)
        result = kge_components(obs, sim, axis=1, version="2012")
        for k, v in result.value.items():
            assert np.shape(v) == (2,), f"{k} should be an array with default reduction, got {type(v)}"

        # With reduction="none", returns arrays
        result = kge_components(obs, sim, axis=1, reduction="none", version="2012")
        assert hasattr(result, 'value')
        assert isinstance(result.value, dict)

        # Check keys
        assert set(result.value.keys()) == {"r", "alpha", "beta", "gamma"}

        # All values should be arrays of shape (2,)
        for k, v in result.value.items():
            assert isinstance(v, np.ndarray), f"{k} should be array, got {type(v)}"
            assert v.shape == (2,), f"{k} should have shape (2,), got {v.shape}"

    def test_reduction_mean(self):
        """Test reduction='mean' reduces array to scalar."""
        obs = np.array([[1, 2, 3], [4, 5, 6]], dtype=float)
        sim = np.array([[1.1, 2.1, 3.1], [4.1, 5.1, 6.1]], dtype=float)
        
        result = kge_components(obs, sim, axis=0, reduction="mean", version="2012")
        
        assert hasattr(result, 'value')
        assert isinstance(result.value, dict)
        
        # With reduction="mean", should return scalars
        for k, v in result.value.items():
            assert np.isscalar(v), f"{k} should be scalar with reduction='mean', got {type(v)}"

    def test_reduction_none(self):
        """Test reduction='none' keeps arrays."""
        obs = np.array([[1, 2, 3], [4, 5, 6]], dtype=float)
        sim = np.array([[1.1, 2.1, 3.1], [4.1, 5.1, 6.1]], dtype=float)
        
        result = kge_components(obs, sim, axis=0, reduction="none", version="2012")
        
        assert hasattr(result, 'value')
        assert isinstance(result.value, dict)
        
        # With reduction="none", should return arrays
        for k, v in result.value.items():
            assert isinstance(v, np.ndarray), f"{k} should be array with reduction='none', got {type(v)}"

    def test_component_values_are_reasonable(self):
        """Test that component values are in expected ranges."""
        obs = np.array([1, 2, 3, 4, 5, 6])
        sim = np.array([1, 2, 3, 4, 5, 6])  # Perfect match
        
        result = kge_components(obs, sim, axis=None, version="2012")
        
        # Perfect match should give r=1, alpha=1, beta=1, gamma=1
        assert np.isclose(result.value["r"], 1.0, atol=1e-6)
        assert np.isclose(result.value["alpha"], 1.0, atol=1e-6)
        assert np.isclose(result.value["beta"], 1.0, atol=1e-6)
        assert np.isclose(result.value["gamma"], 1.0, atol=1e-6)

    def test_invalid_version_raises(self):
        """Test that an invalid version raises ValueError (the RuntimeError wrapper is gone, D9)."""
        obs = np.array([1, 2, 3])
        sim = np.array([1, 2, 3])
        
        with pytest.raises(ValueError, match="version must be '2009' or '2012'"):
            kge_components(obs, sim, axis=None, version="invalid")

class TestKGEComponentsPublicAPI:
    """Tests for public API imports and dispatch."""

    def test_kge_components_import(self):
        """Test that kge_components is importable from hydrometrics."""
        from hydrometrics import kge_components
        assert callable(kge_components)

    def test_kge_components_in_all(self):
        """Test that kge_components is in __all__."""
        import hydrometrics
        assert "kge_components" in hydrometrics.__all__

    def test_regNSE_import(self):
        """Test that regNSE is importable."""
        from hydrometrics import regNSE
        assert callable(regNSE)

    def test_unique_all_entries(self):
        """Test that __all__ has unique entries."""
        import hydrometrics
        assert len(hydrometrics.__all__) == len(set(hydrometrics.__all__))