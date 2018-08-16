import pysher,sys,logging,time,csv,json,datetime

def main():

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.WARNING)
    # output = logging.StreamHandler(sys.stdout)
    output = logging.FileHandler('galileu.log')
    formatter = logging.Formatter('%(message)s\n-')
    output.setFormatter(formatter)
    logger.addHandler(output)
    ts_first_error = 0
    ts_last_error = 0

    def func(last_data):
        with open('lattest.csv', 'a', newline='') as csvfile:
            # spamwriter = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            spamwriter = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            data_dict = json.loads(last_data)
            spamwriter.writerow([data_dict['timestamp'],data_dict['price'],data_dict['amount']])

    def connect_handler(data):
        channel = pusher.subscribe('live_trades')
        channel.bind('trade', func)

    while True:
        try:
            appkey = 'de504dc5763aeef9ff52'
            logger.warning('\nConnecting at {}.'.format(datetime.datetime.utcfromtimestamp(time.time())))
            pusher = pysher.Pusher(appkey)
            pusher.connection.bind('pusher:connection_established', connect_handler)
            pusher.connect()
            if ts_first_error != 0:
                ts_connection = time.time()
                time_off = ts_connection - ts_first_error
                logger.warning('The connection was lost for about {} seconds.'.format(time_off))    

            while True:
                time.sleep(1)

        except:
            ts_error = time.time()
            logger.exception('Something wrong happened at {}, {}.'.format(ts_error,datetime.datetime.utcfromtimestamp(ts_error)))
            # There are two ways the code can go through this statement. 
            # First way. Time since last error occurred is too small. If that's the case, pusher may be down and
            # we need to chill a bit before trying to reconnect. 
            if (ts_error - ts_last_error)<1:
                time.sleep(1)
            # Second way. Time since last error occurred is not that small. If that's the case, pusher may not be
            # the reason for the error. Rather, the problem may be due to some error elsewhere, so we will not
            # overload the server by trying to reconnect straight away.
            else:
                ts_first_error = ts_error
                with open('egg.csv', 'a', newline='') as csvfile:
                    spamwriter = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
                    spamwriter.writerow(['BREAK at {}, {}.'.format(ts_first_error,datetime.datetime.utcfromtimestamp(time.time()))])
            ts_last_error = ts_error

if __name__ == '__main__':
    main()