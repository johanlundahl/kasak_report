import argparse
import requests
import time
import json
from models import Day, CarWash
import kasak_params as kp
import slack

def filter_count(lst, func):
    lst = [list(filter(func, x)) for x in lst]
    return list(map(len, lst))

unknown_check = lambda x: x.returned == 0 and x.comment == ''
commented_check = lambda x: x.returned == 0 and x.comment != ''
returned_check = lambda x: x.returned == 1

    
def decode(json_object):
    if 'bookingCarRegistration' in json_object:
        return CarWash(reg=json_object['bookingCarRegistration'], 
                       date=json_object['bookingDate'],
                       pickup_time=json_object['bookingPickupTime'],
                       return_time=json_object['bookingReturnTime'],
                       company=json_object['customerCompany'],
                       picked_up=json_object['carStatusArrived'],
                       returned=json_object['carStatusDeparted'],
                       comment=json_object['bookingNotification'],
                       return_assigned=json_object['bookingPickupDriverID']!='',
                       pickup_assigned=json_object['bookingPickupDriverID']!='')
    return json_object 

        
def collect_washes(start_day, end_day):
    total_car_washes = []
    a_day = start_day
    while a_day <= end_day:
        washes, code = get_washes_for(a_day)
        total_car_washes = total_car_washes + washes
        a_day = a_day.next()
        time.sleep(1)
    return total_car_washes

def get_washes_for(day):
    response = requests.get(url = kp.kasak_carstatus_url.format(day))
    try:
        objs = json.loads(response.text, object_hook=decode)
        return [objs[i] for i in objs], response.status_code
    except ValueError:
        return [], response.status_code
    
def get_washes_as_list(weekdays):
    days = []
    for day in weekdays:
        washes, code = get_washes_for(day)
        days.append(washes)
    return days
    
def get_todays_washes():
    today = Day.today()
    return get_washes_for(today)

    
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('start', type=Day)
    parser.add_argument('end', type=Day)
    args = parser.parse_args()

    cars = collect_washes(args.start, args.end)
    
    with open('output/stat_{}_{}.csv'.format(args.start, args.end), 'w') as stat:
        for car in cars:
            stat.write('{};{};{};{};{};{};{};{};\n'.format(car.date, car.pickup_time, car.picked_up, car.return_time, car.returned, car.reg, car.company, car.comment))
        
