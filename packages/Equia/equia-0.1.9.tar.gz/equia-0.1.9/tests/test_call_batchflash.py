import pytest
from typing import Union
from equia.models import (
    CalculationComposition, ProblemDetails,
    BatchFlashFixedTemperaturePressureCalculationInput, BatchFlashCalculationResult, 
)
from equia.equia_client import EquiaClient
from equia.demofluids.demofluid1_nHexane_Ethylene_HDPE7 import demofluid1_nHexane_Ethylene_HDPE7
from equia.models.batchflash_fixed_temperature_pressure_calculation_item import BatchFlashFixedTemperaturePressureCalculationItem
from equia.units import Units
from utility.api_access import ApiAccess

@pytest.mark.asyncio
async def test_call_batchflash():
    client = EquiaClient(ApiAccess.url, ApiAccess.access_key)

    input: BatchFlashFixedTemperaturePressureCalculationInput = client.get_batchflash_fixed_temperature_pressure_input()
    input.fluid = demofluid1_nHexane_Ethylene_HDPE7()
    input.units = str(Units(C_in="Massfraction", C_out="Massfraction", T_in="Kelvin", T_out="Kelvin", P_in="Bar", P_out="Bar"))
    input.components = [
        CalculationComposition(amount=0.78),
        CalculationComposition(amount=0.02),
        CalculationComposition(amount=0.20)
    ]

    item1 = BatchFlashFixedTemperaturePressureCalculationItem()
    item1.temperature = 445
    item1.pressure = 20

    input.points.append(item1)

    result: Union[BatchFlashCalculationResult, ProblemDetails] = await client.call_batchflash_fixed_temperature_pressure_async(input)

    await client.cleanup()

    #assert result.status == 400
    assert result.success is True
    assert len(result.points[0].phases) == 4
