.. _life_of_a_request:

Life of a Request
=================

Below we describe the events in the life of a request passing through an Curve gateway instance. We first
describe how Curve fits into the request path and then the internal events that take place following
the arrival of a request at Curve from downtream clients. We follow the request until the corresponding
dispatch upstream and the response path.

.. image:: /_static/img/network-topology-ingress-egress.jpg
   :width: 100%
   :align: center

Terminology
-----------

Curve uses the following terms through its' codebase and documentation:

* *Listeners*: The Curve primitive responsible for binding to an IP/port, accepting new HTTP connections and orchestrating
  the downstream facing aspects of prompt processing. Curve relies almostly exclusively on `Envoy's Listener subsystem <curve _overview_listeners>`_.
* *Downstream*: an entity connecting to Curve. This may be another AI agent (side car or networked) or a remote client.
* *LLM Providers*: a set of upstream LLMs (API-based or network nodes) that Curve routes/forwards user and application-specific prompts to.
  Curve offers a simply abstract to call different LLMs via model-id, add LLM specific retry, failover and routing capabilities.
  Curve build's on top of Envoy's `Cluster substem <https://www.envoyproxy.io/docs/envoy/latest/intro/curve _overview/upstream/cluster_manager#curve -overview-cluster-manager>`
* *Upstream*: A set of hosts that can recieve traffic from an instance of the Curve gateway.
* *Prompt Targets*: A core primitive offered in Curve. Prompt targets are endpoints that receive prompts that are processed by Curve.
  For example, Curve enriches incoming prompts with metadata like knowing when a request is a follow-up or clarifying prompt so that you can
  build faster, more accurate RAG apps. To support agentic apps, like scheduling travel plans or sharing comments on a document - via prompts,

Network topology
----------------

How a request flows through the components in a network (including Curve) depends on the network’s topology.
Curve can be used in a wide variety of networking topologies. We focus on the inner operation of Curve below,
but briefly we address how Curve relates to the rest of the network in
this section.

* Ingress listeners take requests from upstream clients like a web UI or clients that forward prompts to you local application
  Responses from the local application flow back through Curve to the downstream.

* Egress listeners take requests from the local application and forward them to LLMs. These receiving nodes
  will also be typically running Curve and accepting the request via their ingress listeners.

.. image:: /_static/img/network-topology-ingress-egress.jpg
   :width: 100%
   :align: center

In practice, Curve can be deployed on the edge and as an internal load balancer between AI agents. A request path may
traverse multiple Curve gateways:

.. image:: /_static/img/network-topology-agent.jpg
   :width: 100%
   :align: center

Configuration
-------------

Today, only support a static bootstrap configuration file for simplicity today:

.. literalinclude:: /_config/getting-started.yml
    :language: yaml


High level curve itecture
-----------------------

The request processing path in Curve has two main parts:

* :ref:`Listener subsystem <curve _overview_listeners>` which handles **downstream** request
  processing. It is also responsible for managing the downstream request lifecycle and for the
  response path to the client. The downstream HTTP/2 codec lives here.
* :ref:`Prompt subsystem <curve _overview_prompt_handling>` which is responsible for selecting and
  processing  the **upstream** connection to an endpoint. This is where knowledge of targets and
  endpoint health, load balancing and connection pooling exists. The upstream HTTP/2 codec lives
  here.

The two subsystems are bridged with the HTTP router filter, which forwards the HTTP request from
downstream to upstream.

Curve utilizes `Envoy event-based thread model <https://blog.envoyproxy.io/envoy-threading-model-a8d44b922310>`_.
A main thread is responsible forthe server lifecycle, configuration processing, stats, etc. and some number
of :ref:`worker threads <curve _overview_threading>` process requests. All threads operate around an event
loop (`libevent <https://libevent.org/>`_) and any given downstream TCP connection will be handled by exactly
one worker thread for its lifetime. Each worker thread maintains its own pool of TCP connections to upstream
endpoints. Today, Curve implemenents its core functionality around prompt handling in worker threads.

Worker threads rarely share state and operate in a trivially parallel fashion. This threading model
enables scaling to very high core count CPUs.

Request Flow
------------

Overview
^^^^^^^^
A brief outline of the life cycle of a request and response using the example configuration above:

1. **TCP Connection Establishment**:
   A TCP connection from downstream is accepted by an Curve listener running on a worker thread. The listener filter chain provides SNI and other pre-TLS information. The transport socket, typically TLS, decrypts incoming data for processing.

2. **Prompt Guardrails Check**:
   Curve first checks the incoming prompts for guardrails such as jailbreak attempts and toxicity. This ensures that harmful or unwanted behaviors are detected early in the request processing pipeline.

3. **Intent Matching**:
   The decrypted data stream is deframed by the HTTP/2 codec in Curve's HTTP connection manager. Curve performs intent matching using the name and description of the defined prompt targets, determining which endpoint should handle the prompt.

4. **Parameter Gathering with Curve-FC1B**:
   If a prompt target requires specific parameters, Curve engages Curve-FC1B to extract the necessary details from the incoming prompt(s). This process gathers the critical information needed for downstream API calls.

5. **API Call Execution**:
   Curve routes the prompt to the appropriate backend API or function call. If an endpoint cluster is identified, load balancing is performed, circuit breakers are checked, and the request is proxied to the upstream endpoint. For more details on routing and load balancing, refer to the [Envoy routing documentation](https://www.envoyproxy.io/docs/envoy/latest/intro/curve _overview/intro/curve _overview).

6. **Default Summarization by Upstream LLM**:
   By default, if no specific endpoint processing is needed, the prompt is sent to an upstream LLM for summarization. This ensures that responses are concise and relevant, enhancing user experience in RAG (Retrieval-Augmented Generation) and agentic applications.

7. **Error Handling and Forwarding**:
   Errors encountered during processing, such as failed function calls or guardrail detections, are forwarded to designated error targets. Error details are communicated through specific headers to the application:

   - ``X-Function-Error-Code``: Code indicating the type of function call error.
   - ``X-Prompt-Guard-Error-Code``: Code specifying violations detected by prompt guardrails.
   - Additional headers carry messages and timestamps to aid in debugging and logging.

8. **Response Handling**:
   The upstream endpoint’s TLS transport socket encrypts the response, which is then proxied back downstream. Responses pass through HTTP filters in reverse order, ensuring any necessary processing or modification before final delivery.
