# Q23 — Evaluator access handoff

Fill this section after publishing and testing the deployment. Evaluators must not need to request access.

- **Public source repository:** https://github.com/akritah/CampusAid (repository visibility verified; current local submission files have not been pushed)
- **One public app URL:** `PENDING — publish Vercel frontend and verify in an incognito browser`
- **Colab fallback:** `code/CampusAid_Evaluator_Demo.ipynb` is prepared locally with saved outputs. Publish it to the public repository, then open it in Colab if the full web deployment cannot be completed.
- **Student evaluator username:** `PENDING — provision a dedicated student account`
- **Student evaluator password:** `PENDING — provide directly in Q23, not in this repository`
- **What the evaluator can try:** sign in; ask the attendance question and inspect the cited source; ask a question from another indexed policy; file and track a test grievance; try the voice complaint flow.
- **Access check:** verify the public URL and login from a signed-out/incognito browser before submission.

Do not commit API keys, passwords, or tokens. Keep the Gemini key in the Render backend environment only. Use `DEMO_USERS_JSON` with a unique 12+ character password to seed a student account; account creation happens only when the username is first absent from the configured database. Set the password in Render and communicate it through the assignment's Q23 response, not a public file.
