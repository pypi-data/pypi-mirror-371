import time
import logging
import numpy as np
import pandas as pd
from pathlib import Path
from decimal import Decimal
from pyrfc import Connection
from typing import Type, Tuple
from lib_utilys import read_json
from lib_sap.purchase_order import po_getdetail, po_getsalesmen, po_confirm

pd.options.mode.copy_on_write = True

logger = logging.getLogger(__name__)

class OrderRsp:
    def __init__(self, uid, adress, message, business, subject, text, pdf):
        self.uid = uid
        self.adress = adress
        self.message = message
        self.business = business
        self.subject = subject
        self.text = text
        self.pdf = pdf
        self.vendor_order = None
        self.creditor_number = None
        self.gln = None
        self.po_number = None
        self.po_date = None
        self.df = pd.DataFrame()

    def configure_ordersp(self, kv_pairs: dict, UNITMAP_PATH: Path):
        """Configures key-value pairs for the order response."""
        df = pd.DataFrame(kv_pairs.get('Material_list'))
        df = self._parse_units(df, UNITMAP_PATH)
        df = self._set_line_level(df, kv_pairs)
        df = self._calc_missing_price(df)
        df = self._rename_columns(df)
        self.df = self._group_by_material(df)
        self.vendor_order = kv_pairs.get('Vendor_order')
        self.creditor_number = kv_pairs.get('Creditor_number')
        self.gln = kv_pairs.get('Creditor_international_location_number')
        self.po_number = kv_pairs.get('Purchase_order')
        self.po_date = kv_pairs.get('Purchase_order_date')
        self.total_value = kv_pairs.get('Invoice_value')
        self.total_tax = kv_pairs.get('Total_tax')
        self.net_value = kv_pairs.get('Net_value')

    def _parse_units(self, df: pd.DataFrame, UNITMAP_PATH: Path) -> pd.DataFrame:
        """Parses units in the DataFrame based on a unit map."""
        unit_map = read_json(UNITMAP_PATH).get('units')
        df['Unit'] = df['Unit'].apply(lambda x: unit_map.get(x, x))
        return df

    def _calc_missing_price(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculates missing product line price based on other prices and quantity."""
        df.loc[df['Product_line_price'].isna() & ~df['Product_net_price'].isna(),
                'Product_line_price'] = df['Product_net_price'] * df['Quantity']
        df.loc[df['Product_line_price'].isna() & ~df['Product_price'].isna() & ~df['Discount'].isna(),
                'Product_line_price'] = (df['Product_price'] * df['Quantity']) * (1 - (df['Discount'] / 100))
        return df

    def _set_line_level(self, df: pd.DataFrame, kv_pairs: dict):
        """Sets line-level details in the order response DataFrame."""
        df.loc[df['Delivery_date'].isna(), 'Delivery_date'] = kv_pairs.get('Delivery_date')
        if kv_pairs.get('Price_unit') is None:
            df.loc[df['Price_unit'].isna(), 'Price_unit'] = 1
        else:
            df.loc[df['Price_unit'].isna(), 'Price_unit'] = kv_pairs.get('Price_unit')
        if df['Position_number'].isna().all():
            df['Position_number'] = df['Vendor_position_number']
        return df
    
    def _rename_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Renames columns in the DataFrame to match SAP standards."""
        rename_map = {
            'EAN': 'EAN_UPC',
            'Material_number_vendor': 'VEND_MAT',
            'Material_number': 'MATERIAL',
            'Position_number': 'PO_ITEM',
            'Delivery_date': 'DELIV_DATE',
            'Discount': 'DISCOUNT',
            'Quantity': 'QUANTITY',
            'Material_description_vendor': 'SHORT_TEXT',
            'Price_unit': 'PRICE_UNIT',
            'Product_line_price': 'NET_VALUE',
            'Product_net_price': 'NET_PRICE',
            'Product_price': 'GROS_PRICE',
            'Purchase_order_line': 'PO_NUMBER',
            'Purchase_order_line_date': 'PO_DATE',
            'Unit': 'UNIT',
            'Vendor_position_number': 'VEND_PO_ITEM',
        }
        return df.rename(columns=rename_map)

    def _group_by_material(self, df: pd.DataFrame) -> pd.DataFrame:
        """Groups the DataFrame by material and aggregates relevant fields."""
        df = df.groupby('VEND_MAT').agg({
            'DELIV_DATE': 'first',       # TODO: make robust to multiple delivery dates for the same material
            'DISCOUNT': 'first',
            'EAN_UPC': 'first',
            'GROS_PRICE': 'sum',
            'MATERIAL': 'first',
            'NET_PRICE': 'first',
            'NET_VALUE': 'sum',
            'PO_DATE': 'first',
            'PO_ITEM': 'first',
            'PO_NUMBER': 'first',
            'PRICE_UNIT': 'first',
            'QUANTITY': 'sum',
            'SHORT_TEXT': 'first',
            'UNIT': 'first',
            'VEND_PO_ITEM': 'first',
        }).reset_index()
        return df

class Order:
    def __init__(self):
        self.po_number = None
        self.vendor = None
        self.co_code = None
        self.df = pd.DataFrame()
    
    def configure_order(self, sapconn: Type[Connection], po_number: int, FIELD_PATH: Path):
        self.po_number = po_number
        po_details = po_getdetail(sapconn, str(po_number))
        df = self._parse_po_details(sapconn, po_details, FIELD_PATH)
        self.df = self._add_additional_columns(df)

    def _parse_po_details(self, sapconn: Type[Connection], po_details: dict, FIELD_PATH: Path) -> pd.DataFrame:
        """Parses purchase order details into a DataFrame."""
        keep_fields = read_json(FIELD_PATH).get('fields')
        
        df_items = pd.DataFrame(po_details['PO_ITEMS'])
        df_items = df_items.loc[:, keep_fields]
        df_items['PO_ITEM_LIST'] = df_items['PO_ITEM'].copy()
        df_items['QUANTITY_LIST_ord'] = df_items['QUANTITY'].copy()
        df_items['NET_VALUE_LIST'] = df_items['NET_VALUE'].copy()
        df_items['GROS_VALUE_LIST'] = df_items['GROS_VALUE'].copy()

        df_schedules = pd.DataFrame(po_details['PO_ITEM_SCHEDULES'])
        df_schedules = df_schedules.loc[:, ['PO_ITEM', 'DELIV_DATE']]
        logger.debug(f"PO_ITEMS: {df_items.shape}, PO_ITEM_SCHEDULES: {df_schedules.shape}")

        df_details = pd.merge(df_items, df_schedules, on='PO_ITEM', how='left')
        logger.debug(f"PO_DETAILS after merge: {df_details.shape}")

        df_history = pd.DataFrame(po_details['PO_ITEM_HISTORY'])
        if not df_history.empty:
            df_history = df_history[df_history['HIST_TYPE'] == 'E']
            df_history.rename({'QUANTITY': 'DELVRD_QUANTITY', 'ENTRY_DATE': 'DELVRD_DATE'}, axis=1, inplace=True)
            df_history = df_history.loc[:, ['PO_ITEM', 'DELVRD_QUANTITY', 'DELVRD_DATE']]
        else:
            df_history = pd.DataFrame(columns=['PO_ITEM', 'DELVRD_QUANTITY', 'DELVRD_DATE'])
        df_details = pd.merge(df_details, df_history, on='PO_ITEM', how='left')
        logger.debug(f"PO_ITEM_HISTORY: {df_history.shape}")
        logger.debug(f"PO_DETAILS after history merge: {df_details.shape}")

        df_account = pd.DataFrame(po_details['PO_ITEM_ACCOUNT_ASSIGNMENT'])
        if not df_account.empty:
            df_account = df_account.loc[:, ['PO_ITEM', 'SD_DOC', 'SDOC_ITEM']]
            df_account.rename({'SD_DOC': 'SALES_ORDER', 'SDOC_ITEM': 'SALES_ITEM'}, axis=1, inplace=True)
            df_account['SALESMEN'] = df_account['SALES_ORDER'].apply(lambda x: po_getsalesmen(sapconn, x))
        else:
            df_account = pd.DataFrame(columns=['PO_ITEM', 'SALES_ORDER', 'SALES_ITEM', 'SALESMEN'])
        df_details = pd.merge(df_details, df_account, on='PO_ITEM', how='left')
        logger.debug(f"PO_ITEM_ACCOUNT_ASSIGNMENT: {df_account.shape}")
        logger.debug(f"PO_DETAILS after account merge: {df_details.shape}")

        df_confirmations = pd.DataFrame(po_details['PO_ITEM_CONFIRMATIONS'])
        if not df_confirmations.empty:
            df_confirmations = df_confirmations.groupby('PO_ITEM').agg({
                'CONF_SER': list,
                'QUANTITY':  list,
                'DELIV_DATE': list
                }).reset_index()
            df_confirmations = df_confirmations.loc[:, ['PO_ITEM', 'CONF_SER', 'QUANTITY', 'DELIV_DATE']]
            df_confirmations.rename({'QUANTITY': 'CONF_QTY', 'DELIV_DATE': 'CONF_DATE'}, axis=1, inplace=True)
        else:
            df_confirmations = pd.DataFrame(columns=['PO_ITEM', 'CONF_SER', 'CONF_QTY', 'CONF_DATE'])
        df_details = pd.merge(df_details, df_confirmations, on='PO_ITEM', how='left')
        logger.debug(f"PO_ITEM_CONFIRMATIONS: {df_confirmations.shape}")
        logger.debug(f"PO_DETAILS after confirmations merge: {df_details.shape}")

        df_details['CONF_QTY'] = df_details['CONF_QTY'].apply(lambda x: x if isinstance(x, list) else [])
        df_details['CONF_SER'] = df_details['CONF_SER'].apply(lambda x: x if isinstance(x, list) else [])
        df_details['CONF_DATE'] = df_details['CONF_DATE'].apply(lambda x: x if isinstance(x, list) else [])
        
        df_details = df_details[df_details['DELETE_IND'] == '']
        df_details = df_details.groupby('MATERIAL').agg({
            'PO_NUMBER': 'first',
            'PO_ITEM': 'first',
            'PO_ITEM_LIST': list,
            'SHORT_TEXT': 'first',
            'CO_CODE': 'first',
            'QUANTITY': 'sum',
            'QUANTITY_LIST_ord': list,
            'UNIT': 'first',
            'NET_PRICE': 'first',
            'PRICE_UNIT': 'first',
            'NET_VALUE': 'sum',
            'NET_VALUE_LIST': list,
            'GROS_VALUE': 'sum',
            'GROS_VALUE_LIST': list,
            'EAN_UPC': 'first',
            'VEND_MAT': 'first',
            'INFO_REC': 'first',
            'ACCTASSCAT': list,
            'DELIV_DATE': 'first',
            'DELVRD_QUANTITY': list,
            'DELVRD_DATE': list,
            'SALES_ORDER': list,
            'SALES_ITEM': list,
            'SALESMEN': list,
            'CONF_SER': list,
            'CONF_QTY': list,
            'CONF_DATE': list,
        }).reset_index()

        df_header = pd.DataFrame(po_details['PO_HEADER'], index=[0])
        self.vendor = df_header['VENDOR'].iloc[0]
        self.co_code = df_header['CO_CODE'].iloc[0]

        return df_details

    def _add_additional_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Adds additional columns to the DataFrame."""
        df['GROSS_PRICE'] = df['GROS_VALUE'] / df['QUANTITY']
        return df

def match_ordersp_to_order(df_rsp: pd.DataFrame, df_ord: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    rsp = df_rsp.copy()
    ord_ = df_ord.copy()
    rsp['_rsp_id'] = np.arange(len(rsp))
    ord_['_ord_id'] = np.arange(len(ord_))

    matches_list = []
    unmatched_list = []

    vm = pd.merge(
        rsp, ord_, on='VEND_MAT', how='outer',
        suffixes=('_rsp', '_ord'), indicator='vm_merge'
    )
    vm_matched   = vm[vm['vm_merge'] == 'both'].copy()
    vm_rsp_only_ids  = vm.loc[vm['vm_merge'] == 'left_only',  '_rsp_id'].unique()
    vm_ord_only_ids  = vm.loc[vm['vm_merge'] == 'right_only', '_ord_id'].unique()

    matches_list.append(vm_matched.assign(matched_on='VEND_MAT'))

    rsp_unm = rsp[rsp['_rsp_id'].isin(vm_rsp_only_ids)].copy()
    ord_unm = ord_[ord_['_ord_id'].isin(vm_ord_only_ids)].copy()

    ean = pd.merge(
        rsp_unm, ord_unm, on='EAN_UPC', how='outer',
        suffixes=('_rsp', '_ord'), indicator='ean_merge'
    )
    ean_matched  = ean[ean['ean_merge'] == 'both'].copy()
    ean_rsp_only_ids = ean.loc[ean['ean_merge'] == 'left_only',  '_rsp_id'].unique()
    ean_ord_only_ids = ean.loc[ean['ean_merge'] == 'right_only', '_ord_id'].unique()

    matches_list.append(ean_matched.assign(matched_on='EAN_UPC'))

    rsp_unm = rsp_unm[rsp_unm['_rsp_id'].isin(ean_rsp_only_ids)].copy()
    ord_unm = ord_unm[ord_unm['_ord_id'].isin(ean_ord_only_ids)].copy()

    mat = pd.merge(
        rsp_unm, ord_unm, on='MATERIAL', how='outer',
        suffixes=('_rsp', '_ord'), indicator='mat_merge'
    )
    mat_matched  = mat[mat['mat_merge'] == 'both'].copy()
    mat_rsp_only_ids = mat.loc[mat['mat_merge'] == 'left_only',  '_rsp_id'].unique()
    mat_ord_only_ids = mat.loc[mat['mat_merge'] == 'right_only', '_ord_id'].unique()

    matches_list.append(mat_matched.assign(matched_on='MATERIAL'))

    rsp_unm = rsp_unm[rsp_unm['_rsp_id'].isin(mat_rsp_only_ids)].copy()
    ord_unm = ord_unm[ord_unm['_ord_id'].isin(mat_ord_only_ids)].copy()

    item = pd.merge(
        rsp_unm, ord_unm, on='PO_ITEM', how='outer',
        suffixes=('_rsp', '_ord'), indicator='item_merge'
    )
    item_matched  = item[item['item_merge'] == 'both'].copy()
    item_rsp_only = item[item['item_merge'] == 'left_only'].copy()
    item_ord_only = item[item['item_merge'] == 'right_only'].copy()

    matches_list.append(item_matched.assign(matched_on='PO_ITEM'))
    unmatched_list.extend([
        item_rsp_only.assign(matched_on='UNMATCHED_RSP'),
        item_ord_only.assign(matched_on='UNMATCHED_ORD')
    ])

    matches = pd.concat(matches_list, ignore_index=True) if matches_list else pd.DataFrame()
    unmatched = pd.concat(unmatched_list, ignore_index=True) if unmatched_list else pd.DataFrame()

    matches = matches[sorted(matches.columns)]
    unmatched = unmatched[sorted(unmatched.columns)]
    rsp_unmatched = unmatched[unmatched['matched_on'].str.startswith('UNMATCHED_RSP')]
    ord_unmatched = unmatched[unmatched['matched_on'].str.startswith('UNMATCHED_ORD')]

    matches = _coalesce_join_keys(matches, ['VEND_MAT', 'EAN_UPC', 'MATERIAL'])

    if len(rsp_unmatched) > 0:
        logger.warning(f"{len(rsp_unmatched)} lines in order response could not be matched to order lines.")

    return matches, rsp_unmatched, ord_unmatched

def _coalesce_join_keys(df: pd.DataFrame, fields: list[str]) -> pd.DataFrame:
    for f in fields:
        candidates = [f, f"{f}_rsp", f"{f}_ord"]
        present = [c for c in candidates if c in df.columns]
        if not present:
            continue

        for col in present:
            if pd.api.types.is_string_dtype(df[col]) or pd.api.types.is_object_dtype(df[col]):
                s = df[col].astype("string")
                df[col] = s.where(~s.str.fullmatch(r"\s*"), pd.NA)

        s = df[present[0]] if f in present else None
        for c in [f"{f}_rsp", f"{f}_ord"]:
            if c in df.columns:
                s = df[c] if s is None else s.combine_first(df[c])
        if s is not None:
            df[f] = s

        df.drop(columns=[c for c in (f"{f}_rsp", f"{f}_ord") if c in df.columns],
                inplace=True, errors='ignore')
    return df

def check_ordersp_to_order(merged: pd.DataFrame, tolerance: float=1.0) -> bool:
    """Checks if the order response matches the order."""
    date_explode = merged.explode('CONF_DATE').explode('CONF_DATE')
    rsp_dates_expl = pd.to_datetime(date_explode['DELIV_DATE_rsp'], format='%Y%m%d')
    conf_dates_expl = pd.to_datetime(date_explode['CONF_DATE'], format='%Y%m%d')
    cdt_condition = rsp_dates_expl.eq(conf_dates_expl)
    cdt_condition_impl = cdt_condition.groupby(level=0).all()
    # NOTE: Zevij confirms POs via EDI and sends an email, as this inherently will not satify the condition under else statement,,
    # NOTE: we create a condition that checks if the response quantity and date are exactly the same as the once already confirmed.
    is_confirmed = (merged.loc[:, 'CONF_QTY'].apply(lambda x: sum(sum(lst) for lst in x)) == merged.loc[:, 'QUANTITY_rsp']) & cdt_condition_impl
    eq_or_more = merged.loc[:, 'QUANTITY_ord'] >= merged.loc[:, 'QUANTITY_rsp'] + \
        merged.loc[:, 'CONF_QTY'].apply(lambda x: sum(sum(lst) for lst in x))
    qty_condition = is_confirmed | eq_or_more
        
    nv_condition = merged.loc[:, 'NET_VALUE_ord' : 'NET_VALUE_rsp'].diff(axis=1).iloc[:, -1] <= tolerance

    # NOTE: We assume that when the supplier does not provide a delivery date, it is the same as the order date.

    merged['DELIV_DATE_rsp'] = merged['DELIV_DATE_rsp'].fillna(merged['DELIV_DATE_ord'])
    rsp_dates = pd.to_datetime(merged['DELIV_DATE_rsp'], format='%Y%m%d') 
    ord_dates = pd.to_datetime(merged['DELIV_DATE_ord'], format='%Y%m%d')
    dt_condition = rsp_dates <= ord_dates + pd.tseries.offsets.BDay(n=2)
    cop_condition = merged.loc[:, 'ACCTASSCAT'].str.join(',').str.contains('M')  # Coupled to sales order
    fyi_condition = (~dt_condition) & (cop_condition)  # Notify sales department

    logger.debug(f"condition shapes: dt_condition={dt_condition.shape}, cop_condition={cop_condition.shape}")
    logger.debug(f"Condition shapes: qty_condition={qty_condition.shape}, nv_condition={nv_condition.shape}, fyi_condition={fyi_condition.shape}")

    notify = merged.loc[fyi_condition, :]
    review = merged.loc[(~qty_condition) | (~nv_condition), :]
    perfect = merged.loc[qty_condition & nv_condition & dt_condition, :]
    eligible = merged.loc[qty_condition & nv_condition & (~fyi_condition), :]

    logger.debug(f"\nPerfect matches: {perfect.shape} \nEligible matches: {eligible.shape} \nFYI matches: {notify.shape} \nReview matches: {review.shape} \nout of total matches {merged.shape}")
    
    fyi_items = notify['PO_ITEM_LIST']
    print(f"FYI items: {fyi_items.tolist()}")
    logger.info(f"The following PO_ITEMS should be notified to sales department: {fyi_items.tolist()}")

    return notify, review, eligible, perfect

    # TODO: integrate robustness in unit conversion (e.g. 1 ZAK vs. 100 STUKS))

def create_confirmation(sapconn: Type[Connection], eligible: pd.DataFrame, po_number: int, co_code: str, vendor_order: str, sleep_interval: int = 600):
    df_item, df_itemx = _create_item_attr(eligible, co_code, vendor_order)
    df_confirm, df_confirmx = _create_confirmation_attr(eligible)
    while True:
        result = po_confirm(sapconn, str(po_number), df_item, df_itemx, df_confirm, df_confirmx)
        df_result = pd.DataFrame(result.get('RETURN'))
        is_locked = df_result.get('NUMBER', pd.Series()).eq('006').any()
        if not is_locked:
            logger.info("Confirmation created successfully.")
            break
        user = df_result['MESSAGE_V1'].values[0]
        logger.info("Purchase order %s is locked by %s; retrying in %s seconds",
                    po_number, user, sleep_interval)
        # TODO: Implement email notification to user
        time.sleep(sleep_interval)

def _waterfall_rsp_quantities(row: pd.Series):
    """Distributes response quantities over original order quantities."""
    # NOTE: In the case of multiple PO_ITEMS with the same material, the lowest will be assigned the quantity from the response first.
    # NOTE: If higher PO_ITEMS are assigned response quantity first manually, this will break as we rely on right padding.
    if len(row['QUANTITY_LIST_ord']) > 1:
        conf_list = [sum(lst) for lst in row['CONF_QTY']]
        ord_list = (np.array(row['QUANTITY_LIST_ord']) - np.array(conf_list)).tolist()
        rsp_qty = row['QUANTITY_rsp']
        rsp_list = []

        remainder = rsp_qty
        for q in ord_list:
            take = min(q, remainder)
            rsp_list.append(take)
            remainder -= take
        
        row['QUANTITY_LIST_rsp'] = rsp_list
    else:
        row['QUANTITY_LIST_rsp'] = [row['QUANTITY_rsp']]
    return row

def explode_to_original_rows(eligible: pd.DataFrame) -> pd.DataFrame:
    """Divides eligible DataFrame back over the original rows."""
    waterfall_eligible = eligible.apply(_waterfall_rsp_quantities, axis=1)
    cols_to_explode = ['PO_ITEM_LIST', 'QUANTITY_LIST_ord', 'NET_VALUE_LIST', 
                       'GROS_VALUE_LIST', 'SALESMEN', 'SALES_ITEM', 
                       'SALES_ORDER', 'ACCTASSCAT', 'QUANTITY_LIST_rsp',
                       'CONF_QTY', 'CONF_SER', 'CONF_DATE']

    exp, lode = False, False
    if waterfall_eligible.apply(lambda row: len(row.loc['DELVRD_DATE']) == len(row.loc['PO_ITEM_LIST']), axis=1).all():
        cols_to_explode.append('DELVRD_DATE')
        exp = True
    if waterfall_eligible.apply(lambda row: len(row.loc['DELVRD_QUANTITY']) == len(row.loc['PO_ITEM_LIST']), axis=1).all():
        cols_to_explode.append('DELVRD_QUANTITY')
        lode = True

    df_exploded = waterfall_eligible.explode(cols_to_explode, ignore_index=True)
    df_exploded.loc[:, 'PO_ITEM_ord'] = df_exploded['PO_ITEM_LIST']
    df_exploded.loc[:, 'QUANTITY_ord'] = df_exploded['QUANTITY_LIST_ord']
    df_exploded.loc[:, 'QUANTITY_rsp'] = df_exploded['QUANTITY_LIST_rsp']
    df_exploded.loc[:, 'NET_VALUE'] = df_exploded['NET_VALUE_LIST']
    df_exploded.loc[:, 'GROS_VALUE'] = df_exploded['GROS_VALUE_LIST']
    if exp:
        df_exploded.loc[:, 'DELVRD_DATE'] = df_exploded['DELVRD_DATE']
    if lode:
        df_exploded.loc[:, 'DELVRD_QUANTITY'] = df_exploded['DELVRD_QUANTITY']
    nonzero = df_exploded['QUANTITY_rsp'] != Decimal(0)
    df_exploded.drop(index=df_exploded[~nonzero].index, inplace=True)
    return df_exploded

def _create_item_attr(eligible: pd.DataFrame, co_code: str, vendor_order: str) -> pd.DataFrame:
    """Creates confirmation attributes for the order response."""
    df_item = eligible.loc[:, ['PO_ITEM_ord', 'MATERIAL', 'VEND_MAT', 'QUANTITY_ord']]
    df_item = df_item.rename(columns={
        'PO_ITEM_ord': 'ITEM_NO',
        'QUANTITY_ord': 'QUANTITY'
    })
    df_item['PLANT'] = co_code
    df_item['ACKNOWL_NO'] = vendor_order
    df_item['ACKN_REQD'] = '0'
    df_itemx = df_item.copy()
    df_itemx.loc[:, ['MATERIAL', 'VEND_MAT', 'PLANT', 'QUANTITY', 'ACKNOWL_NO', 'ACKN_REQD']] = 'X'
    df_itemx['ITEM_NOX'] = 'X'
    df_item = df_item.to_dict(orient='records')
    df_itemx = df_itemx.to_dict(orient='records')
    return df_item, df_itemx

def _create_confirmation_attr(eligible: pd.DataFrame) -> pd.DataFrame:
    """Creates confirmation attributes for the order response."""
    df_appended = eligible.apply(_append_new_confirmation, axis=1)
    df_exploded = df_appended.explode(['CONF_QTY', 'CONF_SER', 'CONF_DATE'], ignore_index=True)
    df_confirm = df_exploded.loc[:, ['PO_ITEM_ord', 'CONF_DATE', 'CONF_QTY', 'CONF_SER']]
    df_confirm = df_confirm.rename(columns={
        'PO_ITEM_ord': 'ITEM_NO',
        'CONF_DATE': 'DELIV_DATE',
        'CONF_QTY': 'QUANTITY'
    })
    df_confirm['DELIV_DATE_TYP'] = 'D'
    df_confirm['CONF_CATEGORY'] = 'AB'
    df_confirmx = df_confirm.copy()
    df_confirmx.loc[:, ['DELIV_DATE_TYP', 'DELIV_DATE', 'QUANTITY', 'CONF_CATEGORY']] = 'X'
    df_confirmx['ITEM_NOX'] = 'X'
    df_confirm = df_confirm.to_dict(orient='records')
    df_confirmx = df_confirmx.to_dict(orient='records')
    return df_confirm, df_confirmx

def _append_new_confirmation(row: pd.Series) -> str:
    """Structures confirmations as preparation for correct explosion."""
    conf_ser_list = row['CONF_SER'].copy()
    conf_qty_list = row['CONF_QTY'].copy()
    conf_date_list = row['CONF_DATE'].copy()

    if len(conf_ser_list) == 0:
        conf_ser_list.append('0001')
        conf_qty_list.append(row['QUANTITY_rsp'])
        conf_date_list.append(row['DELIV_DATE_rsp'])
    else:
        total_conf_qtys = sum(row['CONF_QTY'])
        last_conf_qty = row['CONF_QTY'][-1]
        new_conf_qty = row['QUANTITY_rsp']
        order_qty = row['QUANTITY_ord']

        if order_qty == new_conf_qty:
            if len(conf_ser_list) == 0:
                conf_ser_list.append('0001')
                conf_qty_list.append(new_conf_qty)
                conf_date_list.append(row['DELIV_DATE_rsp'])
            else:
                conf_ser_list[-1] = '0001'
                conf_qty_list[-1] = new_conf_qty
                conf_date_list[-1] = row['DELIV_DATE_rsp']
        elif new_conf_qty + total_conf_qtys <= order_qty:
            conf_ser_list.append(str(int(max(conf_ser_list)) + 1).zfill(4))
            conf_qty_list.append(new_conf_qty)
            conf_date_list.append(row['DELIV_DATE_rsp'])
        elif (new_conf_qty == last_conf_qty) and (new_conf_qty + total_conf_qtys > order_qty):
            conf_ser_list[-1] = str(int(max(conf_ser_list))).zfill(4)
            conf_qty_list[-1] = new_conf_qty
            conf_date_list[-1] = row['DELIV_DATE_rsp']

    row['CONF_SER'] = conf_ser_list
    row['CONF_QTY'] = conf_qty_list
    row['CONF_DATE'] = conf_date_list
    return row


def parse_po_details(sapconn: Type[Connection], po_details: dict, FIELD_PATH: Path) -> pd.DataFrame:
    """Parses purchase order details into a DataFrame."""
    keep_fields = read_json(FIELD_PATH).get('fields')
    
    df_items = pd.DataFrame(po_details['PO_ITEMS'])
    df_items = df_items.loc[:, keep_fields]
    df_items['PO_ITEM_LIST'] = df_items['PO_ITEM'].copy()
    df_items['QUANTITY_LIST_ord'] = df_items['QUANTITY'].copy()
    df_items['NET_VALUE_LIST'] = df_items['NET_VALUE'].copy()
    df_items['GROS_VALUE_LIST'] = df_items['GROS_VALUE'].copy()

    df_schedules = pd.DataFrame(po_details['PO_ITEM_SCHEDULES'])
    df_schedules = df_schedules.loc[:, ['PO_ITEM', 'DELIV_DATE']]
    logger.debug(f"PO_ITEMS: {df_items.shape}, PO_ITEM_SCHEDULES: {df_schedules.shape}")

    df_details = pd.merge(df_items, df_schedules, on='PO_ITEM', how='left')
    logger.debug(f"PO_DETAILS after merge: {df_details.shape}")

    df_history = pd.DataFrame(po_details['PO_ITEM_HISTORY'])
    if not df_history.empty:
        df_history = df_history[df_history['HIST_TYPE'] == 'E']
        df_history.rename({'QUANTITY': 'DELVRD_QUANTITY', 'ENTRY_DATE': 'DELVRD_DATE'}, axis=1, inplace=True)
        df_history = df_history.loc[:, ['PO_ITEM', 'DELVRD_QUANTITY', 'DELVRD_DATE']]
    else:
        df_history = pd.DataFrame(columns=['PO_ITEM', 'DELVRD_QUANTITY', 'DELVRD_DATE'])
    df_details = pd.merge(df_details, df_history, on='PO_ITEM', how='left')
    logger.debug(f"PO_ITEM_HISTORY: {df_history.shape}")
    logger.debug(f"PO_DETAILS after history merge: {df_details.shape}")

    df_account = pd.DataFrame(po_details['PO_ITEM_ACCOUNT_ASSIGNMENT'])
    if not df_account.empty:
        df_account = df_account.loc[:, ['PO_ITEM', 'SD_DOC', 'SDOC_ITEM']]
        df_account.rename({'SD_DOC': 'SALES_ORDER', 'SDOC_ITEM': 'SALES_ITEM'}, axis=1, inplace=True)
        df_account['SALESMEN'] = df_account['SALES_ORDER'].apply(lambda x: po_getsalesmen(sapconn, x))
    else:
        df_account = pd.DataFrame(columns=['PO_ITEM', 'SALES_ORDER', 'SALES_ITEM', 'SALESMEN'])
    df_details = pd.merge(df_details, df_account, on='PO_ITEM', how='left')
    logger.debug(f"PO_ITEM_ACCOUNT_ASSIGNMENT: {df_account.shape}")
    logger.debug(f"PO_DETAILS after account merge: {df_details.shape}")

    df_confirmations = pd.DataFrame(po_details['PO_ITEM_CONFIRMATIONS'])
    if not df_confirmations.empty:
        df_confirmations = df_confirmations.groupby('PO_ITEM').agg({
            'CONF_SER': list,
            'QUANTITY':  list,
            'DELIV_DATE': list
            }).reset_index()
        df_confirmations = df_confirmations.loc[:, ['PO_ITEM', 'CONF_SER', 'QUANTITY', 'DELIV_DATE']]
        df_confirmations.rename({'QUANTITY': 'CONF_QTY', 'DELIV_DATE': 'CONF_DATE'}, axis=1, inplace=True)
    else:
        df_confirmations = pd.DataFrame(columns=['PO_ITEM', 'CONF_SER', 'CONF_QTY', 'CONF_DATE'])
    df_details = pd.merge(df_details, df_confirmations, on='PO_ITEM', how='left')
    logger.debug(f"PO_ITEM_CONFIRMATIONS: {df_confirmations.shape}")
    logger.debug(f"PO_DETAILS after confirmations merge: {df_details.shape}")

    df_details['CONF_QTY'] = df_details['CONF_QTY'].apply(lambda x: x if isinstance(x, list) else [])
    df_details['CONF_SER'] = df_details['CONF_SER'].apply(lambda x: x if isinstance(x, list) else [])
    df_details['CONF_DATE'] = df_details['CONF_DATE'].apply(lambda x: x if isinstance(x, list) else [])
    
    df_details = df_details[df_details['DELETE_IND'] == '']
    df_details = df_details.groupby('MATERIAL').agg({
        'PO_NUMBER': 'first',
        'PO_ITEM': 'first',
        'PO_ITEM_LIST': list,
        'SHORT_TEXT': 'first',
        'CO_CODE': 'first',
        'QUANTITY': 'sum',
        'QUANTITY_LIST_ord': list,
        'UNIT': 'first',
        'NET_PRICE': 'first',
        'PRICE_UNIT': 'first',
        'NET_VALUE': 'sum',
        'NET_VALUE_LIST': list,
        'GROS_VALUE': 'sum',
        'GROS_VALUE_LIST': list,
        'EAN_UPC': 'first',
        'VEND_MAT': 'first',
        'INFO_REC': 'first',
        'ACCTASSCAT': list,
        'DELIV_DATE': 'first',
        'DELVRD_QUANTITY': list,
        'DELVRD_DATE': list,
        'SALES_ORDER': list,
        'SALES_ITEM': list,
        'SALESMEN': list,
        'CONF_SER': list,
        'CONF_QTY': list,
        'CONF_DATE': list,
    }).reset_index()

    df_header = pd.DataFrame(po_details['PO_HEADER'], index=[0])
    vendor = df_header['VENDOR'].iloc[0]
    co_code = df_header['CO_CODE'].iloc[0]

    return df_details, vendor, co_code

def add_additional_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Adds additional columns to the DataFrame."""
    df['GROSS_PRICE'] = df['GROS_VALUE'] / df['QUANTITY']
    return df

def parse_units_rsp(df: pd.DataFrame, UNITMAP_PATH: Path) -> pd.DataFrame:
    """Parses units in the DataFrame based on a unit map."""
    unit_map = read_json(UNITMAP_PATH).get('units')
    df['Unit'] = df['Unit'].apply(lambda x: unit_map.get(x, x))
    return df

def set_line_level(df: pd.DataFrame, kv_pairs: dict):
    """Sets line-level details in the order response DataFrame."""
    df.loc[df['Delivery_date'].isna(), 'Delivery_date'] = kv_pairs.get('Delivery_date')
    if kv_pairs.get('Price_unit') is None:
        df.loc[df['Price_unit'].isna(), 'Price_unit'] = 1
    else:
        df.loc[df['Price_unit'].isna(), 'Price_unit'] = kv_pairs.get('Price_unit')
    if df['Position_number'].isna().all():
        df['Position_number'] = df['Vendor_position_number']
    return df

def calc_missing_price(df: pd.DataFrame) -> pd.DataFrame:
    """Calculates missing product line price based on other prices and quantity."""
    df.loc[df['Product_line_price'].isna() & ~df['Product_net_price'].isna(),
            'Product_line_price'] = df['Product_net_price'] * df['Quantity']
    df.loc[df['Product_line_price'].isna() & ~df['Product_price'].isna() & ~df['Discount'].isna(),
            'Product_line_price'] = (df['Product_price'] * df['Quantity']) * (1 - (df['Discount'] / 100))
    return df

def rename_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Renames columns in the DataFrame to match SAP standards."""
    rename_map = {
        'EAN': 'EAN_UPC',
        'Material_number_vendor': 'VEND_MAT',
        'Material_number': 'MATERIAL',
        'Position_number': 'PO_ITEM',
        'Delivery_date': 'DELIV_DATE',
        'Discount': 'DISCOUNT',
        'Quantity': 'QUANTITY',
        'Material_description_vendor': 'SHORT_TEXT',
        'Price_unit': 'PRICE_UNIT',
        'Product_line_price': 'NET_VALUE',
        'Product_net_price': 'NET_PRICE',
        'Product_price': 'GROS_PRICE',
        'Purchase_order_line': 'PO_NUMBER',
        'Purchase_order_line_date': 'PO_DATE',
        'Unit': 'UNIT',
        'Vendor_position_number': 'VEND_PO_ITEM',
    }
    return df.rename(columns=rename_map)

def group_by_material(df: pd.DataFrame) -> pd.DataFrame:
    """Groups the DataFrame by material and aggregates relevant fields."""
    df = df.groupby('VEND_MAT').agg({
        'DELIV_DATE': 'first',       # TODO: make robust to multiple delivery dates for the same material
        'DISCOUNT': 'first',
        'EAN_UPC': 'first',
        'GROS_PRICE': 'sum',
        'MATERIAL': 'first',
        'NET_PRICE': 'first',
        'NET_VALUE': 'sum',
        'PO_DATE': 'first',
        'PO_ITEM': 'first',
        'PO_NUMBER': 'first',
        'PRICE_UNIT': 'first',
        'QUANTITY': 'sum',
        'SHORT_TEXT': 'first',
        'UNIT': 'first',
        'VEND_PO_ITEM': 'first',
    }).reset_index()
    return df


def create_item_objects(eligible: pd.DataFrame, co_code: str, vendor_order: str) -> pd.DataFrame:
    """Creates confirmation attributes for the order response."""
    df_item = eligible.loc[:, ['PO_ITEM_ord', 'MATERIAL', 'VEND_MAT', 'QUANTITY_ord']]
    df_item = df_item.rename(columns={
        'PO_ITEM_ord': 'ITEM_NO',
        'QUANTITY_ord': 'QUANTITY'
    })
    df_item['PLANT'] = co_code
    df_item['ACKNOWL_NO'] = vendor_order
    df_item['ACKN_REQD'] = '0'
    df_itemx = df_item.copy()
    df_itemx.loc[:, ['MATERIAL', 'VEND_MAT', 'PLANT', 'QUANTITY', 'ACKNOWL_NO', 'ACKN_REQD']] = 'X'
    df_itemx['ITEM_NOX'] = 'X'
    df_item = df_item.to_dict(orient='records')
    df_itemx = df_itemx.to_dict(orient='records')
    return df_item, df_itemx

def create_confirmation_objects(eligible: pd.DataFrame) -> pd.DataFrame:
    """Creates confirmation attributes for the order response."""
    df_appended = eligible.apply(_append_new_confirmation, axis=1)
    df_exploded = df_appended.explode(['CONF_QTY', 'CONF_SER', 'CONF_DATE'], ignore_index=True)
    df_confirm = df_exploded.loc[:, ['PO_ITEM_ord', 'CONF_DATE', 'CONF_QTY', 'CONF_SER']]
    df_confirm = df_confirm.rename(columns={
        'PO_ITEM_ord': 'ITEM_NO',
        'CONF_DATE': 'DELIV_DATE',
        'CONF_QTY': 'QUANTITY'
    })
    df_confirm['DELIV_DATE_TYP'] = 'D'
    df_confirm['CONF_CATEGORY'] = 'AB'
    df_confirmx = df_confirm.copy()
    df_confirmx.loc[:, ['DELIV_DATE_TYP', 'DELIV_DATE', 'QUANTITY', 'CONF_CATEGORY']] = 'X'
    df_confirmx['ITEM_NOX'] = 'X'
    df_confirm = df_confirm.to_dict(orient='records')
    df_confirmx = df_confirmx.to_dict(orient='records')
    return df_confirm, df_confirmx

def _append_new_confirmation(row: pd.Series) -> str:
    """Structures confirmations as preparation for correct explosion."""
    conf_ser_list = row['CONF_SER'].copy()
    conf_qty_list = row['CONF_QTY'].copy()
    conf_date_list = row['CONF_DATE'].copy()

    if len(conf_ser_list) == 0:
        conf_ser_list.append('0001')
        conf_qty_list.append(row['QUANTITY_rsp'])
        conf_date_list.append(row['DELIV_DATE_rsp'])
    else:
        total_conf_qtys = sum(row['CONF_QTY'])
        last_conf_qty = row['CONF_QTY'][-1]
        new_conf_qty = row['QUANTITY_rsp']
        order_qty = row['QUANTITY_ord']

        if order_qty == new_conf_qty:
            if len(conf_ser_list) == 0:
                conf_ser_list.append('0001')
                conf_qty_list.append(new_conf_qty)
                conf_date_list.append(row['DELIV_DATE_rsp'])
            else:
                conf_ser_list[-1] = '0001'
                conf_qty_list[-1] = new_conf_qty
                conf_date_list[-1] = row['DELIV_DATE_rsp']
        elif new_conf_qty + total_conf_qtys <= order_qty:
            conf_ser_list.append(str(int(max(conf_ser_list)) + 1).zfill(4))
            conf_qty_list.append(new_conf_qty)
            conf_date_list.append(row['DELIV_DATE_rsp'])
        elif (new_conf_qty == last_conf_qty) and (new_conf_qty + total_conf_qtys > order_qty):
            conf_ser_list[-1] = str(int(max(conf_ser_list))).zfill(4)
            conf_qty_list[-1] = new_conf_qty
            conf_date_list[-1] = row['DELIV_DATE_rsp']

    row['CONF_SER'] = conf_ser_list
    row['CONF_QTY'] = conf_qty_list
    row['CONF_DATE'] = conf_date_list
    return row