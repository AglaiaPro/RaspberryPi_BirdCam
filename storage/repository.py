import logging
from datetime import datetime, timezone
from storage.models import Event
from storage.db import get_db

logger: logging.Logger = logging.getLogger(__name__)

class EventRepository:

    def add_event(self, device_id, temperature, media_path, event_type):
        logger.debug(f"adding event: {device_id}")
        session = get_db()
        try:
            event = Event(
                device_id=device_id,
                temperature=temperature,
                media_path=media_path,
                event_type=event_type,
                timestamp=datetime.now(timezone.utc).isoformat()
            )
            session.add(event)
            session.commit()
            session.refresh(event)
            logger.debug(f"event id created: {event.id}")
            return event
        finally:
            session.close()

    def get_all_events(self):
        session = get_db()
        try:
            return session.query(Event).all()
        finally:
            session.close()

    def get_synced(self):
        session = get_db()
        try:
            return session.query(Event) \
                .filter(Event.synced == True) \
                .order_by(Event.timestamp.asc()) \
                .all()
        finally:
            session.close()

    def get_unsynced(self):
        logger.debug("fetching unsynced events")
        session = get_db()
        try:
            return session.query(Event).filter(Event.synced == False).all()
        finally:
            session.close()

    def mark_synced(self, event_id, file_url):
        logger.debug(f"marking synced: {event_id}")
        session = get_db()
        try:
            event = session.get(Event, event_id)
            if event:
                event.synced = True
                event.file_url = file_url
                session.commit()
        finally:
            session.close()

    def delete_event(self, event_id):
        logger.debug(f"deleting event: {event_id}")
        session = get_db()
        try:
            event = session.get(Event, event_id)
            if event:
                session.delete(event)
                session.commit()
        finally:
            session.close()
