%matplotlib inline
from datetime import datetime
from heapq import nlargest
import operator
from collections import defaultdict
import time
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# a combination of hotel_country + hotel_market + srch_destination_id is one ID
# find most popular 10 ID
# for the class project, we only use 2013 as train and 2014 as test

f = open("data/train.csv", "r")
f.readline()
top = defaultdict(int)
total = 0
start = time.time()

while 1:
    line = f.readline().strip()
    total += 1
        
    if total % 5000000 == 0:
        print('Read {} lines...'.format(total))
    if line == '':
         break

    arr = line.split(",")
    hotel_country = arr[21]
    hotel_market = arr[22]
    srch_destination_id = arr[16]
    book_year = arr[0][:4]
    
    if book_year == '2013':
        top[(hotel_country, hotel_market, srch_destination_id)] += 1
        
print('Done')
f.close()

end = time.time()
print(end - start)

# check out most 10

sorted_top = sorted(top.items(), key=operator.itemgetter(1), reverse=True)
nTop = 10
ids = []
for i in range(nTop):
    ids.append((sorted_top[i])[0])

ids

# subset data
f = open("data/train.csv", "r")
f.readline()

def dl():
    return defaultdict(list)

features = defaultdict(dl)
total = 0
missline = 0

start = time.time()
while 1:
    line = f.readline().strip()
    total += 1

    
    if total % 5000000 == 0:
        print('Read {} lines...'.format(total))

    if line == '':
        break
    
    arr = line.split(",")
    srch_destination_id = arr[16]
    hotel_country = arr[21]
    hotel_market = arr[22]
    id = (hotel_country, hotel_market, srch_destination_id)
    
    if srch_destination_id != '' and hotel_country != '' and hotel_market != '' and (id in ids):
        try:
            search_time_DT = datetime.strptime(arr[0], '%Y-%m-%d %H:%M:%S')
            checkInDateDT = datetime.strptime(arr[11], "%Y-%m-%d")
            checkOutDateDT = datetime.strptime(arr[12], "%Y-%m-%d") 
            ci_year = checkInDateDT.year
            co_year = checkOutDateDT.year
            
            arr[0] = search_time_DT.hour                      #srch_time_hour
            arr[1] = search_time_DT.weekday()                 #srch_time_weekday
            #arr[2]                                           #posa_continent
            #arr[3]                                           #user_location_country
            #arr[4]                                           #user_location_region
            arr[5] = search_time_DT.year                      #srch_time_year
            #arr[6]                                           #orig_dest_distance
            arr[7] = search_time_DT.timetuple().tm_yday       #srch_time_day_of_year
            #arr[8]                                           #is_mobile
            #arr[9]                                           #is_package
            #arr[10]                                          #channel
            arr[11] = checkInDateDT.timetuple().tm_yday       #srch_ci_day
            arr[12] = checkOutDateDT.timetuple().tm_yday      #srch_co_day
            #arr[13]                                          #srch_adult_count
            #arr[14]                                          #srch_child_count
            #arr[15]                                          #srch_room_count
            arr[16] = arr[12] - arr[11]+(co_year-ci_year)*356 #stay
            #arr[17]                                          #srch_dest_type_id
            #arr[18]                                          #is_booking should be weighted
            arr[19] = arr[11]-arr[7]+(ci_year-arr[5])*365     #plan_ahead
            arr[20] = srch_destination_id                     #srch_destination_id
            #arr[21]                                          #hotel_country
            #arr[22]                                          #hotel_market
            #arr[23]                                          #hotel_cluster
            
            if arr[16] < 0:
                arr[16] = 1
                
            if arr[19] < 0:
                arr[19] = 1
            
        except:
            missline += 1
            continue
            
        colNames = ['hour','dow','user_continent','user_country','user_region',
                    'year','dist','doy','mobile','package',
                    'channel','ci_day','co_day','adults','children',
                    'room','stay','type','booking','plan',
                    'srch_destination_id','hotel_country','hotel_market','hotel_cluster']

        for i in range(len(arr)):
            features[id][colNames[i]].append(arr[i])

f.close()
end = time.time()
print(end - start)
print missline

# transfer check in/out day to heat

import collections as cl
check_InOut_time = defaultdict(lambda: defaultdict(list))
check_InOut_PopTable = defaultdict(lambda: defaultdict(lambda: defaultdict(float)))

start = time.time()

for k,v in features.iteritems():
    check_InOut_time[k]['ci_day'] = [day for day in v['ci_day']]
    check_InOut_time[k]['co_day'] = [day for day in v['co_day']]
    temp_ci_day = check_InOut_time[k]['ci_day']
    temp_co_day = check_InOut_time[k]['co_day']
    counter_ci_day = cl.Counter(temp_ci_day)
    counter_co_day = cl.Counter(temp_co_day)

    ####### fit ci day ########
    xci= np.array(counter_ci_day.keys())
    yci = np.array(counter_ci_day.values())
    parameter = np.polyfit(xci,yci,12)
    p12ci = np.poly1d(parameter)
    yci_new = p12ci(xci)
    for i in range(len(xci)):
        check_InOut_PopTable[k]['ci_pop'][xci[i]] = yci_new[i]
    check_InOut_time[k]['ci_pop'] = [check_InOut_PopTable[k]['ci_pop'][day] for day in v['ci_day']]
    #plt.plot(xci,yci_new,'b-',xci,yci)
    #plt.show()

    ####### fit co day ########
    xco= np.array(counter_co_day.keys())
    yco = np.array(counter_co_day.values())
    parameter = np.polyfit(xco,yco,12)
    p12co = np.poly1d(parameter)
    yco_new = p12co(xco)
    for i in range(len(xco)):
        check_InOut_PopTable[k]['co_pop'][xco[i]] = yco_new[i]
    check_InOut_time[k]['co_pop'] = [check_InOut_PopTable[k]['co_pop'][day] for day in v['co_day']]
    #plt.plot(xco,yco_new,'b-',xco,yco)
    #plt.show()
    
end = time.time()
print (end - start)

for k,v in features.iteritems():
    v['ci_day'] = check_InOut_time[k]['ci_pop']
    
for k,v in features.iteritems():
    v['co_day'] = check_InOut_time[k]['co_pop']

for k, v in features.iteritems():
    df = pd.DataFrame(v)
    filename = k[0]+'-'+k[1]+'-'+k[2]+'.csv'
    df.to_csv('data/csv2/'+filename)


