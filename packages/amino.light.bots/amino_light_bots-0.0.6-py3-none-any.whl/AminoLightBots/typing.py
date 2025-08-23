
import AminoLightPy
from typing import BinaryIO
from packaging import version
from AminoLightPy import SubClient
from .util import ContentType

from AminoLightPy.lib.util.objects import Message
from AminoLightPy.lib.util.objects import Event

class CustomMessage(Message):
    def __init__(self, data: dict, sub_client: SubClient, content_type: ContentType):
        super().__init__(data)

        self.sub_client = sub_client
        self.content_type = content_type.value

    def reply(self, message: str):
        response = self.sub_client.send_message(
            chatId=self.chatId,
            replyTo=self.messageId,
            message=message,
        )
        
        if version.parse(AminoLightPy.__version__) >= version.parse("0.2.2"):
            return CustomMessage(data=response.json, sub_client=self.sub_client)
        
        return response

    def get_sub_client(self):
        return self.sub_client

    def delete(self, as_admin=False):
        return self.sub_client.delete_message(
            chatId=self.chatId,
            messageId=self.messageId,
            asStaff=as_admin
        )

    def read(self):
        return self.sub_client.mark_as_read(
            chatId=self.chatId,
            replyTo=self.messageId,
        )
    
    def image(self, image_file: BinaryIO):
        response = self.sub_client.send_message(
            chatId=self.chatId,
            file=image_file,
        )

        if version.parse(AminoLightPy.__version__) >= version.parse("0.2.2"):
            return CustomMessage(data=response.json, sub_client=self.sub_client)
        
        return response
    
    
    def audio(self, audio_file: BinaryIO):
        response = self.sub_client.send_message(
            chatId=self.chatId,
            file=audio_file,
            fileType="audio"
        )

        if version.parse(AminoLightPy.__version__) >= version.parse("0.2.2"):
            return CustomMessage(data=response.json, sub_client=self.sub_client)
        
        return response

class CustomEvent(Event):
    def __init__(self, data: dict, content_type: ContentType):
        super().__init__(data)

        self.content_type = content_type