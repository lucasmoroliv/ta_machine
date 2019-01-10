from selenium import webdriver
import os,time,logging,csv,warnings,sys
import pandas as pd
warnings.simplefilter(action='ignore', category=FutureWarning)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter("%(asctime)s - %(name)s - %(message)s")
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)

def main():

    t = time.time()
    user_input = sys.argv[1:]

    # Paths of both the new and old historical data files.  
    if user_input == "lucas":
        new_historicalData = "C:\\Users\\lucas\\Downloads\\bitstampUSD.csv.gz"
        old_historicalData = "C:\\Users\\lucas\\code\\projects\\ta_machine\\builders\\warehouse\\historical_data\\bitstampUSD.csv"
        chromedriver_path = "C:\\Users\\lucas\\code\\chromedriver"
    
    if user_input == "kenji":
        new_historicalData = "C:\\Users\\Danil\\Downloads\\bitstampUSD.csv.gz"
        old_historicalData = "C:\\Users\\Danil\\Desktop\\ta_machine\\builders\\warehouse\\historical_data\\bitstampUSD.csv"
        chromedriver_path = "C:\\Users\\Danil\\Desktop\\code\\chromedriver"
    
    # Delete compressed bitstampUSD file if it is in Downloads directory. 
    if os.path.exists(new_historicalData):
        os.remove(new_historicalData)
        logger.info("Deleting {}.".format(new_historicalData))


    download_file(chromedriver_path)
    t0 = time.time()
    logger.info("Download started.")
    wait_download(new_historicalData)
    logger.info("Download done in about {} seconds.".format(time.time()-t0))

    # Get dataframe from new_historicalData. The file does not need to be extracted, since pandas get the file as it is.  
    logger.info("Reading compressed file into pandas.")
    t1 = time.time()
    df = pd.read_csv(new_historicalData, names=['timestamp','price','volume'])
    logger.info("Reading done in {} seconds.".format(time.time()-t1))
    # Delete the row with the wrong price. Timestamp 1466685414.  
    logger.info("Deleting row with wrong price data.")
    df = df[df.timestamp != 1466685414]

    # Write the df dataframe in csv format, in the file with path "old_historicalData"   
    with open(old_historicalData, 'a') as f:
        t2 = time.time()
        logger.info("Starting to write dataframe into csv format.")
        df.to_csv(f, index=False, header=False)
        logger.info("Writing done in {} seconds.".format(time.time()-t2))

    # Delete new_historicalData. 
    logger.info("Deleting {}.".format(new_historicalData))
    os.remove(new_historicalData)
    
    logger.info("Program ran in {} seconds.".format(time.time()-t))

def download_file(chromedriver_path):
    browser = webdriver.Chrome(chromedriver_path)
    browser.get("http://api.bitcoincharts.com/v1/csv/bitstampUSD.csv.gz")

def wait_download(file_path):
    while not os.path.exists(file_path):
        time.sleep(1)
        
def get_raw(file_path):
    return pd.read_csv(file_path, header=None, names=['timestamp','price','volume'])

if __name__ == "__main__":
    t0 = time.time()
    main()
