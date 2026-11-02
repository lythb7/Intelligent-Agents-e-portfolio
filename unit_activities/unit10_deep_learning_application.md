# Unit 10: Deep Learning in Action

*Research an application of Deep Learning that you think is going to have an impact on society, and post an overview of the technology, a brief synopsis of how it works, and its potential impacts.*

## Application: AlphaFold and protein structure prediction

**What it does.** A protein's function depends on the three-dimensional shape its chain of amino acids folds into, and determining that shape experimentally takes months of laboratory work per protein. AlphaFold 2 (Jumper et al., 2021) predicts the structure from the amino-acid sequence alone, in minutes, with accuracy that matched experimental methods for most targets in the CASP14 assessment. The predicted structures of over 200 million proteins have since been released in an open database (Varadi et al., 2022).

**How it works.** The system is a deep neural network with two unusual design choices. First, it does not look at the target sequence in isolation; it aligns it with evolutionarily related sequences, because positions that mutate together across species tend to be physically close in the folded structure. Second, its core module, the Evoformer, applies attention jointly to that alignment and to a matrix of pairwise distances between residues, passing information back and forth between the two so that the sequence view and the geometric view refine one another. A structure module then turns the pair representation into explicit atom coordinates, and the network reports a per-residue confidence score (pLDDT) alongside each prediction. The model was trained end-to-end on known structures from the Protein Data Bank.

**Potential impacts.** The social good is substantial: faster target identification in drug discovery, structures for proteins from neglected diseases that no laboratory would have prioritised, and enzyme design for applications such as plastic degradation. The ethical and socio-technical issues are less visible but real. The confidence score is easy to ignore, and a low-confidence region presented as a picture looks exactly as solid as a high-confidence one, so over-trust is a genuine risk in downstream research. The same capability lowers the barrier to designing harmful proteins, which is why dual-use governance for biological design tools is now an active policy question. And the model's accuracy depends on deep evolutionary alignments, so it is weakest precisely for orphan and designed proteins, which concentrates its benefits where data already exist. I'd argue AlphaFold is the clearest case so far of deep learning changing a scientific field, and that its lesson for practitioners is to ship the uncertainty estimate as prominently as the prediction.

### References

Jumper, J. et al. (2021) Highly accurate protein structure prediction with AlphaFold. *Nature* 596: 583-589. DOI: https://doi.org/10.1038/s41586-021-03819-2 [Accessed 29 October 2026].

Varadi, M. et al. (2022) AlphaFold Protein Structure Database: massively expanding the structural coverage of protein-sequence space with high-accuracy models. *Nucleic Acids Research* 50(D1): D439-D444. DOI: https://doi.org/10.1093/nar/gkab1061 [Accessed 30 October 2026].
