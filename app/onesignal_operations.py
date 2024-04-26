
import os
import onesignal
from onesignal.api import default_api
from onesignal.model.generic_error import GenericError
from onesignal.model.rate_limiter_error import RateLimiterError
from onesignal.model.notification import Notification
from onesignal.model.create_notification_success_response import CreateNotificationSuccessResponse
from pprint import pprint
from dotenv import load_dotenv

from app.crud.attendee_crud import get_all_attendee_profiles_by_conference_id, get_attendees_by_conference_id

load_dotenv()
app_key = os.environ.get("ONESIGNAL_API_KEY")
user_key = os.environ.get("ONESIGNAL_USER_KEY")
configuration = onesignal.Configuration(
    app_key = app_key,
    user_key = user_key
)
app_id = os.environ.get("ONESIGNAL_APP_ID")

def create_notification(db,conference_id,headings, content, picture):
    attendees = get_attendees_by_conference_id(db, conference_id)
    external_user_ids = [attendee.uuid for attendee in attendees]
    with onesignal.ApiClient(configuration) as api_client:
        api_instance = default_api.DefaultApi(api_client)
        notification = Notification(
            app_id=app_id,
            headings={"en": headings},
            contents={"en": content},
            include_external_user_ids=external_user_ids,
            big_picture=picture
        )
    try:
        api_instance.create_notification(notification)
    except onesignal.ApiException as e:
        print("Exception when calling DefaultApi->create_notification: %s\n" % e)