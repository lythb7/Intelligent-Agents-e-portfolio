# Forum posts: text and screenshots

All nine contributions to the three collaborative discussions, as posted on the module forum on 2 November 2026. Each entry gives the forum URL, the screenshot files in `screenshots/` and the full text of the post. Screenshots are the live forum pages captured in scrolled parts (`_1`, `_2`, ... from top to bottom); the `_full` files for Discussion 1 are single full-length captures of the same posts.

## Collaborative Discussion 1: Agent-Based Systems

### Initial Post

URL: https://www.my-course.co.uk/mod/forum/discuss.php?d=398146

Screenshots: [discussion1_initial_post_1.png](screenshots/discussion_1/discussion1_initial_post_1.png), [discussion1_initial_post_2.png](screenshots/discussion_1/discussion1_initial_post_2.png), [discussion1_initial_post_3.png](screenshots/discussion_1/discussion1_initial_post_3.png), [discussion1_initial_post_full.png](screenshots/discussion_1/discussion1_initial_post_full.png)

*Discuss what has led to the rise of agent-based systems and the benefits that this approach can offer to organisations.*

I'd like to approach this from the perspective of someone whose background is in machine learning rather than distributed systems, because the rise of agents makes more sense to me once I noticed what the object-oriented and statistical paradigms could not easily express. Wooldridge and Jennings (1995) define an agent as a computer system situated in an environment that acts autonomously, reactively, proactively and socially to meet its design objectives. The important word is *autonomously*: an object does what it is told when its method is invoked, whereas an agent decides whether and how to act. Jennings (2000) argues that this is exactly the abstraction needed once software systems became large, open and made of components owned by different parties, because a central controller cannot know enough, or be trusted enough, to direct everything.

Three developments, in my reading, drove the shift. The first is the growth of distributed, networked systems in which components must coordinate without shared memory or a single point of control. The second is the recognition, from Brooks (1991) onward, that situated behaviour with local sensing can produce robust results where central planning struggles. The third is the need to model systems whose global behaviour emerges from many local interactions, which is why agent-based modelling became a standard tool in economics, epidemiology and logistics (Bonabeau, 2002).

The benefits for organisations follow from those origins. Decomposing a system into agents that negotiate rather than obey allows parts to be added, replaced or owned by different departments without rewriting the whole; Wang et al. (2016) show this in a smart-factory setting where product, machine and conveyor agents negotiate schedules and recover from deadlock through local rules. Agent-based simulation lets an organisation test policy before committing to it. And the agent metaphor maps naturally on to services that act on a person's behalf, such as the student-services assistant I am building in this module. The cost, which I think is sometimes understated, is that emergent behaviour is harder to verify than a central algorithm, so the approach suits problems where flexibility matters more than predictability.

### References

Bonabeau, E. (2002) Agent-based modeling: Methods and techniques for simulating human systems. *Proceedings of the National Academy of Sciences* 99(suppl. 3): 7280-7287. DOI: https://doi.org/10.1073/pnas.082080899 [Accessed 1 November 2026].

Brooks, R.A. (1991) Intelligence without representation. *Artificial Intelligence* 47(1-3): 139-159. DOI: https://doi.org/10.1016/0004-3702(91)90053-M [Accessed 1 November 2026].

Jennings, N.R. (2000) On agent-based software engineering. *Artificial Intelligence* 117(2): 277-296. DOI: https://doi.org/10.1016/S0004-3702(99)00107-1 [Accessed 1 November 2026].

Wang, S., Wan, J., Zhang, D., Li, D. and Zhang, C. (2016) Towards smart factory for industry 4.0: a self-organized multi-agent system with big data based feedback and coordination. *Computer Networks* 101: 158-168. DOI: https://doi.org/10.1016/j.comnet.2015.12.017 [Accessed 1 November 2026].

Wooldridge, M. and Jennings, N.R. (1995) Intelligent agents: theory and practice. *The Knowledge Engineering Review* 10(2): 115-152. DOI: https://doi.org/10.1017/S0269888900008122 [Accessed 1 November 2026].

### Peer Response to Pitshou Bokoro

URL: https://www.my-course.co.uk/mod/forum/discuss.php?d=360588#p812990

Screenshots: [discussion1_response_pitshou_bokoro_1.png](screenshots/discussion_1/discussion1_response_pitshou_bokoro_1.png), [discussion1_response_pitshou_bokoro_2.png](screenshots/discussion_1/discussion1_response_pitshou_bokoro_2.png), [discussion1_response_pitshou_bokoro_3.png](screenshots/discussion_1/discussion1_response_pitshou_bokoro_3.png), [discussion1_response_pitshou_bokoro_full.png](screenshots/discussion_1/discussion1_response_pitshou_bokoro_full.png)

Hi Pitshou,

I liked the condition-monitoring framing, because it makes the benefits concrete rather than abstract: a sensor agent that detects an anomaly locally does not need to ship raw data to a central service, and the failure of one agent leaves the others working. That is the distributed-intelligence argument Jennings (2000) makes, and your smart-grid example is a good instance of it.

The point I'd push on is coordination. The same decentralisation that gives fault tolerance also creates interactions nobody designed. Wang et al. (2016) describe exactly this in a smart-factory setting: product, machining and conveying agents negotiate well until several of them want the same shared resource, at which point the system deadlocks, and the authors have to add a central feedback and coordination layer to break the tie. Reynolds (1987) showed the other side of the coin decades earlier, that simple local rules produce convincing global behaviour, but convincing is not the same as verified, and in a monitoring system that decides when to take a turbine offline the difference matters.

So the measure I'd add to your list is an explicit coordination and escalation design: which agent arbitrates when two diagnoses conflict, what the system does when an agent goes quiet rather than failing loudly, and how a human operator sees the agents' reasoning. In my own project I ended up keeping a trace of every inter-agent message for that reason. It is not glamorous, but it is what turns emergent behaviour into something an engineer can sign off.

**References**

Jennings, N.R. (2000) On agent-based software engineering. Artificial Intelligence 117(2): 277-296. DOI: https://doi.org/10.1016/S0004-3702(99)00107-1 [Accessed 2 November 2026].

Reynolds, C.W. (1987) Flocks, herds and schools: A distributed behavioral model. ACM SIGGRAPH Computer Graphics 21(4): 25-34. DOI: https://doi.org/10.1145/37402.37406 [Accessed 2 November 2026].

Wang, S., Wan, J., Zhang, D., Li, D. and Zhang, C. (2016) Towards smart factory for industry 4.0: a self-organized multi-agent system with big data based feedback and coordination. Computer Networks 101: 158-168. DOI: https://doi.org/10.1016/j.comnet.2015.12.017 [Accessed 2 November 2026].

### Peer Response to Maha Hegde

URL: https://www.my-course.co.uk/mod/forum/discuss.php?d=345598#p812992

Screenshots: [discussion1_response_maha_hegde_1.png](screenshots/discussion_1/discussion1_response_maha_hegde_1.png), [discussion1_response_maha_hegde_2.png](screenshots/discussion_1/discussion1_response_maha_hegde_2.png), [discussion1_response_maha_hegde_3.png](screenshots/discussion_1/discussion1_response_maha_hegde_3.png)

Hi Maha,

Your two angles are a useful way in, and I'd like to connect them to the older agent literature, because I think the connection changes what "agent" means in each case. Wooldridge and Jennings (1995) define an agent by autonomy, reactivity, pro-activeness and social ability, and that definition predates large language models by nearly thirty years. The RPA-to-agentic progression you cite is really a story about autonomy being added back to automation: a level-one bot executes a fixed script, whereas an agent decides what to do. The generative-AI angle is a story about social ability, because natural language suddenly made agents easy to instruct. Neither angle on its own gives you the other properties, which is why many products called agents today are still fragile.

On the point that generative systems can plan but not act, Ross is right that tool-calling has closed much of that gap, but I'd argue it has made your security point sharper rather than weaker. Once a model can call tools, anything the model reads becomes a potential instruction, which is the indirect prompt injection problem Greshake et al. (2023) demonstrate against deployed assistants. The measure that follows is to keep the model's decision surface small and validate it in code. In my chatbot project the model may only choose one of ten named operations, every argument is checked locally, and the student identifier is taken from the authenticated session rather than from anything the model produces. That is a direct application of the security framing you end with, and I think it is the design habit the agentic wave most needs.

**References**

Greshake, K., Abdelnabi, S., Mishra, S., Endres, C., Holz, T. and Fritz, M. (2023) Not what you've signed up for: Compromising real-world LLM-integrated applications with indirect prompt injection. Proceedings of the 16th ACM Workshop on Artificial Intelligence and Security (AISec '23): 79-90. DOI: https://doi.org/10.1145/3605764.3623985 [Accessed 2 November 2026].

Wooldridge, M. and Jennings, N.R. (1995) Intelligent agents: theory and practice. The Knowledge Engineering Review 10(2): 115-152. DOI: https://doi.org/10.1017/S0269888900008122 [Accessed 2 November 2026].

## Collaborative Discussion 2: Agent Communication Languages

### Initial Post

URL: https://www.my-course.co.uk/mod/forum/discuss.php?d=398147

Screenshots: [discussion2_initial_post_1.png](screenshots/discussion_2/discussion2_initial_post_1.png), [discussion2_initial_post_2.png](screenshots/discussion_2/discussion2_initial_post_2.png), [discussion2_initial_post_3.png](screenshots/discussion_2/discussion2_initial_post_3.png), [discussion2_initial_post_4.png](screenshots/discussion_2/discussion2_initial_post_4.png)

*What are the potential advantages and disadvantages of the use of agent communication languages such as KQML? How do they compare with method invocation in Python or Java?*

A method call in Python or Java is an instruction: the caller names the operation, supplies the arguments, and blocks until it gets a value back. KQML, by contrast, treats communication as a set of speech acts (Finin et al., 1994). A message has a performative such as *ask-one*, *tell* or *achieve* that says what kind of act it is, a content expression in some separate language, and context such as the ontology and the conversation it belongs to. The underlying idea comes from Searle (1969): asking and telling are different acts even when the proposition is the same.

I'd argue the main advantage is independence. Because the performative is separated from the content and from the agent's internals, two agents written by different teams in different languages can talk as long as they agree on the vocabulary and ontology, and a receiver remains free to refuse, delay or answer partially. That autonomy is the whole point of an agent, and a method call cannot express it: an object cannot say *sorry*. KQML also supports interaction patterns that are awkward in direct invocation, such as *subscribe* for ongoing updates and facilitators that broker requests to whichever agent advertises a capability (Labrou, Finin and Peng, 1999). In my own chatbot project, routing requests to specialist agents by capability rather than by object reference made the specialists replaceable and the whole exchange inspectable.

The disadvantages are real. KQML's semantics were informal, so different implementations interpreted performatives differently, which is one reason FIPA later specified its ACL with formal preconditions and effects (FIPA, 2002). There is overhead in parsing and routing messages that a direct call avoids, and debugging an asynchronous conversation is harder than reading a stack trace. Agreeing an ontology is often the hardest part; Payne and Tamma (2014) show that even the mapping between two agents' vocabularies can require negotiation. So the comparison is not about which is better in general. Method invocation is right inside a single trusted program; an ACL earns its cost when the parties are autonomous, heterogeneous or separately owned.

### References

FIPA (2002) *FIPA ACL message structure specification*. SC00061G. Geneva: Foundation for Intelligent Physical Agents. Available from: http://www.fipa.org/specs/fipa00061/SC00061G.html [Accessed 1 November 2026].

Finin, T., Fritzson, R., McKay, D. and McEntire, R. (1994) KQML as an agent communication language. *Proceedings of the Third International Conference on Information and Knowledge Management (CIKM '94)*: 456-463. DOI: https://doi.org/10.1145/191246.191322 [Accessed 1 November 2026].

Labrou, Y., Finin, T. and Peng, Y. (1999) Agent communication languages: the current landscape. *IEEE Intelligent Systems* 14(2): 45-52. DOI: https://doi.org/10.1109/5254.757631 [Accessed 1 November 2026].

Payne, T.R. and Tamma, V. (2014) Negotiating over ontological correspondences with asymmetric and incomplete knowledge. *Proceedings of the 13th International Conference on Autonomous Agents and Multiagent Systems (AAMAS 2014)*: 517-524.

Searle, J.R. (1969) *Speech Acts: An Essay in the Philosophy of Language*. Cambridge: Cambridge University Press.

### Peer Response to Adaeze Ugochukwu

URL: https://www.my-course.co.uk/mod/forum/discuss.php?d=360667#p812993

Screenshots: [discussion2_response_adaeze_ugochukwu_1.png](screenshots/discussion_2/discussion2_response_adaeze_ugochukwu_1.png), [discussion2_response_adaeze_ugochukwu_2.png](screenshots/discussion_2/discussion2_response_adaeze_ugochukwu_2.png), [discussion2_response_adaeze_ugochukwu_3.png](screenshots/discussion_2/discussion2_response_adaeze_ugochukwu_3.png)

Hi Adaeze,

The healthcare decision-support example is a good one because it shows the part of KQML that is easy to overlook: the mediator agent you describe is a facilitator in Finin et al.'s (1994) sense, an agent whose job is to broker requests to whichever source can answer them, so that a clinic's system never has to know where the knowledge lives. That indirection is what makes the architecture extensible, and it is the feature a remote method call cannot give you, because RMI binds the caller to a specific interface at a specific address (Labrou, Finin and Peng, 1999).

Where I'd add to your limitations is the ontology problem, which I think is deeper than standardisation of vocabularies. Even when two agents agree a protocol, they may carve the domain up differently, and Payne and Tamma (2014) show that reconciling two agents' correspondences can itself require a negotiation dialogue, with each side disclosing only part of what it knows. In healthcare that is not a corner case; two hospitals' coding of the same condition routinely differs. So the honest comparison with method invocation is that Java solves this at compile time by forcing a shared interface, whereas an ACL pushes the problem to run time where it is more flexible and much harder.

A practical measure, which I used in my own project, is to keep the content language deliberately tiny and let the performatives do the work: a handful of operations, strict schemas for each, and a sorry performative so that an agent can say it does not understand rather than guessing. It does not solve ontology alignment, but it makes the failure visible instead of silent.

**References**

Finin, T., Fritzson, R., McKay, D. and McEntire, R. (1994) KQML as an agent communication language. Proceedings of the Third International Conference on Information and Knowledge Management (CIKM '94): 456-463. DOI: https://doi.org/10.1145/191246.191322 [Accessed 2 November 2026].

Labrou, Y., Finin, T. and Peng, Y. (1999) Agent communication languages: the current landscape. IEEE Intelligent Systems 14(2): 45-52. DOI: https://doi.org/10.1109/5254.757631 [Accessed 2 November 2026].

Payne, T.R. and Tamma, V. (2014) Negotiating over ontological correspondences with asymmetric and incomplete knowledge. Proceedings of the 13th International Conference on Autonomous Agents and Multiagent Systems (AAMAS 2014): 517-524.

### Peer Response to Fatema Mohammed Ahmed Aal Malek Alshehhi

URL: https://www.my-course.co.uk/mod/forum/discuss.php?d=360480#p812994

Screenshots: [discussion2_response_fatema_alshehhi_1.png](screenshots/discussion_2/discussion2_response_fatema_alshehhi_1.png), [discussion2_response_fatema_alshehhi_2.png](screenshots/discussion_2/discussion2_response_fatema_alshehhi_2.png), [discussion2_response_fatema_alshehhi_3.png](screenshots/discussion_2/discussion2_response_fatema_alshehhi_3.png)

Hi Fatema,

I agree with your conclusion that the choice depends on coupling, and I'd like to add one distinction that I think explains why. A method call and a KQML message differ not only in cost but in what they can express. When I call a method, the callee has no vocabulary for declining, deferring or answering partially; it returns a value or throws. In KQML the performative carries that information: a receiver can reply with sorry, meaning it understood the request and cannot help, which is a different message from an error and from an empty tell. Finin et al. (1994) built this on Searle's (1969) account of speech acts, where asking and telling are different acts even when the proposition is the same. That expressiveness is the real reason an ACL suits autonomous agents, and it is independent of the performance overhead you rightly mention.

On the complexity point, I'd separate two costs. Learning KIF or another content language is a one-off cost. The ongoing cost is that KQML's performative semantics were informal, so two implementations could read the same message differently, which is what led FIPA (2002) to specify its ACL with formal preconditions and effects. A measure that addresses both, and one I used in my own chatbot project, is to keep the content language tiny: a handful of named operations with strict schemas, exchanged over an in-process bus. The parsing overhead becomes negligible, the semantics are whatever the schema says, and you keep the part of the ACL that matters, which is that the agents can refuse, clarify and be replaced independently of one another.

**References**

FIPA (2002) FIPA ACL message structure specification. SC00061G. Geneva: Foundation for Intelligent Physical Agents. Available from: http://www.fipa.org/specs/fipa00061/SC00061G.html [Accessed 2 November 2026].

Finin, T., Fritzson, R., McKay, D. and McEntire, R. (1994) KQML as an agent communication language. Proceedings of the Third International Conference on Information and Knowledge Management (CIKM '94): 456-463. DOI: https://doi.org/10.1145/191246.191322 [Accessed 2 November 2026].

Searle, J.R. (1969) Speech Acts: An Essay in the Philosophy of Language. Cambridge: Cambridge University Press.

## Collaborative Discussion 3: Deep Learning

### Initial Post

URL: https://www.my-course.co.uk/mod/forum/discuss.php?d=398148

Screenshots: [discussion3_initial_post_1.png](screenshots/discussion_3/discussion3_initial_post_1.png), [discussion3_initial_post_2.png](screenshots/discussion_3/discussion3_initial_post_2.png), [discussion3_initial_post_3.png](screenshots/discussion_3/discussion3_initial_post_3.png), [discussion3_initial_post_4.png](screenshots/discussion_3/discussion3_initial_post_4.png)

*The advent of new technologies supported by Deep Learning models means it is now possible to generate "new" content, for example DALL-E to generate images or ChatGPT to create prose. Do you think these technologies offer any ethical issues that should be considered, and if not, why not?*

I think they do, and I'd like to be specific about which issues are new rather than repeating general worries about AI. Generative models are trained on very large corpora scraped from the web and produce outputs by sampling from what they have learned. Three problems follow directly from that mechanism.

The first is provenance. Carlini et al. (2023) showed that diffusion models can reproduce near-copies of individual training images, which means the question of whose work a generated picture contains is not hypothetical. For text, Bender et al. (2021) make the related point that fluency is not understanding: a model that generates convincing prose with no grounding in facts will produce confident falsehoods, and the reader has no signal that distinguishes them from the truth. Having worked with these models in my project, where I deliberately prevented the model from generating any factual content, I'd say this is the issue practitioners most underestimate.

The second is harm at scale. Weidinger et al. (2021) catalogue risks including discrimination through learned stereotypes, leakage of private information memorised from training data, and misuse for disinformation. None of these is unique to deep learning, but generation makes them cheap: a persuasive fake article or image now costs seconds.

The third is accountability. When an image generator produces defamatory or infringing content, responsibility is spread across the data sources, the model developer, the deployer and the user, and existing law was not written for that distribution. The EU AI Act's transparency duties for generative systems (European Parliament and Council, 2024) are an early attempt to pin some of it down.

I don't think these issues argue against the technology. They argue for the kind of design the module has pushed me towards: keep the generative component bounded, label what it produces, and make the deterministic parts of a system responsible for anything that must be true.

### References

Bender, E.M., Gebru, T., McMillan-Major, A. and Shmitchell, S. (2021) On the dangers of stochastic parrots: Can language models be too big? *Proceedings of the 2021 ACM Conference on Fairness, Accountability, and Transparency (FAccT '21)*: 610-623. DOI: https://doi.org/10.1145/3442188.3445922 [Accessed 1 November 2026].

Carlini, N., Hayes, J., Nasr, M., Jagielski, M., Sehwag, V., Tramèr, F., Balle, B., Ippolito, D. and Wallace, E. (2023) Extracting training data from diffusion models. *Proceedings of the 32nd USENIX Security Symposium*: 5253-5270. Available from: https://www.usenix.org/conference/usenixsecurity23/presentation/carlini [Accessed 1 November 2026].

European Parliament and Council (2024) Regulation (EU) 2024/1689 laying down harmonised rules on artificial intelligence (Artificial Intelligence Act). *Official Journal of the European Union* L, 12 July 2024. Available from: https://eur-lex.europa.eu/eli/reg/2024/1689/oj [Accessed 1 November 2026].

Weidinger, L. et al. (2021) Ethical and social risks of harm from language models. arXiv.org. Available from: https://arxiv.org/abs/2112.04359 [Accessed 1 November 2026].

### Peer Response to Adaeze Ugochukwu

URL: https://www.my-course.co.uk/mod/forum/discuss.php?d=360747#p812995

Screenshots: [discussion3_response_adaeze_ugochukwu_1.png](screenshots/discussion_3/discussion3_response_adaeze_ugochukwu_1.png), [discussion3_response_adaeze_ugochukwu_2.png](screenshots/discussion_3/discussion3_response_adaeze_ugochukwu_2.png), [discussion3_response_adaeze_ugochukwu_3.png](screenshots/discussion_3/discussion3_response_adaeze_ugochukwu_3.png), [discussion3_response_adaeze_ugochukwu_4.png](screenshots/discussion_3/discussion3_response_adaeze_ugochukwu_4.png)

Hi Adaeze,

The fabricated medical-image example is the one that worries me most in your post, because it attacks the evidence base rather than any single decision. A biased model produces a wrong answer that can, in principle, be audited; a fabricated figure in a published paper corrupts what everyone downstream believes is true.

Two measures seem to me to follow directly. The first is provenance at the point of creation. The Coalition for Content Provenance and Authenticity (C2PA, 2024) specifies cryptographically signed content credentials that record how an image was produced and edited, and journals could require them for submitted figures in the same way they already require raw data. The EU AI Act goes some way towards making this the default by obliging providers of generative systems to mark synthetic output in a machine-readable form (European Parliament and Council, 2024). Neither stops a determined fraudster, but both raise the cost and give reviewers something to check.

The second addresses your bias point. Gebru et al. (2021) proposed datasheets for datasets, a standard document recording who is represented in training data, how it was collected and what it should not be used for. For clinical models the NHS concern you cite is exactly a datasheet question: if the population in the data does not match the population the model will serve, that should be visible before deployment, not discovered afterwards in outcome disparities.

What both measures have in common is that they move responsibility upstream, to the people with the information, rather than asking the end user to spot a fake. I'd argue that is the right place for it.

**References**

C2PA (2024) Content Credentials: C2PA Technical Specification, version 2.1. Coalition for Content Provenance and Authenticity. Available from: https://c2pa.org/specifications/specifications/2.1/specs/C2PA_Specification.html [Accessed 2 November 2026].

European Parliament and Council (2024) Regulation (EU) 2024/1689 laying down harmonised rules on artificial intelligence (Artificial Intelligence Act). Official Journal of the European Union L, 12 July 2024. Available from: https://eur-lex.europa.eu/eli/reg/2024/1689/oj [Accessed 2 November 2026].

Gebru, T., Morgenstern, J., Vecchione, B., Vaughan, J.W., Wallach, H., Daumé III, H. and Crawford, K. (2021) Datasheets for datasets. Communications of the ACM 64(12): 86-92. DOI: https://doi.org/10.1145/3458723 [Accessed 2 November 2026].

### Peer Response to Sarah Thompson

URL: https://www.my-course.co.uk/mod/forum/discuss.php?d=360699#p812997

Screenshots: [discussion3_response_sarah_thompson_1.png](screenshots/discussion_3/discussion3_response_sarah_thompson_1.png), [discussion3_response_sarah_thompson_2.png](screenshots/discussion_3/discussion3_response_sarah_thompson_2.png), [discussion3_response_sarah_thompson_3.png](screenshots/discussion_3/discussion3_response_sarah_thompson_3.png)

Hi Sarah,

Thank you for taking the discussion into code generation, which for a working developer is the most immediately relevant case. The figures you cite on vulnerability rates match earlier controlled work: Pearce et al. (2022) found that around forty per cent of the Copilot completions they examined in security-relevant scenarios were vulnerable, and the reason has not changed since. A language model optimises for code that looks right, and as Bender et al. (2021) argue for text, fluency is not understanding. Secure code is secure because of context the model never sees.

The measure that follows, and the one I applied in my own project this term, is to treat generated code exactly as one would treat code from an unknown contributor. In practice that meant three things. Every behavioural claim, including the security claims, became a test before the code was accepted, so a plausible-looking access check that checked nothing would fail loudly. Static tools ran on every change and their output was kept, not just glanced at; a security linter and a dependency audit are cheap and they catch the boring, common mistakes that generated code reproduces at scale. And the parts of the system where correctness mattered most were kept small enough that I could read and explain every line, which is my answer to the vibe-coding problem you raise: the engineer still has to own the code, and the honest way to own it is to be able to defend it in a review.

Your governance point is the one I'd extend. Policies about whether to use these tools matter less than policies about what evidence a change must carry before it ships. That is a question organisations already know how to answer; they just have to apply it to code they did not type.

**References**

Bender, E.M., Gebru, T., McMillan-Major, A. and Shmitchell, S. (2021) On the dangers of stochastic parrots: Can language models be too big? Proceedings of the 2021 ACM Conference on Fairness, Accountability, and Transparency (FAccT '21): 610-623. DOI: https://doi.org/10.1145/3442188.3445922 [Accessed 2 November 2026].

Pearce, H., Ahmad, B., Tan, B., Dolan-Gavitt, B. and Karri, R. (2022) Asleep at the keyboard? Assessing the security of GitHub Copilot's code contributions. 2022 IEEE Symposium on Security and Privacy (SP): 754-768. DOI: https://doi.org/10.1109/SP46214.2022.9833571 [Accessed 2 November 2026].
