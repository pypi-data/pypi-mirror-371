from typing import Any, Dict, List, Type, TypeVar, Union

import attr

from ..models.calculation_composition import CalculationComposition
from ..types import UNSET, Unset

T = TypeVar("T", bound="BatchFlashFixedTemperaturePressureCalculationItem")

@attr.s(auto_attribs=True)
class BatchFlashFixedTemperaturePressureCalculationItem:
    """Item for batch flash calculation.

    Attributes
    ----------
    temperature : float
        Temperature in units given in `BatchFlashFixedTemperaturePressureCalculationInput.units` attribute.
    pressure : float
        Pressure in units given in `BatchFlashFixedTemperaturePressureCalculationInput.units` attribute.
    """
    temperature: Union[Unset, float] = UNSET #Temperature in units given in 'Units' argument
    pressure: Union[Unset, float] = UNSET #Pressure in units given in 'Units' argument

    def to_dict(self) -> Dict[str, Any]:
        """Dump `BatchFlashFixedTemperaturePressureCalculationItem` instance to a dict."""

        temperature = self.temperature
        pressure = self.pressure

        field_dict: Dict[str, Any] = {}
        if temperature is not UNSET:
            field_dict["temperature"] = temperature
        if pressure is not UNSET:
            field_dict["pressure"] = pressure

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Load `BatchFlashFixedTemperaturePressureCalculationItem` instance from a dict."""
        d = src_dict.copy()

        temperature = d.pop("temperature", UNSET)
        pressure = d.pop("pressure", UNSET)

        flash_calculation_input = cls(
            temperature=temperature,
            pressure=pressure,
        )

        return flash_calculation_input
