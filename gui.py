from PyQt5 import QtCore, QtGui, QtWidgets, uic
import psycopg2,sqlalchemy,sys,hashlib
from pprint import pprint
import pandas as pd

def main():

    class MyWindow(QtWidgets.QMainWindow):
        def __init__(self):
            super().__init__()
            uic.loadUi('example.ui',self)
            
            self.p = {
            'path_candle_file': None, # VARCHAR(80)
            'timeframe_start': None, # TIMESTAMP
            'timeframe_end': None, # TIMESTAMP
            'candle_sec': None, # INTEGER
            'path_historical_data' : None, # VARCHAR(80)
            'buy': None, # VARCHAR(40)
            'sell': None, # VARCHAR(40)
            'filter': None, # VARCHAR(20)
            'f1_above_path_candle_file': None, # VARCHAR(80)
            'f1_above_indicator': None, # VARCHAR(3)
            'f1_above_average': None, # INTEGER
            'f1_below_path_candle_file': None, # VARCHAR(80)
            'f1_below_indicator': None, # VARCHAR(3)
            'f1_below_average': None, # INTEGER
            'pattern': None, # VARCHAR(20)
            'p1_threshold' : None,  # INTEGER
            'p2_td_s': None, # INTEGER
            'p3_td_c': None, # INTEGER
            "p4_shorter_rsi": None,
            "p4_longer_rsi_max": None,
            "p4_longer_rsi_min": None,
            "p4_longer_path_candle_file": None,
            # -------------
            'max_order': None, # INTEGER
            'space': None, # REAL
            'last_price_approach': None, # VARCHAR(20)
            'percentile_last_price': None, # INTEGER
            # -------------
            'games': None, # INTEGER
            'samples': None, # INTEGER
            'bag_percentage': None, # REAL
            'initial_bag': None, # REAL
            'market_order': None, # REAL
            'limit_order': None # REAL
            }

            self.setWindowTitle('Input interface')
            self.B_add_case.clicked.connect(self.click_B_add_case)
            self.E_percentile_last_price.hide()
            
            # Assigning events to QCheckBoxes and QListWidgets.
            self.LI_pattern.itemClicked.connect(self.click_LI_pattern)            
            self.LI_filter.itemClicked.connect(self.click_LI_filter)            
            self.LI_last_price_approach.itemClicked.connect(self.click_LI_last_price_approach)            
            
            # The two static functions below will create the QLineEdits and QLabels for each pattern and filter.
            self.patternBox()
            self.filterBox()
            self.last_price_approachBox()

            # In order to don't waste time typing many times the same inputs on the GUI, I will add them by default while testing the program.
            self.E_path_candle_file.setText("builders/warehouse/candle_data/30min_bitstamp.csv")
            self.E_timeframe_start.setText("2014-01-01 00:00:00")
            self.E_timeframe_end.setText("2018-04-19 00:00:00")
            self.E_candle_sec.setText("1800")
            self.E_buy.setText("1-sellEnd_1open*1.0001")
            self.E_sell.setText("buy-10_realhighest")
            self.E_path_historical_data.setText("builders/warehouse/historical_data/bitstampUSD.csv")
            self.E_initial_bag.setText("10000")
            self.E_market_order.setText("-0.00075")
            self.E_limit_order.setText("0.00025")
            self.E_bag_percentage.setText("1")
            self.E_games.setText("25")
            self.E_max_order.setText("500")
            self.E_samples.setText("50")
            self.E_space.setText("0.02")
            self.E_p1_threshold.setText("30")

        def last_price_approachBox(self):
            # Setting the default values. LI_last_price_approach will have the item average selected as default, E_percentile_last_price will
            # be hidden and self.p["last_price_approach"] will be set to "average".    
            self.LI_last_price_approach.setCurrentRow(0)
            self.E_percentile_last_price.hide()
            self.p["last_price_approach"] = "average"

        def filterBox(self):

            # Create the lables for patterns.
            self.L_f1_above_path_candle_file = QtWidgets.QLabel('f1_above_path_candle_file',self)
            self.L_f1_above_indicator = QtWidgets.QLabel('f1_above_indicator',self)
            self.L_f1_above_average = QtWidgets.QLabel('f1_above_average',self)
            self.L_f1_below_path_candle_file = QtWidgets.QLabel('f1_below_path_candle_file',self)
            self.L_f1_below_indicator = QtWidgets.QLabel('f1_below_indicator',self)
            self.L_f1_below_average = QtWidgets.QLabel('f1_below_average',self)

            # Create the lineEdits for patterns.
            self.E_f1_above_path_candle_file = QtWidgets.QLineEdit(self)
            self.E_f1_above_indicator = QtWidgets.QLineEdit(self)
            self.E_f1_above_average = QtWidgets.QLineEdit(self)
            self.E_f1_below_path_candle_file = QtWidgets.QLineEdit(self)
            self.E_f1_below_indicator = QtWidgets.QLineEdit(self)
            self.E_f1_below_average = QtWidgets.QLineEdit(self)

            # Creating variable containing font configuration.
            newFont = QtGui.QFont('MS Shell Dlg 2',12) 
            
            # Adding the configuration to the pattern labels.
            self.L_f1_above_path_candle_file.setFont(newFont)
            self.L_f1_above_indicator.setFont(newFont)
            self.L_f1_above_average.setFont(newFont)
            self.L_f1_below_path_candle_file.setFont(newFont)
            self.L_f1_below_indicator.setFont(newFont)
            self.L_f1_below_average.setFont(newFont)

            # Positioning the labels.
            self.L_f1_above_path_candle_file.setGeometry(750,280,200,25)
            self.L_f1_above_indicator.setGeometry(750,313,200,25)
            self.L_f1_above_average.setGeometry(750,346,200,25)
            self.L_f1_below_path_candle_file.setGeometry(750,379,200,25)
            self.L_f1_below_indicator.setGeometry(750,412,200,25)
            self.L_f1_below_average.setGeometry(750,445,200,25)

            # Positioning the lineEdits.
            self.E_f1_above_path_candle_file.setGeometry(970,280,431,25)
            self.E_f1_above_indicator.setGeometry(970,313,431,25)
            self.E_f1_above_average.setGeometry(970,346,431,25)
            self.E_f1_below_path_candle_file.setGeometry(970,379,431,25)
            self.E_f1_below_indicator.setGeometry(970,412,431,25)   
            self.E_f1_below_average.setGeometry(970,445,431,25)

            # Hidding all the widgets made in the function.
            self.L_f1_above_path_candle_file.hide()
            self.L_f1_above_indicator.hide()
            self.L_f1_above_average.hide()
            self.L_f1_below_path_candle_file.hide()
            self.L_f1_below_indicator.hide()
            self.L_f1_below_average.hide()
            self.E_f1_above_path_candle_file.hide()
            self.E_f1_above_indicator.hide()
            self.E_f1_above_average.hide()
            self.E_f1_below_path_candle_file.hide()
            self.E_f1_below_indicator.hide()
            self.E_f1_below_average.hide()

            # The item "none" will be selected by default.
            self.LI_filter.setCurrentRow(0)
            self.p["filter"] == "none"

        def patternBox(self):

            # Create the lables for patterns.
            self.L_p1_threshold = QtWidgets.QLabel('p1_threshold',self)
            self.L_p2_td_s = QtWidgets.QLabel('p2_td_s',self)
            self.L_p3_td_c = QtWidgets.QLabel('p3_td_c',self)
            self.L_p4_shorter_rsi = QtWidgets.QLabel('p4_shorter_rsi',self)
            self.L_p4_longer_rsi_max = QtWidgets.QLabel('p4_longer_rsi_max',self)
            self.L_p4_longer_rsi_min = QtWidgets.QLabel('p4_longer_rsi_min',self)
            self.L_p4_longer_path_candle_file = QtWidgets.QLabel('p4_longer_path_candle_file',self)

            # Create the lineEdits for patterns.
            self.E_p1_threshold = QtWidgets.QLineEdit(self)
            self.E_p2_td_s = QtWidgets.QLineEdit(self)
            self.E_p3_td_c = QtWidgets.QLineEdit(self)
            self.E_p4_shorter_rsi = QtWidgets.QLineEdit(self)
            self.E_p4_longer_rsi_max = QtWidgets.QLineEdit(self)
            self.E_p4_longer_rsi_min = QtWidgets.QLineEdit(self)
            self.E_p4_longer_path_candle_file = QtWidgets.QLineEdit(self)

            # Creating variable containing font configuration.
            newFont = QtGui.QFont('MS Shell Dlg 2',12) 
            
            # Adding the configuration to the pattern labels.
            self.L_p1_threshold.setFont(newFont)
            self.L_p2_td_s.setFont(newFont)
            self.L_p3_td_c.setFont(newFont)
            self.L_p4_shorter_rsi.setFont(newFont)
            self.L_p4_longer_rsi_max.setFont(newFont)
            self.L_p4_longer_rsi_min.setFont(newFont)
            self.L_p4_longer_path_candle_file.setFont(newFont)

            # Positioning the labels.
            self.L_p1_threshold.setGeometry(750,20,200,25)
            self.L_p2_td_s.setGeometry(750,20,200,25)
            self.L_p3_td_c.setGeometry(750,20,200,25)
            self.L_p4_shorter_rsi.setGeometry(750,20,200,25)
            self.L_p4_longer_rsi_max.setGeometry(750,53,200,25)
            self.L_p4_longer_rsi_min.setGeometry(750,86,200,25)
            self.L_p4_longer_path_candle_file.setGeometry(750,119,200,25)

            # Positioning the lineEdits.
            self.E_p1_threshold.setGeometry(870,20,100,25)
            self.E_p2_td_s.setGeometry(870,20,100,25)
            self.E_p3_td_c.setGeometry(870,20,100,25)
            self.E_p4_shorter_rsi.setGeometry(970,20,431,25)
            self.E_p4_longer_rsi_max.setGeometry(970,53,431,25)
            self.E_p4_longer_rsi_min.setGeometry(970,86,431,25)
            self.E_p4_longer_path_candle_file.setGeometry(970,119,431,25)

            # Hidding all the widgets made in the function.
            self.L_p1_threshold.hide()
            self.L_p2_td_s.hide()
            self.L_p3_td_c.hide()
            self.L_p4_shorter_rsi.hide()
            self.L_p4_longer_rsi_max.hide()
            self.L_p4_longer_rsi_min.hide()
            self.L_p4_longer_path_candle_file.hide()
            self.E_p1_threshold.hide()
            self.E_p2_td_s.hide()
            self.E_p3_td_c.hide()
            self.E_p4_shorter_rsi.hide()
            self.E_p4_longer_rsi_max.hide()
            self.E_p4_longer_rsi_min.hide()
            self.E_p4_longer_path_candle_file.hide()

            # The item 'pattern1' in the ListWidget will be selected by default, L_p1_threshold and 
            # E_p1_threshold will be visible, and value 'pattern1' will be assigned to p['pattern'].
            self.LI_pattern.setCurrentRow(0)
            self.L_p1_threshold.show()
            self.E_p1_threshold.show()
            self.p['pattern'] = 'pattern1'
            
        def click_LI_filter(self,item):
            if item.text() == 'none':
                self.L_f1_above_path_candle_file.hide()
                self.L_f1_above_indicator.hide()
                self.L_f1_above_average.hide()
                self.L_f1_below_path_candle_file.hide()
                self.L_f1_below_indicator.hide()
                self.L_f1_below_average.hide()
                self.E_f1_above_path_candle_file.hide()
                self.E_f1_above_indicator.hide()
                self.E_f1_above_average.hide()
                self.E_f1_below_path_candle_file.hide()
                self.E_f1_below_indicator.hide()
                self.E_f1_below_average.hide()
                self.p['filter'] = None
                self.E_f1_above_path_candle_file.setText("")
                self.E_f1_above_indicator.setText("")
                self.E_f1_above_average.setText("")
                self.E_f1_below_path_candle_file.setText("")
                self.E_f1_below_indicator.setText("")
                self.E_f1_below_average.setText("")
            if item.text() == 'filter1':
                self.L_f1_above_path_candle_file.show()
                self.L_f1_above_indicator.show()
                self.L_f1_above_average.show()
                self.L_f1_below_path_candle_file.show()
                self.L_f1_below_indicator.show()
                self.L_f1_below_average.show()
                self.E_f1_above_path_candle_file.show()
                self.E_f1_above_indicator.show()
                self.E_f1_above_average.show()
                self.E_f1_below_path_candle_file.show()
                self.E_f1_below_indicator.show()
                self.E_f1_below_average.show()
                self.p['filter'] = 'filter1'

        def click_LI_pattern(self,item):
            if item.text() == 'pattern1':
                self.L_p1_threshold.show()
                self.E_p1_threshold.show()
                self.L_p2_td_s.hide()
                self.E_p2_td_s.hide()
                self.L_p3_td_c.hide()
                self.E_p3_td_c.hide()
                self.L_p4_shorter_rsi.hide()
                self.E_p4_shorter_rsi.hide()
                self.L_p4_longer_rsi_max.hide()
                self.E_p4_longer_rsi_max.hide()
                self.L_p4_longer_rsi_min.hide()
                self.E_p4_longer_rsi_min.hide()
                self.L_p4_longer_path_candle_file.hide()
                self.E_p4_longer_path_candle_file.hide()
                self.p['pattern'] = 'pattern1'
                self.E_p2_td_s.setText("")
                self.E_p3_td_c.setText("")
                self.E_p4_shorter_rsi.setText("")
                self.E_p4_longer_rsi_max.setText("")
                self.E_p4_longer_rsi_min.setText("")
                self.E_p4_longer_path_candle_file.setText("")
            if item.text() == 'pattern2':
                self.L_p1_threshold.hide()
                self.E_p1_threshold.hide()
                self.L_p2_td_s.show()
                self.E_p2_td_s.show()
                self.L_p3_td_c.hide()
                self.E_p3_td_c.hide()
                self.L_p4_shorter_rsi.hide()
                self.E_p4_shorter_rsi.hide()
                self.L_p4_longer_rsi_max.hide()
                self.E_p4_longer_rsi_max.hide()
                self.L_p4_longer_rsi_min.hide()
                self.E_p4_longer_rsi_min.hide()
                self.L_p4_longer_path_candle_file.hide()
                self.E_p4_longer_path_candle_file.hide()
                self.p['pattern'] = 'pattern2'
                self.E_p1_threshold.setText("")
                self.E_p3_td_c.setText("")
                self.E_p4_shorter_rsi.setText("")
                self.E_p4_longer_rsi_max.setText("")
                self.E_p4_longer_rsi_min.setText("")
                self.E_p4_longer_path_candle_file.setText("")
            if item.text() == 'pattern3':
                self.L_p1_threshold.hide()
                self.E_p1_threshold.hide()
                self.L_p2_td_s.hide()
                self.E_p2_td_s.hide()
                self.L_p3_td_c.show()
                self.E_p3_td_c.show()
                self.L_p4_shorter_rsi.hide()
                self.E_p4_shorter_rsi.hide()
                self.L_p4_longer_rsi_max.hide()
                self.E_p4_longer_rsi_max.hide()
                self.L_p4_longer_rsi_min.hide()
                self.E_p4_longer_rsi_min.hide()
                self.L_p4_longer_path_candle_file.hide()
                self.E_p4_longer_path_candle_file.hide()
                self.p['pattern'] = 'pattern3'
                self.E_p1_threshold.setText("")
                self.E_p2_td_s.setText("")
                self.E_p4_shorter_rsi.setText("")
                self.E_p4_longer_rsi_max.setText("")
                self.E_p4_longer_rsi_min.setText("")
                self.E_p4_longer_path_candle_file.setText("")
            if item.text() == 'pattern4':
                self.L_p1_threshold.hide()
                self.E_p1_threshold.hide()
                self.L_p2_td_s.hide()
                self.E_p2_td_s.hide()
                self.L_p3_td_c.hide()
                self.E_p3_td_c.hide()
                self.L_p4_shorter_rsi.show()
                self.E_p4_shorter_rsi.show()
                self.L_p4_longer_rsi_max.show()
                self.E_p4_longer_rsi_max.show()
                self.L_p4_longer_rsi_min.show()
                self.E_p4_longer_rsi_min.show()
                self.L_p4_longer_path_candle_file.show()
                self.E_p4_longer_path_candle_file.show()
                self.p['pattern'] = 'pattern4'
                self.E_p1_threshold.setText("")
                self.E_p2_td_s.setText("")
                self.E_p3_td_c.setText("")

        def click_LI_last_price_approach(self,item):
            if item.text() == "average":
                self.E_percentile_last_price.hide()
                self.E_percentile_last_price.setText("") 
                self.p["last_price_approach"] = "average"
            if item.text() == "percentile":
                self.E_percentile_last_price.show()
                self.p["last_price_approach"] = "percentile"

        def click_B_add_case(self):
            
            def find_phs(p):
            # It receives the p dictionary and gives back ph1, ph2 and ph3.
                ph1_dict = {}
                ph2_dict = {}
                ph3_dict = {}
                for item in p: 
                    if item not in ["space","percentile_last_price","last_price_approach","games","samples","bag_percentage","initial_bag","market_order","limit_order"]:
                        ph1_dict[item] = p[item]
                for item in p: 
                    if item not in ["games","samples","bag_percentage","initial_bag","market_order","limit_order"]:
                        ph2_dict[item] = p[item]
                for item in p: 
                    ph3_dict[item] = p[item]

                ph1 = encrypt_string(dict2str(ph1_dict))
                ph2 = encrypt_string(dict2str(ph2_dict))
                ph3 = encrypt_string(dict2str(ph3_dict))
                return ph1,ph2,ph3

            def insertCase(p):
                dbname = 'postgres'
                user = 'postgres'
                host = 'localhost'
                password = 'DarkZuoqson-postgresql32229751!'
                conn = psycopg2.connect(host=host,dbname=dbname,user=user,password=password)
                c = conn.cursor()
                c.execute(
                    """
                INSERT INTO cases (path_candle_file,timeframe_start,timeframe_end,candle_sec,path_historical_data,buy,sell,filter,f1_above_path_candle_file,f1_above_indicator,f1_above_average,f1_below_path_candle_file,f1_below_indicator,f1_below_average,pattern,p1_threshold,p2_td_s,p3_td_c,p4_shorter_rsi,p4_longer_rsi_max,p4_longer_rsi_min,p4_longer_path_candle_file,max_order,space,last_price_approach,percentile_last_price,games,samples,bag_percentage,initial_bag,market_order,limit_order,ph1,ph2,ph3,state) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING case_id
                    """,(
                    p['path_candle_file'], # VARCHAR(80)
                    p['timeframe_start'], # TIMESTAMP
                    p['timeframe_end'], # TIMESTAMP
                    p['candle_sec'], # INTEGER
                    p['path_historical_data'], # VARCHAR(80)
                    p['buy'], # VARCHAR(40)
                    p['sell'], # VARCHAR(40)
                    p['filter'], # VARCHAR(20)
                    p['f1_above_path_candle_file'], # VARCHAR(80)
                    p['f1_above_indicator'], # VARCHAR(3)
                    p['f1_above_average'], # INTEGER
                    p['f1_below_path_candle_file'], # VARCHAR(80)
                    p['f1_below_indicator'], # VARCHAR(3)
                    p['f1_below_average'], # INTEGER   
                    p['pattern'], # VARCHAR(20)
                    p['p1_threshold'], # INTEGER
                    p['p2_td_s'], # INTEGER
                    p['p3_td_c'], # INTEGER
                    p["p4_shorter_rsi"], # INTEGER
                    p["p4_longer_rsi_max"], # INTEGER
                    p["p4_longer_rsi_min"], # INTEGER
                    p["p4_longer_path_candle_file"], # VARCHAR(80)
                    p['max_order'], # INTEGER
                    p['space'], # REAL
                    p['last_price_approach'], # VARCHAR(20)
                    p['percentile_last_price'], # INTEGER
                    p['games'], # INTEGER
                    p['samples'], # INTEGER
                    p['bag_percentage'], # REAL
                    p['initial_bag'], # REAL
                    p['market_order'], # REAL
                    p['limit_order'], # REAL
                    ph1,
                    ph2,
                    ph3,
                    'ph0'
                    ) 
                )
                query = c.fetchone()
                QtWidgets.QMessageBox.about(self,"SUCCESSFUL INSERTION","The id of the new case is {}.".format(query[0]))
                conn.commit()

            def inputChecking(self):
                # Check if the user inserted all the parameters required.
                # Firstly it checks if there is any empty qLineEdit.  
                missingList = []
                keys1 = [i for i in list(self.p) if i not in ["p4_longer_path_candle_file","p4_longer_rsi_min","p4_longer_rsi_max","p4_shorter_rsi","filter","pattern","last_price_approach","percentile_last_price","p1_threshold","p2_td_s","p3_td_c","f1_above_path_candle_file","f1_above_indicator","f1_above_average","f1_below_path_candle_file","f1_below_indicator","f1_below_average"]]
                for key in keys1:
                    if len(getattr(self, 'E_' + key).text()) == 0:
                        missingList.append(key)
                # Secondly it checks if the parameters for the pattern chosen were inserted.
                if self.p["pattern"] == "pattern1":
                    if len(self.E_p1_threshold.text()) == 0:
                        missingList.append("p1_threshold")
                if self.p["pattern"] == "pattern2":
                    if len(self.E_p2_td_s.text()) == 0:
                        missingList.append("p2_td_s")
                if self.p["pattern"] == "pattern3":
                    if len(self.E_p3_td_c.text()) == 0:
                        missingList.append("p3_td_c")
                if self.p["pattern"] == "pattern4":
                    if len(self.E_p4_shorter_rsi.text()) == 0:
                        missingList.append("p4_shorter_rsi")
                    if len(self.E_p4_longer_rsi_max.text()) == 0:
                        missingList.append("p4_longer_rsi_max")
                    if len(self.E_p4_longer_rsi_min.text()) == 0:
                        missingList.append("p4_longer_rsi_min")
                    if len(self.E_p4_longer_path_candle_file.text()) == 0:
                        missingList.append("p4_longer_path_candle_file")
                # Thirdly it checks if the parameters for the filter chosen were inserted.
                if self.p["filter"] == "filter1":
                    if len(self.E_f1_above_path_candle_file.text()) == 0: 
                        missingList.append("f1_above_path_candle_file")
                    if len(self.E_f1_above_indicator.text()) == 0:
                        missingList.append("f1_above_indicator")
                    if len(self.E_f1_above_average.text()) == 0:
                        missingList.append("f1_above_average")
                    if len(self.E_f1_below_path_candle_file.text()) == 0: 
                        missingList.append("f1_below_path_candle_file")
                    if len(self.E_f1_below_indicator.text()) == 0:
                        missingList.append("f1_below_indicator")
                    if len(self.E_f1_below_average.text()) == 0:
                        missingList.append("f1_below_average")
                # Fourthly it checks if the E_percentile_last_price value was given in case C_percentile_toggle is checked.
                if self.p["last_price_approach"] == "percentile":
                    if len(self.E_percentile_last_price.text()) == 0:
                        missingList.append("percentile_last_price")
                return missingList
            
            def repeatedCase(ph3):
                # The function returns a boolean object with the value True whether there is already an equal case in the table "cases"
                # and False if the case is new to it.
                dbname = 'postgres'
                user = 'postgres'
                host = 'localhost'
                password = 'DarkZuoqson-postgresql32229751!'
                conn = psycopg2.connect(host=host,dbname=dbname,user=user,password=password)
                c = conn.cursor()

                c.execute(
                    "SELECT case_id FROM cases WHERE ph3 = '{}'".format(ph3) 
                )
                query = c.fetchone()
                if query == None:
                    return False
                else:   
                    QtWidgets.QMessageBox.about(self,"ERROR: Such case already exist.","The current case is equal to case with case_id {}.".format(query[0]))
                    return True
                
            # Finding missingList, which is a list containing all the QLineEdits that should have been filled but
            # were not. 
            missingList = inputChecking(self)

            # In case there is any item in missingList, meaning that there is some parameter that was not given 
            # by the user, the program will create a pop up window telling which of the parameters are missing.
            if len(missingList) != 0:
                QtWidgets.QMessageBox.about(self,"ERROR: Missing Parameter","{}\n{}".format("The following parameters are missing:\n",list2str(missingList)))
            # In case missingList is empty, meaning the user has given all the parameters required, the program
            # will insert the case into the database.   
            else:
                # In order to insert new data into the database, the program first updates self.p.
                for key in [item for item in self.p if item not in ["pattern","filter","last_price_approach"]]:
                    given_value = getattr(self, 'E_' + key).text()
                    if given_value == "":
                        self.p[key] = None
                    else:
                        self.p[key] = getattr(self, 'E_' + key).text()

                # Finding ph1, ph2 and ph3.
                ph1,ph2,ph3 = find_phs(self.p)
                # Before inserting the case into the table "cases" we must check whether there is already an equal case in there.
                if repeatedCase(ph3):
                    pass
                else:
                    # Inserting the case as a new row into the table "cases".
                    insertCase(self.p)

    app = QtWidgets.QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec_())

def sort_dict(dct):
    # It returns a dictionary sorted alphabetically.
    keys = sorted(list(dct))
    return {item:dct[item] for item in keys}

def dict2str(dct):
    # It returns a srting object with the values of the dictionary's keys concateneted. The keys are in alphabetical order.
    # If the value is the object None it will be converted to the string object "None".
    string = ''
    sorted_dct = sort_dict(dct)
    for key,value in sorted_dct.items():
        string = string + str(value)
    return string

def encrypt_string(hash_string):
    sha_signature = hashlib.md5(hash_string.encode()).hexdigest()
    return sha_signature

def list2str(inputList):
    string = ''
    for item in inputList:
        string = string + item + "\n"
    return string

def createDatabase():
    dbname = 'postgres'
    user = 'postgres'
    host = 'localhost'
    password = 'DarkZuoqson-postgresql32229751!'
    conn = psycopg2.connect(host=host,dbname=dbname,user=user,password=password)
    c = conn.cursor()

    c.execute(
        """
    CREATE TABLE cases(
        case_id SERIAL PRIMARY KEY,
        path_candle_file VARCHAR(80),
        timeframe_start TIMESTAMP,
        timeframe_end TIMESTAMP,
        candle_sec INTEGER,
        path_historical_data VARCHAR(80),
        buy VARCHAR(40),
        sell VARCHAR(40),
        filter VARCHAR(20),
        f1_above_path_candle_file VARCHAR(80),
        f1_above_indicator VARCHAR(3),
        f1_above_average INTEGER,
        f1_below_path_candle_file VARCHAR(80),
        f1_below_indicator VARCHAR(3),
        f1_below_average INTEGER,
        pattern VARCHAR(20),
        p1_threshold INTEGER,
        p2_td_s INTEGER,
        p3_td_c INTEGER,
        p4_shorter_rsi INTEGER,
        p4_longer_rsi_max INTEGER,
        p4_longer_rsi_min INTEGER,
        p4_longer_path_candle_file VARCHAR(80),
        max_order INTEGER,
        space REAL,
        last_price_approach VARCHAR(20),
        percentile_last_price INTEGER,
        games INTEGER,
        samples INTEGER,
        bag_percentage REAL,
        initial_bag REAL,
        market_order REAL,
        limit_order REAL,
        ph1 VARCHAR(32),
        ph2 VARCHAR(32),
        ph3 VARCHAR(32),
        state VARCHAR(20)
    )
        """
    )
    conn.commit()

if __name__ == '__main__':
    main()
    # createDatabase()
