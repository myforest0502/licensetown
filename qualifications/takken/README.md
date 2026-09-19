# Takken: dormant, fail-closed boundary

Only qualification metadata is defined here. There is no configured bank or
learning-history store; the existing registries reject `takken` with
QuestionBankProviderNotConfigured / LearningHistoryStoreNotConfigured.
Metadata lookup is not permission to start a session or fall back to PT.

Do not add guessed subjects, questions, tags, Knowledge Nodes, Safety rules or
PT-derived strategy semantics. A future implementation requires reviewed data
and explicit provider/store registration with separate routing acceptance.
See ../README.md and ../../docs/TAKKEN_PHASE_E_READINESS_V01.md.
