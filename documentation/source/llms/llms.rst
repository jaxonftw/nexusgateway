.. _llms_in_curve :

LLMs
====

Curve utilizes purpose-built, industry leading, LLMs to handle the crufty and undifferentiated work around
accepting, handling and processing prompts. The following sections talk about some of the core models that
are built-in Curve.

Curve-Guard-v1
-------------
LLM-powered applications are susceptible to prompt attacks, which are prompts intentionally designed to
subvert the developer’s intended behavior of the LLM. Curve-Guard-v1 is a classifier model trained on a large
corpus of attacks, capable of detecting explicitly malicious prompts (and toxicity).

The model is useful as a starting point for identifying and guardrailing against the most risky realistic
inputs to LLM-powered applications. Our goal in embedding Curve-Guard in the Curve gateway is to enable developers
to focus on their business logic and factor out security and safety outside application logic. Wth Curve-Guard-v1
developers can take to significantly reduce prompt attack risk while maintaining control over the user experience.

Below is our test results of the strength of our model as compared to Prompt-Guard from `Meta LLama <https://huggingface.co/meta-llama/Prompt-Guard-86M>`_.

.. list-table::
   :header-rows: 1
   :widths: 15 15 10 15 15

   * - Dataset
     - Jailbreak (Yes/No)
     - Samples
     - Prompt-Guard Accuracy
     - Curve-Guard Accuracy
   * - casual_conversation
     - 0
     - 3725
     - 1.00
     - 1.00
   * - commonqa
     - 0
     - 9741
     - 1.00
     - 1.00
   * - financeqa
     - 0
     - 1585
     - 1.00
     - 1.00
   * - instruction
     - 0
     - 5000
     - 1.00
     - 1.00
   * - jailbreak_behavior_benign
     - 0
     - 100
     - 0.10
     - 0.20
   * - jailbreak_behavior_harmful
     - 1
     - 100
     - 0.30
     - 0.52
   * - jailbreak_judge
     - 1
     - 300
     - 0.33
     - 0.49
   * - jailbreak_prompts
     - 1
     - 79
     - 0.99
     - 1.00
   * - jailbreak_tweet
     - 1
     - 1282
     - 0.16
     - 0.35
   * - jailbreak_v
     - 1
     - 20000
     - 0.90
     - 0.93
   * - jailbreak_vigil
     - 1
     - 104
     - 1.00
     - 1.00
   * - mental_health
     - 0
     - 3512
     - 1.00
     - 1.00
   * - telecom
     - 0
     - 4000
     - 1.00
     - 1.00
   * - truthqa
     - 0
     - 817
     - 1.00
     - 0.98
   * - weather
     - 0
     - 3121
     - 1.00
     - 1.00

.. list-table::
   :header-rows: 1
   :widths: 15 20

   * - Statistics
     - Overall performance
   * - Overall Accuracy
     - 0.93568 (Prompt-Guard), 0.95267 (Curve-Guard)
   * - True positives rate (TPR)
     - 0.8468 (Prompt-Guard), 0.8887 (Curve-Guard)
   * - True negative rate (TNR)
     - 0.9972 (Prompt-Guard), 0.9970 (Curve-Guard)
   * - False positive rate (FPR)
     - 0.0028 (Prompt-Guard), 0.0030 (Curve-Guard)
   * - False negative rate (FNR)
     - 0.1532 (Prompt-Guard), 0.1113 (Curve-Guard)

.. list-table::
   :header-rows: 1
   :widths: 15 20

   * - Metrics
     - Values
   * - AUC
     - 0.857 (Prompt-Guard), 0.880 (Curve-Guard)
   * - Precision
     - 0.715 (Prompt-Guard), 0.761 (Curve-Guard)
   * - Recall
     - 0.999 (Prompt-Guard), 0.999 (Curve-Guard)



Curve-FC
-------
Curve-FC is a lean, powerful and cost-effective agentic model designed for function calling scenarios.
You can run Curve-FC locally, or use the cloud-hosted version for as little as $0.05/M token (100x cheaper
than GPT-4o), with a p50 latency of 200ms (5x faster than GPT-4o), while meeting frontier model performance.

.. Note::
  Function calling helps you personalize the GenAI experience by calling application-specific operations via
  prompts. This involves any predefined functions or APIs you want to expose to perform tasks, gather
  information, or manipulate data - via prompts.

  You can get started with function calling simply by configuring a prompt target with a name, description
  and set of parameters needed by a specific backend function or a hosted API. The name, and description helps
  Curve-FC match a user prompt to a function or API that can process it.

By using Curve-FC, Curve enables you to easily build agentic workflows tailored to domain-specific use cases -
from updating insurance claims to creating ad campaigns. Curve-FC analyzes prompts, extracts critical information
from prompts, engages in lightweight conversations with the user to gather any missing parameters need before
handling control back to Curve to make the API call to your hosted backend. Curve-FC handles the muck of information
extraction so that you can focus on the business logic of your application.
