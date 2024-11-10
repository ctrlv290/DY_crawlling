import logger
from classes import DBConn

def slt_settle_arr(dbc = DBConn, ord_data = list):
    if (dbc == None or len(ord_data) == 0):
        return None

    dbc.add_sql("SELECT order_idx, market_order_no, market_order_subno FROM DY_ORDER WHERE 1 = 0\n")

    for val in ord_data :
        dbc.add_sql(" OR (market_order_no = N'" + val["ORD_NO"] + "' AND market_order_subno = N'" + val["ORD_SUB_NO"] + "')\n")

    dbc.add_sql(";")
    
    cursor = dbc.cursor()
    print(dbc.get_sql())
    cursor.execute(dbc.get_sql())

    if (cursor.rowcount == 0) :
        logger.print("SQL QUERY : " + dbc.get_sql() + "\n해당 쿼리로 검색한 내용이 없습니다.")
        return None
    
    row = cursor.fetchone()

    selected_list = dict()

    while row:
        ord_idx = str(row[0])
        ord_num = str(row[1])
        ord_sub = str(row[2])

        #selected_list[ord_idx] = [ord_num, ord_sub]

        for val in ord_data :
            if ((val["ORD_NO"] == ord_num) and (val["ORD_SUB_NO"] == ord_sub)) :
                selected_list[ord_idx] = [ord_num, ord_sub, val["SEL_FEE_AMT"]]

        row = cursor.fetchone()

    dbc.set_sql("SELECT S.settle_idx\n")
    dbc.add_sql(", S.order_idx\n")
    dbc.add_sql(", S.order_pack_idx\n")
    dbc.add_sql(", S.order_unit_price\n")
    dbc.add_sql(", S.order_amt\n")
    dbc.add_sql(", S.order_cnt\n")
    dbc.add_sql(", S.product_option_sale_price\n")
    dbc.add_sql(", S.product_option_purchase_price\n")
    dbc.add_sql(", S.product_delivery_fee_sale\n")
    dbc.add_sql(", S.product_delivery_fee_buy\n")
    dbc.add_sql(", S.settle_sale_supply\n")
    dbc.add_sql(", S.settle_sale_supply_ex_vat\n")
    dbc.add_sql(", S.settle_sale_sum\n")
    dbc.add_sql(", S.settle_sale_commission_ex_vat\n")
    dbc.add_sql(", S.settle_sale_commission_in_vat\n")
    dbc.add_sql(", S.settle_delivery_ex_vat\n")
    dbc.add_sql(", S.settle_delivery_in_vat\n")
    dbc.add_sql(", S.settle_delivery_commission_ex_vat\n")
    dbc.add_sql(", S.settle_delivery_commission_in_vat\n")
    dbc.add_sql(", S.settle_purchase_supply\n")
    dbc.add_sql(", S.settle_purchase_supply_ex_vat\n")
    dbc.add_sql(", S.settle_purchase_delivery_ex_vat\n")
    dbc.add_sql(", S.settle_purchase_delivery_in_vat\n")
    dbc.add_sql(", S.settle_purchase_sum\n")
    dbc.add_sql(", S.settle_sale_profit\n")
    dbc.add_sql(", S.settle_sale_amount\n")
    dbc.add_sql(", S.settle_sale_cost\n")
    dbc.add_sql(", S.settle_purchase_unit_supply\n")
    dbc.add_sql(", S.settle_purchase_unit_supply_ex_vat\n")
    dbc.add_sql(", S.market_order_no\n")
    
    dbc.add_sql("FROM DY_SETTLE AS S\n")
    dbc.add_sql("WHERE settle_closing = N'N' AND settle_type = N'SHIPPED' AND settle_was_edited = N'N'")
    
    if (len(selected_list) > 0) :
        dbc.add_sql(" AND (\n")
        is_first = False

        for key, val in selected_list.items() :
            if (is_first) :
                dbc.add_sql(" OR ")
            else :
                is_first = True

            dbc.add_sql(" (order_idx = N'" + key + "' AND market_order_no = N'" + val[0] + "')\n")

        dbc.add_sql(")")

    dbc.add_sql(";")

    cursor = dbc.cursor()
    print(dbc.get_sql())
    cursor.execute(dbc.get_sql())

    if (cursor.rowcount == 0) :
        logger.print("SQL QUERY : " + dbc.get_sql() + "\n해당 쿼리로 검색한 내용이 없습니다.")
        return None
    
    settle_selected_list = list()

    row = cursor.fetchone()
    while row:
        settle_one = list(row)
        print(row)

        for key, val in selected_list.items() :
            if (str(settle_one[1]) == key and settle_one[29] == val[0]) :
                settle_one.append(val[1])
                settle_one.append(val[2])
                settle_selected_list.append(settle_one)
        
        row = cursor.fetchone()

    return settle_selected_list

def upt_scheduled_payment(dbc = DBConn, settle_list = list, ord_data = list, is_dev = bool):
    if (dbc == None or len(settle_list) == 0):
        return False

    count = 0
    cursor = dbc.cursor()

    for row in settle_list :
        settle = dict()

        settle["settle_idx"] = str(row[0])
        settle["order_idx"] = str(row[1])
        settle["order_pack_idx"] = str(row[2])

        settle["order_unit_price"] = row[3]
        settle["order_amt"] = row[4]
        settle["order_cnt"] = row[5]

        settle["product_option_sale_price"] = row[6]
        settle["product_option_purchase_price"] = row[7]
        settle["product_delivery_fee_sale"] = row[8]
        settle["product_delivery_fee_buy"] = row[9]

        settle["settle_sale_supply"] = row[10]
        settle["settle_sale_supply_ex_vat"] = row[11]

        if (row[13] == 0) :
            if (len(row) != 32) :
                print("error")
                return False
            else :
                settle["settle_sale_commission_ex_vat"] = settle["settle_sale_supply"] - int(row[31])
                settle["settle_sale_commission_in_vat"] = round(1.1 * settle["settle_sale_commission_ex_vat"])
        else :
            logger.print(str(row[0]) + " : 에 이미 수수료가 있습니다. 수수료 : " + str(row[13]))
            continue

        settle["settle_delivery_ex_vat"] = row[15]
        settle["settle_delivery_in_vat"] = row[16]

        settle["settle_delivery_commission_ex_vat"] = row[17]
        settle["settle_delivery_commission_in_vat"] = row[18]

        settle["settle_sale_sum"] = settle["settle_sale_supply"] - settle["settle_sale_commission_in_vat"] + settle["settle_delivery_in_vat"] - settle["settle_delivery_commission_in_vat"]

        settle["settle_purchase_unit_supply"] = row[27]
        settle["settle_purchase_unit_supply_ex_vat"] = row[28]

        settle["settle_purchase_supply"] = row[19]
        settle["settle_purchase_supply_ex_vat"] = row[20]

        settle["settle_purchase_delivery_ex_vat"] = row[21]
        settle["settle_purchase_delivery_in_vat"] = row[22]

        settle["settle_purchase_sum"] = settle["settle_purchase_supply"] + settle["settle_purchase_delivery_in_vat"]

        settle["settle_sale_profit"] = settle["settle_sale_supply_ex_vat"] - settle["settle_sale_commission_ex_vat"] + settle["settle_delivery_ex_vat"] - settle["settle_delivery_commission_ex_vat"] - settle["settle_purchase_supply_ex_vat"] - settle["settle_purchase_delivery_ex_vat"]

        settle["settle_sale_amount"] = settle["settle_sale_supply"] + settle["settle_delivery_in_vat"] - settle["settle_sale_commission_ex_vat"] - settle["settle_delivery_commission_ex_vat"]
        settle["settle_sale_cost"] = settle["settle_purchase_supply_ex_vat"] + settle["settle_purchase_delivery_ex_vat"]

        dbc.set_sql("UPDATE DY_SETTLE\n")
        dbc.add_sql("SET\n")
        dbc.add_sql("settle_sale_commission_ex_vat = " + str(settle["settle_sale_commission_ex_vat"]) + "\n")
        dbc.add_sql(", settle_sale_commission_in_vat = " + str(settle["settle_sale_commission_in_vat"]) + "\n")
        dbc.add_sql(", settle_sale_sum = " + str(settle["settle_sale_sum"]) + "\n")
        dbc.add_sql(", settle_sale_profit = " + str(settle["settle_sale_profit"]) + "\n")
        dbc.add_sql(", settle_sale_amount = " + str(settle["settle_sale_amount"]) + "\n")
        dbc.add_sql(", settle_sale_cost = " + str(settle["settle_sale_cost"]) + "\n")
        dbc.add_sql("WHERE settle_idx = N'" + settle["settle_idx"] + "'")

        print(dbc.get_sql())
        if (not is_dev) :
            cursor.execute(dbc.get_sql())
        count += 1

    logger.print("총 " + str(count) + "개의 주문의 정산예정금을 업데이트 하였습니다.")
    
    if (not is_dev) :
        dbc.commit()

    return True