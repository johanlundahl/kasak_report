from models import Day, Week
import stats as stats
import chart

def percent(number):
    return int(100*number)

def filter_count(lst, func):
    lst = [list(filter(func, x)) for x in lst]
    return list(map(len, lst))

unknown_check = lambda x: x.returned == 0 and x.comment == ''
commented_check = lambda x: x.returned == 0 and x.comment != ''
returned_check = lambda x: x.returned == 1

    
today = Day.today()
week = Week.from_day(today)
weekdays = week.weekdays()

week_washes = []
days = []
for day in weekdays:
    washes, code = stats.get_washes_for(day)
    week_washes += washes
    days.append(washes)

unknown = filter_count(days, unknown_check)
commented = filter_count(days, commented_check)
returned = filter_count(days, returned_check)

#x_axis = list(map(lambda x: x.short_name(), weekdays))

#chart1 = chart.StackedBar(x_axis)
#chart1.add_bar(unknown, 'okända')
#chart1.add_bar(commented, 'kommenterade')
#chart1.add_bar(returned, 'levererade')
#chart1.save('week.png')
    
success_rate = percent(sum(returned)/len(week_washes))
comment_rate = percent(sum(commented)/len(week_washes))
message = 'Vecka {} tvättades {}% av bokningarna. {}% med kommentar. '.format(week._number, success_rate, comment_rate)

stats.post_to_slack(message)
