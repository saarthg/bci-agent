import base64
from email.message import EmailMessage
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from langchain_core.tools import tool

from smartHomeAgent import track_call, tracked_calls


@tool
def gmail_create_draft(content: str, to: str, subject: str):
  """Create and insert a draft email. Takes in the content, the receiver email address, and the subject.
   Returns: Draft object, including draft id and message meta data.
  """
  track_call("gmail_create_draft")
  SCOPES = ["https://www.googleapis.com/auth/gmail.compose"]
  creds = None
  # The file token.json stores the user's access and refresh tokens, and is
  # created automatically when the authorization flow completes for the first
  # time.
  if os.path.exists("token.json"):
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
  # If there are no (valid) credentials available, let the user log in.
  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(
            "credentials.json", SCOPES
        )
        creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open("token.json", "w") as token:
        token.write(creds.to_json())

  try:
    # create gmail api client
    service = build("gmail", "v1", credentials=creds)

    message = EmailMessage()

    message.set_content(content)

    message["To"] = to
    #message["From"] = from1
    message["Subject"] = subject

    # encoded message
    encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

    create_message = {"message": {"raw": encoded_message}}
    # pylint: disable=E1101
    draft = (
        service.users()
        .drafts()
        .create(userId="me", body=create_message)
        .execute()
    )

    print(f'Draft id: {draft["id"]}\nDraft message: {draft["message"]}')

  except HttpError as error:
    print(f"An error occurred: {error}")
    draft = None

  return draft


@tool
def speech_based_search(query: str):
    """This function performs a speech-based web search for a given query."""
    track_call("speech_based_search")
    return f"Searching the web for: {query}"

@tool
def navigate_links_or_menus(link_or_menu: str):
    """This function assists with navigation between links and menus."""
    track_call("navigate_links_or_menus", link_or_menu)
    return f"Navigated to {link_or_menu}."

@tool
def manage_emails(action: str, content: str = None):
    """This function handles writing, replying to, or summarizing emails.
    Takes in the action: 'write', 'reply', 'summarize'. Also takes in content."""
    track_call("manage_emails", action, content)
    if action == "write":
        return f"Email written: {content}"
    elif action == "reply":
        return f"Reply sent: {content}"
    elif action == "summarize":
        return f"Email summary: {content[:100]}..."
    else:
        return "Invalid email action specified."

@tool
def search_files(keyword: str):
    """This function searches for files by keywords or topics. Takes in the specific keyword/topic."""
    track_call("search_files", keyword)
    return f"Searching for files related to '{keyword}'."

@tool
def enable_navigation_and_multiapp():
    """This function enables seamless navigation and multi-app coordination."""
    track_call("enable_navigation_and_multiapp")
    return "Multi-app navigation enabled."

@tool
def file_operations(action: str, file_name: str):
    """This function handles file opening or saving.
    Action: 'open', 'save'. Also takes in the file_name"""
    track_call("file_operations", action, file_name)
    return f"File {file_name} {action}d."

@tool
def manage_messages(app: str, action: str, content: str = None):
    """This function handles composing, reading, or replying to messages in apps like WhatsApp or iMessage.
    Takes in the app, an action: 'compose', 'read', 'reply', and the content."""
    track_call("manage_messages", app, action, content)
    return f"{action.capitalize()}d message in {app}: {content}"

@tool
def manage_social_media(action: str, content: str = None):
    """This function helps create posts, comment, or manage accounts on social media.
    Action: 'post', 'comment', 'update'. Content specifies the text or details."""
    track_call("manage_social_media", action, content)
    return f"{action.capitalize()}d on social media: {content}"

@tool
def schedule_meeting(title: str, time: str, attendees: list):
    """This function schedules meetings and sends invites."""
    track_call("schedule_meeting", title, time, attendees)
    return f"Scheduled meeting '{title}' at {time} for attendees: {', '.join(attendees)}."

@tool
def perform_online_banking(action: str, details: str):
    """This function supports online banking activities. Actions include 'transfer', 'check balance', etc."""
    track_call("perform_online_banking", action, details)
    return f"Performed banking action '{action}': {details}"

@tool
def browse_and_purchase_items(item: str):
    """This function assists with browsing and purchasing items online."""
    track_call("browse_and_purchase_items", item)
    return f"Browsing and purchasing item: {item}"

@tool
def order_groceries(items: list, delivery_time: str):
    """This function helps order groceries online or schedule deliveries."""
    track_call("order_groceries", items, delivery_time)
    return f"Ordered groceries: {', '.join(items)} for delivery at {delivery_time}."

@tool
def book_ride(service: str, pickup_location: str, dropoff_location: str):
    """This function books rides via services like Uber or Lyft."""
    track_call("book_ride", service, pickup_location, dropoff_location)
    return f"Ride booked on {service} from {pickup_location} to {dropoff_location}."

@tool
def public_transit_schedule(origin: str, destination: str):
    """This function provides public transit schedules and guidance."""
    track_call("public_transit_schedule", origin, destination)
    return f"Fetching transit schedule from {origin} to {destination}."

@tool
def fill_online_form(form_name: str, details: dict):
    """This function helps fill out online forms or documents."""
    track_call("fill_online_form", form_name, details)
    return f"Filled out form '{form_name}' with details: {details}"



