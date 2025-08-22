from gdm.distribution.components import DistributionBus, DistributionRegulator
from gdm.distribution.controllers import RegulatorController
from gdm.distribution.enums import Phase

from ditto.readers.cim_iec_61968_13.equipment.distribution_transformer_equipment import (
    DistributionTransformerEquipmentMapper,
)

from ditto.readers.cim_iec_61968_13.cim_mapper import CimMapper
from ditto.readers.cim_iec_61968_13.common import phase_mapper


class DistributionRegulatorMapper(CimMapper):
    def __init__(self, system):
        super().__init__(system)

    def parse(self, row):
        return DistributionRegulator(
            name=self.map_name(row),
            buses=self.map_bus(row),
            equipment=self.map_equipment(row),
            winding_phases=self.map_winding_phases(row),
            controllers=self.map_controllers(row),
        )

    def map_name(self, row):
        return row["xfmr"]

    def map_winding_phases(self, row):
        if "wdg_1_phase" in row:
            phase_1 = [phase_mapper[phs] for phs in row["wdg_1_phase"].replace("N", "")]
        else:
            phase_1 = [Phase.A, Phase.B, Phase.C]

        if "wdg_2_phase" in row:
            phase_2 = [phase_mapper[phs] for phs in row["wdg_2_phase"].replace("N", "")]
        else:
            phase_2 = [Phase.A, Phase.B, Phase.C]

        return [phase_1, phase_2]

    def map_bus(self, row):
        bus_1_name = row["bus_1"]
        bus_2_name = row["bus_2"]
        bus_1 = self.system.get_component(DistributionBus, bus_1_name)
        bus_2 = self.system.get_component(DistributionBus, bus_2_name)
        return [bus_1, bus_2]

    def map_equipment(self, row):
        xfmr_equip_mapper = DistributionTransformerEquipmentMapper(self.system)
        xfmr_equip = xfmr_equip_mapper.parse(row)
        return xfmr_equip

    def map_controllers(self, row):
        reg_controllers = self.system.get_component(RegulatorController, row["xfmr"])
        return [reg_controllers]
