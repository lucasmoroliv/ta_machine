from pprint import pprint
import psycopg2,logging,time,datetime,sqlalchemy,sys
import pandas as pd
import numpy as np
from itertools import chain


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter("%(asctime)s - %(name)s - %(message)s")
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)

class NoInputGivenError(Exception):
    pass

class NotDistinctError(Exception):
    pass

class NoMatchingCasesError(Exception):
    pass

def main():

    try:
        user_input = sys.argv[1:]
        
        # Checking if there is at least one case_id given. Otherwise error is raised.
        if len(user_input) == 0:
            raise NoInputGivenError

        # If any of the item of cases_toDelete_list is not convertible to integer, a ValueError will be raised.
        cases_toDelete_list = list(map(int,user_input))
        
        # Checking if the case_ids are distinct.
        if len(set(cases_toDelete_list)) != len(cases_toDelete_list):
            raise NotDistinctError 

        # Checking if all the case_id given exist in the database. If don't, NoMatchingCasesError will be raised and the
        # case_ids not matching the one in the database will be returned in the error message.
        no_matching = []
        cases_df = get_cases_df()
        for item in cases_toDelete_list:
            if item not in cases_df.index:
                no_matching.append(item)
        no_matching = list(map(str,no_matching))
        if len(no_matching) > 0:
            raise NoMatchingCasesError("There is no case_id {} in the database.".format(", ".join(no_matching)))
            
    except NoInputGivenError:
        logger.exception("You must inform at least one case_id of the case you want to delete from the database.")
        sys.exit()
    except ValueError:
        logger.exception("The case_id has to be of type integer.")
        sys.exit()
    except NotDistinctError:
        logger.exception("The case_ids given were not distinct.")
        sys.exit()
    except NoMatchingCasesError:
        logger.exception("Some case_id given doesn't exist in the database.")
        sys.exit()
    else:

        # The dictionary below has for each state value the respective phases which were ran.
        state_ran = {
            "ph0": [],
            "ph1": ["ph1"],
            "ph2": ["ph1","ph2"],
            "ph3": ["ph1","ph2","ph3"],
        }
        
        # The two dataframes below hold respectively the rows of case_ids the user asked to delete and the ones that are not.
        toDelete_df = cases_df.loc[cases_toDelete_list]
        toStay_df = cases_df[~cases_df.index.isin(cases_toDelete_list)]

        # maybeDelete_list will be a list of lists. Every list of this list will have three items: 1) case_id 2) ph 3) hash. In this list is still included the "please_dont_delete" hashes,
        # which are the hashes that should not be deleted because there is at least a case that needs it.  
        maybeDelete_list = []
        for index,row in toDelete_df.iterrows():
            [maybeDelete_list.append([index,ph,row[ph]]) for ph in state_ran[row["state"]]]

        # The list below will have all the hashes that are supposed to be deleted, assuming there are no other case that need any of them.
        hashes_maybeDelete_list = [item[2] for item in maybeDelete_list]

        
        hashes_maybeDelete_set = set(hashes_maybeDelete_list)
        hashes_maybeDelete_list = hashes_maybeDelete_set
            
        nested_lists = toStay_df[["ph1","ph2","ph3"]].values
        hashes_toStay_set = set(chain.from_iterable(nested_lists))
        
        please_dont_delete = list(hashes_toStay_set.intersection(hashes_maybeDelete_set))
        
        toDelete_list = [item for item in maybeDelete_list if item[2] not in please_dont_delete]

        for item in toDelete_list:
            case_id = item[0]
            ph = item[1]
            hashh = item[2]
            logger.info("Deleting hash {}, which is phase{} of case_id {}.".format(hashh,ph[2],case_id))
            delete_hash_in_table(ph,hashh)
            
        for case_id in cases_toDelete_list:
            logger.info("Deleting case_id {} from the cases table.".format(case_id))
            delete_case(case_id)

def delete_hash_in_table(ph,hashh):
    dbname = 'postgres'
    user = 'postgres'
    host = 'localhost'
    password = 'DarkZuoqson-postgresql32229751!'
    conn = psycopg2.connect(host=host,dbname=dbname,user=user,password=password)
    c = conn.cursor()
    c.execute("DELETE FROM phase{} WHERE {} = '{}'".format(ph[-1],"ph"+ph[-1],hashh))    
    conn.commit()

def delete_case(case_id):
    dbname = 'postgres'
    user = 'postgres'
    host = 'localhost'
    password = 'DarkZuoqson-postgresql32229751!'
    conn = psycopg2.connect(host=host,dbname=dbname,user=user,password=password)
    c = conn.cursor()
    c.execute("DELETE FROM cases WHERE case_id = '{}'".format(case_id))    
    conn.commit()

def get_cases_df():
    db_engine = sqlalchemy.create_engine("postgresql://postgres:DarkZuoqson-postgresql32229751!@localhost/postgres")
    query = "SELECT case_id,ph1,ph2,ph3,state FROM cases ORDER BY case_id"
    return pd.read_sql_query(query,db_engine,index_col="case_id")

if __name__ == '__main__':
    time1 = time.time()
    main()
    time2 = time.time()
    print('---------------------------------------')
    print('Runtime: ',time2-time1)
    print('Ran at: ',datetime.datetime.fromtimestamp(time2))