import json
import time
import datetime
from . import Market_Interface

class Market_11st(Market_Interface.Market_Interface):
    def __init__(self, id, pw):
        super(Market_11st, self).__init__(id, pw)
        self.set_market_name("11번가")

    def login(self):
        driver = self.get_webdriver()
        if (driver == None):
            return False

        driver.get("https://login.soffice.11st.co.kr/login/Login.page")
        driver.implicitly_wait(3)

        login_name = driver.find_element_by_name('loginName')
        login_name.send_keys(self.id)
        login_pw = driver.find_element_by_name('passWord')
        login_pw.send_keys(self.pw)

        driver.find_element_by_class_name('btn_Atype').click()
        time.sleep(3)

        cookies = driver.get_cookies()

        for cookie in cookies:
            self.__session__.cookies.set(cookie['name'], cookie['value'])

        return True

    def logout(self):
        driver = self.get_webdriver()
        if (driver == None):
            return False

        driver.delete_all_cookies()

        return True

    def get_product_order_list(self):
        to_dt = datetime.datetime.now()
        from_dt = to_dt + datetime.timedelta(days = -7)

        params = dict()
        params["addrSeq"] = ""
        params["gblRcvrBaseAddr"] = ""
        params["gblRcvrDtlsAddr"] = ""
        params["gblRcvrMailNo"] = "17382"
        params["gblRcvrNm"] = ""
        params["gblRcvrPrtblNo"] = ""
        params["gblRcvrTlphn"] = ""
        params["isAbrdSellerYn"] = ""
        params["isItalyAgencyYn"] = ""
        params["limit"] = 30
        params["prdNo"] = ""
        params["shBuyerText"] = "good"
        params["shBuyerType"] = ""
        params["shDateFrom"] = from_dt.strftime("%Y%m%d")
        params["shDateTo"] = to_dt.strftime("%Y%m%d")
        params["shDateType"] = "01"
        params["shDelay"] = ""
        params["shDelayReport"] = ""
        params["shDlvClfCd"] = ""
        params["shErrYN"] = ""
        params["shGblDlv"] = "ALL"
        params["shOrdLang"] = ""
        params["shOrderType"] = "on"
        params["shProductStat"] = "ALL"#301 배송완료 202 발주완료 ALL all
        params["shPurchaseConfirm"] = ""
        params["shStckNo"] = ""
        params["shToday"] = ""
        params["shUsimDlvYn"] = "N"
        params["shVisitDlvYn"] = "N"
        params["start"] = 0

        res = self.__session__.post("https://soffice.11st.co.kr/escrow/OrderingLogisticsAction.tmall?method=getOrderLogisticsList&listType=orderingLogistics", data = params)
        res.raise_for_status()

        res.encoding = None
        json_res = json.loads(res.text)

        if (int(json_res["totalCount"]) == 0):
            return None
        else:
            return json_res["orderingLogistics"]