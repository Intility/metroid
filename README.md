# Metro for Python

### Subscribe to messages
1. Receive incoming message
3. Async handle message (Suggested: `apply_async()` and send the task to a worker)
3.1. We need to define an API (message.content, topic, subscription, sequence_number)
4. Defer message

@task
def my_task():
    pass

my_task.apply_async()

### Worker
1. `my_func(message.content, topic, subscription, sequence_number)`
2. Does work with content
3. Calls `Metro.defer_message(topic, subscription, sequence_number)`
3.1 `defer_message` complete message



### 2 APIer
1. Get all deferred tasks Azure with 30 sec cache
2. Start task with user.is_admin check
