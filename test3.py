import sys
from PyQt5 import QtCore, QtGui, QtWidgets, uic
import psycopg2

def main():

    p = {
    'path_candle_file' : 'builders/warehouse/candle_data/' + '30min_bitstamp.csv',
    'timeframeStart' : '2014-01-01 00:00:00',
    'timeframeEnd' : '2018-04-19 00:00:00',
    'candle_sec': '1800',
    'buy': '1-sellEnd_0high+5',
    'sell': 'buy-10_realHighest',
    'path_historical_data' : 'builders/warehouse/historical_data/' + 'bitstampUSD.csv',
    # 'F1_toogle': False,
    # 'F1_condition': 'condition1',
    # 'F1_path_trendline_file': 'builders/warehouse/trendlines/' + '30min_2014-01-01_2018-06-19_40_150_4_15_001_001_4.txt', 
    # 'F1_mode': 'greater_than_limit',
    # 'F1_condition_parameter': 'm',     
    # 'F1_limit': '0',
    # 'F1_limit1': '0',
    # 'F1_limit2': '0',
    # 'F2_toggle': False,
    # 'F2_above_path_candle_file': 'builders/warehouse/candle_data/' + '30min_bitstamp.csv',
    # 'F2_above_indicador': 'SMA',
    # 'F2_above_average': '30',
    # 'F2_bellow_candle_file': 'builders/warehouse/candle_data/' + '30min_bitstamp.csv',
    # 'F2_bellow_indicador': 'SMA',
    # 'F2_bellow_average': '7',
    # 'P1_threshold' : '30',
    # 'P2_td_s': '-9',
    # 'P3_td_c': '13',
    # 'pattern': 'pattern1',
    'maxOrder': '500', # in USD
    'space': '0.02',
    # 'lastPrice_approach': 'percentile',
    # 'C_percentile': False
    # 'C_average': True
    'lastPrice_percentile': '50',
    'games': '25',
    'samples': '50',
    'bagPercentage': '1',
    'initialBag': '10000',
    'marketOrder': '-0.00075',
    'limitOrder': '0.00025'
    }

    # dbname = 'postgres'
    # user = 'postgres'
    # host = 'localhost'
    # password = 'DarkZuoqson-postgresql32229751!'
    # conn = psycopg2.connect(host=host,dbname=dbname,user=user,password=password)
    # c = conn.cursor()

    class MyWindow(QtWidgets.QMainWindow):
        def __init__(self):
            super().__init__()
            uic.loadUi('example.ui',self)
            
            self.setWindowTitle('Input interface')
            self.B_OK.clicked.connect(self.on_click)
            self.B_OK.setToolTip('This is an example button')
            self.E_lastPrice_percentile.hide()
            self.C_percentile.stateChanged.connect(self.clickBox_percentile)
            self.C_average.stateChanged.connect(self.clickBox_average)
            self.LI_pattern.itemClicked.connect(self.Clicked1)            
            self.L_P1_threshold.hide()
            self.E_P1_threshold.hide()
            self.L_P2_td_s.hide()
            self.E_P2_td_s.hide()
            self.L_P3_td_c.hide()
            self.E_P3_td_c.hide()
            


        def Clicked1(self,item):
            print("You clicked: "+item.text())
            if item.text() == 'pattern1':
                self.L_P1_threshold.show()
                self.E_P1_threshold.show()
                self.L_P2_td_s.hide()
                self.E_P2_td_s.hide()
                self.L_P3_td_c.hide()
                self.E_P3_td_c.hide()
            if item.text() == 'pattern2':
                self.L_P1_threshold.hide()
                self.E_P1_threshold.hide()
                self.L_P2_td_s.show()
                self.E_P2_td_s.show()
                self.L_P3_td_c.hide()
                self.E_P3_td_c.hide()
            if item.text() == 'pattern3':
                self.L_P1_threshold.hide()
                self.E_P1_threshold.hide()
                self.L_P2_td_s.hide()
                self.E_P2_td_s.hide()
                self.L_P3_td_c.show()
                self.E_P3_td_c.show()



        def clickBox_percentile(self,state):
            if state == QtCore.Qt.Checked:
                self.E_lastPrice_percentile.show()
                self.C_average.setChecked(False)
                self.C_percentile.setChecked(True)
            else:
                self.E_lastPrice_percentile.hide()

        def clickBox_average(self,state):
            if state == QtCore.Qt.Checked:
                self.E_lastPrice_percentile.hide()
                self.C_percentile.setChecked(False)
                self.C_average.setChecked(True)

        def on_click(self):
            print(dir(self))
            # for edit in list(p):
            #     x = getattr(self, 'E_' + edit).text()
            #     print(x)

            # if self.C_percentile.isChecked() == True:
            #     print('Percentile is checked.')
            # elif self.C_percentile.isChecked() == False:
            #     print('Percentile is not checked.')

    app = QtWidgets.QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec_())

# def insertInto(recordList,c,conn):
#     c.execute("INSERT INTO testing VALUES ({},{},{})".format(recordList[0],recordList[1],recordList[2]))
#     conn.commit()



if __name__ == '__main__':
    main()
