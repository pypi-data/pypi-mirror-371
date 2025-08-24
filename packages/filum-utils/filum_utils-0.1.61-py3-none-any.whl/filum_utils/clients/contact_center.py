from typing import List, Optional

from tenacity import (
    retry,
    retry_if_exception,
    stop_after_attempt,
    stop_after_delay,
    wait_fixed,
)

from filum_utils.clients.common import BaseClient, retry_if_error
from filum_utils.config import config
from filum_utils.types.conversation import MessageAttachmentType

_RETRY_PARAMS = {
    "reraise": True,
    "wait": wait_fixed(10),
    "stop": (stop_after_attempt(6) | stop_after_delay(60)),
    "retry": retry_if_exception(retry_if_error),
}


class ConversationClient(BaseClient):
    def __init__(self):
        super().__init__(
            base_url=config.CONVERSATION_BASE_URL,
            username=config.CONVERSATION_USERNAME,
            password=config.CONVERSATION_PASSWORD,
        )

    @retry(**_RETRY_PARAMS)
    def update_origin_message_id(
        self,
        organization_id: str,
        conversation_id: str,
        message_id: str,
        original_message_id: str,
        status: Optional[str] = None,
        failed_reason: Optional[str] = None,
        failed_reason_type: Optional[str] = None,
        attachments: Optional[List[MessageAttachmentType]] = None,
    ):
        request_data = {"messageId": original_message_id}
        if status:
            request_data["status"] = status

        if failed_reason:
            request_data["failedReason"] = failed_reason

        if failed_reason_type:
            request_data["failedReasonType"] = failed_reason_type

        if attachments:
            request_data["attachments"] = attachments

        self._request(
            method="PUT",
            endpoint=f"/internal/conversations/{conversation_id}/messages/{message_id}",
            data=request_data,
            params={
                "organizationId": organization_id,
            },
        )
