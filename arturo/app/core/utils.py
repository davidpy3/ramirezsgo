from config.wsgi import *
from core.clinic.crm.models import Sale, DateMedical
from core.security.models import *
from core.user.models import *


def search_content_type(name):
    for i in ContentType.objects.all():
        if i.name.lower() == name.lower():
            return i
    return None


if __name__ == '__main__':
    pass

# weekday = 0
# lastperiod_date = datetime.strptime('01-05-2020', '%d-%m-%Y')
# datenow = datetime.now().date()
# while lastperiod_date.date() < datenow:
#     if lastperiod_date.weekday() == 6:
#         weekday += 1
#     lastperiod_date = lastperiod_date + timedelta(days=1)
# print(weekday)
for d in DateMedical.objects.all():
    print(d.get_weekday())
