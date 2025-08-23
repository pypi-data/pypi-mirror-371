from faststream.rabbit import RabbitQueue, QueueType
from faststream.rabbit.schemas.queue import QuorumQueueArgs


table_moderator_queue = RabbitQueue(
    "moderator.table",
    queue_type=QueueType.QUORUM,
    durable=True,
    declare=True,
    arguments=QuorumQueueArgs(
        {
            "x-dead-letter-exchange": "dlx",
            "x-dead-letter-routing-key": "dlx.moderator.table",
            "x-dead-letter-strategy": "at-least-once",
            "x-overflow": "reject-publish",
        }
    ),
)

table_moderator_dlx_queue = RabbitQueue(
    "dlx.moderator.table",
    queue_type=QueueType.QUORUM,
    durable=True,
    declare=True,
)
