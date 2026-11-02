"""UniBot: a small multi-agent student-services chatbot.

The package is organised around four cooperating agents (see ``unibot.agents``)
that exchange typed messages over an in-process message bus (``unibot.bus``).
The only non-deterministic component is the optional language-model
interpreter in ``unibot.interpreters``; everything that touches student
records, deadlines or files is ordinary Python so that it can be tested and
reasoned about without a network connection.
"""

__version__ = "1.0.0"
