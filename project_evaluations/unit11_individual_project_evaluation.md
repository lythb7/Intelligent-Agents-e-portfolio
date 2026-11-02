# Unit 11: Evaluation of the Development Individual Project

The individual project turned the Unit 7 design into a tested, documented system: a FastAPI web interface and terminal client over four cooperating agents, SQLite storage, ReportLab PDF generation, a rule-based interpreter and an optional language-model interpreter behind the same interface.

Against the requirements, the prototype delivers all four: conversation with greeting and sign-off, a timetable of current modules, a downloadable transcript generated from live marks, and PDF briefs for assignments whose deadlines have not passed, with enrolment and deadline re-checked at download. Against quality criteria, the final state is 53 passing tests, flake8 clean, pylint 10/10, bandit and pip-audit clear, with the before-and-after outputs kept as evidence.

The most useful outcome was a measurement rather than an assumption. On a 24-scenario set the rule interpreter handled every direct request but only two of five paraphrases and none of the prompt-injection or off-topic cases, scoring 14 of 24; the language-model interpreter, running on the cheapest current Claude model, scored 23 of 24 at about a fiftieth of a cent per call. Every miss on either side was a safe miss, because the architecture never lets the interpreter touch records, and that separation is the design decision I am most confident about.

The limitations are honest ones for a prototype: synthetic data, in-memory sessions, a single process and a synchronous bus. If I continued, I would connect the specialists to a real student-record API, replace the login form with single sign-on, and run the live interpreter comparison on a larger and independently written scenario set so that the evaluation is not shaped by the same person who wrote the rules.

---

*Artefacts: the [project report](../development_project/project_report/34119_IA_PCOM7E_Development_Individual_Project_Report.docx) and the [source, tests and tool output](../development_project/chatbot/README.md), whose README explains how to run it.*
