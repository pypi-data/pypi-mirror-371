from __future__ import annotations
from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import Callable, List, Dict, Optional, Annotated, Union, Literal, Any
from google import genai
import time
import requests
import json as libJson


def get_time_ms() -> int:
    return time.time_ns() // 1_000_000


llm_provider_config: Optional[LLMConfig] = None


class AgentResponseContinue(BaseModel):
    type: Literal["continue"] = "continue"
    messages: List[str]


class AgentResponseFinish(BaseModel):
    type: Literal["finish"] = "finish"
    messages: Optional[List[str]] = None
    command: str


AgentResponse = Annotated[
    Union[AgentResponseContinue, AgentResponseFinish], Field(discriminator="type")
]


class OpenAIConfig(BaseModel):
    provider: Literal["openai"] = "openai"
    apiKey: str


class GoogleConfig(BaseModel):
    provider: Literal["google"] = "google"
    apiKey: str


LLMConfig = Annotated[
    Union[OpenAIConfig, GoogleConfig], Field(discriminator="provider")
]


class HTTPFacade:
    events: List[Event]

    def __init__(self, events: List[Event]):
        self.events = events

    def get(self, url: str, headers: Dict[str, str]) -> requests.Response:
        start = get_time_ms()
        reponse = requests.get(url=url, headers=headers)
        stop = get_time_ms()

        self.events.append(
            APICallEvent(
                payload=APICallEventPayload(
                    url=url,
                    requestMethod="GET",
                    requestHeaders=headers,
                    requestBody=None,
                    responseHeaders=reponse.headers,
                    responseStatusCode=reponse.status_code,
                    responseBody=reponse.text,
                    durationInMillis=stop - start,
                )
            )
        )
        return reponse

    def post(self, url: str, json: Any, headers: Dict[str, str]) -> requests.Response:
        start = get_time_ms()
        reponse = requests.post(url=url, json=json, headers=headers)
        stop = get_time_ms()

        self.events.append(
            APICallEvent(
                payload=APICallEventPayload(
                    url=url,
                    requestMethod="POST",
                    requestHeaders=headers,
                    requestBody=libJson.dumps(json),
                    responseHeaders=reponse.headers,
                    responseStatusCode=reponse.status_code,
                    responseBody=reponse.text,
                    durationInMillis=stop - start,
                )
            )
        )
        return reponse

    def put(self, url: str, json: Any, headers: Dict[str, str]) -> requests.Response:
        start = get_time_ms()
        reponse = requests.put(url=url, json=json, headers=headers)
        stop = get_time_ms()

        self.events.append(
            APICallEvent(
                payload=APICallEventPayload(
                    url=url,
                    requestMethod="PUT",
                    requestHeaders=headers,
                    requestBody=libJson.dumps(json),
                    responseHeaders=reponse.headers,
                    responseStatusCode=reponse.status_code,
                    responseBody=reponse.text,
                    durationInMillis=stop - start,
                )
            )
        )
        return reponse

    def delete(self, url: str, headers: Dict[str, str]) -> requests.Response:
        start = get_time_ms()
        reponse = requests.delete(url=url, headers=headers)
        stop = get_time_ms()

        self.events.append(
            APICallEvent(
                payload=APICallEventPayload(
                    url=url,
                    requestMethod="DELETE",
                    requestHeaders=headers,
                    requestBody=None,
                    responseHeaders=reponse.headers,
                    responseStatusCode=reponse.status_code,
                    responseBody=reponse.text,
                    durationInMillis=stop - start,
                )
            )
        )
        return reponse


class LLMCallEventPayload(BaseModel):
    prompt: str
    response: str
    model: str
    durationInMillis: int


class APICallEventPayload(BaseModel):
    url: str
    requestHeaders: Dict[str, str]
    requestMethod: str
    requestBody: Optional[str]
    responseHeaders: Dict[str, str]
    responseStatusCode: int
    responseBody: Optional[str]
    durationInMillis: int


class LLMCallEvent(BaseModel):
    type: Literal["llm_call"] = "llm_call"
    payload: LLMCallEventPayload


class APICallEvent(BaseModel):
    type: Literal["api_call"] = "api_call"
    payload: APICallEventPayload


Event = Annotated[Union[LLMCallEvent, APICallEvent], Field(discriminator="type")]


class GoogleLLMFacade:
    config: Optional[GoogleConfig]
    events: List[Event]
    client: Optional[genai.Client]

    def __init__(self, config: Optional[GoogleConfig], events: List[Event]):
        self.events = events
        self.config = config
        self.client = None

    def generate_content(
        self, model: str, contents: List[str]
    ) -> genai.types.GenerateContentResponse:
        if self.config is None:
            raise Exception("LLM requires config.")

        if self.client is None:
            self.client = genai.Client(api_key=self.config.apiKey)

        start = get_time_ms()
        response = self.client.models.generate_content(model=model, contents=contents)
        stop = get_time_ms()

        self.events.append(
            LLMCallEvent(
                payload=LLMCallEventPayload(
                    model=model,
                    prompt="\n".join(contents),
                    response=response.model_dump_json(),
                    durationInMillis=stop - start,
                )
            )
        )

        return response


class LLMFacade:
    google: GoogleLLMFacade

    def __init__(self, config: Optional[LLMConfig], events: List[Event]):
        self.google = GoogleLLMFacade(config=None, events=events)

        match config:
            case GoogleConfig() as googleConfig:
                self.google = GoogleLLMFacade(config=googleConfig, events=events)


class Context:
    messages: List[str]
    storeValue: Callable[[str, str], None]
    llm: LLMFacade
    http: HTTPFacade

    def __init__(
        self,
        messages: List[str],
        storeValue: Callable[[str, str], None],
        llm: LLMFacade,
        http: HTTPFacade,
    ) -> None:
        self.messages = messages
        self.storeValue = storeValue
        self.llm = llm
        self.http = http


class ProtocolAgentSendMessagePayload(BaseModel):
    message: str
    messages: List[str]


class ProtocolAgentGoToNextBlockPayload(BaseModel):
    message: Optional[str] = None
    messages: Optional[List[str]] = None
    nextBlockReferenceKey: str


class ProtocolAgentSendMessageCommand(BaseModel):
    type: Literal["send_message"] = "send_message"
    payload: ProtocolAgentSendMessagePayload


class ProtocolAgentGoToNextBlockCommand(BaseModel):
    type: Literal["go_to_next_block"] = "go_to_next_block"
    payload: ProtocolAgentGoToNextBlockPayload


ProtocolAgentCommand = Annotated[
    Union[
        ProtocolAgentSendMessageCommand,
        ProtocolAgentGoToNextBlockCommand,
    ],
    Field(discriminator="type"),
]


class ProtocolAgentResponse(BaseModel):
    command: ProtocolAgentCommand
    valuesToSave: Optional[Dict[str, str]] = None
    events: List[Event]


def configure_llm(config: LLMConfig) -> None:
    global llm_provider_config
    llm_provider_config = config


def start_agent(handler: Callable[[Context], AgentResponse]) -> FastAPI:
    app = FastAPI()

    @app.get("/")
    def handle() -> ProtocolAgentResponse:
        valueStorage: Dict[str, str] = {}
        events: List[Event] = []

        def storeValue(key: str, value: str) -> None:
            valueStorage[key] = value

        llm_facade = LLMFacade(config=llm_provider_config, events=events)
        http_facade = HTTPFacade(events=events)

        context = Context(
            messages=["1", "2"], storeValue=storeValue, llm=llm_facade, http=http_facade
        )
        result = handler(context)

        match result:
            case AgentResponseContinue(messages=messages):
                response = ProtocolAgentResponse(
                    command=ProtocolAgentSendMessageCommand(
                        payload=ProtocolAgentSendMessagePayload(
                            message="\n".join(messages), messages=messages
                        )
                    ),
                    valuesToSave=valueStorage,
                    events=events,
                )

            case AgentResponseFinish(messages=messages, command=command):
                payload = ProtocolAgentGoToNextBlockPayload(
                    nextBlockReferenceKey=command,
                )
                if messages != None:
                    payload.messages = messages
                    payload.message = "\n".join(messages)

                response = ProtocolAgentResponse(
                    command=ProtocolAgentGoToNextBlockCommand(payload=payload),
                    valuesToSave=valueStorage,
                    events=events,
                )

        print(response)
        return response

    return app
