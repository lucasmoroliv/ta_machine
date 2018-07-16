import pusherclient,sys,logging,time,csv,json
# Add a logging handler so we can see the raw communication data
root = logging.getLogger()
root.setLevel(logging.INFO)
ch = logging.StreamHandler(sys.stdout)
root.addHandler(ch)

global pusher

def main():
    # We can't subscribe until we've connected, so we use a callback handler
    # to subscribe when able
    def connect_handler(data):
        channel = pusher.subscribe('live_trades')
        channel.bind('trade', callback)

    # Strangely enough, the callback function starts working when we add data as an argument.
    def callback(data):
        with open('egg.csv', 'a', newline='') as csvfile:
            spamwriter = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            data_dict = json.loads(data)
            spamwriter.writerow([data_dict['timestamp'],data_dict['price'],data_dict['amount']])

    pusher = pusherclient.Pusher('de504dc5763aeef9ff52')
    pusher.connection.bind('pusher:connection_established', connect_handler)
    pusher.connect()

    while True:
        # Do other things in the meantime here...
        time.sleep(1)


if __name__ == '__main__':
    time1 = time.time()
    main()
    time2 = time.time()
    print('Time to run the program: ',time2-time1)
