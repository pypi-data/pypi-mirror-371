from pathlib import Path
import pandas as pd
from simera import Ratesheet, RatesheetManager, Shipment, Cost, Config, ZipcodeManager, calculate_cost

sc = Config()
zm = ZipcodeManager()
rm = RatesheetManager(sc.path.resources / 'ratesheets')

ratesheets = rm.read_excel('_test A.xlsb')

shipments = [Shipment({'lane': {'dest_ctry': 'PL', 'dest_zip': '10000'},
                       'units': {'tsc_pkg_Lcm_100': 2, 'm3': round(kg / 150, 3), 'shipment': 1, 'kg': kg}}) for kg in [25, 30, 60]]

shipments_cost, shipments_without_cost = calculate_cost(shipments, ratesheets)
cost = pd.DataFrame([shp.cost_summary for shp in shipments_cost]).sort_values(['sh_id', 'cost_total'], ignore_index=True)

rm.show_files(['!TSC_', '!PAR_'])
rm.show_files(['!TSC_', '!PAR_'])

ratesheets = rm.read_excel(['!TSC_', '!PAR_'])
ratesheets = rm.read_excel('_test')

ratesheets = rm.read_excel_and_to_pickle('_ratesheets_all.pkl')
ratesheets = rm.read_excel_and_to_pickle('_ratesheets_ltl_par.pkl', '!TSC')
ratesheets = rm.read_excel_and_to_pickle('_ratesheets_ltl_par-tsc-demo.pkl', ['!TSC_', '!PAR_'])
ratesheets = rm.read_pickle('_ratesheets_ltl_par.pkl')
ratesheets = rm.read_pickle('_ratesheets_ltl_par-tsc-demo.pkl')


rm.to_pickle(ratesheets, 'TSC-DEMO2.pkl')

countries = ['PL']
shipments = [Shipment({'lane': {'dest_ctry': ctry, 'dest_zip': zm.zipcode_clean_first[ctry], 'src_site': 'DC_PL_FUCKA'},
                       'meta': {'trpmode': 'LTL'},
                       'units': {'tsc_pkg_Lcm_100': 0, 'm3': kg / 150, 'shipment': 1, 'kg': kg}}) for ctry in countries for kg in [10, 20, 30, 50, 100]]

shipments_cost, shipments_without_cost = calculate_cost(shipments, ratesheets)
cost = pd.DataFrame([shp.cost_summary for shp in shipments_cost]).sort_values(['sh_id', 'cost_total'], ignore_index=True)


# ======================================================================================================================
# Testing cost
# ======================================================================================================================
test_files = [
    Path(sc.path.resources / 'ratesheets/_test A.xlsb'),
]
sheet_names = {file: pd.ExcelFile(file).sheet_names for file in test_files}
sheet_names_tuple = []
for k, v in sheet_names.items():
    for item in v:
        sheet_names_tuple.append((k, item))
ratesheets = [Ratesheet(file, sheet_name) for file, sheet_name in sheet_names_tuple]

countries = ['PT']
countries = set()
for ratesheet in ratesheets:
    for c in ratesheet.shortcuts.dest_countries:
        countries.add(c)

units_defaults = sc.config.ratesheet.get('custom_defaults')
shipments = [Shipment({'lane': {'dest_ctry': ctry, 'dest_zip': zm.zipcode_clean_first[ctry]},
                       'units': {**units_defaults, 'm3': kg / 150, 'shipment': 1, 'kg': kg}}) for ctry in countries for kg in [10, 20, 30, 50, 100]]
shipments_cost, shipments_without_cost = calculate_cost(shipments, ratesheets)
cost = pd.DataFrame([shp.cost_summary for shp in shipments_cost]).sort_values(['sh_id', 'cost_total'], ignore_index=True)

cols_to_drop = cost[[col for col in units_defaults.keys() if col not in ['shipment', 'package']]].sum() == 0
cols_to_drop = cols_to_drop[cols_to_drop].index
cost.drop(columns=cols_to_drop, inplace=True)
cost_best = cost.sort_values(by=['sh_id', 'cost_total'], ascending=[True, True]).drop_duplicates(subset=['sh_id'], keep='first')

sh0 = Shipment({'lane': {'dest_ctry': 'HR', 'dest_zip': '12345'},
                'units': {**units_defaults, 'm3': 10 / 150, 'shipment': 1, 'kg': 10, 'tsc_pkg_LGcm_300': 1, 'tsc_pkg_Lcm_100-76': 1}})
shipments = [sh0]
ratesheets_test = [rs for rs in ratesheets if rs.input.file_path.name == 'TSC_PAR_FED_STD_SINGL.xlsb']
shipments_cost, shipments_without_cost = calculate_cost(shipments, ratesheets_test)
cost = pd.DataFrame([shp.cost_summary for shp in shipments_cost]).sort_values(['sh_id', 'cost_total'], ignore_index=True)

# ======================================================================================================================
# First demo fro LTL vs PAR
# ======================================================================================================================

def normalize_ratesheets_max(ratesheets):
    for rs in ratesheets:
        a = rs.meta.shipment_size_max['func_input']
        m3 = a.get('m3')
        kg = a.get('kg')
        new_values = {}
        if m3 is not None:
            new_values.update({'m3': m3 - 0.0001})
        if kg is not None:
            new_values.update({'kg': kg - 0.0001})
        rs.meta.shipment_size_max['func_input'] = new_values
    return ratesheets

ratesheets = rm.read_excel_and_to_pickle('_ratesheets_ltl_par.pkl', ['!TSC-DEMO', '!TSC_PAR'])
ratesheets = rm.read_excel_and_to_pickle('_ratesheets_ltl_par-tsc-demo.pkl', ['!PAR_*', '!TSC_PAR'])

ratesheets_fre = rm.read_pickle('_ratesheets_ltl_par.pkl')
ratesheets_tsc = rm.read_pickle('_ratesheets_ltl_par-tsc-demo.pkl')

ratesheets_fre = normalize_ratesheets_max(ratesheets_fre)
ratesheets_tsc = normalize_ratesheets_max(ratesheets_tsc)

countries = ['PL', 'DE', 'NL', 'ES', 'FR', 'IT']
shipments = [Shipment({'lane': {'dest_ctry': ctry, 'dest_zip': zm.zipcode_clean_first[ctry]},
                       'units': {'m3': kg / 150, 'shipment': 1, 'kg': kg, 'tsc_pkg_Lcm_100': 0}}) for ctry in countries for kg in [1, 10, 25, 50, 100, 1000, 5000]]
shipments = [Shipment({'lane': {'dest_ctry': ctry, 'dest_zip': zm.zipcode_clean_first[ctry]},
                       'units': {'m3': kg / 150, 'shipment': 1, 'kg': kg, 'tsc_pkg_Lcm_100': 1}}) for ctry in countries for kg in [1, 10, 25, 50, 100, 1000, 5000]]

shipments_cost, shipments_without_cost = calculate_cost(shipments, ratesheets_fre)
shipments_cost, shipments_without_cost = calculate_cost(shipments, ratesheets_tsc)
# shipments_cost, shipments_without_cost = calculate_cost(shipments, [rs])
# shipments_cost, shipments_without_cost = calculate_cost(shipments, [rs_with_whs])
cost = pd.DataFrame([shp.cost_summary for shp in shipments_cost]).sort_values(['sh_id', 'cost_total'], ignore_index=True)
afters = (('m3_chg', 'kg'), ('kg_chg', 'm3_chg'), ('service1', 'service'), ('service2', 'service1'), ('channel', 'service2'),
          ('trp|max|trp_min', 'trp|sum|trp_var'), ('trp_par|sum|par_pack', 'trp|max|trp_min'), ('trp|sum|tsc_pkg_Lcm_100', 'trp_par|sum|par_pack'), ('trp|sum|trp_lhl', 'trp|sum|tsc_pkg_Lcm_100'))
for col, after in afters:
    if col in cost.columns and after in cost.columns:
        cost.insert(cost.columns.get_loc(after) + 1, col, cost.pop(col))
cost.drop(columns=['rs_id', 'default_ratesheet', 'transit_time', 'sheet_name', 'channel'], inplace=True)
cost.to_clipboard(index=False)

filter_mask = cost.src_site.isin(['DC_NL_EINDHOVEN'])
filter_mask = cost.src_site.isin(['DC_PL_PILA'])
filter_mask = cost.src_site.str.startswith('DC_')
cost = cost[filter_mask].copy()
cost_see = cost[['sh_id', 'dest_ctry', 'dest_zip', 'm3', 'kg', 'm3_chg', 'kg_chg', 'package', 'total_shipments', 'src_site',
                 'carrier', 'trpmode', 'service', 'service1', 'cost_total', 'trp|sum|trp_var', 'trp|mul|trp_fsc']]
cost_best = cost.sort_values(by=['sh_id', 'cost_total'], ascending=[True, True]).drop_duplicates(subset=['sh_id'], keep='first')
