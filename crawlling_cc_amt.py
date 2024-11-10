import os
import sys
import json
import enum
import datetime
import logger

from classes import DBConn
from classes import Market_Interface
from classes import Market_11st
from classes import Market_Interpark

import dyflux_helper

g_cfg = None
g_is_debug = True
g_driver_path = ""

def set_order_data_from_market(input = list, output = list, market_name = str):
    if (len(input) == 0 or output == None):
        return False

    if ("11번가" in market_name):
        logger.print(market_name + " 수신 데이터")

        for logis in input :
            out_ord = dict()
            out_ord["ORD_NO"] = str(logis["ORD_NO"])
            out_ord["ORD_SUB_NO"] = str(logis["ORD_PRD_SEQ"])
            out_ord["SEL_FEE_AMT"] = str(int(logis["SEL_FEE_AMT"].replace(",","")) - int(logis["REAL_LST_DLV_CST"].replace(",","")))

            output.append(out_ord)

            logger.print("주문번호 : " + out_ord["ORD_NO"] + ", 상품순번 : " + out_ord["ORD_SUB_NO"] + ", 정산예정금 : " + out_ord["SEL_FEE_AMT"])
    elif ("인터파크" in market_name):
        logger.print(market_name + " 수신 데이터")

        for v in input :
            out_ord = dict()
            out_ord["ORD_NO"] = str(v["주문번호"])
            out_ord["ORD_SUB_NO"] = str(v["주문순번"])
            out_ord["SEL_FEE_AMT"] = str(int(v["실제주문금액"].replace(".0","")) - int(v["기본판매수수료"].replace(".0","")))

            output.append(out_ord)

            logger.print("주문번호 : " + out_ord["ORD_NO"] + ", 상품순번 : " + out_ord["ORD_SUB_NO"] + ", 정산예정금 : " + out_ord["SEL_FEE_AMT"])
        pass
    else:
        print("마켓 이름이 올바르지 않습니다.")

    return True

def market_login_and_get_ord_list(market = Market_Interface, output = list):
    rst = market.login()
    if (rst == False):
        logger.print(market.get_market_name() + " - 로그인하지 못했습니다. 개발자에게 문의해주세요.")
        sys.exit()

    rst = market.get_product_order_list()
    if (rst == None):
        logger.print(market.get_market_name() + " 배송 완료 주문이 존재하지 않습니다.")
    else:
        set_order_data_from_market(rst, output, market.get_market_name())

def init():
    global g_cfg
    global g_is_debug
    global g_driver_path

    if getattr(sys, 'frozen', False):
        application_path = os.path.dirname(sys.executable)
    elif __file__:
        application_path = os.path.dirname(__file__)

    config_path = os.path.join(application_path, "config.json")

    if (not os.path.isfile(config_path)):
        print(config_path + " 설정 파일이 존재하지 않습니다.")
        sys.exit()

    g_cfg = json.load(open(config_path, "r", encoding="UTF-8"))
    g_is_debug = bool(g_cfg["debug"])

    log_path = os.path.join(application_path, g_cfg["logfile"])

    rst = logger.init(log_path)
    if (not rst):
        print("로그 파일이 존재하지 않습니다.")
        sys.exit()
    global g_driver_path
    g_driver_path = os.path.join(application_path, "chromedriver.exe")

    if (not os.path.isfile(g_driver_path)):
        print(g_driver_path + " 웹 드라이버 파일이 존재하지 않습니다.")
        sys.exit()

    logger.print("############### " + datetime.datetime.today().strftime("%Y%m%d-%H:%M") + " ###############")

##init
init()

##data
ord_data = list()

for market_data in g_cfg["markets"]:
    market = None

    if (market_data["yn"] == 1):
        if (market_data["tp"] == 1):
            market = Market_11st.Market_11st(market_data["id"], market_data["pw"])
        elif (market_data["tp"] == 2):
            market = Market_Interpark.Market_Interpark(market_data["id"], market_data["pw"])

        market.set_market_name(market_data["name"])
        market.set_driver_file(g_driver_path)
        market_login_and_get_ord_list(market, ord_data)

        market.close_webdriver()

dbc = DBConn.DBConn(srv = 'www.dyflux.co.kr', id = 'sa', pw = 'd!@#y!@#', port = '14353', db = 'DYFLUX_dy')
dbc.connect()

ord_state_list = dyflux_helper.slt_settle_arr(dbc, ord_data)
if (ord_state_list != None):
    if (len(ord_state_list) == 0):
        print("발주 상태에 주문이 없습니다.\n")
        logger.print("발주 상태에 주문이 없습니다.")
    else :
        udt_rst = dyflux_helper.upt_scheduled_payment(dbc, ord_state_list, ord_data, g_is_debug)
        if (not udt_rst):
            print("db update fail.\n")
            logger.print("발주 상태에 주문이 확인되었지만, 해당 내용을 데이터베이스에 업데이트 하지 못했습니다. 개발자에게 문의주세요.")

dbc.close()

logger.print("############### " + datetime.datetime.today().strftime("%Y%m%d-%H:%M") + " ###############\n")
logger.end()