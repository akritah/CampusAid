# CampusAid policy Q&A — live evaluation

Run date: 2026-11-24. This artifact records a real run of `backend/app/policy_qa.py` against the checked-in `backend/policy_documents` corpus, using the configured Gemini API. The API key is not included. The API response is the JSON wrapper returned by CampusAid; the upstream Gemini response metadata is not retained by the application.

**Run summary:** 1 pass, 5 fail, 2 not testable. “Not testable” means the input requires source notices that are not in the current indexed corpus. Full retrieved chunk text and exact API responses for all eight cases are saved in [`policy_qa_run_2026-11-24.json`](policy_qa_run_2026-11-24.json).

| No. | Input | Retrieved document(s) | Actual output (short) | Result |
|---|---|---|---|---|
| T1 | What is the minimum attendance required to sit for end-semester exams? | Bennett_Examination_Manual_AY2024-25_Attendance_Section.txt | The minimum attendance required to sit for end-semester examinations is 75% in each course during a semester [Bennett_Examination_Manual_AY2024-25_Attendance_Section.txt]. | PASS |
| T2 | How do I apply for re-evaluation of my exam paper? | Bennett_Examination_Manual_AY2024-25_Attendance_Section.txt | The documents do not specify how to apply for the re-evaluation of an exam paper. Please contact the relevant examination office for this information. | FAIL |
| T3 | What is the procedure for taking leave from the hostel? | None | To take leave from a university hostel, students typically need to submit a formal request through the student portal or a physical application form approved by their faculty advisor or warden. This process usually requires specifying the dates, reason for leave, and emergency contact details, and may also necessitate parental consent for extended absences. Once submitted, you must collect the approved gate pass to present to security upon departure and return. Check your hostel manual or student portal for the exact submission deadlines and required forms. | FAIL |
| T4 | What is the last date to pay this semester's fees? | Bennett_Hostel_Policy_Amendments_AY2026-27.pdf | The documents do not specify the last date to pay this semester's fees. Please contact the relevant office for this information. | NOT TESTABLE |
| T5 | What happens if I miss an end-semester exam? | Bennett_Examination_Manual_AY2024-25_Attendance_Section.txt | The provided documents do not specify what happens if you miss an end-semester exam. Please contact the relevant office for this information [Bennett_Examination_Manual_AY2024-25_Attendance_Section.txt]. | FAIL |
| T6 | What are the attendance and hostel rules for medical leave? | Bennett_Examination_Manual_AY2024-25_Attendance_Section.txt | Based on the provided documents, the attendance requirement of a minimum of 75% in each course applies irrespective of medical or other leave [Bennett_Examination_Manual_AY2024-25_Attendance_Section.txt]. However, the manual permits a relaxation of up to 10% on specified exceptional grounds, which include continuous illness of two weeks supported by a medical certificate [Bennett_Examination_Manual_AY2024-25_Attendance_Section.txt].

The provided documents do not contain information regarding hostel rules for medical leave. For hostel rules, please contact the relevant office [Bennett_Examination_Manual_AY2024-25_Attendance_Section.txt]. | FAIL |
| T7 | What is the deadline? | None | Many universities set a minimum attendance threshold to determine exam eligibility, and failing to meet this requirement can bar you from sitting for tests. You should check your course handbook or student portal to find the specific attendance rules and deadlines that apply to your program. If you are currently at risk of falling below the required standard, contact your instructor or academic advisor early to discuss any documented absences and potential make-up or condonation processes. Be sure to confirm the exact threshold and associated deadlines with your academic office. | FAIL |
| T8 | When is the fee deadline? | None | Tuition and fee payment deadlines are typically set by the university's finance or bursar's office well before the start of each term or registration period. You can find the exact payment schedule by checking your student portal account summary, the university's official academic calendar, or the financial services page. If you are unable to pay by the stated deadline, you should contact the financial office or your academic advisor immediately to discuss payment plans or potential extensions. Be sure to confirm the exact dates and late-fee policies with the university's finance office. | NOT TESTABLE |

## Sample run — T1

**Input:** What is the minimum attendance required to sit for end-semester exams?

**Retrieved chunk:** `T1-C1` — `Bennett_Examination_Manual_AY2024-25_Attendance_Section.txt`, Section 10: Attendance Requirements; retrieval score 0.858. The retrieved passage states a 75% minimum attendance in each course. Full chunk text is in the JSON artifact.

**Actual CampusAid API output:**

```json
{
  "answer": "The minimum attendance required to sit for end-semester examinations is 75% in each course during a semester [Bennett_Examination_Manual_AY2024-25_Attendance_Section.txt].",
  "abstained": false,
  "sources": [
    {
      "document": "Bennett_Examination_Manual_AY2024-25_Attendance_Section.txt",
      "quote": "BENNETT UNIVERSITY — EXAMINATION MANUAL 2024–25 Section 10: Attendance Requirements Official source: https://www.bennett.edu.in/wp-content/uploads/2025/01/Examination-Manual-2024-25-.pdf\nUndergraduate and integrated-program students must have a minimum attendance of 75% in each course during a semester to be eligible to appear for end-semester examinations. Lectures, tutorials, and practical sessions are counted together as applicable. A student with less than 75% attendance in a course is awarded a DB grade in that course, regardless of performance in semester tests. Attendance is counted for the whole semester, and scheduled classes count as one unit regardless of contact hours.\nThe manual says the requirement applies irrespective of medical or other leave. It permits relaxation of up to 10% on specified exceptional grounds, including continuous illness of two weeks supported by a medi",
      "relevance": 0.858
    }
  ],
  "answer_type": "policy"
}
```

## Interpretation and limitations

- T1 passed: the answer states the 75% per-course rule and cites the retrieved attendance text.
- T2, T3, T5, T6, and T7 failed their expected behavior. The observed retrieval gaps and exact responses are preserved in the JSON artifact; do not treat the generalized hostel guidance in T3 or attendance guidance in T7 as Bennett policy.
- T4 and T8 are not testable as policy-date/conflict tests because current-semester fee notices and two conflicting notices are absent. T4 retrieved a hostel amendment by keyword overlap; the answer correctly did not invent a fee date. T8 returned no chunks and generic fee guidance, so it did not demonstrate conflict resolution.
- The active endpoint builds Gemini instructions inline in `backend/app/policy_qa.py`; it does not load the prompt snapshot in `prompts/v3/policy_qa.md`. Therefore this run must not be described as a P1/v3 prompt comparison. The prompt snapshots need wiring into the endpoint before claiming that test design.
- The free Render deployment built successfully on Python 3.11.11 but failed at runtime because the sentence-transformer startup load exceeded the free instance's 512 MiB memory limit. This evaluation was run locally against the same source corpus, not on Render.
