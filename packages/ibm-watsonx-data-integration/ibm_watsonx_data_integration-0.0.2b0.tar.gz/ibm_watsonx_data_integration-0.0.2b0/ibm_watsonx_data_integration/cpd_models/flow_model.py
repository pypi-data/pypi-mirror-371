#  IBM Confidential
#  PID 5900-BAF
#  Copyright StreamSets Inc., an IBM Company 2025

"""Module containing Flow Model."""

from abc import ABC, abstractmethod
from ibm_watsonx_data_integration.common.models import BaseModel
from typing import Any
from typing_extensions import override


class Flow(BaseModel):
    """Represents a flow.

    Currently, this is an empty class used to indicate the required inheritance structure, primarily for job creation.
    A proper implementation will be addressed in the following ticket: https://streamsets.atlassian.net/browse/WSDK-335

    :meta: private
    """

    pass


class PayloadExtender(ABC):
    """Interface class for flows with custom payload logic.

    This interface should be implemented by any flow that requires custom logic for generating a job's payload.
    It ensures a consistent contract for flows that need to override the default payload creation behavior.

    :meta: private
    """

    @abstractmethod
    def extend(self, payload: dict[str, Any], flow: Flow) -> dict[str, Any]:
        """Here we should modify and return payload for job creation."""
        raise NotImplementedError


class DefaultFlowPayloadExtender(PayloadExtender):
    """Default payload extender which setup only `asset_ref`.

    :meta: private
    """

    @override
    def extend(self, payload: dict[str, Any], flow: Flow) -> dict[str, Any]:
        payload["asset_ref"] = flow.flow_id
        return payload
