# Messages 


```python

# get template service
svc_template = di.get(DI_SERVICES).get(SVC_MESSAGE_TEMPLATE) # type: MessageTemplateService  
svc_queue = di.get(DI_SERVICES).get(SVC_MESSAGE_QUEUE).queue(msg) # type: MessageQueueService

# get message builder for template 'sample_template', lang='en' and channel SMTP (0)
builder = svc.get_builder('sample_template', 'en', 0)

if not builder is None:
    # template not found
    raise ValueError("invalid email template")

msg = builder.assemble(
    'from@mydomain.local',
    'to@mydomain.local',
    {
        '{name}': 'John Doe'
    })

# send message to queue
svc_queue.queue(msg)

```

