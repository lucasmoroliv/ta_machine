import pysher,sys,logging,time,csv,json,datetime

def main():

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    output = logging.StreamHandler(sys.stdout)
    # output = logging.FileHandler('galileu.log')
    formatter = logging.Formatter('%(message)s\n-')
    output.setFormatter(formatter)
    logger.addHandler(output)

    def func(last_data):
        with open('lattest.csv', 'a', newline='') as csvfile:
            # spamwriter = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            spamwriter = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            data_dict = json.loads(last_data)
            spamwriter.writerow([data_dict['timestamp'],data_dict['price'],data_dict['amount']])

    def connect_handler(data):
        channel = pusher.subscribe('live_trades')
        channel.bind('trade', func)

    appkey = 'de504dc5763aeef9ff52'
    pusher = pysher.Pusher(appkey)
    pusher.connection.bind('pusher:connection_established', connect_handler)
    pusher.connect()

    while True:
        time.sleep(1)

if __name__ == '__main__':
    main()