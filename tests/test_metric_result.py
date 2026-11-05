"""
Tests for MetricResult class.
"""

import numpy as np
import pytest
from hydrometrics.core.result import MetricResult


class TestMetricResultScalar:
    """Tests for scalar MetricResult values."""

    def test_scalar_value_str(self):
        result = MetricResult(
            value=0.75,
            name="Test Metric",
            direction="maximize",
            bounds=(0.0, 1.0),
            parameters={"axis": None},
            reference="Test Reference",
            nan_info={"policy": "omit", "n_nan_removed": 0, "n_total": 10},
        )
        s = str(result)
        assert "Test Metric" in s
        assert "0.75" in s
        assert "maximize" in s

    def test_scalar_value_repr(self):
        result = MetricResult(
            value=0.75,
            name="Test Metric",
            direction="maximize",
            bounds=(0.0, 1.0),
            parameters={"axis": None},
            reference="Test Reference",
            nan_info={"policy": "omit", "n_nan_removed": 0, "n_total": 10},
        )
        r = repr(result)
        assert "MetricResult" in r
        assert "name='Test Metric'" in r
        assert "value=0.75" in r
        assert "direction='maximize'" in r

    def test_scalar_value_to_dict(self):
        result = MetricResult(
            value=0.75,
            name="Test Metric",
            direction="maximize",
            bounds=(0.0, 1.0),
            parameters={"axis": None},
            reference="Test Reference",
            nan_info={"policy": "omit", "n_nan_removed": 0, "n_total": 10},
        )
        d = result.to_dict()
        assert d["value"] == 0.75
        assert d["name"] == "Test Metric"
        assert d["direction"] == "maximize"
        assert d["bounds"] == (0.0, 1.0)

    def test_scalar_float_conversion(self):
        result = MetricResult(
            value=0.75,
            name="Test Metric",
            direction="maximize",
            bounds=(0.0, 1.0),
            parameters={},
            reference="Test Reference",
            nan_info={"policy": "omit", "n_nan_removed": 0, "n_total": 10},
        )
        assert float(result) == 0.75

    def test_scalar_numpy_float_conversion(self):
        result = MetricResult(
            value=np.float64(0.75),
            name="Test Metric",
            direction="maximize",
            bounds=(0.0, 1.0),
            parameters={},
            reference="Test Reference",
            nan_info={"policy": "omit", "n_nan_removed": 0, "n_total": 10},
        )
        assert float(result) == 0.75

    def test_scalar_0d_array_float_conversion(self):
        result = MetricResult(
            value=np.array(0.75),
            name="Test Metric",
            direction="maximize",
            bounds=(0.0, 1.0),
            parameters={},
            reference="Test Reference",
            nan_info={"policy": "omit", "n_nan_removed": 0, "n_total": 10},
        )
        assert float(result) == 0.75

    def test_is_scalar_true(self):
        result = MetricResult(
            value=0.75,
            name="Test Metric",
            direction="maximize",
            bounds=(0.0, 1.0),
            parameters={},
            reference="Test Reference",
            nan_info={"policy": "omit", "n_nan_removed": 0, "n_total": 10},
        )
        assert result.is_scalar is True

    def test_scalar_value_property(self):
        result = MetricResult(
            value=0.75,
            name="Test Metric",
            direction="maximize",
            bounds=(0.0, 1.0),
            parameters={},
            reference="Test Reference",
            nan_info={"policy": "omit", "n_nan_removed": 0, "n_total": 10},
        )
        assert result.scalar_value == 0.75
class TestMetricResultArray:
    """Tests for array MetricResult values."""

    def test_array_value_str(self):
        result = MetricResult(
            value=np.array([0.1, 0.2, 0.3]),
            name="Test Metric",
            direction="maximize",
            bounds=(0.0, 1.0),
            parameters={"axis": 0},
            reference="Test Reference",
            nan_info={"policy": "omit", "n_nan_removed": 0, "n_total": 10},
        )
        s = str(result)
        assert "Test Metric" in s
        assert "array(3,)" in s

    def test_array_value_repr(self):
        result = MetricResult(
            value=np.array([0.1, 0.2, 0.3]),
            name="Test Metric",
            direction="maximize",
            bounds=(0.0, 1.0),
            parameters={"axis": 0},
            reference="Test Reference",
            nan_info={"policy": "omit", "n_nan_removed": 0, "n_total": 10},
        )
        r = repr(result)
        assert "MetricResult" in r
        assert "array(3,)" in r

    def test_array_value_to_dict(self):
        result = MetricResult(
            value=np.array([0.1, 0.2, 0.3]),
            name="Test Metric",
            direction="maximize",
            bounds=(0.0, 1.0),
            parameters={"axis": 0},
            reference="Test Reference",
            nan_info={"policy": "omit", "n_nan_removed": 0, "n_total": 10},
        )
        d = result.to_dict()
        assert "value" in d
        assert list(d["value"]) == [0.1, 0.2, 0.3]

    def test_array_float_conversion_raises(self):
        result = MetricResult(
            value=np.array([0.1, 0.2, 0.3]),
            name="Test Metric",
            direction="maximize",
            bounds=(0.0, 1.0),
            parameters={"axis": 0},
            reference="Test Reference",
            nan_info={"policy": "omit", "n_nan_removed": 0, "n_total": 10},
        )
        with pytest.raises(TypeError, match="Cannot convert non-scalar"):
            float(result)

    def test_is_scalar_false(self):
        result = MetricResult(
            value=np.array([0.1, 0.2, 0.3]),
            name="Test Metric",
            direction="maximize",
            bounds=(0.0, 1.0),
            parameters={"axis": 0},
            reference="Test Reference",
            nan_info={"policy": "omit", "n_nan_removed": 0, "n_total": 10},
        )
        assert result.is_scalar is False

    def test_scalar_value_property_raises(self):
        result = MetricResult(
            value=np.array([0.1, 0.2, 0.3]),
            name="Test Metric",
            direction="maximize",
            bounds=(0.0, 1.0),
            parameters={"axis": 0},
            reference="Test Reference",
            nan_info={"policy": "omit", "n_nan_removed": 0, "n_total": 10},
        )
        with pytest.raises(ValueError, match="Result is not a scalar"):
            _ = result.scalar_value

    def test_2d_array(self):
        result = MetricResult(
            value=np.array([[0.1, 0.2], [0.3, 0.4]]),
            name="Test Metric",
            direction="maximize",
            bounds=(0.0, 1.0),
            parameters={"axis": 0},
            reference="Test Reference",
            nan_info={"policy": "omit", "n_nan_removed": 0, "n_total": 10},
        )
        assert result.is_scalar is False
        d = result.to_dict()
        assert d["value"] == [[0.1, 0.2], [0.3, 0.4]]
class TestMetricResultDict:
    """Tests for dictionary MetricResult values (e.g., kge_components)."""

    def test_dict_value_str(self):
        result = MetricResult(
            value={"r": 0.9, "alpha": 1.0, "beta": 0.95, "gamma": 1.02},
            name="KGE Components",
            direction="maximize",
            bounds=(-1.0, 1.0),
            parameters={"axis": None, "version": "2012"},
            reference="Gupta et al. (2009)",
            nan_info={"policy": "omit", "n_nan_removed": 0, "n_total": 10},
        )
        s = str(result)
        assert "KGE Components" in s
        assert "r: 0.9" in s
        assert "alpha: 1" in s  # 1.0 renders as 1 in str()

    def test_dict_value_repr(self):
        result = MetricResult(
            value={"r": 0.9, "alpha": 1.0, "beta": 0.95, "gamma": 1.02},
            name="KGE Components",
            direction="maximize",
            bounds=(-1.0, 1.0),
            parameters={"axis": None, "version": "2012"},
            reference="Gupta et al. (2009)",
            nan_info={"policy": "omit", "n_nan_removed": 0, "n_total": 10},
        )
        r = repr(result)
        assert "MetricResult" in r
        assert "dict{" in r
        assert "r: float" in r

    def test_dict_value_to_dict(self):
        result = MetricResult(
            value={"r": 0.9, "alpha": 1.0, "beta": 0.95, "gamma": 1.02},
            name="KGE Components",
            direction="maximize",
            bounds=(-1.0, 1.0),
            parameters={"axis": None, "version": "2012"},
            reference="Gupta et al. (2009)",
            nan_info={"policy": "omit", "n_nan_removed": 0, "n_total": 10},
        )
        d = result.to_dict()
        assert d["value"]["r"] == 0.9
        assert d["value"]["alpha"] == 1.0
        assert d["value"]["beta"] == 0.95
        assert d["value"]["gamma"] == 1.02

    def test_dict_with_array_values_str(self):
        result = MetricResult(
            value={"r": np.array([0.9, 0.8]), "alpha": np.array([1.0, 1.1])},
            name="KGE Components",
            direction="maximize",
            bounds=(-1.0, 1.0),
            parameters={"axis": 0, "version": "2012"},
            reference="Gupta et al. (2009)",
            nan_info={"policy": "omit", "n_nan_removed": 0, "n_total": 10},
        )
        s = str(result)
        assert "array(2,)" in s

    def test_dict_with_array_values_to_dict(self):
        result = MetricResult(
            value={"r": np.array([0.9, 0.8]), "alpha": np.array([1.0, 1.1])},
            name="KGE Components",
            direction="maximize",
            bounds=(-1.0, 1.0),
            parameters={"axis": 0, "version": "2012"},
            reference="Gupta et al. (2009)",
            nan_info={"policy": "omit", "n_nan_removed": 0, "n_total": 10},
        )
        d = result.to_dict()
        assert list(d["value"]["r"]) == [0.9, 0.8]
        assert list(d["value"]["alpha"]) == [1.0, 1.1]
class TestMetricResultNonFinite:
    """Tests for non-finite values in MetricResult."""

    def test_nan_value_str(self):
        result = MetricResult(
            value=np.nan,
            name="Test Metric",
            direction="maximize",
            bounds=(0.0, 1.0),
            parameters={},
            reference="Test Reference",
            nan_info={"policy": "omit", "n_nan_removed": 1, "n_total": 10},
        )
        s = str(result)
        assert "nan" in s.lower()

    def test_inf_value_str(self):
        result = MetricResult(
            value=np.inf,
            name="Test Metric",
            direction="maximize",
            bounds=(0.0, 1.0),
            parameters={},
            reference="Test Reference",
            nan_info={"policy": "omit", "n_nan_removed": 0, "n_total": 10},
        )
        s = str(result)
        assert "inf" in s.lower()

    def test_neg_inf_value_str(self):
        result = MetricResult(
            value=-np.inf,
            name="Test Metric",
            direction="maximize",
            bounds=(0.0, 1.0),
            parameters={},
            reference="Test Reference",
            nan_info={"policy": "omit", "n_nan_removed": 0, "n_total": 10},
        )
        s = str(result)
        assert "inf" in s.lower()

    def test_nan_in_array_str(self):
        result = MetricResult(
            value=np.array([0.1, np.nan, 0.3]),
            name="Test Metric",
            direction="maximize",
            bounds=(0.0, 1.0),
            parameters={},
            reference="Test Reference",
            nan_info={"policy": "omit", "n_nan_removed": 1, "n_total": 10},
        )
        s = str(result)
        # Array str representation shows shape, not individual values
        assert "array(3,)" in s

    def test_nan_in_dict_str(self):
        result = MetricResult(
            value={"r": 0.9, "alpha": np.nan},
            name="KGE Components",
            direction="maximize",
            bounds=(-1.0, 1.0),
            parameters={},
            reference="Gupta et al. (2009)",
            nan_info={"policy": "omit", "n_nan_removed": 1, "n_total": 10},
        )
        s = str(result)
        assert "nan" in s.lower()


class TestMetricResultValidation:
    """Tests for MetricResult validation."""

    def test_invalid_direction_raises(self):
        with pytest.raises(ValueError, match="direction must be"):
            MetricResult(
                value=0.5,
                name="Test",
                direction="invalid",
                bounds=(0.0, 1.0),
                parameters={},
                reference="Test",
                nan_info={},
            )

    def test_invalid_bounds_raises(self):
        with pytest.raises(ValueError, match="bounds must be a tuple of length 2"):
            MetricResult(
                value=0.5,
                name="Test",
                direction="maximize",
                bounds=(0.0,),
                parameters={},
                reference="Test",
                nan_info={},
            )