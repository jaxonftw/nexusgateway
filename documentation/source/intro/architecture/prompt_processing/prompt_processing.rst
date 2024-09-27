.. _curve _overview_prompt_handling:

Prompts
-------

Curve's primary design point is to securely accept, process and handle prompts. To do that effectively, 
Curve relies on Envoy's HTTP `connection management <https://www.envoyproxy.io/docs/envoy/v1.31.2/intro/curve _overview/http/http_connection_management>`_, 
subsystem and its **prompt handler** subsystem engineered with purpose-built :ref:`LLMs <llms_in_curve >` to 
implement critical functionality on behalf of developers so that you can stay focused on business logic.

.. Note::
   Curve's **prompt handler** subsystem interacts with the **model** subsytem through Envoy's cluster manager
   system to ensure robust, resilient and fault-tolerant experience in managing incoming prompts. Read more
   about the :ref:`model subsystem <curve _model_serving>` and how the LLMs are hosted in Curve.

Messages
--------

Curve accepts messages directly from the body of the HTTP request in a format that follows the `Hugging Face Messages API <https://huggingface.co/docs/text-generation-inference/en/messages_api>`_. 
This design allows developers to pass a list of messages, where each message is represented as a dictionary 
containing two key-value pairs:

    - **Role**: Defines the role of the message sender, such as "user" or "assistant".
    - **Content**: Contains the actual text of the message.


Prompt Guardrails
-----------------

Curve is engineered with :ref:`Curve-Guard <llms_in_curve >`, an industry leading safety layer, powered by a 
compact and high-performimg LLM that monitors incoming prompts to detect and reject jailbreak attempts - 
ensuring that unauthorized or harmful behaviors are intercepted early in the process.

To add jailbreak guardrails, see example below: 

.. literalinclude:: /_config/getting-started.yml
    :language: yaml
    :linenos:
    :emphasize-lines: 24-27
    :caption: :download:`curve -getting-started.yml </_config/getting-started.yml>`

.. Note::
   As a roadmap item, Curve will expose the ability for developers to define custom guardrails via Curve-Guard-v2,
   and add support for additional safety checks defined by developers and hazardous categories like, violent crimes, privacy, hate,  
   etc. To offer feedback on our roadmap, please visit our `github page <https://github.com/orgs/curvelaboratory/projects/1>`_


Prompt Targets
--------------

Once a prompt passes any configured guardrail checks, Curve processes the contents of the incoming conversation 
and identifies where to forwad the conversation to via its essential ``prompt_targets`` primitve. Prompt targets 
are endpoints that receive prompts that are processed by Curve. For example, Curve enriches incoming prompts with 
metadata like knowing when a user's intent has changed so that you can build faster, more accurate RAG apps.

Configuring ``prompt_targets`` is simple. See example below:

.. literalinclude:: /_config/getting-started.yml
    :language: yaml
    :linenos:
    :emphasize-lines: 29-38
    :caption: :download:`curve -getting-started.yml </_config/getting-started.yml>`


Intent Detection and Prompt Matching:
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Curve uses fast Natural Language Inference (NLI) and embedding approaches to first detect the intent of each 
incoming prompt. This intent detection phase analyzes the prompt's content and matches it against predefined 
prompt targets, ensuring that each prompt is forwarded to the most appropriate endpoint. Curve’s intent 
detection framework considers both the name and description of each prompt target, and uses a composite matching
score between an NLI and cosine similarity to enchance accuracy in forwarding decisions.

- **Embeddings**: By embedding the prompt and comparing it to known target vectors, Curve effectively identifies 
  the closest match, ensuring that the prompt is handled by the correct downstream service.

- **NLI**: NLI techniques further refine the matching process by evaluating the semantic alignment between the 
  prompt and potential targets.

Agentic Apps via Prompt Targets
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To support agentic apps, like scheduling travel plans or sharing comments on a document - via prompts, Curve uses 
its function calling abilities to extract critical information from the incoming prompt (or a set of prompts) 
needed by a downstream backend API or function call before calling it directly. For more details on how you can
build agentic applications using Curve, see our full guide :ref:`here <curve _function_calling_agentic_guide>`:

.. Note::
   Curve :ref:`Curve-FC <llms_in_curve >` is the dedicated agentic model engineered in Curve to extract information from 
   a (set of) prompts and executes necessary backend API calls. This allows for efficient handling of agentic tasks, 
   such as scheduling data retrieval, by dynamically interacting with backend services. Curve-FC is a flagship 1.3 
   billion parameter model that matches performance  with frontier models like Claude Sonnet 3.5 ang GPT-4, while 
   being 100x cheaper ($0.05M/token hosted) and 10x faster (p50 latencies of 200ms).

Prompting LLMs
--------------
Curve is a single piece of software that is designed to manage both ingress and egress prompt traffic, drawing its 
distributed proxy nature from the robust `Envoy <https://envoyproxy.io>`_. This makes it extremely efficient and capable 
of handling upstream connections to LLMs. If your application is originating code to an API-based LLM, simply use 
Curve's Python or JavaScript client SDK to send traffic to the desired LLM of choice. By sending traffic through Curve, 
you can propagate traces, manage and monitor traffic, apply rate limits, and utilize a large set of traffic management 
capabilities in a central place.

.. Attention:: 
   When you start Curve, it automatically creates a listener port for egress calls to upstream LLMs. This is based on the 
   ``llm_providers`` configuration section in the ``prompt_config.yml`` file. Curve binds itself to a local address such as 
   127.0.0.1:9000/v1  or a DNS-based address like curve .local:9000/v1 for outgoing traffic.
   
Example: Using the Curve Python SDK
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   from curve _client import CurveClient

   # Initialize the Curve client
   client = CurveClient(base_url="http://127.0.0.1:9000/v1")

   # Define your LLM provider and prompt
   model_id = "openai"
   prompt = "What is the capital of France?"

   # Send the prompt to the LLM through Curve
   response = client.completions.create(llm_provider=llm_provider, prompt=prompt)

   # Print the response
   print("LLM Response:", response)

Example: Using OpenAI Client with Curve as an Egress Gateway
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python 

   import openai

   # Set the OpenAI API base URL to the Curve gateway endpoint
   openai.api_base = "http://127.0.0.1:9000/v1"

   # No need to set openai.api_key since it's configured in Curve's gateway

   # Use the OpenAI client as usual
   response = openai.Completion.create(
      model="text-davinci-003",
      prompt="What is the capital of France?"
   )

   print("OpenAI Response:", response.choices[0].text.strip())

In these examples:

    The CurveClient is used to send traffic directly through the Curve egress proxy to the LLM of your choice, such as OpenAI.
    The OpenAI client is configured to route traffic via Curve by setting the proxy to 127.0.0.1:9000, assuming Curve is 
    running locally and bound to that address and port.

This setup allows you to take advantage of Curve's advanced traffic management features while interacting with LLM APIs like OpenAI.