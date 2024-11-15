# build filter using rust toolchain
FROM rust:1.82.0 as builder
RUN rustup -v target add wasm32-wasip1
WORKDIR /curve 
COPY crates .

RUN cd prompt_gateway && cargo build --release --target wasm32-wasip1
RUN cd llm_gateway && cargo build --release --target wasm32-wasip1

# copy built filter into envoy image
FROM envoyproxy/envoy:v1.32-latest as envoy

#Build config generator, so that we have a single build image for both Rust and Python
FROM python:3.12-slim as curve 

RUN apt-get update && apt-get install -y gettext-base curl supervisor && apt-get clean && rm -rf /var/lib/apt/lists/*

COPY --from=builder /curve /target/wasm32-wasip1/release/prompt_gateway.wasm /etc/envoy/proxy-wasm-plugins/prompt_gateway.wasm
COPY --from=builder /curve /target/wasm32-wasip1/release/llm_gateway.wasm /etc/envoy/proxy-wasm-plugins/llm_gateway.wasm
COPY --from=envoy /usr/local/bin/envoy /usr/local/bin/envoy
WORKDIR /app
COPY curve /requirements.txt .
RUN pip install -r requirements.txt
COPY curve /tools/cli/config_generator.py .
COPY curve /envoy.template.yaml .
COPY curve /curve_config_schema.yaml .
COPY curve /supervisord.conf /etc/supervisor/conf.d/supervisord.conf
COPY curve /stream_traces.py .

RUN pip install requests
RUN touch /var/log/envoy.log

ENTRYPOINT ["supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
