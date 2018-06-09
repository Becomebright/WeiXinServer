from datetime import *
from app.models import *

# dt = datetime.today()
# duration = timedelta(0, 7200)  # 2hours

# c = Conference(name='hhx', date=dt, duration=duration)
# db.session.add(c)
# db.session.commit()

# c = Conference.query.filter_by(name='hhx')
# c = Conference.query.get(1)
# print(c)
# print(c.get_end_time())

#
from app.views import get_conf_dict

user = User.query.get(1)
e = Enroll(time=datetime.today())
e.conference = Conference.query.get(3)
db.session.add(e)
db.session.commit()
user.enrolls.append(e)


for conf in Conference.query.all():
    print(conf)
    print(get_conf_dict(conf=conf, user=user))
