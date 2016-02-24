from pyparse import pyparse
from pyparse.core.data.object import Object
from pyparse.core.data.fields import *
from pyparse.core.data.query import Query
from pyparse.core.data.types import *

#pyparse.setup('', '')


class VisitedCity(Object):
    location = GeoPointField()
    visit_date = DateTimeField()
    city = Field()
    day_span = Field()
    labels = ListField()

tokyo = VisitedCity.query().all().filter(city='Tokyo').fetch().contents[0]
""":type: VisitedCity"""
# tokyo.labels += ['Asia']
# print(hasattr(tokyo, 'xd'))
# tokyo.save()
print(tokyo)

# tpe = VisitedCity()
# tpe.location = GeoPoint(25.040, 121.532)
# tpe.visit_date = datetime.datetime(2015, 7, 3)
# tpe.city = 'Taipei'
# tpe.day_span = 14
#
# print(tpe)
# print('-'*40)
#
# # tpe.save()
#
# q = Query(class_name='VisitedCity').all().filter(city__in=['Tokyo', 'San Francisco'])
# print(q.get_arguments())
# visited_cities = q.fetch().contents
# print(visited_cities)
# print('-'*40)
#
# now = datetime.datetime.utcnow().replace(tzinfo=UTC())
# print(now)
# visited_cities[0]['visitDate'] = now
# visited_cities[0].save()
# print(visited_cities[0])
