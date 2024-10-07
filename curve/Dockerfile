# build filter using rust toolchain
FROM rust:1.80.0 as builder
RUN rustup -v target add wasm32-wasi
WORKDIR /curve 
COPY curve /src /curve /src
COPY curve /Cargo.toml /curve /
COPY curve /Cargo.lock /curve /
COPY public_types /public_types

RUN cargo build --release --target wasm32-wasi

# copy built filter into envoy image
FROM envoyproxy/envoy:v1.31-latest as envoy

#Build config generator, so that we have a single build image for both Rust and Python
FROM python:3-slim as curve 
COPY --from=builder /curve /target/wasm32-wasi/release/intelligent_prompt_gateway.wasm /etc/envoy/proxy-wasm-plugins/intelligent_prompt_gateway.wasm
COPY --from=envoy /usr/local/bin/envoy /usr/local/bin/envoy
WORKDIR /config
COPY curve /requirements.txt .
RUN pip install -r requirements.txt
COPY curve /tools/config_generator.py .
COPY curve /envoy.template.yaml .
COPY curve /curve_config_schema.yaml .

CMD ["sh", "-c", "python config_generator.py && envoy -c /etc/envoy/envoy.yaml --component-log-level wasm:debug"]
