import sys
from PyQt5 import QtCore, QtGui, QtWidgets, uic
import psycopg2

def main():

    # 'path_candle_file' : 'builders/warehouse/candle_data/' + '30min_bitstamp.csv',
    # 'timeframeStart' : '2014-01-01 00:00:00',
    # 'timeframeEnd' : '2018-04-19 00:00:00',
    # 'candle_sec': '1800',
    # 'path_historical_data' : 'builders/warehouse/historical_data/' + 'bitstampUSD.csv',
    # 'buy': '1-sellEnd_1open*1.0001',
    # 'sell': 'buy-10_realHighest',
    # 'F1_toggle': False,
    # 'F1_above_path_candle_file': 'builders/warehouse/candle_data/' + '30min_bitstamp.csv',
    # 'F1_above_indicador': 'SMA',
    # 'F1_above_average': '30',
    # 'F1_below_path_candle_file': 'builders/warehouse/candle_data/' + '30min_bitstamp.csv',
    # 'F1_below_indicador': 'SMA',
    # 'F1_below_average': '7',
    # 'pattern': 'pattern1',
    # 'P1_threshold' : '30',
    # 'P2_td_s': '-9',
    # 'P3_td_c': '13',
    # 'max_order': '500', # in USD
    # # -------------
    # 'setup_file': 'setup1540319594.txt',
    # 'space': 0.02,
    # 'percentile_lastPrice': 50
    # # -------------
    # 'testedSetup_file': 'triplets_setup1540319594_0.02_50.txt',
    # 'games': 25,
    # 'samples': 50,
    # 'bagPercentage': 1,
    # 'initialBag': 10000,
    # 'marketOrder': -0.00075,
    # 'limitOrder': 0.00025

    p = {
    'path_candle_file': 'builders/warehouse/candle_data/' + '30min_bitstamp.csv', # VARCHAR(80)
    'timeframeStart': '2014-01-01 00:00:00', # TIMESTAMP
    'timeframeEnd': '2018-04-19 00:00:00', # TIMESTAMP
    'candle_sec': '1800', # INTEGER
    'path_historical_data' :'builders/warehouse/historical_data/' + 'bitstampUSD.csv', # VARCHAR(80)
    'buy': '1-sellEnd_0high*1.0001', # VARCHAR(40)
    'sell': 'buy-10_realHighest', # VARCHAR(40)
    'filter': 'filter1', # VARCHAR(20)
    'F1_above_path_candle_file': 'builders/warehouse/candle_data/' + '30min_bitstamp.csv', # VARCHAR(80)
    'F1_above_indicador': 'SMA', # VARCHAR(3)
    'F1_above_average': '30', # INTEGER
    'F1_below_candle_file': 'builders/warehouse/candle_data/' + '30min_bitstamp.csv', # VARCHAR(80)
    'F1_below_indicador': 'SMA', # VARCHAR(3)
    'F1_below_average': '7', # INTEGER
    'pattern': 'pattern1', # VARCHAR(20)
    'P1_threshold' : '30',  # INTEGER
    'P2_td_s': '-9', # INTEGER
    'P3_td_c': '13', # INTEGER
    'max_order': '500', # INTEGER
    'space': '0.02', # REAL
    'percentile_toggle': False, # BOOLEAN
    'average_toggle': True, # BOOLEAN
    'percentile_lastPrice': '50' # INTEGER
    'games': '25', # INTEGER
    'samples': '50', # INTEGER
    'bagPercentage': '1', # REAL
    'initialBag': '10000', # REAL
    'marketOrder': '-0.00075', # REAL
    'limitOrder': '0.00025' # REAL
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
            self.E_percentile_lastPrice.hide()

            self.C_percentile_toggle.stateChanged.connect(self.click_C_percentile_toggle)
            self.C_average_toggle.stateChanged.connect(self.click_C_average_toggle)
            self.LI_pattern.itemClicked.connect(self.click_LI_pattern)            
            self.LI_filter.itemClicked.connect(self.click_LI_filter)            
            
            self.patternBox()
            self.filterBox()

        def filterBox(self):

            # Create the lables for patterns.
            self.L_F1_above_path_candle_file = QtWidgets.QLabel('F1_above_path_candle_file',self)
            self.L_F1_above_indicador = QtWidgets.QLabel('F1_above_indicador',self)
            self.L_F1_above_average = QtWidgets.QLabel('F1_above_average',self)
            self.L_F1_below_path_candle_file = QtWidgets.QLabel('F1_below__path_candle_file',self)
            self.L_F1_below_indicador = QtWidgets.QLabel('F1_below_indicador',self)
            self.L_F1_below_average = QtWidgets.QLabel('F1_below_average',self)

            # Create the lineEdits for patterns.
    
            self.E_F1_above_path_candle_file = QtWidgets.QLineEdit(self)
            self.E_F1_above_indicador = QtWidgets.QLineEdit(self)
            self.E_F1_above_average = QtWidgets.QLineEdit(self)
            self.E_F1_below_path_candle_file = QtWidgets.QLineEdit(self)
            self.E_F1_below_indicador = QtWidgets.QLineEdit(self)
            self.E_F1_below_average = QtWidgets.QLineEdit(self)

            # Creating variable containing font configuration.
            newFont = QtGui.QFont('MS Shell Dlg 2',12) 
            
            # Adding the configuration to the pattern labels.
            self.L_F1_above_path_candle_file.setFont(newFont)
            self.L_F1_above_indicador.setFont(newFont)
            self.L_F1_above_average.setFont(newFont)
            self.L_F1_below_path_candle_file.setFont(newFont)
            self.L_F1_below_indicador.setFont(newFont)
            self.L_F1_below_average.setFont(newFont)

            # Positioning the labels.
            self.L_F1_above_path_candle_file.setGeometry(750,180,200,25)
            self.L_F1_above_indicador.setGeometry(750,213,200,25)
            self.L_F1_above_average.setGeometry(750,246,200,25)
            self.L_F1_below_path_candle_file.setGeometry(750,279,200,25)
            self.L_F1_below_indicador.setGeometry(750,312,200,25)
            self.L_F1_below_average.setGeometry(750,345,200,25)

            # Positioning the lineEdits.
            self.E_F1_above_path_candle_file.setGeometry(970,180,431,25)
            self.E_F1_above_indicador.setGeometry(970,213,431,25)
            self.E_F1_above_average.setGeometry(970,246,431,25)
            self.E_F1_below_path_candle_file.setGeometry(970,279,431,25)
            self.E_F1_below_indicador.setGeometry(970,312,431,25)
            self.E_F1_below_average.setGeometry(970,345,431,25)

            # Hiding all the widgets made in the function.
            self.L_F1_above_path_candle_file.hide()
            self.L_F1_above_indicador.hide()
            self.L_F1_above_average.hide()
            self.L_F1_below_path_candle_file.hide()
            self.L_F1_below_indicador.hide()
            self.L_F1_below_average.hide()
            self.E_F1_above_path_candle_file.hide()
            self.E_F1_above_indicador.hide()
            self.E_F1_above_average.hide()
            self.E_F1_below_path_candle_file.hide()
            self.E_F1_below_indicador.hide()
            self.E_F1_below_average.hide()

        def click_LI_filter(self,item):
            if item.text() == 'filter1':
                self.L_F1_above_path_candle_file.show()
                self.L_F1_above_indicador.show()
                self.L_F1_above_average.show()
                self.L_F1_below_path_candle_file.show()
                self.L_F1_below_indicador.show()
                self.L_F1_below_average.show()
                self.E_F1_above_path_candle_file.show()
                self.E_F1_above_indicador.show()
                self.E_F1_above_average.show()
                self.E_F1_below_path_candle_file.show()
                self.E_F1_below_indicador.show()
                self.E_F1_below_average.show()
            if item.text() == 'none':
                self.L_F1_above_path_candle_file.hide()
                self.L_F1_above_indicador.hide()
                self.L_F1_above_average.hide()
                self.L_F1_below_path_candle_file.hide()
                self.L_F1_below_indicador.hide()
                self.L_F1_below_average.hide()
                self.E_F1_above_path_candle_file.hide()
                self.E_F1_above_indicador.hide()
                self.E_F1_above_average.hide()
                self.E_F1_below_path_candle_file.hide()
                self.E_F1_below_indicador.hide()
                self.E_F1_below_average.hide()

        def patternBox(self):

            # Create the lables for patterns.
            self.L_P1_threshold = QtWidgets.QLabel('P1_threshold',self)
            self.L_P2_td_s = QtWidgets.QLabel('P2_td_s',self)
            self.L_P3_td_c = QtWidgets.QLabel('P3_td_c',self)

            # Create the lineEdits for patterns.
            self.E_P1_threshold = QtWidgets.QLineEdit(self)
            self.E_P2_td_s = QtWidgets.QLineEdit(self)
            self.E_P3_td_c = QtWidgets.QLineEdit(self)

            # Creating variable containing font configuration.
            newFont = QtGui.QFont('MS Shell Dlg 2',12) 
            
            # Adding the configuration to the pattern labels.
            self.L_P1_threshold.setFont(newFont)
            self.L_P2_td_s.setFont(newFont)
            self.L_P3_td_c.setFont(newFont)

            # Positioning the labels.
            self.L_P1_threshold.setGeometry(750,70,200,25)
            self.L_P2_td_s.setGeometry(750,70,200,25)
            self.L_P3_td_c.setGeometry(750,70,200,25)

            # Positioning the lineEdits.
            self.E_P1_threshold.setGeometry(870,70,100,25)
            self.E_P2_td_s.setGeometry(870,70,100,25)
            self.E_P3_td_c.setGeometry(870,70,100,25)

            # Hiding all the widgets made in the function.
            self.L_P1_threshold.hide()
            self.L_P2_td_s.hide()
            self.L_P3_td_c.hide()
            self.E_P1_threshold.hide()
            self.E_P2_td_s.hide()
            self.E_P3_td_c.hide()

        def click_LI_pattern(self,item):
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

        def click_C_percentile_toggle(self,state):
            if state == QtCore.Qt.Checked:
                self.E_percentile_lastPrice.show()
                self.C_average_toggle.setChecked(False)
                self.C_percentile_toggle.setChecked(True)
            else:
                self.E_percentile_lastPrice.hide()

        def click_C_average_toggle(self,state):
            if state == QtCore.Qt.Checked:
                self.E_percentile_lastPrice.hide()
                self.C_percentile_toggle.setChecked(False)
                self.C_average_toggle.setChecked(True)

        def on_click(self):
            for edit in list(p):
                if len(getattr(self, 'E_' + edit).text()) == 0:
                    print("There is nothing in the edit: ",edit)







    app = QtWidgets.QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec_())

# def insertInto(recordList,c,conn):
#     c.execute("INSERT INTO testing VALUES ({},{},{})".format(recordList[0],recordList[1],recordList[2]))
#     conn.commit()



if __name__ == '__main__':
    main()
