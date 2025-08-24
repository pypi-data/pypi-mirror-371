from .basic_docs import add_api_code_docs, py_code, js_code, go_code

# Get user events
add_api_code_docs(
    "GET",
    "/users/event/{user_id}",
    py_code(
        """
from memobase import MemoBaseClient

client = MemoBaseClient(project_url='PROJECT_URL', api_key='PROJECT_TOKEN')
u = client.get_user(uid)

events = u.event(topk=10, max_token_size=1000, need_summary=True)
"""
    ),
    js_code(
        """
import { MemoBaseClient } from '@memobase/memobase';

const client = new MemoBaseClient(process.env.MEMOBASE_PROJECT_URL, process.env.MEMOBASE_API_KEY);
const user = await client.getUser(userId);

const events = await user.event();
"""
    ),
    go_code(
        """
import (
    "fmt"
    "log"

    "github.com/memodb-io/memobase/src/client/memobase-go/core"
)

func main() {
    projectURL := "YOUR_PROJECT_URL"
    apiKey := "YOUR_API_KEY"
    // Initialize the client
    client, err := core.NewMemoBaseClient(
        projectURL,
        apiKey,
    )
    if err != nil {
        log.Fatalf("Failed to create client: %v", err)
    }

    // Get a user
    userID := "EXISTING_USER_ID" // Replace with an actual user ID
    user, err := client.GetUser(userID, false)
    if err != nil {
        log.Fatalf("Failed to get user: %v", err)
    }

    // Get user events
    events, err := user.Event(10, nil, false)
    if err != nil {
        log.Fatalf("Failed to get events: %v", err)
    }

    fmt.Printf("Found %d events\n", len(events))
}
"""
    ),
)

# Update user event
add_api_code_docs(
    "PUT",
    "/users/event/{user_id}/{event_id}",
    py_code(
        """
from memobase import MemoBaseClient

client = MemoBaseClient(project_url='PROJECT_URL', api_key='PROJECT_TOKEN')
uid = client.add_user()
u = client.get_user(uid)
# ... insert messages to user

events = u.event(topk=5)
eid = events[0].id

u.update_event(eid, {"event_tip": "The event is about..."})
print(u.event(topk=1))
"""
    ),
    go_code(
        """
import (
    "fmt"
    "log"

    "github.com/memodb-io/memobase/src/client/memobase-go/core"
)

func main() {
    projectURL := "YOUR_PROJECT_URL"
    apiKey := "YOUR_API_KEY"
    // Initialize the client
    client, err := core.NewMemoBaseClient(
        projectURL,
        apiKey,
    )
    if err != nil {
        log.Fatalf("Failed to create client: %v", err)
    }

    // Get a user
    userID := "EXISTING_USER_ID" // Replace with an actual user ID
    user, err := client.GetUser(userID, false)
    if err != nil {
        log.Fatalf("Failed to get user: %v", err)
    }

    // Update an event
    eventID := "EXISTING_EVENT_ID" // Replace with an actual event ID
    eventData := map[string]interface{}{"event_tip": "The event is about..."}
    err = user.UpdateEvent(eventID, eventData)
    if err != nil {
        log.Fatalf("Failed to update event: %v", err)
    }
    fmt.Printf("Successfully updated event with ID: %s\n", eventID)
}
"""
    ),
)

# Delete user event
add_api_code_docs(
    "DELETE",
    "/users/event/{user_id}/{event_id}",
    py_code(
        """
from memobase import MemoBaseClient

client = MemoBaseClient(project_url='PROJECT_URL', api_key='PROJECT_TOKEN')
uid = client.add_user()
u = client.get_user(uid)
# ... insert messages to user

events = u.event(topk=1)
print(events)

eid = events[0].id
u.delete_event(eid)

print(u.event(topk=1))
"""
    ),
    go_code(
        """
import (
    "fmt"
    "log"

    "github.com/memodb-io/memobase/src/client/memobase-go/core"
)

func main() {
    projectURL := "YOUR_PROJECT_URL"
    apiKey := "YOUR_API_KEY"
    // Initialize the client
    client, err := core.NewMemoBaseClient(
        projectURL,
        apiKey,
    )
    if err != nil {
        log.Fatalf("Failed to create client: %v", err)
    }

    // Get a user
    userID := "EXISTING_USER_ID" // Replace with an actual user ID
    user, err := client.GetUser(userID, false)
    if err != nil {
        log.Fatalf("Failed to get user: %v", err)
    }

    // Delete an event
    eventID := "EXISTING_EVENT_ID" // Replace with an actual event ID
    err = user.DeleteEvent(eventID)
    if err != nil {
        log.Fatalf("Failed to delete event: %v", err)
    }
    fmt.Printf("Successfully deleted event with ID: %s\n", eventID)
}
"""
    ),
)

# Search user events
add_api_code_docs(
    "GET",
    "/users/event/search/{user_id}",
    py_code(
        """
from memobase import MemoBaseClient
from memobase.core.blob import ChatBlob

client = MemoBaseClient(project_url='PROJECT_URL', api_key='PROJECT_TOKEN')
uid = client.add_user()
u = client.get_user(uid)

b = ChatBlob(messages=[
    {
        "role": "user",
        "content": "Hi, I'm here again"
    },
    {
        "role": "assistant",
        "content": "Hi, Gus! How can I help you?"
    }
])
u.insert(b)
u.flush(sync=True)

events = u.search_event('query')
print(events)
"""
    ),
    go_code(
        """
import (
    "fmt"
    "log"

    "github.com/memodb-io/memobase/src/client/memobase-go/core"
)

func main() {
    projectURL := "YOUR_PROJECT_URL"
    apiKey := "YOUR_API_KEY"
    // Initialize the client
    client, err := core.NewMemoBaseClient(
        projectURL,
        apiKey,
    )
    if err != nil {
        log.Fatalf("Failed to create client: %v", err)
    }

    // Get a user
    userID := "EXISTING_USER_ID" // Replace with an actual user ID
    user, err := client.GetUser(userID, false)
    if err != nil {
        log.Fatalf("Failed to get user: %v", err)
    }

    // Search for events
    events, err := user.SearchEvent("query", 10, 0.7, 7)
    if err != nil {
        log.Fatalf("Failed to search events: %v", err)
    }

    fmt.Printf("Found %d events\n", len(events))
}
"""
    ),
)


add_api_code_docs(
    "GET",
    "/users/event_gist/search/{user_id}",
    py_code(
        """from memobase import MemoBaseClient
from memobase.core.blob import ChatBlob

client = MemoBaseClient(project_url='PROJECT_URL', api_key='PROJECT_TOKEN')
uid = client.add_user()
u = client.get_user(uid)

b = ChatBlob(messages=[
    {
        "role": "user",
        "content": "Hi, I'm here again"
    },
    {
        "role": "assistant",
        "content": "Hi, Gus! How can I help you?"
    }
])
u.insert(b)
u.flush(sync=True)

events = u.search_event_gist('query')
print(events)"""
    ),
)
