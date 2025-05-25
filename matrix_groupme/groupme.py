from faye import FayeClient
import httpx

import time


from faye import Extension, Message

class SigningExtension(Extension):
    def __init__(self, access_token: str):
        self.access_token = access_token

    async def process_outgoing(self, message: Message) -> Message | None:
        """
        Sign outgoing messages with the access token and current timestamp.
        """
        if not message.ext:
            message.ext = {}
        message.ext["access_token"] = self.access_token
        message.ext["timestamp"] = int(time.time())
        return message


class GroupMeClient:
    
    def __init__(self, access_token: str):
        self.access_token = access_token
        self.api_url = "https://api.groupme.com/v3"
        self.push_url = "https://push.groupme.com/faye"

        self.faye = FayeClient(self.push_url)
        self.faye.add_extension(SigningExtension(self.access_token))
        self.http = httpx.AsyncClient(
            params={"access_token": self.access_token},
        )
        self.me = {}

    async def connect(self):
        if not self.me:
            await self.get_me()

        await self.faye.connect()
        await self.faye.subscribe(f"/user/{self.me["id"]}", self.handle_user_message)

    async def get_me(self):
        """
        Fetch the current user's information.
        """
        response = await self.http.get(
            f"{self.api_url}/users/me",
        )

        if response.status_code == 200:
            self.me = response.json().get("response", {})
            print(self.me)
            return self.me
        else:
            raise Exception(f"Failed to fetch user info: {response.text}")

    async def handle_user_message(self, message: Message):
        print(f"Received message: {message.data}")
