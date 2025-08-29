from sqlalchemy import create_engine, Column, String, Text
from sqlalchemy.orm import declarative_base, sessionmaker

engine = create_engine("sqlite:///calls.db")
Session = sessionmaker(bind=engine)
Base = declarative_base()

class Call(Base):
    __tablename__ = "calls"
    call_id = Column(String, primary_key=True)
    transcript = Column(Text)
    diarization = Column(Text)
    sentiment = Column(Text)

Base.metadata.create_all(engine)

def save_transcription(call_id, transcript, diarization, sentiment):
    session = Session()
    call = Call(call_id=call_id, transcript=transcript,
                diarization=str(diarization), sentiment=str(sentiment))
    session.add(call); session.commit(); session.close()

def get_transcription(call_id):
    session = Session()
    call = session.query(Call).filter(Call.call_id==call_id).first()
    session.close()
    return call.transcript if call else ""

def list_call_ids():
    session = Session()
    calls = session.query(Call.call_id).all()
    session.close()
    return [c[0] for c in calls]   # extract call_id from tuples
