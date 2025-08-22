import devnotify
from devnotify import DevNotify

devnotify.api_key = "your_api_key_here"

client = DevNotify()
client.send("New user signed up", title="Signup Event", tags=["users", "signup"])
