import config
import datetime


def filter_library_and_date_and_rfid(library=None, date=None, rfid=None, over=True):
    print('filter ', over)
    if date:
        date = date.strftime('%Y-%m-%d')
    filter = ''
    ands = 0
    if library or date or rfid:
        filter = 'where '
    if library:
        filter = filter + f"INV.T090F like '{library}%'"
        ands += 1
    if date:
        if ands > 0:
            filter = filter + ' and '
        if over:
            filter = filter + f"DATEINV >= '{date}'"
        else:
            filter = filter + f"(DATEINV < '{date}' or DATEINV is NULL)"
        ands += 1
    if rfid:
        if ands > 0:
            filter = filter + ' and '
        filter = filter + f"RFID='{rfid}'"
    return filter


def request_empty_inv(library=None):
    return f"""select distinct INV.DOC_ID, INV.INV_ID, INV.T090e, IDX100a.TERM, IDX245a.TERM, IDX260c.TERM, IDX090a.TERM, INV.T090F, INV.SOURCE, IDX500a.TERM
    from INV 
    join IDX100aX ON INV.DOC_ID = IDX100aX.DOC_ID 
    join IDX100a on IDX100a.IDX_ID = IDX100aX.IDX_ID
    join IDX245aX on INV.DOC_ID = IDX245aX.DOC_ID
    join IDX245a on IDX245a.IDX_ID = IDX245aX.IDX_ID
    join IDX260cX on INV.DOC_ID = IDX260cX.DOC_ID
    join IDX260c on IDX260c.IDX_ID = IDX260cX.IDX_ID
    join IDX090aX on INV.DOC_ID = IDX090aX.DOC_ID
    join IDX090a on IDX090a.IDX_ID = IDX090aX.IDX_ID
    join IDX500aX on INV.DOC_ID = IDX500aX.DOC_ID
    join IDX500a on IDX500a.IDX_ID = IDX500aX.IDX_ID
    where INV.T090F like '{config.FILIALS[library]}%' and
    T090e is null and
    INV.[SOURCE] not like '%подписка%'"""


def request_count_empty_inv(id):
    return f"""select count(*)
    from INV
    where DOC_ID = {id} and
    INV.T090e is not null"""


def request_all_empty_inv(id):
    return f"""select INV.INV_ID, INV.T090e, IDX100a.TERM, IDX245a.TERM, IDX260c.TERM, IDX090a.TERM, INV.T090F, INV.SOURCE, IDX500a.TERM
    from INV
    join IDX100aX ON INV.DOC_ID = IDX100aX.DOC_ID 
    join IDX100a on IDX100a.IDX_ID = IDX100aX.IDX_ID
    join IDX245aX on INV.DOC_ID = IDX245aX.DOC_ID
    join IDX245a on IDX245a.IDX_ID = IDX245aX.IDX_ID
    join IDX260cX on INV.DOC_ID = IDX260cX.DOC_ID
    join IDX260c on IDX260c.IDX_ID = IDX260cX.IDX_ID
    join IDX090aX on INV.DOC_ID = IDX090aX.DOC_ID
    join IDX090a on IDX090a.IDX_ID = IDX090aX.IDX_ID
    join IDX500aX on INV.DOC_ID = IDX500aX.DOC_ID
    join IDX500a on IDX500a.IDX_ID = IDX500aX.IDX_ID
    where INV.DOC_ID = {id}"""


def upload_dateinv_by_rfid(rfid):
    filter = filter_library_and_date_and_rfid(rfid=rfid)
    return f"""UPDATE inv SET dateinv = CONVERT (date, GETDATE()) 
    {filter}"""


def request_author(doc_id):
    return f"select TERM from IDX100a where IDX_ID = (select IDX_ID from IDX100aX where DOC_ID='{doc_id}')"


def request_book_by_t090f(library=None, date=None, rfid=None, over=True):
    if library:
        library = config.FILIALS[library]
    filter = filter_library_and_date_and_rfid(library, date, rfid, over)

    request = f"""select INV.T090e, IDX100a.TERM, IDX245a.TERM, IDX260c.TERM, IDX090a.TERM, INV.T090F, IDX500a.TERM, INV.DATEINV
    from INV
    join IDX100aX ON INV.DOC_ID = IDX100aX.DOC_ID 
    join IDX100a on IDX100a.IDX_ID = IDX100aX.IDX_ID
    join IDX245aX on INV.DOC_ID = IDX245aX.DOC_ID
    join IDX245a on IDX245a.IDX_ID = IDX245aX.IDX_ID
    join IDX260cX on INV.DOC_ID = IDX260cX.DOC_ID
    join IDX260c on IDX260c.IDX_ID = IDX260cX.IDX_ID
    join IDX090aX on INV.DOC_ID = IDX090aX.DOC_ID
    join IDX090a on IDX090a.IDX_ID = IDX090aX.IDX_ID
    join IDX500aX on INV.DOC_ID = IDX500aX.DOC_ID
    join IDX500a on IDX500a.IDX_ID = IDX500aX.IDX_ID
    {filter}"""
    return request


def request_count_book(library=None, date=None):
    library = config.FILIALS[library]
    filter = filter_library_and_date_and_rfid(library, date)

    request = f"""SELECT COUNT(*) 
    FROM inv 
    {filter}"""
    return request


def request_last_date_inv():
    # Запрос даты последней инвентаризации
    return f"""select top (1) DATEINV from INV order by DATEINV desc"""
