# Individual Reflection: Intelligent Agents Module

*e-Portfolio: [PORTFOLIO WEB ADDRESS TO BE ADDED]*  
*Module: Intelligent Agents (IA_PCOM7E)*  
*Student Name: Lyth Hishmeh*  
*Student ID: 34119*  
*Word Count: Approximately 1,000 words*

## What? – Description of the Learning Experience

This reflection covers my experience of the Intelligent Agents module, which I completed as a reassessment. I was not able to take part in the module's original schedule because of my disability, a form of chronic fatigue that worsens through the winter, and because of difficult personal circumstances in the same period that I will not detail here. The practical consequence was that work designed to be done in a team over twelve weeks, with seminars and a running forum, was done by me alone in a compressed period, and this reflection is partly about what that changed.

The module introduced agent-based computing: what an agent is, the reactive, deliberative and hybrid architectures that have been proposed, how agents communicate through speech-act languages such as KQML, and how these ideas sit alongside the statistical and deep-learning methods I already use professionally. The assessed work was a design proposal and prototype for a university chatbot that retrieves a student's timetable, transcript and active assignment briefs, a tested and documented version of that prototype, and this portfolio. My background is in machine learning, so I came in expecting the chatbot to be mostly a language-model problem.

## So What? – Analysis and Interpretation

Using Rolfe, Freshwater and Jasper's (2001) framework, the honest starting point is my emotional response. I began the reassessment anxious and somewhat resentful of the circumstances, and conscious that the mark is capped whatever I produce. Moon (2004) observes that reflection has most to offer when an experience is uncomfortable, and I found that the discomfort pushed me towards a more deliberate way of working than I would normally adopt: short sessions, a written decision log, and tests written before the code they exercised. I had to work that way because my energy was unreliable, and it turned out to be better practice regardless. The anxiety had a less helpful effect too: on low days I avoided the parts of the work I was least sure of, which is why the conversation layer, the part I understood least, was built last and tested hardest.

The intellectual shift came from the readings on agents rather than from the chatbot itself. Wooldridge's (2009) account of autonomy and social ability, and Finin et al.'s (1994) separation of a message's performative from its content, gave me a vocabulary for something I had felt but not articulated in previous projects: that the interesting engineering in a system built from several components is in the boundaries between them. I designed the chatbot as four agents exchanging typed messages over a bus, with a deliberately narrow place for the language model to make one decision, and the consequence was that every security property I cared about could be stated as a test. My prior experience with models made me more sceptical of them, not less; having seen how fluently a model produces wrong output, I was unwilling to let it generate a fact, and Bender et al.'s (2021) critique gave that instinct an academic grounding.

What produced the most learning was failure. The first full test run failed six tests, and four of them were defects in rules I had written by hand and believed were obviously correct. Schön's (1983) distinction between reflection-in-action and reflection-on-action was useful here: in the moment I fixed the bugs, but stepping back afterwards I recognised a pattern in my own behaviour, which is that I trust transparent code more than it deserves because I can read it. The measured comparison of the two interpreters made the same point with numbers. The rule-based interpreter handled fourteen of twenty-four scenarios and the language model twenty-three; I would not have believed the gap was that large without measuring it.

On collaboration, I have to be candid. I worked independently, and the rubric's phrase "collaboration or independent working" is the fair frame for what I did. I read and responded to the forum posts of peers from the original cohort, which was useful because it exposed me to interpretations of agent-based systems that differ from my own, but it is not the same as negotiating a design with teammates. Kolb's (1984) cycle of experience, reflection, conceptualisation and experimentation ran entirely inside my own head, which is faster but loses the correction that other people provide. The clearest evidence is that the most consequential bugs were in the part of the system nobody else had looked at.

## Now What? – Future Application and Development

Three things change in how I work. First, I now treat a language model in a system the way I would treat any untrusted input: useful, bounded, validated, with a deterministic fallback. That principle transfers directly to my professional work, where the pressure to put a model at the centre of a product is strong and the case for keeping it at the edge is rarely made explicitly. Second, I will keep the practice of recording before-and-after tool output as a matter of course, because the remediation story turned out to be more persuasive evidence of competence than a clean final run would have been. Third, I intend to apply the agent abstraction beyond chatbots. Several systems I have built would have been clearer as cooperating agents with explicit messages than as the monoliths they became, and I now have both the vocabulary and a worked example to argue for that.

Personally, the module reinforced a lesson I first wrote about in a previous reflection: that progress under chronic illness is possible when it is paced, and that depth of understanding matters more than the speed at which it arrives. I would rather have done this work with a team and on time. Given that I could not, I am satisfied that what I produced is honest about its limits, tested against the claims it makes, and built on ideas I can now explain and defend.

## References

Bender, E.M., Gebru, T., McMillan-Major, A. and Shmitchell, S. (2021) On the dangers of stochastic parrots: Can language models be too big? *Proceedings of the 2021 ACM Conference on Fairness, Accountability, and Transparency (FAccT '21)*: 610-623. DOI: https://doi.org/10.1145/3442188.3445922 [Accessed 31 October 2026].

Finin, T., Fritzson, R., McKay, D. and McEntire, R. (1994) KQML as an agent communication language. *Proceedings of the Third International Conference on Information and Knowledge Management (CIKM '94)*: 456-463. DOI: https://doi.org/10.1145/191246.191322 [Accessed 30 October 2026].

Kolb, D.A. (1984) *Experiential Learning: Experience as the Source of Learning and Development*. Englewood Cliffs, NJ: Prentice-Hall.

Moon, J.A. (2004) *A Handbook of Reflective and Experiential Learning: Theory and Practice*. London: RoutledgeFalmer.

Rolfe, G., Freshwater, D. and Jasper, M. (2001) *Critical Reflection for Nursing and the Helping Professions: A User's Guide*. Basingstoke: Palgrave Macmillan.

Schön, D.A. (1983) *The Reflective Practitioner: How Professionals Think in Action*. New York: Basic Books.

Wooldridge, M. (2009) *An Introduction to MultiAgent Systems*. 2nd edn. Chichester: John Wiley & Sons.
