from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from decouple import config
from .models import Base

engine = create_engine(config('SQLALCHEMY_DATABASE_URL'), echo=True)
SessionMaker = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class StartDB:
    def __init__(self):
        self.engine = engine
        self.SessionMaker = SessionMaker
    
    def init_db(self):
        Base.metadata.create_all(bind=self.engine)

    def drop_db(self):
        Base.metadata.drop_all(bind=self.engine)

    def reset_db(self):
        self.drop_db()
        self.init_db()


class OrmDataBase:
    def __init__(self):
        self.session = SessionMaker()
    
    def notification_db(self):
        print('Database running...')

    def get_db(self, query, full: bool = False):
        self.notification_db()
        result = self.session.execute(query)
        if full:
            return result.scalars().all()
        else:
            return result.scalar()

    def request_db(self, query):
        self.notification_db()
        result = self.session.execute(query)
        print(result)
        return result

        
    def commit_db(self):
        print('Committing changes to the database...')
        self.session.commit()
        
start_db = StartDB()
orm_db = OrmDataBase()
