import uuid  # type: ignore
import json
import logging

from fastapi import Request
from typing import Any, Optional, List, Union  # type: ignore
from langchain_openai.chat_models import ChatOpenAI
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import settings
from src.chat.helpers import exa_search, get_generated_image
from src.chat.services import map_all_urls, contains_any_url, update_chat_image_chat_id
from src.chat.models import ChatMessage, ChatRole

logger = logging.getLogger(__name__)
GPT4 = "gpt-4o"
GPT3 = "gpt-3.5-turbo-0125"


class Chat:
    def __init__(self, db: AsyncSession, user_id: uuid.UUID):
        self.db = db
        self.user_id = user_id
        self.messages: list[ChatMessage] = []
        self.tools = [exa_search, get_generated_image]
        self.chat_model = ChatOpenAI(
            openai_api_key=settings.OPENAI_API_KEY, model=GPT4
        ).bind_tools(self.tools)

    async def get_messages(self, db: AsyncSession):
        stmt = (
            select(ChatMessage)
            .where(ChatMessage.user_id == self.user_id)
            .order_by(ChatMessage.created_at.asc())
        )
        result = await db.execute(stmt)
        return result.scalars().all()

    async def initialize_task_chat(
        self, db: AsyncSession, stream: bool = False
    ) -> dict:
        try:
            system_prompt = (
                "You are Sales chatbot AI conversational assistant."
                "You are an expert in business strategy. "
                "Done share any text from previous messages with the user."
                "Greet the user and ask them how you can help them."
                "Keep the conversation short and concise along with making it interesting."
            )

            # This is for system prompt
            message = await self.add_system_message(
                db=db,
                content=system_prompt,
                commit=True,
                user_id=self.user_id,
            )

            message_history = await self.get_message_history()

            logger.debug(f"message_history: {message_history}")

            if stream:

                def response():
                    content = ""
                    for chunk in self.chat_model.astream(message_history):
                        content += chunk
                        yield chunk
                    message.content = content
                    db.add(message)

                return response()
            else:
                completion = await self.chat_model.ainvoke(message_history)

                message = await self.add_assistant_message(
                    db=db, content=completion.content, commit=True, user_id=self.user_id
                )
                logger.debug(f"message: {message}")

                await db.commit()
                await db.refresh(message)

                return message
        except Exception as e:
            logger.error(f"Error: {e}")
            raise

    async def add_message(
        self,
        db: AsyncSession,
        role: str,
        content: str,
        user_id: uuid.UUID,
        commit: bool = False,
    ):
        try:
            logger.info("I am here in add_message !!!")
            message = ChatMessage(user_id=user_id, role=role, message=content)

            db.add(message)

            if commit:
                await db.commit()
                await db.refresh(message)
            else:
                await db.flush()

            self.messages.append(message)
            return message

        except Exception as e:
            logger.error(f"Error adding message: {e}")
            raise e

    async def add_system_message(
        self,
        db: AsyncSession,
        content: str,
        commit: bool = True,
        user_id: Optional[uuid.UUID] = None,
    ):
        return await self.add_message(
            db=db, role="system", content=content, commit=commit, user_id=user_id
        )

    async def add_user_message(
        self,
        db: AsyncSession,
        content: str,
        commit: bool = True,
        user_id: Optional[uuid.UUID] = None,
    ):
        return await self.add_message(
            db=db, role="user", content=content, commit=commit, user_id=user_id
        )

    async def add_assistant_message(
        self,
        db: AsyncSession,
        content: str,
        commit: bool = True,
        user_id: Optional[uuid.UUID] = None,
    ):
        return await self.add_message(
            db=db, role="assistant", content=content, commit=commit, user_id=user_id
        )

    async def get_all_messages_roles(self, user_id: uuid.UUID):
        stmt = (
            select(ChatMessage)
            .where(
                (ChatMessage.user_id == user_id)
                & (
                    ChatMessage.role.in_(
                        [ChatRole.ASSISTANT, ChatRole.USER, ChatRole.SYSTEM]
                    )
                )
            )
            .order_by(ChatMessage.created_at.asc())
        )
        result = await self.db.execute(stmt)
        messages = result.scalars().all()

        return list(messages) if messages else None

    async def get_message_history(self):
        message_history: list[HumanMessage | AIMessage | SystemMessage] = []
        messages = await self.get_all_messages_roles(user_id=self.user_id)
        for message in messages:
            if message.role == "user":
                message_history.append(HumanMessage(content=message.message))
            elif message.role == "assistant":
                message_history.append(AIMessage(content=message.message))
            elif message.role == "system":
                message_history.append(SystemMessage(content=message.message))
        return message_history

    async def task_chat(
        self,
        request: Request,
        db: AsyncSession,
        user_message: str,
        stream: bool = False,
    ):
        try:
            logger.debug(f"user_message: {user_message}")
            await self.add_user_message(
                db=db, content=user_message, user_id=self.user_id
            )

            message_history = await self.get_message_history()

            if stream:

                async def response():
                    content = ""
                    async for chunk in self.chat_model.astream(message_history):
                        content += chunk
                        yield chunk
                    message.content = content
                    db.add(message)

                return response()

            message = await self.process_completion(
                request, db, message_history, self.user_id
            )
            await db.commit()
            await db.refresh(message)

            return message

        except Exception as e:
            logger.error(f"Error: {e}")
            raise

    async def process_completion(
        self,
        request: Request,
        db: AsyncSession,
        message_history: List[Union[HumanMessage, AIMessage, SystemMessage]],
        user_id: uuid.UUID,
    ):
        try:
            while True:
                completion = await self.chat_model.ainvoke(message_history)
                logger.debug(f"completion: {completion}")

                tool_calls = completion.tool_calls
                if not tool_calls:
                    break

                message_history.append(completion)
                for tool_call in tool_calls:
                    if selected_tool := {
                        "exa_search": exa_search,
                        "get_generated_image": get_generated_image,
                    }.get(tool_call["name"].lower()):
                        tool_output = await selected_tool.ainvoke(tool_call["args"])
                        message_history.append(
                            ToolMessage(tool_output, tool_call_id=tool_call["id"])
                        )

            chat_image_ids = []
            if contains_any_url(
                completion.content, "https://oaidalleapiprodscus.blob.core.windows.net"
            ):
                result = await map_all_urls(request, db, completion.content)
                url_mapping = result["url_mapping"]
                chat_image_ids = result["chat_image_ids"]

                for original_url, local_url in url_mapping.items():
                    completion.content = completion.content.replace(
                        original_url, local_url
                    )

            message = await self.add_assistant_message(
                db=db, content=completion.content, commit=True, user_id=user_id
            )
            logger.debug(f"Message: {message}")

            if chat_image_ids:
                for chat_image_id in chat_image_ids:
                    await update_chat_image_chat_id(db, chat_image_id, message.id)

            return message

        except Exception as e:
            logger.error(f"Error processing completion: {e}")
            raise

    async def get_all_messages(self):
        stmt = (
            select(ChatMessage)
            .where(
                (ChatMessage.user_id == self.user_id)
                & (ChatMessage.role.in_([ChatRole.ASSISTANT, ChatRole.USER]))
            )
            .order_by(ChatMessage.created_at.asc())
        )
        result = await self.db.execute(stmt)
        messages = result.scalars().all()
        logger.debug(f"messages: {messages}")
        return list(messages) if messages else None

    # TODO: This need to be discussed if we need Vision feature in the app
    async def vision_chat(
        self,
        db: AsyncSession,
        user_message: Union[str, Any],
        image_data: str,
    ):
        try:
            chat_model = ChatOpenAI(
                openai_api_key=settings.OPENAI_API_KEY, model=GPT4, temperature=0.7
            )

            message_history = await self.get_message_history()

            message = [
                {"type": "image_url", "image_url": {"url": image_data}},
                {"type": "text", "text": user_message},
            ]

            message_history = message_history[-4:]

            message_history.append(HumanMessage(content=message))

            completion = await chat_model.ainvoke(message_history)

            message_history.append(AIMessage(content=completion.content))
            message_history.append(
                HumanMessage(
                    content=self.talking_prompt(image_review=completion.content)
                )
            )

            talk_completion = await chat_model.ainvoke(message_history)

            final_completion = json.dumps(
                [
                    # this will be dislayed in chat modal
                    {"reviews": completion.content},
                    # elevel labs to get voice response
                    {"conversation": talk_completion.content},
                ]
            )

            await self.add_user_message(
                db=db,
                content=str(message[1]["text"]),
                commit=True,
                user_id=self.user_id,
            )
            message = await self.add_assistant_message(
                db=db, content=final_completion, commit=True, user_id=self.user_id
            )

            await db.commit()
            await db.refresh(message)

            return message

        except Exception as e:
            logger.error(f"Error: {e}")
            raise
