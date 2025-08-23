from typing import TypeVar

from pyagenity.utils import Message

from .agent_state import AgentState
from .base_context import BaseContextManager


S = TypeVar("S", bound=AgentState)


class MessageContextManager(BaseContextManager[S]):
    """
    Manages the context field for AI interactions.

    This class trims the context (message history) based on a maximum number of user messages,
    ensuring the first message (usually a system prompt) is always preserved.
    Generic over AgentState or its subclasses.
    """

    def __init__(self, max_messages: int = 10) -> None:
        """
        Initialize the MessageContextManager.

        Args:
            max_messages (int): Maximum number of
                user messages to keep in context. Default is 10.
        """
        self.max_messages = max_messages

    def _trim(self, messages: list[Message]) -> list[Message] | None:
        # check context is empty
        if not messages:
            return None

        if len(messages) <= self.max_messages:
            # no trimming needed
            return None

        # Keep first message (usually system prompt)
        # and recent messages
        first_message = messages[0]
        # now keep last messages from user set values
        # but we have to count from the user message
        final_messages = []
        user_message_count = 0

        for i in range(len(messages)):
            if messages[i].role == "user":
                user_message_count += 1

            if user_message_count > self.max_messages:
                break

            final_messages.append(messages[i])

        return [first_message, *final_messages]

    async def trim_context(self, state: S) -> S:
        """
        Trim the context in the given AgentState based on the maximum number of user messages.

        The first message (typically a system prompt) is always preserved. Only the most recent
        user messages up to `max_messages` are kept, along with the first message.

        Args:
            state (AgentState): The agent state containing the context to trim.

        Returns:
            S: The updated agent state with trimmed context.
        """
        messages = state.context
        trimmed_messages = self._trim(messages)
        if trimmed_messages is None:
            return state
        state.context = trimmed_messages
        return state
