# Copyright 2021-2025 ONDEWO GmbH
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from typing import Iterator

from google.protobuf.empty_pb2 import Empty
from ondewo.utils.async_base_services_interface import AsyncBaseServicesInterface

from ondewo.s2t.speech_to_text_pb2 import (
    AddDataToUserLanguageModelRequest,
    CreateUserLanguageModelRequest,
    DeleteUserLanguageModelRequest,
    ListS2tDomainsRequest,
    ListS2tDomainsResponse,
    ListS2tLanguageModelsRequest,
    ListS2tLanguageModelsResponse,
    ListS2tLanguagesRequest,
    ListS2tLanguagesResponse,
    ListS2tNormalizationPipelinesRequest,
    ListS2tNormalizationPipelinesResponse,
    ListS2tPipelinesRequest,
    ListS2tPipelinesResponse,
    S2tGetServiceInfoResponse,
    S2tPipelineId,
    Speech2TextConfig,
    TrainUserLanguageModelRequest,
    TranscribeFileRequest,
    TranscribeFileResponse,
    TranscribeStreamRequest,
    TranscribeStreamResponse,
)
from ondewo.s2t.speech_to_text_pb2_grpc import Speech2TextStub


class Speech2Text(AsyncBaseServicesInterface):
    """
    Exposes the s2t endpoints of ONDEWO s2t in a user-friendly way.

    See speech_to_text.proto.
    """

    @property
    def stub(self) -> Speech2TextStub:
        stub: Speech2TextStub = Speech2TextStub(channel=self.grpc_channel)
        return stub

    async def transcribe_file(self, request: TranscribeFileRequest) -> TranscribeFileResponse:
        response: TranscribeFileResponse = await self.stub.TranscribeFile(request)
        return response

    async def transcribe_stream(
        self,
        request_iterator: Iterator[TranscribeStreamRequest],
    ) -> Iterator[TranscribeStreamResponse]:
        response: Iterator[TranscribeStreamResponse] = await self.stub.TranscribeStream(request_iterator)
        return response

    async def get_s2t_pipeline(self, request: S2tPipelineId) -> Speech2TextConfig:
        response: Speech2TextConfig = await self.stub.GetS2tPipeline(request)
        return response

    async def create_s2t_pipeline(self, request: Speech2TextConfig) -> S2tPipelineId:
        response: S2tPipelineId = await self.stub.CreateS2tPipeline(request)
        return response

    async def delete_s2t_pipeline(self, request: S2tPipelineId) -> Empty:
        response: Empty = await self.stub.DeleteS2tPipeline(request)
        return response

    async def update_s2t_pipeline(self, request: Speech2TextConfig) -> Empty:
        response: Empty = await self.stub.UpdateS2tPipeline(request)
        return response

    async def list_s2t_pipelines(self, request: ListS2tPipelinesRequest) -> ListS2tPipelinesResponse:
        response: ListS2tPipelinesResponse = await self.stub.ListS2tPipelines(request)
        return response

    async def list_s2t_languages(self, request: ListS2tLanguagesRequest) -> ListS2tLanguagesResponse:
        response: ListS2tLanguagesResponse = await self.stub.ListS2tLanguages(request)
        return response

    async def list_s2t_domains(self, request: ListS2tDomainsRequest) -> ListS2tDomainsResponse:
        response: ListS2tDomainsResponse = await self.stub.ListS2tDomains(request)
        return response

    async def get_service_info(self, request: Empty) -> S2tGetServiceInfoResponse:
        response: S2tGetServiceInfoResponse = await self.stub.GetServiceInfo(request)
        return response

    async def list_s2t_language_models(self, request: ListS2tLanguageModelsRequest) -> ListS2tLanguageModelsResponse:
        response: ListS2tLanguageModelsResponse = await self.stub.ListS2tLanguageModels(request)
        return response

    async def create_user_language_model(self, request: CreateUserLanguageModelRequest) -> Empty:
        response: Empty = await self.stub.CreateUserLanguageModel(request)
        return response

    async def delete_user_language_model(self, request: DeleteUserLanguageModelRequest) -> Empty:
        response: Empty = await self.stub.DeleteUserLanguageModel(request)
        return response

    async def add_data_to_user_language_model(self, request: AddDataToUserLanguageModelRequest) -> Empty:
        response: Empty = await self.stub.AddDataToUserLanguageModel(request)
        return response

    async def train_user_language_model(self, request: TrainUserLanguageModelRequest) -> Empty:
        response: Empty = await self.stub.TrainUserLanguageModel(request)
        return response

    async def list_s2t_normalization_pipelines(
        self,
        request: ListS2tNormalizationPipelinesRequest,
    ) -> ListS2tNormalizationPipelinesResponse:
        response: ListS2tNormalizationPipelinesResponse = await self.stub.ListS2tNormalizationPipelines(request)
        return response
