import os
import logging
from typing import Any, Type, Iterator, Tuple
from pyrfc import Connection, ConnectionParameters

logger = logging.getLogger(__name__)

def po_getdetail(sappconn: Type[Connection], po_number: str) -> dict:
    """Fetches purchase order details from SAP."""
    result = sappconn.call(
        'BAPI_PO_GETDETAIL',
        PURCHASEORDER=po_number,
        ITEMS='X',
        ACCOUNT_ASSIGNMENT='X',
        SCHEDULES='X',
        HISTORY='X',
        ITEM_TEXTS='X',
        HEADER_TEXTS='X',
        CONFIRMATIONS='X',
        SERVICE_TEXTS='X',
        EXTENSIONS='X',
    )
    return result

def po_getsalesmen(sapconn: Type[Connection], sales_order: str) -> str:
    """Fetches salesmen details for a given sales order."""
    query_table = 'VBAP'
    query_fields = [{'FIELDNAME': 'ERNAM'}]
    options = [{'TEXT': f"VBELN = '{sales_order}'"}]
    result = sapconn.call('RFC_READ_TABLE',
                          QUERY_TABLE=query_table,
                          FIELDS=query_fields,
                          OPTIONS=options
                          )
    return result['DATA'][0]['WA'] if result['DATA'] else None

def po_confirm(sapconn: Type[Connection], po_number: str, item: list, itemx: list, confirm: list, confirmx: list):
    """Confirms a purchase order in SAP."""
    try:
        result = sapconn.call(
            'ZWRAP_PO_CONFIRM',
            DOCUMENT_NO=po_number,
            #ITEM=item,
            #ITEMX=itemx,
            CONFIRMATION=confirm,
            CONFIRMATIONX=confirmx
        )
        return result
    except Exception as e:
        if 'DYNPRO_SEND_IN_BACKGROUND' in str(e):
            return {'RETURN': []}
        logger.exception("Failed to confirm purchase order")
        raise