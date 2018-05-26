from checkbook.categorizer import Categorizer
from checkbook.database import Database
from checkbook.loader import Loader
from checkbook.writer import Writer

db = Database()
Loader.load_incoming(db)
Categorizer.process_db(db)
db.save()

Writer.write_master(db)
Writer.write_summary(db)
