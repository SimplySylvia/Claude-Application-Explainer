---
type: llm
---

The user asked a plain question. It should be answered in chat from the code, with at most an offer to build a fuller guide.

PASS if the reply explains what React Router is, describes how ./app uses it (for example createBrowserRouter in client/src/routes.jsx, or the /admin route behind the newAdmin flag), and offers to build a topic explainer or guide without starting one.
FAIL if the reply doesn't describe the app's own use of React Router, or it starts building a guide or scaffolding files.
