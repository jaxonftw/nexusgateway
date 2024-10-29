use std::{collections::HashMap, time::Duration};

use common::{
    common_types::{
        open_ai::{
            to_server_events, CurveState, ChatCompletionStreamResponse, ChatCompletionsRequest,
        },
        PromptGuardRequest, PromptGuardTask,
    },
    consts::{
        CURVE_FC_MODEL_NAME, CURVE_INTERNAL_CLUSTER_NAME, CURVE_STATE_HEADER,
        CURVE_UPSTREAM_HOST_HEADER, ASSISTANT_ROLE, CHAT_COMPLETIONS_PATH, GUARD_INTERNAL_HOST,
        HEALTHZ_PATH, REQUEST_ID_HEADER, TOOL_ROLE, USER_ROLE,
    },
    errors::ServerError,
    http::{CallArgs, Client},
};
use http::StatusCode;
use log::{debug, trace, warn};
use proxy_wasm::{traits::HttpContext, types::Action};
use serde_json::Value;

use crate::stream_context::{ResponseHandlerType, StreamCallContext, StreamContext};

// HttpContext is the trait that allows the Rust code to interact with HTTP objects.
impl HttpContext for StreamContext {
    // Envoy's HTTP model is event driven. The WASM ABI has given implementors events to hook onto
    // the lifecycle of the http request and response.
    fn on_http_request_headers(&mut self, _num_headers: usize, _end_of_stream: bool) -> Action {
        // Remove the Content-Length header because further body manipulations in the gateway logic will invalidate it.
        // Server's generally throw away requests whose body length do not match the Content-Length header.
        // However, a missing Content-Length header is not grounds for bad requests given that intermediary hops could
        // manipulate the body in benign ways e.g., compression.
        self.set_http_request_header("content-length", None);

        let request_path = self.get_http_request_header(":path").unwrap_or_default();
        if request_path == HEALTHZ_PATH {
            if self.embeddings_store.is_none() {
                self.send_http_response(503, vec![], None);
            } else {
                self.send_http_response(200, vec![], None);
            }
            return Action::Continue;
        }

        self.is_chat_completions_request = request_path == CHAT_COMPLETIONS_PATH;

        trace!(
            "on_http_request_headers S[{}] req_headers={:?}",
            self.context_id,
            self.get_http_request_headers()
        );

        self.request_id = self.get_http_request_header(REQUEST_ID_HEADER);

        Action::Continue
    }

    fn on_http_request_body(&mut self, body_size: usize, end_of_stream: bool) -> Action {
        // Let the client send the gateway all the data before sending to the LLM_provider.
        // TODO: consider a streaming API.
        if !end_of_stream {
            return Action::Pause;
        }

        if body_size == 0 {
            return Action::Continue;
        }

        self.request_body_size = body_size;

        trace!(
            "on_http_request_body S[{}] body_size={}",
            self.context_id,
            body_size
        );

        let body_bytes = match self.get_http_request_body(0, body_size) {
            Some(body_bytes) => body_bytes,
            None => {
                self.send_server_error(
                    ServerError::LogicError(format!(
                        "Failed to obtain body bytes even though body_size is {}",
                        body_size
                    )),
                    None,
                );
                return Action::Pause;
            }
        };

        debug!(
            "developer => curve: {}",
            String::from_utf8_lossy(&body_bytes)
        );

        // Deserialize body into spec.
        // Currently OpenAI API.
        let deserialized_body: ChatCompletionsRequest = match serde_json::from_slice(&body_bytes) {
            Ok(deserialized) => deserialized,
            Err(e) => {
                self.send_server_error(
                    ServerError::Deserialization(e),
                    Some(StatusCode::BAD_REQUEST),
                );
                return Action::Pause;
            }
        };

        self.curve _state = match deserialized_body.metadata {
            Some(ref metadata) => {
                if metadata.contains_key(CURVE_STATE_HEADER) {
                    let curve _state_str = metadata[CURVE_STATE_HEADER].clone();
                    let curve _state: Vec<CurveState> = serde_json::from_str(&curve _state_str).unwrap();
                    Some(curve _state)
                } else {
                    None
                }
            }
            None => None,
        };

        self.streaming_response = deserialized_body.stream;

        let last_user_prompt = match deserialized_body
            .messages
            .iter()
            .filter(|msg| msg.role == USER_ROLE)
            .last()
        {
            Some(content) => content,
            None => {
                warn!("No messages in the request body");
                return Action::Continue;
            }
        };

        self.user_prompt = Some(last_user_prompt.clone());

        let user_message_str = self.user_prompt.as_ref().unwrap().content.clone();

        let prompt_guard_jailbreak_task = self
            .prompt_guards
            .input_guards
            .contains_key(&common::configuration::GuardType::Jailbreak);

        self.chat_completions_request = Some(deserialized_body);

        if !prompt_guard_jailbreak_task {
            debug!("Missing input guard. Making inline call to retrieve embeddings");
            let callout_context = StreamCallContext {
                response_handler_type: ResponseHandlerType::CurveGuard,
                user_message: user_message_str.clone(),
                prompt_target_name: None,
                request_body: self.chat_completions_request.as_ref().unwrap().clone(),
                similarity_scores: None,
                upstream_cluster: None,
                upstream_cluster_path: None,
            };
            self.get_embeddings(callout_context);
            return Action::Pause;
        }

        let get_prompt_guards_request = PromptGuardRequest {
            input: self
                .user_prompt
                .as_ref()
                .unwrap()
                .content
                .as_ref()
                .unwrap()
                .clone(),
            task: PromptGuardTask::Jailbreak,
        };

        let json_data: String = match serde_json::to_string(&get_prompt_guards_request) {
            Ok(json_data) => json_data,
            Err(error) => {
                self.send_server_error(ServerError::Serialization(error), None);
                return Action::Pause;
            }
        };

        let mut headers = vec![
            (CURVE_UPSTREAM_HOST_HEADER, GUARD_INTERNAL_HOST),
            (":method", "POST"),
            (":path", "/guard"),
            (":authority", GUARD_INTERNAL_HOST),
            ("content-type", "application/json"),
            ("x-envoy-max-retries", "3"),
            ("x-envoy-upstream-rq-timeout-ms", "60000"),
        ];

        if self.request_id.is_some() {
            headers.push((REQUEST_ID_HEADER, self.request_id.as_ref().unwrap()));
        }

        let call_args = CallArgs::new(
            CURVE_INTERNAL_CLUSTER_NAME,
            "/guard",
            headers,
            Some(json_data.as_bytes()),
            vec![],
            Duration::from_secs(5),
        );
        let call_context = StreamCallContext {
            response_handler_type: ResponseHandlerType::CurveGuard,
            user_message: self.user_prompt.as_ref().unwrap().content.clone(),
            prompt_target_name: None,
            request_body: self.chat_completions_request.as_ref().unwrap().clone(),
            similarity_scores: None,
            upstream_cluster: None,
            upstream_cluster_path: None,
        };

        if let Err(e) = self.http_call(call_args, call_context) {
            self.send_server_error(ServerError::HttpDispatch(e), None);
        }

        Action::Pause
    }

    fn on_http_response_headers(&mut self, _num_headers: usize, _end_of_stream: bool) -> Action {
        trace!(
            "on_http_response_headers recv [S={}] headers={:?}",
            self.context_id,
            self.get_http_response_headers()
        );
        // delete content-lenght header let envoy calculate it, because we modify the response body
        // that would result in a different content-length
        self.set_http_response_header("content-length", None);
        Action::Continue
    }

    fn on_http_response_body(&mut self, body_size: usize, end_of_stream: bool) -> Action {
        trace!(
            "recv [S={}] bytes={} end_stream={}",
            self.context_id,
            body_size,
            end_of_stream
        );

        if !self.is_chat_completions_request {
            debug!("non-streaming request");
            return Action::Continue;
        }

        let body = if self.streaming_response {
            let streaming_chunk = match self.get_http_response_body(0, body_size) {
                Some(chunk) => chunk,
                None => {
                    warn!(
                        "response body empty, chunk_start: {}, chunk_size: {}",
                        0, body_size
                    );
                    return Action::Continue;
                }
            };

            if streaming_chunk.len() != body_size {
                warn!(
                    "chunk size mismatch: read: {} != requested: {}",
                    streaming_chunk.len(),
                    body_size
                );
            }

            streaming_chunk
        } else {
            debug!("non streaming response bytes read: 0:{}", body_size);
            match self.get_http_response_body(0, body_size) {
                Some(body) => body,
                None => {
                    warn!("non streaming response body empty");
                    return Action::Continue;
                }
            }
        };

        let body_utf8 = match String::from_utf8(body) {
            Ok(body_utf8) => body_utf8,
            Err(e) => {
                debug!("could not convert to utf8: {}", e);
                return Action::Continue;
            }
        };

        if self.streaming_response {
            trace!("streaming response");

            if self.tool_calls.is_some() && !self.tool_calls.as_ref().unwrap().is_empty() {
                let chunks = vec![
                    ChatCompletionStreamResponse::new(
                        None,
                        Some(ASSISTANT_ROLE.to_string()),
                        Some(CURVE_FC_MODEL_NAME.to_string()),
                        self.tool_calls.to_owned(),
                    ),
                    ChatCompletionStreamResponse::new(
                        self.tool_call_response.clone(),
                        Some(TOOL_ROLE.to_string()),
                        Some(CURVE_FC_MODEL_NAME.to_string()),
                        None,
                    ),
                ];

                let mut response_str = to_server_events(chunks);
                // append the original response from the model to the stream
                response_str.push_str(&body_utf8);
                self.set_http_response_body(0, body_size, response_str.as_bytes());
                self.tool_calls = None;
            }
        } else if let Some(tool_calls) = self.tool_calls.as_ref() {
            if !tool_calls.is_empty() {
                if self.curve _state.is_none() {
                    self.curve _state = Some(Vec::new());
                }

                let mut data = serde_json::from_str(&body_utf8).unwrap();
                // use serde::Value to manipulate the json object and ensure that we don't lose any data
                if let Value::Object(ref mut map) = data {
                    // serialize curve  state and add to metadata
                    let metadata = map
                        .entry("metadata")
                        .or_insert(Value::Object(serde_json::Map::new()));
                    if metadata == &Value::Null {
                        *metadata = Value::Object(serde_json::Map::new());
                    }

                    let fc_messages = vec![
                        self.generate_toll_call_message(),
                        self.generate_api_response_message(),
                    ];
                    let fc_messages_str = serde_json::to_string(&fc_messages).unwrap();
                    let curve _state = HashMap::from([("messages".to_string(), fc_messages_str)]);
                    let curve _state_str = serde_json::to_string(&curve _state).unwrap();
                    metadata.as_object_mut().unwrap().insert(
                        CURVE_STATE_HEADER.to_string(),
                        serde_json::Value::String(curve _state_str),
                    );
                    let data_serialized = serde_json::to_string(&data).unwrap();
                    debug!("curve <= developer: {}", data_serialized);
                    self.set_http_response_body(0, body_size, data_serialized.as_bytes());
                };
            }
        }

        trace!("recv [S={}] end_stream={}", self.context_id, end_of_stream);

        Action::Continue
    }
}
