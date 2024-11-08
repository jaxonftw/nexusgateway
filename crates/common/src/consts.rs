pub const DEFAULT_EMBEDDING_MODEL: &str = "curvelaboratory/bge-large-en-v1.5";
pub const DEFAULT_INTENT_MODEL: &str = "curvelaboratory/bart-large-mnli";
pub const DEFAULT_PROMPT_TARGET_THRESHOLD: f64 = 0.8;
pub const DEFAULT_HALLUCINATED_THRESHOLD: f64 = 0.25;
pub const RATELIMIT_SELECTOR_HEADER_KEY: &str = "x-curve -ratelimit-selector";
pub const SYSTEM_ROLE: &str = "system";
pub const USER_ROLE: &str = "user";
pub const TOOL_ROLE: &str = "tool";
pub const ASSISTANT_ROLE: &str = "assistant";
pub const CURVE_FC_REQUEST_TIMEOUT_MS: u64 = 120000; // 2 minutes
pub const MODEL_SERVER_NAME: &str = "server";
pub const ZEROSHOT_INTERNAL_HOST: &str = "zeroshot";
pub const CURVE_FC_INTERNAL_HOST: &str = "curve _fc";
pub const HALLUCINATION_INTERNAL_HOST: &str = "hallucination";
pub const EMBEDDINGS_INTERNAL_HOST: &str = "embeddings";
pub const GUARD_INTERNAL_HOST: &str = "guard";
pub const CURVE_ROUTING_HEADER: &str = "x-curve -llm-provider";
pub const MESSAGES_KEY: &str = "messages";
pub const CURVE_PROVIDER_HINT_HEADER: &str = "x-curve -llm-provider-hint";
pub const CHAT_COMPLETIONS_PATH: &str = "/v1/chat/completions";
pub const HEALTHZ_PATH: &str = "/healthz";
pub const CURVE_STATE_HEADER: &str = "x-curve -state";
pub const CURVE_FC_MODEL_NAME: &str = "Curve-Function-1.5B";
pub const REQUEST_ID_HEADER: &str = "x-request-id";
pub const TRACE_PARENT_HEADER: &str = "traceparent";
pub const CURVE_INTERNAL_CLUSTER_NAME: &str = "curve _internal";
pub const CURVE_UPSTREAM_HOST_HEADER: &str = "x-curve -upstream";
pub const CURVE_LLM_UPSTREAM_LISTENER: &str = "curve _llm_listener";
pub const CURVE_MODEL_PREFIX: &str = "Curve";
pub const HALLUCINATION_TEMPLATE: &str =
    "It seems I'm missing some information. Could you provide the following details ";
