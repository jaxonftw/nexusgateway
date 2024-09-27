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
FROM envoyproxy/envoy:v1.30-latest
COPY --from=builder /curve /target/wasm32-wasi/release/intelligent_prompt_gateway.wasm /etc/envoy/proxy-wasm-plugins/intelligent_prompt_gateway.wasm
# CMD ["envoy", "-c", "/etc/envoy/envoy.yaml"]
# CMD ["envoy", "-c", "/etc/envoy/envoy.yaml", "--log-level", "debug"]
CMD ["envoy", "-c", "/etc/envoy/envoy.yaml", "--component-log-level", "wasm:debug"]
