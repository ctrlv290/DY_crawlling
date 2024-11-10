import time
import json
import datetime
from . import Market_Interface
from bs4 import BeautifulSoup

class Market_Interpark(Market_Interface.Market_Interface):
    def __init__(self, id, pw):
        super(Market_Interpark, self).__init__(id, pw)
        self.set_market_name("인터파크")

    def login(self):
        driver = self.get_webdriver()
        if (driver == None):
            return False

        driver.get("http://ipss.interpark.com/member/login.do?_method=initial&imfsUserPath=&imfsUserQuery=null&FromLogin=Y&str=null&logintgt=null")
        driver.implicitly_wait(3)

        driver.switch_to.frame(driver.find_element_by_xpath("//iframe[contains(@name, 'subIframe')]"))

        login_name = driver.find_element_by_name("sc.memId")
        login_name.send_keys(self.id)
        login_pw = driver.find_element_by_name("sc.pwd")
        login_pw.send_keys(self.pw)

        driver.find_element_by_class_name('btnRed').click()
        time.sleep(5)

        cookies = driver.get_cookies()

        for cookie in cookies:
            self.__session__.cookies.set(cookie['name'], cookie['value'])

        return True

    def get_product_order_list(self):
        to_dt = datetime.datetime.now()
        from_dt = to_dt + datetime.timedelta(days = -7)

        params = dict()
        params["sc.selectedOrderclmNo"] = ""
        params["sc.allRows"] = "true"
        params["sc.page"] = "0"
        params["sc.gridId"] = "list"
        params["sc.hdelvNo"] = "169168"
        if (self.get_market_name() == "인터파크 법인"):
            params["sc.entrNo"] = "3002821861"
        elif (self.get_market_name() == "인터파크 개인"):
            params["sc.entrNo"] = "3002806651"
        params["sc.supplyCtrtSeq"] = "1"
        params["sc.dateTp"] = "2"
        params["sc.strDt"] = from_dt.strftime("%Y%m%d")
        params["sc.strHour"] = "00"
        params["sc.endDt"] = to_dt.strftime("%Y%m%d")
        params["sc.endHour"] = "23"
        params["sc.searchTp"] = ""
        params["sc.searchNm"] = ""
        params["sc.clmreqStat"] = ""

        res = self.__session__.post("http://ipss.interpark.com/delivery/ProDeliveryCheckList.do?_method=excelDownForProduct&flag=ko", data = params)
        res.raise_for_status()

        res.encoding = None

        excel_data = BeautifulSoup(res.text, "html.parser")

        table = excel_data.select_one("body > table")
        if (table == None) : 
            print("html > body > table 이 존재하지 않습니다.")
            return None

        tr_list = table.select("tr")
        if (len(tr_list) == 0) :
            print("table에 tr tag가 존재하지 않습니다.")
            return None

        ord_list = list()
        ord_list_headers = list()

        for idx, tr in enumerate(tr_list):
            td_list = tr.select("td")
            if (len(td_list) == 0) :
                print("table > tr 에 td가 존재하지 않습니다.")
                return None
            
            if (idx == 0):
                for td in td_list:
                    ord_list_headers.append(td.string)
            else:
                ord_detail_list = dict()

                for idx_2, td in enumerate(td_list):
                    print(td.string)
                    ord_detail_list[ord_list_headers[idx_2]] = td.string

                ord_list.append(ord_detail_list)

        return ord_list