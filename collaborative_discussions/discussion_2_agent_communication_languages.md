# Collaborative Discussion 2: Agent Communication Languages

## Initial Post

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

## Peer Responses

The initial post above was posted to the module forum on 2 November 2026. The two peer responses below were posted as replies in the named students' threads.

### Peer Response to Adaeze Ugochukwu (posted 2 November 2026)

Hi Adaeze,

The healthcare decision-support example is a good one because it shows the part of KQML that is easy to overlook: the mediator agent you describe is a facilitator in Finin et al.'s (1994) sense, an agent whose job is to broker requests to whichever source can answer them, so that a clinic's system never has to know where the knowledge lives. That indirection is what makes the architecture extensible, and it is the feature a remote method call cannot give you, because RMI binds the caller to a specific interface at a specific address (Labrou, Finin and Peng, 1999).

Where I'd add to your limitations is the ontology problem, which I think is deeper than standardisation of vocabularies. Even when two agents agree a protocol, they may carve the domain up differently, and Payne and Tamma (2014) show that reconciling two agents' correspondences can itself require a negotiation dialogue, with each side disclosing only part of what it knows. In healthcare that is not a corner case; two hospitals' coding of the same condition routinely differs. So the honest comparison with method invocation is that Java solves this at compile time by forcing a shared interface, whereas an ACL pushes the problem to run time where it is more flexible and much harder.

A practical measure, which I used in my own project, is to keep the content language deliberately tiny and let the performatives do the work: a handful of operations, strict schemas for each, and a sorry performative so that an agent can say it does not understand rather than guessing. It does not solve ontology alignment, but it makes the failure visible instead of silent.

**References**

Finin, T., Fritzson, R., McKay, D. and McEntire, R. (1994) KQML as an agent communication language. Proceedings of the Third International Conference on Information and Knowledge Management (CIKM '94): 456-463. DOI: https://doi.org/10.1145/191246.191322 [Accessed 2 November 2026].

Labrou, Y., Finin, T. and Peng, Y. (1999) Agent communication languages: the current landscape. IEEE Intelligent Systems 14(2): 45-52. DOI: https://doi.org/10.1109/5254.757631 [Accessed 2 November 2026].

Payne, T.R. and Tamma, V. (2014) Negotiating over ontological correspondences with asymmetric and incomplete knowledge. Proceedings of the 13th International Conference on Autonomous Agents and Multiagent Systems (AAMAS 2014): 517-524.

### Peer Response to Fatema Mohammed Ahmed Aal Malek Alshehhi (posted 2 November 2026)

Hi Fatema,

I agree with your conclusion that the choice depends on coupling, and I'd like to add one distinction that I think explains why. A method call and a KQML message differ not only in cost but in what they can express. When I call a method, the callee has no vocabulary for declining, deferring or answering partially; it returns a value or throws. In KQML the performative carries that information: a receiver can reply with sorry, meaning it understood the request and cannot help, which is a different message from an error and from an empty tell. Finin et al. (1994) built this on Searle's (1969) account of speech acts, where asking and telling are different acts even when the proposition is the same. That expressiveness is the real reason an ACL suits autonomous agents, and it is independent of the performance overhead you rightly mention.

On the complexity point, I'd separate two costs. Learning KIF or another content language is a one-off cost. The ongoing cost is that KQML's performative semantics were informal, so two implementations could read the same message differently, which is what led FIPA (2002) to specify its ACL with formal preconditions and effects. A measure that addresses both, and one I used in my own chatbot project, is to keep the content language tiny: a handful of named operations with strict schemas, exchanged over an in-process bus. The parsing overhead becomes negligible, the semantics are whatever the schema says, and you keep the part of the ACL that matters, which is that the agents can refuse, clarify and be replaced independently of one another.

**References**

FIPA (2002) FIPA ACL message structure specification. SC00061G. Geneva: Foundation for Intelligent Physical Agents. Available from: http://www.fipa.org/specs/fipa00061/SC00061G.html [Accessed 2 November 2026].

Finin, T., Fritzson, R., McKay, D. and McEntire, R. (1994) KQML as an agent communication language. Proceedings of the Third International Conference on Information and Knowledge Management (CIKM '94): 456-463. DOI: https://doi.org/10.1145/191246.191322 [Accessed 2 November 2026].

Searle, J.R. (1969) Speech Acts: An Essay in the Philosophy of Language. Cambridge: Cambridge University Press.

---

*Evidence: screenshots of these posts on the module forum are in the `screenshots/discussion_2/` folder and are linked, with the text of all nine posts and their forum URLs, from [forum_posts.md](forum_posts.md).*
