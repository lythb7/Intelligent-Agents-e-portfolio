# Unit 6: Creating Agent Dialogues

*Design a dialogue between two agents using KQML and KIF.*

The activity asks for a dialogue between Alice, an agent that procures stock, and Bob, an agent that controls stock levels for a warehouse, in which Alice asks about the available stock of 50-inch televisions and the number of HDMI slots they have. The exchange below uses KQML performatives (Finin et al., 1994) with KIF-style content. I wrote it first as a script, then implemented both agents in Python ([`code/agent_dialogue.py`](code/agent_dialogue.py)) so the dialogue can be executed and the output inspected; the printed transcript is in [`outputs/agent_dialogue_output.txt`](outputs/agent_dialogue_output.txt).

The note I'd make about the design is that the performative carries the force of the message and the content carries the proposition. Alice's first message is an *ask-all* because she wants every matching product, not one; the follow-ups are *ask-one* because each asks about a single model; and when she asks about a product Bob does not stock, he answers with *sorry* rather than with an empty *tell*, because "I have none of that" and "I don't know that product" are different answers. The `:reply-with` and `:in-reply-to` fields thread the conversation, which is what lets an agent handle several conversations at once.

```lisp
(ask-all
  :sender Alice :receiver Bob
  :language KIF :ontology warehouse-stock
  :reply-with id1
  :content (in-stock ?product ?units) (screen-size ?product 50))

(tell
  :sender Bob :receiver Alice
  :language KIF :ontology warehouse-stock
  :reply-with id2 :in-reply-to id1
  :content ((in-stock TV-5001 42) (in-stock TV-5002 17)))

(ask-one
  :sender Alice :receiver Bob
  :language KIF :ontology warehouse-stock
  :reply-with id3
  :content (hdmi-ports TV-5001 ?n))

(tell
  :sender Bob :receiver Alice
  :language KIF :ontology warehouse-stock
  :reply-with id4 :in-reply-to id3
  :content (hdmi-ports TV-5001 3))

(ask-one
  :sender Alice :receiver Bob
  :language KIF :ontology warehouse-stock
  :reply-with id5
  :content (hdmi-ports TV-5002 ?n))

(tell
  :sender Bob :receiver Alice
  :language KIF :ontology warehouse-stock
  :reply-with id6 :in-reply-to id5
  :content (hdmi-ports TV-5002 4))

(ask-one
  :sender Alice :receiver Bob
  :language KIF :ontology warehouse-stock
  :reply-with id7
  :content (hdmi-ports TV-9999 ?n))

(sorry
  :sender Bob :receiver Alice
  :language KIF :ontology warehouse-stock
  :reply-with id8 :in-reply-to id7
  :content (unknown-product TV-9999))
```

The same ideas carried straight into my development project, where a dialogue agent sends *ask-one* and *achieve* messages to timetable, transcript and assignment agents over a message bus, and the interface shows the exchange live.

### Reference

Finin, T., Fritzson, R., McKay, D. and McEntire, R. (1994) KQML as an agent communication language. *Proceedings of the Third International Conference on Information and Knowledge Management (CIKM '94)*: 456-463. DOI: https://doi.org/10.1145/191246.191322 [Accessed 27 October 2026].
