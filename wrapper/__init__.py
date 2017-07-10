# import pickledb
import json
# db = pickledb.load('wrapper.db',False)
json = json.loads(open('shape.memory','r+').read())
# db.set('create',json)
# db.dump()

from tinydb import TinyDB
from tinydb.storages import MemoryStorage

db = TinyDB(storage=MemoryStorage)
db.insert(json)
print db.all()