import itertools
from simera import Config
from simera.utils import DataInputError

# class OrderToShipment:
#     pass

sc = Config()

class Shipment:
    """
    Consolidate all orderline level data to shipment data
    """
    # future: itertools.count is unique per python process. When moving to multiprocessing for cost,
    #  make sure it's not shipment are created before split.
    _id_counter = itertools.count(1)

    # Class variables - defaults and choices
    # Note: config values are taken from sc.config (not from ratesheet) as ratesheet could have older version
    _config_choices_volume = sc.config.units_of_measure.get('choices').get('volume')
    _config_choices_weight = sc.config.units_of_measure.get('choices').get('weight')
    _config_choices_volume_and_weight = sc.config.units_of_measure.get('choices').get('volume_and_weight')
    _config_units_of_measure_conversions_volume = sc.config.units_of_measure['conversions']['volume']
    _config_units_of_measure_conversions_weight = sc.config.units_of_measure['conversions']['weight']

    def __init__(self, input_data):
        # Process input data into dict with meta, lane and cost keys. Probably will be extended with SubClasses
        self.id = next(Shipment._id_counter)
        self.input_data = input_data
        self.units = self._get_unit_attributes()
        self.lane = self._get_lane_attributes()
        self.meta = self._get_meta_attributes()
        self.display = self._get_display_in_summary()

    def __repr__(self):
        return f"Shipment <{self.lane.get('dest_ctry')}><{self.id}>"

    def _get_lane_attributes(self):
        lane_items_builtin = [
            'src_site', 'src_region', 'src_ctry', 'src_zip', 'src_zone',
            'dest_site', 'dest_region', 'dest_ctry', 'dest_zip', 'dest_zone',
        ]
        lane_items = dict.fromkeys(lane_items_builtin)
        if (lane_input := self.input_data.get('lane')) is not None:
            lane_items.update(lane_input)

        if lane_items.get('dest_ctry') is None and lane_items.get('dest_zone') is None:
            raise DataInputError(f"Shipment data missing (to determine dest_zone): 'lane.dest_ctry'.",
                                 solution="Provide lane.dest_ctry or lane.dest_zone")
        if lane_items.get('dest_zip') is None and lane_items.get('dest_zone') is None:
            raise DataInputError(f"Shipment data missing (to determine dest_zone): 'lane.dest_zip'.",
                                 solution="Provide lane.dest_zip or lane.dest_zone")
        return lane_items

    def _get_unit_attributes(self):
        cost_units_builtin = []
        cost_units = dict.fromkeys(cost_units_builtin)
        # Update units from input_data
        if (cost_input := self.input_data.get('units')) is not None:
            cost_units.update(cost_input)

        # Convert weight and volume units to 'default_in_calculation' units (m3 and kg). It's for chargeable_ratios
        converted_cost_units = {}
        for cost_unit in cost_units.keys():
            if cost_unit in self._config_choices_volume:
                ratio_to_m3 = self._config_units_of_measure_conversions_volume[cost_unit]['m3']
                converted_cost_units.update({'m3': cost_units[cost_unit] / ratio_to_m3})
                continue
            if cost_unit in self._config_choices_weight:
                ratio_to_kg = self._config_units_of_measure_conversions_weight[cost_unit]['kg']
                converted_cost_units.update({'kg': cost_units[cost_unit] / ratio_to_kg})
        cost_units.update(converted_cost_units)
        return cost_units

    def _get_meta_attributes(self):
        meta_items_builtin = []
        meta_items = dict.fromkeys(meta_items_builtin)
        if (meta_input := self.input_data.get('meta')) is not None:
            meta_items.update(meta_input)
        return meta_items

    def _get_display_in_summary(self):
        items_builtin = []
        items = dict.fromkeys(items_builtin)
        if (display_input := self.input_data.get('display')) is not None:
            items.update(display_input)
        return items


if __name__ == '__main__':
    pass

