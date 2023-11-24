from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import StrOutputParser
from langchain.schema.runnable import Runnable
from langchain.schema.runnable.config import RunnableConfig

import chainlit as cl

@cl.on_chat_start
async def on_chat_start():
    model = ChatOpenAI(streaming=True)
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "I would like you to create a simple melody in LilyPond notation. The melody should be suitable for beginners, consisting of a single line and not exceeding 8 bars in length. Please use a common time signature (like 4/4) and a key that is easy for beginners (such as C major). The melody should be rhythmic and easy to follow, with a mix of quarter notes and half notes, and should stay within one octave range. Avoid complex rhythms or accidentals. Please also add basic dynamic markings (like forte or piano) and tempo indication at the beginning.",
            ),
            ("human", "{question}"),
        ]
    )
    runnable = prompt | model | StrOutputParser()
    cl.user_session.set("runnable", runnable)


@cl.on_message
async def on_message(message: cl.Message):
    runnable = cl.user_session.get("runnable")  # type: Runnable

    msg = cl.Message(content="")

    async for chunk in runnable.astream(
        {"question": message.content},
        config=RunnableConfig(callbacks=[cl.LangchainCallbackHandler()]),
    ):
        await msg.stream_token(chunk)

    await msg.send()