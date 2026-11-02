# Collaborative Discussion 3: Deep Learning

## Initial Post

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

## Peer Responses

The initial post above was posted to the module forum on 2 November 2026. The two peer responses below were posted as replies in the named students' threads.

### Peer Response to Adaeze Ugochukwu (posted 2 November 2026)

Hi Adaeze,

The fabricated medical-image example is the one that worries me most in your post, because it attacks the evidence base rather than any single decision. A biased model produces a wrong answer that can, in principle, be audited; a fabricated figure in a published paper corrupts what everyone downstream believes is true.

Two measures seem to me to follow directly. The first is provenance at the point of creation. The Coalition for Content Provenance and Authenticity (C2PA, 2024) specifies cryptographically signed content credentials that record how an image was produced and edited, and journals could require them for submitted figures in the same way they already require raw data. The EU AI Act goes some way towards making this the default by obliging providers of generative systems to mark synthetic output in a machine-readable form (European Parliament and Council, 2024). Neither stops a determined fraudster, but both raise the cost and give reviewers something to check.

The second addresses your bias point. Gebru et al. (2021) proposed datasheets for datasets, a standard document recording who is represented in training data, how it was collected and what it should not be used for. For clinical models the NHS concern you cite is exactly a datasheet question: if the population in the data does not match the population the model will serve, that should be visible before deployment, not discovered afterwards in outcome disparities.

What both measures have in common is that they move responsibility upstream, to the people with the information, rather than asking the end user to spot a fake. I'd argue that is the right place for it.

**References**

C2PA (2024) Content Credentials: C2PA Technical Specification, version 2.1. Coalition for Content Provenance and Authenticity. Available from: https://c2pa.org/specifications/specifications/2.1/specs/C2PA_Specification.html [Accessed 2 November 2026].

European Parliament and Council (2024) Regulation (EU) 2024/1689 laying down harmonised rules on artificial intelligence (Artificial Intelligence Act). Official Journal of the European Union L, 12 July 2024. Available from: https://eur-lex.europa.eu/eli/reg/2024/1689/oj [Accessed 2 November 2026].

Gebru, T., Morgenstern, J., Vecchione, B., Vaughan, J.W., Wallach, H., Daumé III, H. and Crawford, K. (2021) Datasheets for datasets. Communications of the ACM 64(12): 86-92. DOI: https://doi.org/10.1145/3458723 [Accessed 2 November 2026].

### Peer Response to Sarah Thompson (posted 2 November 2026)

Hi Sarah,

Thank you for taking the discussion into code generation, which for a working developer is the most immediately relevant case. The figures you cite on vulnerability rates match earlier controlled work: Pearce et al. (2022) found that around forty per cent of the Copilot completions they examined in security-relevant scenarios were vulnerable, and the reason has not changed since. A language model optimises for code that looks right, and as Bender et al. (2021) argue for text, fluency is not understanding. Secure code is secure because of context the model never sees.

The measure that follows, and the one I applied in my own project this term, is to treat generated code exactly as one would treat code from an unknown contributor. In practice that meant three things. Every behavioural claim, including the security claims, became a test before the code was accepted, so a plausible-looking access check that checked nothing would fail loudly. Static tools ran on every change and their output was kept, not just glanced at; a security linter and a dependency audit are cheap and they catch the boring, common mistakes that generated code reproduces at scale. And the parts of the system where correctness mattered most were kept small enough that I could read and explain every line, which is my answer to the vibe-coding problem you raise: the engineer still has to own the code, and the honest way to own it is to be able to defend it in a review.

Your governance point is the one I'd extend. Policies about whether to use these tools matter less than policies about what evidence a change must carry before it ships. That is a question organisations already know how to answer; they just have to apply it to code they did not type.

**References**

Bender, E.M., Gebru, T., McMillan-Major, A. and Shmitchell, S. (2021) On the dangers of stochastic parrots: Can language models be too big? Proceedings of the 2021 ACM Conference on Fairness, Accountability, and Transparency (FAccT '21): 610-623. DOI: https://doi.org/10.1145/3442188.3445922 [Accessed 2 November 2026].

Pearce, H., Ahmad, B., Tan, B., Dolan-Gavitt, B. and Karri, R. (2022) Asleep at the keyboard? Assessing the security of GitHub Copilot's code contributions. 2022 IEEE Symposium on Security and Privacy (SP): 754-768. DOI: https://doi.org/10.1109/SP46214.2022.9833571 [Accessed 2 November 2026].

---

*Evidence: screenshots of these posts on the module forum are in the `screenshots/discussion_3/` folder and are linked, with the text of all nine posts and their forum URLs, from [forum_posts.md](forum_posts.md).*
