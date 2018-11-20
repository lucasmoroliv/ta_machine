from pprint import pprint
import psycopg2,logging,time,datetime,sqlalchemy,sys
import pandas as pd
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

        # If any of the item of cases_list is not convertible to integer, a ValueError will be raised.
        cases_list = list(map(int,user_input))
        
        # Checking if the case_ids are distinct.
        if len(set(cases_list)) != len(cases_list):
            raise NotDistinctError 

        # Checking if all the case_id given exist in the database. If don't, NoMatchingCasesError will be raised and the
        # case_ids not matching the one in the database will be returned in the error message.
        no_matching = []
        cases_df = get_cases_df()
        for item in cases_list:
            if item not in cases_df.index:
                no_matching.append(item)
        no_matching = list(map(str,no_matching))
        if len(no_matching)>0:
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

        # hash_list is a list containing all the hashes of phases in the database, either the ones
        # that had been ran and the ones that hadn't.
        
        # The dictionary below has for each state value the respective phases which were ran.
        state_ran = {
            "ph1": ["ph1"],
            "ph2": ["ph1","ph2"],
            "ph3": ["ph1","ph2","ph3"],
        }
        
        for case_id in cases_list:

            # hash_dict is a three key dictionary with ph1, ph2 and ph3 hashes of case_id.
            hash_dict = cases_df.loc[case_id][["ph1","ph2","ph3"]].to_dict()         

            # ran_phases is a list containing the phases of the case that were already ran.
            ran_phases = state_ran[cases_df.loc[case_id]["state"]]
            # print(ran_phases)

            # all_other_hashes is a list of the ph1, ph2 and ph3 hashes of all cases exlucuding the hashes of the case_id. 
            partition_df = cases_df[cases_df.index != case_id][["ph1","ph2","ph3"]]
            nested_list = [list(item) for item in partition_df.values]
            all_other_hashes = list(chain.from_iterable(nested_list))


            for phase in ran_phases:
                hash_to_delete = hash_dict[phase]
                if hash_to_delete in all_other_hashes:
                    # In this case hash should not be deleted because other case_id needs it.
                    logger.info("The hash {}, which is phase{} of case_id {}, will not be deleted because other cases need it.")
                    continue
                else:
                    # In this case there is no problem deleting this hash.
                    logger.info("Deleting hash {}, which is phase{} of case_id {}.".format(hash_dict[phase],phase[-1],case_id))
                    delete_hash_in_table(phase,hash_dict[phase])

            logger.info("Deleting case_id {} from the cases table.".format(case_id))
            delete_case(case_id)

def delete_hash_in_table(phase,hashh):
    dbname = 'postgres'
    user = 'postgres'
    host = 'localhost'
    password = 'DarkZuoqson-postgresql32229751!'
    conn = psycopg2.connect(host=host,dbname=dbname,user=user,password=password)
    c = conn.cursor()
    c.execute("DELETE FROM phase{} WHERE {} = '{}'".format(phase[-1],phase,hashh))    
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