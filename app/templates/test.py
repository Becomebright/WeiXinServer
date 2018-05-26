from datetime import *
from app.models import *

dt = datetime.today()
duration = timedelta(0, 7200)  # 2hours

# c = Conference(name='hhx', date=dt, duration=duration)
# db.session.add(c)
# db.session.commit()

# c = Conference.query.filter_by(name='hhx')
c = Conference.query.get(1)
print(c)
print(c.get_end_time())