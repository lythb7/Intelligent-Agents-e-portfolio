# Unit 7: Evaluation of the Development Team Project

The team project asked for a design proposal and a prototype of a student-services chatbot. I completed it alone during a reassessment period, so this is an evaluation of an individual piece of work against a brief written for a team.

What worked was starting from the requirements rather than the technology. Three of the four requirements are record access with access-control consequences, and only one (conversation) is genuinely uncertain, so the design put deterministic Python around records and documents and treated natural-language understanding as a replaceable component. Decomposing the system into four agents that talk over a KQML-inspired message bus made each part testable in isolation and gave me a trace I could show. The proposal also committed early to the deadline semantics (an assignment is active until its deadline passes, compared as timezone-aware instants), which later saved a class of bugs.

What I would do differently in a team is divide the work along the agent boundaries, because they are natural ownership lines: one person per specialist agent, one on the dialogue agent, with the message format agreed first. Working alone I underestimated how much time the conversation layer would take relative to the data layer; the first test run showed that most defects were in my hand-written language rules, not in the agents.

The design document itself was kept to the word limit by deferring implementation detail to the code and its comments, which I think is the right split for a proposal that is followed by a build.

---

*Artefacts: the [design report](../development_project/design_report/34119_IA_PCOM7E_Development_Team_Project_Design_Report.docx) and the [prototype source](../development_project/chatbot/README.md).*
