import os
import logging
from typing import cast
from dotenv import load_dotenv

load_dotenv()

import boto3
import chainlit as cl
import chainlit.data as cl_data
from chainlit.logger import logger as cl_logger
from chainlit.data.dynamodb import DynamoDBDataLayer
from chainlit.data.storage_clients import S3StorageClient
from langchain_core.messages import HumanMessage, AIMessage
from langchain_aws.chat_models import ChatBedrockConverse

from src.logger import get_logger
from src.llm import BedrockLLM

MODEL_ID = os.environ.get("MODEL_ID", "")
assert MODEL_ID, "MODEL_ID environment variable not set"

logger = get_logger("app")


def init_history_persistent_layer():
    """Initialize the history persistent layer for the ChainLit defaults."""

    # set aws profile
    AWS_PROFILE_NAME = os.environ.get("AWS_PROFILE_NAME", None)
    logger.info(f"AWS_PROFILE_NAME: {AWS_PROFILE_NAME}")
    session = boto3.Session(profile_name=AWS_PROFILE_NAME)

    # set history storage client
    HISTORY_BUCKET_NAME = os.environ.get("HISTORY_BUCKET_NAME", None)
    assert HISTORY_BUCKET_NAME, "HISTORY_BUCKET_NAME environment variable not set"
    storage_client = S3StorageClient(bucket=HISTORY_BUCKET_NAME)
    storage_client.client = session.client("s3")

    # set history persistent db layer
    HISTORY_TABLE_NAME = os.environ.get("HISTORY_TABLE_NAME", None)
    assert HISTORY_TABLE_NAME, "HISTORY_TABLE_NAME environment variable not set"
    cl_data._data_layer = DynamoDBDataLayer(
        table_name=HISTORY_TABLE_NAME,
        client=session.client("dynamodb"),
        storage_provider=storage_client,
    )
    cl_logger.getChild("DynamoDB").setLevel(logging.DEBUG)


# Uncomment the following line if you want to use the [data persistent layer](https://docs.chainlit.io/data-persistence/custom)
# init_history_persistent_layer()


# Uncommnet the following block if you want to use the [ChainLit OAuth](https://docs.chainlit.io/authentication/oauth)
#
# @cl.oauth_callback
# async def oauth_callback(
#     provider_id: str,
#     token: str,
#     raw_user_data: dict[str, str],
#     default_user: cl.User,
#     id_token: Optional[str] = None,
# ) -> Optional[cl.User]:
#     """Callback for Cognito OAuth providers."""
#
#     logger.debug(
#         f"OAuth callback for provider {provider_id}, "
#         f"token: {token}, "
#         f"raw_user_data: {raw_user_data}, "
#         f"id_token: {id_token}"
#     )
#     return default_user


@cl.on_chat_start
async def on_chat_start():
    MODEL_ID = os.environ.get("MODEL_ID", None)
    assert MODEL_ID, "MODEL_ID environment variable not set"

    model = BedrockLLM(
        model=MODEL_ID,
        aws_profile_name=os.environ.get("AWS_PROFILE_NAME", None),
    )
    cl.user_session.set("llm", model.model)
    cl.user_session.set("history-cache", [])


@cl.on_message
async def on_message(message: cl.Message):
    llm = cast(ChatBedrockConverse, cl.user_session.get("llm"))
    history_cache = cast(list, cl.user_session.get("history-cache"))
    history_cache.append(HumanMessage(content=message.content))

    msg = cl.Message(content="")
    for chunk in llm.stream(history_cache):
        content = chunk.content
        if content:
            await msg.stream_token(cast(dict, content)[0].get("text", ""))
            if chunk.response_metadata.get("stopReason", "") == "end_turn":
                history_cache.append(AIMessage(content=msg.content))
                cl.user_session.set("history-cache", history_cache)
    await msg.update()
