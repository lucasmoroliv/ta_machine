from websocket import create_connection
import json,csv,time,calendar
from pprint import pprint 
import dateutil.parser

def main():
    ws = create_connection('wss://www.bitmex.com/realtime?subscribe=trade:XBTUSD')
    check = 0


    while True:
        if check == 'ready_to_start':
            while True:
                with open('lattest2.csv', 'a', newline='') as csvfile:
                    spamwriter = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
                    result = ws.recv()
                    result = json.loads(result)
                    for order in result['data']:
                        spamwriter.writerow([get_timestamp(order['timestamp']),order['price'],order['size'],order['side']])

        result = ws.recv()
        result = json.loads(result)
        if 'action' in result and result['action'] == 'partial':
            check = 'ready_to_start'
        
    ws.close()

def get_timestamp(datestring):
    return calendar.timegm(dateutil.parser.parse(datestring).timetuple())

if __name__ == '__main__':
    main()