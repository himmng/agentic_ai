# Agentic AI Solution
Developing agentic AI solution for businesses to help with
* Sentiment Analysis/Intent Recognition
* Priority/Incident Determination
* Content Summarisation
* Recommendation
* Decision Escalation

Agentic Workflow is developed inside a full-code python environment which can be directly exported to cloud platforms like Azure [^1], AWS, GCloud for scalablity.

### synergy usecase

#### current capabilities

* **Agent Creator/Tester**: Create and Test Agents in Azure
* **data_creation_agent**: Generate real-world syntheic data for synergy (InMoment and Fullstory style)
* **Pseudo API call**: Mimic real-world api call to get data.
* **data_extraction**: Extract key-fields for processing
* **survey_intelligence_agent**: Generate AI summary, recommendation and sentiment 
* **data_enriching**: Enrich the original synthetic data with AI.

The simplar flowchart of our workflow:

```mermaid

%% Synergy Agentic AI - InMoment + FullStory Integration
%% Top-to-Bottom Flow with Colors and Connectors
flowchart TD
    %% ------------------
    %% Phase 1: Customer Interaction
    %% ------------------
    A[Customer Interaction]:::cust -->|Website / Mobile App| B[FullStory Session Data]:::fs
    A -->|Survey / Feedback| C[InMoment Survey Data]:::im

    %% ------------------
    %% Phase 2: Data Extraction
    %% ------------------
    B --> D[FullStory API Extraction]:::api
    C --> E[InMoment API Extraction]:::api

    %% ------------------
    %% Phase 3: Data Normalisation & Correlation
    %% ------------------
    D --> F[Data Normalisation Layer]:::norm
    E --> F
    F --> G[Identity & Temporal Correlation]:::corr
    G --> H[Unified CX JSON]:::json

    %% ------------------
    %% Phase 4: AI Analysis
    %% ------------------
    H --> I[Agentic AI Engine]:::ai
    I -->|Sentiment Analysis| J[Sentiment Model]:::ai
    I -->|Effort & Friction Detection| K[Priority Model]:::ai
    I -->|Root Cause Reasoning| L[Recommendation Engine]:::ai

    %% ------------------
    %% Phase 5: Write-back & Actions
    %% ------------------
    J --> M[AI Insight Object]:::out
    K --> M
    L --> M
    M -->|Tags, Case Notes, Priority, Summary| N[InMoment Update API]:::im

    %% ------------------
    %% Phase 6: Downstream Systems
    %% ------------------
    N --> O[Jira / ServiceNow]:::ds
    N --> P[Power BI / Reporting]:::ds
    N --> Q[Confluence / Knowledge Base]:::ds

    %% ------------------
    %% Phase 7: Reference Linking
    %% ------------------
    B -->|Session URL Reference| N

    %% ------------------
    %% Styles
    %% ------------------
    classDef cust fill:#FFD966,stroke:#333,stroke-width:1px,color:#000,font-weight:bold;
    classDef fs fill:#6FA8DC,stroke:#333,stroke-width:1px,color:#fff,font-weight:bold;
    classDef im fill:#93C47D,stroke:#333,stroke-width:1px,color:#fff,font-weight:bold;
    classDef api fill:#E06666,stroke:#333,stroke-width:1px,color:#fff,font-weight:bold;
    classDef norm fill:#F6B26B,stroke:#333,stroke-width:1px,color:#000,font-weight:bold;
    classDef corr fill:#F9CB9C,stroke:#333,stroke-width:1px,color:#000,font-weight:bold;
    classDef json fill:#B4A7D6,stroke:#333,stroke-width:1px,color:#fff,font-weight:bold;
    classDef ai fill:#8E7CC3,stroke:#333,stroke-width:1px,color:#fff,font-weight:bold;
    classDef out fill:#6AA84F,stroke:#333,stroke-width:1px,color:#fff,font-weight:bold;
    classDef ds fill:#D9D2E9,stroke:#333,stroke-width:1px,color:#000,font-weight:bold;

```

[^1]: The current setup is developed for keeping **Azure** in mind, that can be changed later. For overview [click](https://ai.azure.com).
