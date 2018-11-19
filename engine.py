from pprint import pprint
import psycopg2,logging,time,datetime,sqlalchemy,sys
import pandas as pd
import phase1,phase2,phase3
import multiprocessing

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter("%(asctime)s - %(name)s - %(message)s")

# file_handler  = logging.FileHandler("sample.log")    
# file_handler.setLevel(logging.ERROR)
# file_handler.setFormatter(formatter)
# logger.addHandler(file_handler)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)

def main():
    max_cases = sys.argv[1]
    approach1(max_cases)

def approach1(max_cases):
    while True:
        cases_df = get_cases_df()
        toRun_dict = get_toRun_dict(cases_df)
        if len(toRun_dict) == 0:
            logger.info("There is no phase to run.")
            break
        input_list = get_input_list(toRun_dict,max_cases)
        print("-------------------------\n","input_list:\n",input_list,"\n-------------------------")
        with multiprocessing.Pool(processes=int(max_cases)) as p:
            p.map(phase_runner,input_list)

def get_input_list(toRun_dict,max_cases):
    cases_toRun = []
    hashes_toRun = []
    input_list = []
    for case_id,phase_dict in toRun_dict.items():
        if case_id not in cases_toRun and phase_dict[list(phase_dict)[0]] not in hashes_toRun:
            cases_toRun.append(case_id)
            hashes_toRun.append(phase_dict[list(phase_dict)[0]])
            input_list.append([case_id,list(phase_dict)[0]])
            if len(cases_toRun) == int(max_cases):
                break
    return input_list

def get_cases_df():
    db_engine = sqlalchemy.create_engine("postgresql://postgres:DarkZuoqson-postgresql32229751!@localhost/postgres")
    query = "SELECT case_id,ph1,ph2,ph3,state FROM cases ORDER BY case_id"
    return pd.read_sql_query(query,db_engine)

def get_toRun_dict(cases_df):   
    hashBank = find_hashBank(cases_df)
    toRun_dict = {}
    # The dictionary below has for every key the phases the code must run for the case.
    state_toRun = {
        "ph0": ["ph1","ph2","ph3"],
        "ph1": ["ph2","ph3"],
        "ph2": ["ph3"],
    }
    # Since cases that have the value "ph3" in column "state" have already run all the phases they had to, we
    # make a dataframe called partition_df out of cases_df that have all the cases but the ones with state "ph3".
    partition_df = cases_df[cases_df.state != "ph3"]
    # The loop iterates through every row of partition_df.
    for _,case in partition_df.iterrows():
        # The next loop will iterate through ["ph1","ph2","ph3"], or ["ph2","ph3"] or ["ph3"] depending on each
        # state each case is in. 
        for column in state_toRun[case["state"]]:
            # In case case[column] is in hashBank list, we can make sure that the phase in question don't need to
            # be ran because it has already ran previously and the output of it is somewhere in the database. 
            if case[column] in hashBank:
                # In such case, nothing is done.
                pass
            # In other hand, if case[column] is not in hashBank list, we conclude that we must run this phase.
            else:
                # toRun_list.append([case["case_id"],"phase"+column[2]])
                if str(case["case_id"]) not in list(toRun_dict):
                    toRun_dict[str(case["case_id"])] = {}
                toRun_dict[str(case["case_id"])]["phase"+column[2]] = case[column]
    return toRun_dict
                
def phase_runner(input_item):
    globals()[input_item[1]].engines_door(input_item[0])                
              
def find_hashBank(cases_df):
    # In the dictionary below, each key contains the respective number of phases that have already been ran.
    # So for example, the cases that have the column value "ph2", have already ran phase1 and phase2 modules,
    # and thefore the database contains the results for hashes ph1 and ph2.
    state_ran = {
        "ph1": ["ph1"],
        "ph2": ["ph1","ph2"],
        "ph3": ["ph1","ph2","ph3"],
    }
    hashBank = []
    # We could use cases_df as it is, but there are probably benifts for excluding all the rows containing
    # the column value "ph0", because these cases haven't ran any of the phase modules.
    partition_df = cases_df[cases_df.state != "ph0"]
    for _,row in partition_df.iterrows():
        for column in state_ran[row["state"]]:
            hashBank.append(row[column])
    return set(hashBank)   
    
if __name__ == '__main__':
    time1 = time.time()
    main()
    time2 = time.time()
    print('---------------------------------------')
    print('Runtime: ',time2-time1)
    print('Ran at: ',datetime.datetime.fromtimestamp(time2))
    
    
    
    
