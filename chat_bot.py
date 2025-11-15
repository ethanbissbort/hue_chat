import json
import os
import re
from json import JSONDecodeError
from typing import List

from openai import OpenAI

# Initialize client (will be created on first use if api_key not set at import time)
client = None


class ChatBot:
    def __init__(
            self,
            model="gpt-3.5-turbo",
            header="",
    ):
        """
        Keep track of messages submitted by the user and generate responses
        by calling the OpenAI API.

        Parameters
        ----------
        model
        header
            The header to prepend to the user's messages
        """
        self.model = model
        self.header = header

        self.messages = [{
            "role": "system",
            "content": header,
        }]

    def __call__(self, message: str) -> List[dict]:
        """
        Submit the header and all previous messages to the chat bot and return the response.

        Parameters
        ----------
        message
            A new message added by the user

        Returns
        -------
        The response from OpenAI as a list of dictionaries containing the color and light_id
        for each light.
        """
        global client

        # Initialize client on first use
        if client is None:
            api_key = os.environ.get("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY environment variable is not set")
            client = OpenAI(api_key=api_key)

        self.messages.append({
            "role": "user",
            "content": message,
        })

        result = client.chat.completions.create(
            model=self.model,
            messages=self.messages,
        )
        content = result.choices[0].message.content
        self.messages.append({
            "role": "assistant",
            "content": content,
        })
        try:
            return json.loads(trim(content))
        except JSONDecodeError:
            print(content)
            raise


def trim(s):
    s = re.sub(r"^[a-zA-Z \n:`.,]+", "", s)
    s = re.sub(r"[a-zA-Z \n:`.,]+$", "", s)
    return s