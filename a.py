from django.utils import timezone
import datetime
from django.utils.timezone import now


# print(timezone.now())  # The UTC time
# print(timezone.localtime())  # timezone specified time,if timezone is UTC, it is same as above 
print(datetime.datetime.now())



import sys
print(sys.getsizeof((x*2 for x in range(256))))


print(sys.getsizeof([x*2 for x in range(256)]))