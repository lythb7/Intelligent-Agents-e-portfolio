# Collaborative Discussion 1: Agent-Based Systems

## Initial Post

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

## Peer Responses

The initial post above was posted to the module forum on 2 November 2026. The two peer responses below were posted as replies in the named students' threads.

### Peer Response to Pitshou Bokoro (posted 2 November 2026)

Hi Pitshou,

I liked the condition-monitoring framing, because it makes the benefits concrete rather than abstract: a sensor agent that detects an anomaly locally does not need to ship raw data to a central service, and the failure of one agent leaves the others working. That is the distributed-intelligence argument Jennings (2000) makes, and your smart-grid example is a good instance of it.

The point I'd push on is coordination. The same decentralisation that gives fault tolerance also creates interactions nobody designed. Wang et al. (2016) describe exactly this in a smart-factory setting: product, machining and conveying agents negotiate well until several of them want the same shared resource, at which point the system deadlocks, and the authors have to add a central feedback and coordination layer to break the tie. Reynolds (1987) showed the other side of the coin decades earlier, that simple local rules produce convincing global behaviour, but convincing is not the same as verified, and in a monitoring system that decides when to take a turbine offline the difference matters.

So the measure I'd add to your list is an explicit coordination and escalation design: which agent arbitrates when two diagnoses conflict, what the system does when an agent goes quiet rather than failing loudly, and how a human operator sees the agents' reasoning. In my own project I ended up keeping a trace of every inter-agent message for that reason. It is not glamorous, but it is what turns emergent behaviour into something an engineer can sign off.

**References**

Jennings, N.R. (2000) On agent-based software engineering. Artificial Intelligence 117(2): 277-296. DOI: https://doi.org/10.1016/S0004-3702(99)00107-1 [Accessed 2 November 2026].

Reynolds, C.W. (1987) Flocks, herds and schools: A distributed behavioral model. ACM SIGGRAPH Computer Graphics 21(4): 25-34. DOI: https://doi.org/10.1145/37402.37406 [Accessed 2 November 2026].

Wang, S., Wan, J., Zhang, D., Li, D. and Zhang, C. (2016) Towards smart factory for industry 4.0: a self-organized multi-agent system with big data based feedback and coordination. Computer Networks 101: 158-168. DOI: https://doi.org/10.1016/j.comnet.2015.12.017 [Accessed 2 November 2026].

### Peer Response to Maha Hegde (posted 2 November 2026)

Hi Maha,

Your two angles are a useful way in, and I'd like to connect them to the older agent literature, because I think the connection changes what "agent" means in each case. Wooldridge and Jennings (1995) define an agent by autonomy, reactivity, pro-activeness and social ability, and that definition predates large language models by nearly thirty years. The RPA-to-agentic progression you cite is really a story about autonomy being added back to automation: a level-one bot executes a fixed script, whereas an agent decides what to do. The generative-AI angle is a story about social ability, because natural language suddenly made agents easy to instruct. Neither angle on its own gives you the other properties, which is why many products called agents today are still fragile.

On the point that generative systems can plan but not act, Ross is right that tool-calling has closed much of that gap, but I'd argue it has made your security point sharper rather than weaker. Once a model can call tools, anything the model reads becomes a potential instruction, which is the indirect prompt injection problem Greshake et al. (2023) demonstrate against deployed assistants. The measure that follows is to keep the model's decision surface small and validate it in code. In my chatbot project the model may only choose one of ten named operations, every argument is checked locally, and the student identifier is taken from the authenticated session rather than from anything the model produces. That is a direct application of the security framing you end with, and I think it is the design habit the agentic wave most needs.

**References**

Greshake, K., Abdelnabi, S., Mishra, S., Endres, C., Holz, T. and Fritz, M. (2023) Not what you've signed up for: Compromising real-world LLM-integrated applications with indirect prompt injection. Proceedings of the 16th ACM Workshop on Artificial Intelligence and Security (AISec '23): 79-90. DOI: https://doi.org/10.1145/3605764.3623985 [Accessed 2 November 2026].

Wooldridge, M. and Jennings, N.R. (1995) Intelligent agents: theory and practice. The Knowledge Engineering Review 10(2): 115-152. DOI: https://doi.org/10.1017/S0269888900008122 [Accessed 2 November 2026].

---

*Evidence: screenshots of these posts on the module forum are in the `screenshots/discussion_1/` folder and are linked, with the text of all nine posts and their forum URLs, from [forum_posts.md](forum_posts.md).*
