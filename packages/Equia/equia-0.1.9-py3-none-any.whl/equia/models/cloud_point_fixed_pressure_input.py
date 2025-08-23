from typing import Any, Dict, List, Type, TypeVar, Union

import attr

from ..models.calculation_composition import CalculationComposition
from ..models.api_fluid import ApiFluid
from ..types import UNSET, Unset
from ..str_util import default_input_str

T = TypeVar("T", bound="CloudPointFixedPressureCalculationInput")


@attr.s(auto_attribs=True)
class CloudPointFixedPressureCalculationInput:
    """Input to cloud point calculation.
    
    Attributes
    ----------
    access_key : str
        Access key for the API. This is used to authenticate the user.
    components : List[CalculationComposition]
        List of components in the mixture.
    units : str
        Units for the calculation.
    fluidid : str
        Id of fluid on webserver. Must be defined if no fluid given in `fluid` argument
    fluid : ApiFluid
        Fluid information
    pressure : float
        Pressure in units given in `units` argument.
    """
    access_key: str
    components: List[CalculationComposition]
    units: str
    fluidid: Union[Unset, str] = UNSET
    fluid: Union[Unset, ApiFluid] = UNSET
    pressure: Union[Unset, float] = UNSET
    __str__ = default_input_str
    
    def to_dict(self) -> Dict[str, Any]:
        """Dump `CloudPointFixedPressureCalculationInput` instance to a dict."""
        access_key = self.access_key
        components = []
        for components_item_data in self.components:
            components_item = components_item_data.to_dict()

            components.append(components_item)

        pressure = self.pressure
        units = self.units

        fluidid: Union[Unset, str] = UNSET
        if not isinstance(self.fluidid, Unset):
            fluid = self.fluidid

        fluid: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.fluid, Unset):
            fluid = self.fluid.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "accessKey": access_key,
                "components": components,
            }
        )
        if units is not UNSET:
            field_dict["units"] = units
        if fluidid is not UNSET:
            field_dict["fluidId"] = fluidid
        if fluid is not UNSET:
            field_dict["fluid"] = fluid
        if pressure is not UNSET:
            field_dict["pressure"] = pressure

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        """Load `CloudPointFixedPressureCalculationInput` instance from a dict."""
        d = src_dict.copy()
        access_key = d.pop("accessKey")
        units = d.pop("units", UNSET)

        components = []
        _components = d.pop("components")
        for components_item_data in _components:
            components_item = CalculationComposition.from_dict(components_item_data)

            components.append(components_item)

        _fluidid = d.pop("fluidId", UNSET)
        fluidid: Union[Unset, str]
        if isinstance(_fluidid, Unset):
            fluidid = UNSET
        else:
            fluidid = _fluidid

        _fluid = d.pop("fluid", UNSET)
        fluid: Union[Unset, ApiFluid]
        if isinstance(_fluid, Unset):
            fluid = UNSET
        else:
            fluid = ApiFluid.from_dict(_fluid)

        pressure = d.pop("pressure", UNSET)

        cloud_point_calculation_input = cls(
            access_key=access_key,
            components=components,
            fluidid=fluidid,
            fluid=fluid,
            units=units,
            pressure=pressure,
        )

        return cloud_point_calculation_input

    @classmethod
    def from_input_object(cls: Type[T], input_object: "CloudPointFixedPressureCalculationInput") -> T:
        """Load `CloudPointFixedPressureCalculationInput` instance from a similar instance, such as `FlashFixedTemperaturePressureCalculationInput`.
        This is useful for copying data from one instance to another.
        
        Parameters
        ----------
        input_object : Union[EosPropertiesTPnCalculationInput, FlashFixedTemperaturePressureCalculationInput, CloudPointFixedPressureCalculationInput]
            Instance to copy data from.
        
        Returns
        -------
        EosPropertiesTPnCalculationInput
            New instance with copied data.
        """
        d = input_object.to_dict()
        return cls.from_dict(d)
