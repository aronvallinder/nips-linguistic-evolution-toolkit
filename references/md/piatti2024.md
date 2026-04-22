## **Cooperate or Collapse: Emergence of Sustainable** **Cooperation in a Society of LLM Agents**

**Giorgio Piatti** **[1,]** _[∗]_ **Zhijing Jin** **[1,2,3,]** _[∗]_ **Max Kleiman-Weiner** **[4,]** _[∗]_

**Bernhard Schölkopf** **[2]** **Mrinmaya Sachan** **[1]** **Rada Mihalcea** **[5]**

1 ETH Zürich 2 MPI for Intelligent Systems, Tübingen
3 University of Toronto 4 University of Washington 5 University of Michigan

```
   giorgio.piatti@alumni.ethz.ch zjin@cs.toronto.edu maxkw@uw.edu

```

**Abstract**


As AI systems pervade human life, ensuring that large language models (LLMs)
make safe decisions remains a significant challenge. We introduce the G OV ernance
of the Commons S IM ulation (G OV S IM ), a generative simulation platform designed
to study strategic interactions and cooperative decision-making in LLMs. In
G OV S IM, a society of AI agents must collectively balance exploiting a common resource with sustaining it for future use. This environment enables the study of how
ethical considerations, strategic planning, and negotiation skills impact cooperative
outcomes. We develop an LLM-based agent architecture and test it with the leading
open and closed LLMs. We find that all but the most powerful LLM agents fail to
achieve a sustainable equilibrium in G OV S IM, with the highest survival rate below
54%. Ablations reveal that successful multi-agent communication between agents
is critical for achieving cooperation in these cases. Furthermore, our analyses show
that the failure to achieve sustainable cooperation in most LLMs stems from their
inability to formulate and analyze hypotheses about the long-term effects of their
actions on the equilibrium of the group. Finally, we show that agents that leverage
“Universalization”-based reasoning, a theory of moral thinking, are able to achieve
significantly better sustainability. Taken together, G OV S IM enables us to study the
mechanisms that underlie sustainable self-government with specificity and scale.
We open source the full suite of our research results, including the simulation
environment, agent prompts, and a comprehensive web interface. [1]


**1** **Introduction**


Recent advances in large language models (LLMs) have demonstrated impressive abilities across many
tasks [ 1, 7, 8, 69 ], and LLMs are being integrated into complex agents [ 12, 21 ]. As LLMs become
a central component of these systems, they often inherit critical decision-making responsibilities.
While LLMs have demonstrated proficiency in simple arithmetic tasks, their performance on more
complex economic reasoning and rational decision-making tasks remains limited [ 62 ]. Therefore,
an analysis of their ability to operate safely and reliably, especially in contexts where cooperation is
necessary. Multi-agent interaction is a fundamental feature across many scales of human life. When
cooperation between agents (and humans) is possible, better outcomes for all through joint effort are
possible [ 27, 39, 40, 63 ]. If AI agents take on complex decision-making roles in multi-agent contexts,
they are likely to face cooperation challenges that are similar to those faced by people. Thus, we
need robust and safe AI that cooperates with us as well as (or better than) we can cooperate with each
other [16].


_∗_ Equal contribution.
1
Our code is available at `[https://github.com/giorgiopiatti/GovSim](https://github.com/giorgiopiatti/GovSim)` .


38th Conference on Neural Information Processing Systems (NeurIPS 2024).


**Community of AI Agents**


**Agents must share without**
**depleting the shared resource.**



**Resource Sharing Scenarios**



**Collective Outcome**


**Cooperate**


**Emergent**
**mechanism design**


**Collapse**



**Pasture**



**Fishery** **or**



**Pollution**


Figure 1: Illustration of the G OV S IM benchmark. AI agents engage in three resource-sharing
scenarios: fishery, pasture, and pollution. We find that all but the most powerful LLM agents fail to
achieve a sustainable equilibrium in G OV S IM, with the highest survival rate below 54%.


Despite significant advances in the scale and ability of LLMs, researchers still have only a limited
understanding of their cooperative behavior. Prior multi-agent research has focused on highly
constrained scenarios such as board games or narrowly defined collaborative tasks [ 19, 45, 48, 64, 72 ].
These multi-agent studies complement existing single-agent AI safety benchmarks [ 38, 58 ]. However,
this prior work leaves three key questions open: (1) in contrast to the well-documented mechanisms
that enable cooperation in people [ 20, 56, 57 ], there is limited understanding of how LLMs achieve
and maintain cooperation; (2) how to handle multi-turn LLM interactions that balance safety with
reward maximization in multi-agent settings; and (3) the potential of using LLMs as a simulation
platform for to better understand and test theories of human psychology and economic behavior.


To address these gaps, we develop a novel simulation environment, called the G OV ernance of the
Commons S IM ulation (G OV S IM ). G OV S IM allows us to evaluate LLM-based agents in multiagent, multi-turn resource-sharing scenarios and requires agents to engage in sophisticated strategic
reasoning through ethical decision-making and negotiation. Inspired by game-theoretic research on
the evolution of cooperation [ 5 ] and “The Tragedy of the Commons,” we build G OV S IM to simulate
realistic multi-party _social dilemmas_ such as those faced by groups managing shared resources

[ 27, 63 ]. Our platform can support any text-based agent, including LLMs and humans, and mirrors
some of the complexity in actual human interactions. We use G OV S IM to benchmark the cooperative
behaviors of today’s and future LLMs, using a generative agent architecture [ 60 ], that accommodates
different models.


Within G OV S IM, we develop three common pool resource dilemmas inspired by the economic
analysis of emergent sustainable cooperation [ 25 – 27, 43, 56 ]. We test our generative agents with
fifteen different LLMs, including open-weights and closed-weights models. Surprisingly, we find
that all but the most powerful LLM agents fail to achieve a sustainable equilibrium in G OV S IM, with
the highest survival rate below 54%. Analysis of LLM behavior suggests that the lack of sustainable
governance may result from an inability to mentally simulate the long-term effects of greedy actions
on the equilibrium of the multi-agent system. To address this challenge, we find that prompting
agents to consider the universalization of their action [ 43 ], a process used by people when making
moral judgments in social dilemmas, significantly improves survival time. To evaluate the robustness
of the norms formed by LLMs in G OV S IM, we introduce a greedy newcomer who is unfamiliar
with an already formed norm (i.e., the agent does not observe the prior history of interactions).
This perturbation increases inequality across agents and, in some cases, leads to the collapse of
cooperation. Finally, we perform extensive analyses to understand how each LLM’s individual
reasoning capabilities contribute to achieving sustainable cooperation. We show that communication
between agents is key to success in G OV S IM . Ablation studies show that communication reduces
resource overuse by 21%. Using an automated analysis of agent dialogues, we show that negotiation
is the main type of communication between agents and constitutes 62% of the dialogues. Finally,
other subskills are also important for sustainability. The ability to form beliefs about other agents is
highly correlated (0.83) with community survival time.


In summary, our contributions are as follows:


1. We introduce G OV S IM, the first common pool resource-sharing simulation platform for
LLM agents. G OV S IM enables us to study and benchmark emergent sustainable behavior in
LLMs.


2


Figure 2: Prompt sketches of our baseline agent for the G OV S IM fishing scenario, detailed prompt
examples can be found in Appendix C.


2. Using G OV S IM, we find that only the largest and most powerful LLMs ever reach a
sustainable outcome with the best agent below a 54% survival rate.


3. We develop a more cooperatively capable agent based on the philosophical principle of
universalization. Through ablation and perturbation, we characterize the boundary conditions
for the emergence of sustainable cooperation.


4. We open-source our simulation framework to foster future research: the G OV S IM simulation
environment, agent prompts, and a web interface.


**2** **The G** **OV** **S** **IM** **Environment**


To understand the logic behind the G OV S IM environment, we first briefly summarize the economic theory of cooperation and describe the simulation environment and metrics used to evaluate cooperative
resource management.


**2.1** **Economic Background**

Sustaining cooperation is an essential problem that enables individuals to achieve better outcomes
than they could achieve on their own [ 63, 66, 68 ]. Humans solve cooperation problems across all
scales of life, ranging from small groups of fishermen who harvest a shared resource to multi-national
treaties that restrict pollution to reduce the adverse effects of climate change. However, when _self-_
_interested_ individuals or organizations are faced with paying a _personal cost_ to sustain a _greater good_,
cooperation can be challenging to maintain [27].


Although mechanism designers have developed incentive-compatible systems that can lead to cooperation between self-interested agents, these systems often assume a top-down process that coordinates
the process [ 65, 75 ]. In contrast, humans develop mechanisms from the bottom up and implement
cooperative norms in a decentralized fashion. For example, when managing a shared resource, people
develop rules and norms that lead to long-term sustainable cooperation [20, 56, 57].


**2.2** **G** **OV** **S** **IM** **Description**

The purpose of G OV S IM is to evaluate the ability of LLMs to engage in cooperative behavior and
effective governance of shared resources. In G OV S IM, agents are given a common pool of natural
resources that regenerates over time. The task is to sustainably manage the use of this resource. Take
too much, and the resource will collapse and no longer regenerate again (e.g., the fish in a lake go
extinct). Take too little, and the resource’s economic potential is underutilized. Even a purely selfish
agent that aims to maximize their _long-term_ reward must balance the amount of resources they extract
now with what they will be able to extract in the future. When multiple agents are involved, questions
of fairness arise [41, 42]. Agents must negotiate what they believe to be their fair share.


3


We have implemented three scenarios in G OV S IM inspired by the economics literature on governing
common pool resources. The first is inspired by empirical work on understanding the norms that
emerge in communities of fishermen that prevent overfishing [ 25, 43, 56 ]. In the first scenario,
**fishery**, agents share a fish-filled lake, and each decides how many tons of fish each should catch
each month. The lake supports up to 100 tons of fish, and the fish population doubles at the end of
the month up to this capacity. For example, five fishermen can sustainably catch up to 10 tons of
fish each per month, but if the total amount they catch exceeds 50 tons, the population will start to
decrease. See Figure 2 for prompt sketches regarding this scenario. In the second scenario, **pasture**,
and following Hardin [27] and Greene [26], agents are shepherds and control flocks of sheep. Each
month, they decide how many sheep they’ll allow on a shared pasture. Like the fish, the pasture can
support up to 100 hectares of grass; each sheep consumes 1 hectare per month, and the remaining
grass doubles up to its capacity. In the third scenario, **pollution**, agents are factory owners who must
balance production with pollution. For each pallet of widgets produced, their factory pollutes 1% of
the water in a shared river. Like the previous cases, at the end of the month, the amount of unpolluted
water doubles.


**2.3** **G** **OV** **S** **IM** **Environment Dynamics**

To facilitate comparison across scenarios, the underlying resource regeneration dynamics of each
environment are mathematically equivalent.


**Amount of Shared Resource** _h_ ( _t_ ) **.** The amount of shared resources available at time _t_ is denoted
by _h_ ( _t_ ) . The function _h_ : N _→_ N maps each time step to the corresponding quantity of available
resources. We assume integer units of the shared resource.


The simulation is based on two main phases: harvesting and discussion. At the beginning of the
month, the agents harvest the shared resource. All agents submit their actions privately (how much of
the resource they would like to consume up to the total resources available); their actions are then
executed simultaneously, and each agent’s individual choices are made public. At this point, the
agents have an opportunity to communicate freely with each other using natural language. At the end
of the month, the remaining shared resources double (capped by 100). When _h_ ( _t_ ) falls below _C_ = 5
the resource collapses and nothing else can be extracted. Each scenario describes a type of public
goods game that is repeated for _T_ time steps [ 9 ]. A bound on optimal group behavior is for agents to
jointly consume no more than the sustainability threshold.


**Sustainability Threshold** _f_ ( _t_ ) **.** This threshold represents the maximum resources that can be
extracted at time _t_ without diminishing the resource stock at time _t_ +1, considering the future resource
growth multiplier _g_ . Formally, the sustainability threshold is given by the function _f_ : N _→_ N and is
defined as follows: _f_ ( _t_ ) = max ( _{x | g_ ( _h_ ( _t_ ) _−_ _x_ ) _≥_ _h_ ( _t_ ) _}_ ) _._


Together, G OV S IM can be viewed as a partially observable Markov game that interleaves actions,
observations, and rewards with an unstructured dialogue between agents. Formally, a simulation _D_
is essentially a function that takes as input a tuple ( _I, M, G, E_ ) and returns a trajectory of the joint
policy ( _π_ _i_ ) _i∈I_ ; where _I_ is the set of agents, _π_ _i_ is the policy induced by an LLM _M_ together with
a generative agent architecture _G_, _E_ are the dynamics of the environment. Each agent receives an
individual reward _r_ _i_ _[t]_ [defined by the amount of the resource collected in the time step] _[ t]_ [.]


**2.4** **G** **OV** **S** **IM** **Metrics**

In this section, we introduce metrics that measure different qualities of the collective outcome. We
follow Perolat et al. [61] in defining a suite of metrics since in a mixed incentive repeated game like
G OV S IM, no single scalar metric can track the entire state of the system.


**Survival Time** _m_ **.** To assess the sustainability of a simulation run, we define the number of
units of time survived _m_ as the longest period during which the shared resource remains above _C_ :
_m_ = max ( _{t ∈_ N _| h_ ( _t_ ) _> C}_ ) _._


**Survival Rate** _q_ **.** Moreover, we define the proportion of runs which achieve maximum survival
time, i.e., _m_ = 12, as survival rate: _q_ = [#] _[{]_ # _[m]_ runs [=12] _[}]_ _._


**Total Gain** _R_ _i_ **for Each Agent** _i_ **.** Let _r_ _t_ _[i]_ _[∈]_ [N][ with] _[ t]_ [ = 1] _[, . . ., T]_ [ represent the sequence of resources]
collected by the _i_ -th agent at time _t_ over the simulation duration _T_ . The total gain for each agent, _R_ _i_,
is defined as: _R_ _i_ = [�] _[T]_ _t_ =1 _[r]_ _t_ _[i]_ [.]


4


**Efficiency** _u_ **.** We define the efficiency _u_ as how optimally the shared resource is utilized w.r.t. the
maximal possible efficiency. Intuitively, maximum efficiency max( _u_ ) is achieved when the resource
is consistently regenerated to its maximum capacity such that the amount harvested is equal to the
initial sustainability threshold _f_ (0). Hence, we define _u_ as:

max 0 _, T · f_ (0) _−_ [�] _[T]_ _t_ =1 _[R]_ _[t]_ [�]
�
_u_ = 1 _−_ _._ (1)

_T · f_ (0)


**(In)equality** _e_ **.** We quantify (in)equality _e_, using the the Gini coefficient [ 24 ]. Across the total
gains _{R_ _i_ _}_ _[|I|]_ _i_ =0 [of all] _[ |I|]_ [ agents:]



_e_ = 1 _−_



� _|I|i_ =1 � _|I|j_ =1 _[|][R]_ _[i]_ _[ −]_ _[R]_ _[j]_ _[|]_

_,_ (2)
2 _|I|_ ~~[�]~~ _[|I|]_ _i_ =1 _[R]_ _[i]_



where we normalize the absolute differences between pairs of agents by the total gains of all agents.


**Over-usage** _o_ **.** We quantify the amount of (un)sustainable behavior across a simulation. The overusage _o_, is the percentage of actions across the experiment that exceed the sustainability threshold:


_|I|_ _T_
� _i_ =1 � _t_ =1 [1] [(] _[r]_ _t_ _[i]_ _[> ][f]_ [(] _[t]_ [))]
_o_ = _._ (3)
_|I| · m_


**3** **Experimental Results**


**3.1** **Experimental Setup**

**Agent Architectures** To test LLM performance in G OV S IM, we develop an LLM-based agent
architecture based on the “generative agents” framework [ 60 ]. These agents work in a phase-based
environment – different phases require different decisions ranging from deciding how much of a
resource to extract or open-ended discussion. Each agent receives identical instructions that explain
the dynamics of G OV S IM . The instructions were carefully designed to avoid priming models to be
cooperative or greedy, as shown in Figure 2 for the fishery scenario. Full details are presented in
Appendix B.


**LLMs Benchmarked** We compile a diverse suite of instruction-tuned LLMs for experiments on
G OV S IM . We test existing closed-weights models: GPT-3.5, GPT-4, GPT-4-turbo, and GPT-4o [ 1 ]
via OpenAI API, Claude-3 Haiku, Sonnet, and Opus via Anthropic API. We also tested open-weights
models: Llama-2 (7B, 13B, 70B) [ 69 ], Llama-3 (8B, 70B) [ 51 ], Mistral (7B, 8x7B) [ 34 ], Qwen (72B,
110B) [6]. See Appendix D.1 for exact model identifiers, hardware requirements, and API costs.


When testing LLMs, we ensure reproducibility by setting the text generation temperature to zero,
i.e., greedy decoding. We provide full experimental details in Appendix D and on our GitHub. Each
simulation was repeated with five random seeds. The average scores for each metric are presented in
the main text, while the standard deviations are in the appendix.


**3.2** **Benchmarking G** **OV** **S** **IM**

The G OV S IM environment serves as a _sustainability benchmark_ to evaluate whether LLM agents can
effectively cooperate to maintain a common pool of resources and avoid depletion. Possible outcomes
are reflected in the above metrics over multiple simulations controlled by an LLM _M_ . Intuitively,
cooperation is optimized when agents achieve high total gain, _R_, by maximizing efficiency, _u_, and
achieving high survival time, _m_ .


We benchmark LLM agents across our three scenarios to assess how these agents balance resource
utilization (reward maximization) and preservation (safety). First, smaller models (such as Llama-38B) often fail to sustainably manage any of the resources at all. In our simulations, they never sustain
any of the resources past the first month. Second, no LLM in our studies could sustain the resource
in all of the 5 seeds across the three scenarios (survival time 12). In Table 1, larger models (such
as GPT-4o) show better survival time and total gain, though their success varied across scenarios.
Finally, LLMs performed better in the fishery scenario than in the pasture and pollution scenarios
(cf. Appendix D.2). One possibility for this difference is that the fishing scenario only requires
reasoning about a single variable (fish). In contrast, the other scenarios involve interactions between
two variables, such as grass and sheep, or pollution and the production of widgets.


5


Table 1: Experiment: _default_ . We aggregated across the three scenarios and five runs. We report the
survival rate, the mean, and 95% confidence intervals of survival time (Surv.), total gain (Gain), efficiency (Eff.), equality (Eq.), and Over-usage. The best performance is indicated in bold, and the best
open-weight performance is indicated by underlining. We report Llama-2 results in Appendix D.2.


Model Survival Rate Survival Time Gain Efficiency Equality Over-usage


_**Open-Weights Models**_
Llama-3-8B 0.0 1.0 _±_ 0.00 20.0 _±_ 0.00 16.7 _±_ 0.00 57.3 _±_ 7.00 20.0 _±_ 2.70

Llama-3-70B 0.0 1.0 _±_ 0.00 20.0 _±_ 0.00 16.7 _±_ 0.00 90.7 _±_ 1.80 38.7 _±_ 2.60

Mistral-7B 0.0 1.0 _±_ 0.00 20.0 _±_ 0.00 16.7 _±_ 0.00 82.6 _±_ 4.80 37.3 _±_ 4.70

Mixtral-8x7B 0.0 1.1 _±_ 0.10 20.1 _±_ 0.20 16.7 _±_ 0.20 75.0 _±_ 9.50 33.3 _±_ 6.00
Qwen-72B 0.0 1.8 _±_ 0.80 24.0 _±_ 4.40 20.0 _±_ 3.60 83.9 _±_ 3.10 32.4 _±_ 5.30
Qwen-110B 20.0 4.5 _±_ 2.30 36.3 _±_ 12.00 30.3 _±_ 10.00 89.6 _±_ 3.60 47.0 _±_ 13.40


_**Closed-Weights Models**_
Claude-3 Haiku 0.0 1.0 _±_ 0.00 20.0 _±_ 0.00 16.7 _±_ 0.00 91.0 _±_ 3.50 35.7 _±_ 0.00

Claude-3 Sonnet 0.0 1.3 _±_ 0.30 20.5 _±_ 0.40 17.1 _±_ 0.40 84.4 _±_ 5.60 32.0 _±_ 1.80
Claude-3 Opus 46.7 6.9 _±_ 2.90 58.5 _±_ 22.10 48.8 _±_ 18.40 91.4 _±_ 4.40 21.0 _±_ 8.50
GPT-3.5 0.0 1.1 _±_ 0.20 20.3 _±_ 0.40 16.9 _±_ 0.30 91.2 _±_ 3.20 35.3 _±_ 2.50

GPT-4 6.7 3.9 _±_ 1.50 31.5 _±_ 5.80 26.2 _±_ 4.80 91.4 _±_ 2.30 27.1 _±_ 6.10

GPT-4-turbo 40.0 6.6 _±_ 2.60 62.4 _±_ 22.00 52.0 _±_ 18.30 93.6 _±_ 2.70 15.7 _±_ 8.60

GPT-4o **53.3** **9.3** _±_ 2.20 **66.0** _±_ 14.60 **55.0** _±_ 12.20 **94.4** _±_ 3.10 **10.8** _±_ 8.60


**3.3** **Norm Robustness: A Greedy Newcomer**


Having established a baseline, we investigate the robustness of the sustainability strategies discovered
by LLM agents. Robustness is measured by inserting a new selfish agent into an existing community
of sustainable agents. We start with a community of four agents who had the opportunity to reach
a cooperative equilibrium in the first three months of the simulation. The new player was given
the goal of maximizing their own profit while being indifferent to the welfare of others. This
experiment analyzes how the original group adapts or enforces cooperation to prevent resource
depletion under this perturbation. We use the same setup as Section 3.2 and modify prompts as shown
in Appendix D.4.


We perform this experiment across all scenarios using GPT-4o, the best performing model in Table 1.
Across five seeds, the survival rate drops from 53 _._ 3 _→_ 33 _._ 3, the survival time drops from 9 _._ 3 _→_ 6 _._ 6,
the gain drops from 66 _._ 0 _→_ 34 _._ 8, the efficiency drops from 55 _._ 0 _→_ 31 _._ 3, equality drops from
94 _._ 4 _→_ 71 _._ 7 and over-usage increases from 10 _._ 8 _→_ 15 _._ 7 . Figure 3b shows an example simulation
trajectory of the newcomer perturbation where things go well. The newcomer initially harvests a
large number of shared resource (see month 4), but adjusts to lower harvest rates in subsequent
months. This adjustment results from dynamic interactions with the original four agents who align the
newcomer to a more sustainable norm over time. In Appendix G, we provide a qualitative example of
these interactions, illustrating how the newcomer learns to reduce the number of harvested resources
and comply with the sustainable norm through community discussions. Overall, more work is needed
to improve robustness to perturbations of this type.



#units of shared resource Agent 5 Agent 4


Agent 3 Agent 2 Agent 1


100


80


60


40


20


0
1 2 3 4 5 6 7 8 9 10 11 12


Month


(a) Resource change in the baseline condition.



#units of shared resource Newcomer Villager


100


80


60


40


20


0
1 2 3 4 5 6 7 8 9 10 11 12 13 14 15


Month


(b) Resource change in the newcomer perturbation.



Figure 3: Two example trajectories through the 12 time steps. The pool of shared resources (by the
number of units) at the beginning of each of the 12 months (dotted line), and the number of units of
resource each agent harvests per month (blue bars, red for the newcomer).


6


100 With Communication Without Communication


80


60


40


20


0
Claude-3 Opus GPT-4 GPT-4o Qwen-110B


(a) Over-usage of shared resources in scenarios with
and without communication.



Negotiation Information Relational



2%



1.01%







0.99% 79%





Claude-3 Opus GPT-4 GPT-4o Qwen-110B


(b) Classification of utterance typologies in communication scenarios.



Figure 4: Impact of communication on sustainability: (a) Comparison of over-usage percentages
between simulations with and without communication scenarios. This figure illustrates how the
absence of communication leads to a marked increase in resource over-usage. (b) Distribution of
different types of utterances (information, negotiation, relational) across communication scenarios.


**3.4** **Improving Sustainability by Universalization Reasoning**


Analysis of LLM behavior suggests that the lack of sustainable governance may result from an
inability to mentally simulate the long-term effects of greedy actions on the equilibrium of the
multi-agent system. One approach to make these consequences salient is through a mechanism known
in the moral psychology and philosophy literature as “Universalization” [ 37, 43 ]. The basic idea
of Universalization is that when assessing whether a particular moral rule or action is permissible,
one should ask, “What if **everybody** does that?” [ 37 ]. Previous work has shown this process shapes
people’s moral judgments in social dilemmas [ 43 ]. Here, we hypothesize that a similar mechanism
may make sustainable cooperation more likely in LLMs by making the long-term consequences of
collective action more salient. For instance, a naive model might reason, “I should take as many fish
as I can,” but if forced to consider the universalization of that policy (“we each take as many fish as
we can”), they realize that such a policy will cause rapid collapse.


To study whether Universalization can encourage sustainable cooperation, we augment the memory
of each agent with the following statement, “Given the current situation, if everyone takes more than
_f_ ( _t_ ), the shared resources will decrease next month.”, where _f_ ( _t_ ) is the sustainable threshold defined
in Section 2.4. For this test, we measure the delta between metrics with universalization and without
universalization.


We report the impact of Universalization on the different LLM (excluding Claude-3 Opus due to API
costs) models described in Section 3.1. We find that Universalization, excluding two combinations
that already had a maximum survival time, significantly increases the average survival time by 4
months (t-test; _p <_ 0 _._ 001 ), total gain by 29 units of shared resource (t-test; _p <_ 0 _._ 001 ), and efficiency
by 24% (t-test; _p <_ 0 _._ 001 ). For a detailed breakdown of these improvements across models, see
Appendix D.3.


**3.5** **Ablation of Communication**


A powerful aspect of our framework is that the role of open-ended communication can be studied
explicitly in the context of solving common pool resources problems. To quantify the value of
these communication channels, we ablate agents’ ability to communicate. We perform these tests
on the subset of models that have survival rate greater than 10%, see Table 1 ( _GPT-4o, GPT-4-_
_turbo, Claude-3 Opus, Qwen-110B_ ). Comparing simulations without communication with those with
communication, we find that agents without communication tend to overuse the common resource by
22% (t-test; _p <_ 0 _._ 001 ). This result shows the importance of the communication phase for sustainable
resources. Analyzing the interactions between agents, we find that in most conversations, agents
coordinate on extraction limits equal to or below the sustainable threshold through discussion, thereby
increasing the robustness of resource use.


**3.6** **Analysis of Agent Dialogues**


To provide insight into how open-ended dialogue supports cooperation, we quantitatively analyze
the conversations produced by the LLM during the discussion phase. To support interpretability,
we categorize conversations into three high-level clusters: information sharing, negotiation, and
relational interactions using the following taxonomy:


7


Llama-2-7B Llama-2-13B Llama-2-70B Llama-3-8B Llama-3-70B Mistral-7B Mixtral-8x7B Qwen-72B


Qwen-110B Claude-3 Haiku Claude-3 Sonnet Claude-3 Opus GPT-3.5 GPT-4 GPT-4o



12


10


8


6


4


2


0
0 0.1 0.2 0.3 0.4 0.5 0.6 0.7 0.8 0.9 1



12


10


8


6


4


2


0

|Col1|Col2|Col3|Col4|Col5|Col6|Col7|Col8|Col9|Col10|Col11|
|---|---|---|---|---|---|---|---|---|---|---|
||||||||||||
||||||||||||
||||||||||||
||||||||||||
||||||||||||
||||||||||||

0 0.1 0.2 0.3 0.4 0.5 0.6 0.7 0.8 0.9 1



a) Accuracy: simulation dynamics b) Accuracy: sustainable action (without community interaction)



12


10


8


6


4


2


0
0 0.1 0.2 0.3 0.4 0.5 0.6 0.7 0.8 0.9 1



12


10


8


6


4


2


0

|Col1|Col2|Col3|Col4|Col5|Col6|Col7|Col8|Col9|Col10|
|---|---|---|---|---|---|---|---|---|---|
|||||||||||
|||||||||||
|||||||||||
|||||||||||
|||||||||||

0 0.1 0.2 0.3 0.4 0.5 0.6 0.7 0.8 0.9 1



c) Accuracy: sustainability threshold (assumption) d) Accuracy: sustainability threshold (belief)


Figure 5: Scatter plots showing the correlation between reasoning test accuracy and survival time in
G OV S IM . Accuracy and survival time are averaged across the three scenarios. The x-axis of each plot
shows the accuracy of each LLM on four reasoning tests: (a) simulation dynamics, (b) sustainable
action, (c) sustainability threshold (assumption), (d) sustainability threshold (beliefs). The y-axis
represents the average survival time, with higher values indicating better success in G OV S IM . For a
breakdown of the scores across the three scenarios, see Appendix F.2.


1. **Information:** (a) _Information Sharing:_ disseminating facts among participants. (b) _Problem_
_Identification:_ highlighting challenges that require collective attention and resolution. (c)
_Solution Proposing:_ offering ideas or actions to address identified issues.


2. **Negotiation:** (a) _Persuasion:_ attempting to influence others to achieve a desired outcome.
(b) _Consensus Seeking:_ aiming to align group members on a decision or action plan. (c)
_Expressing Disagreement:_ articulating opposition to proposals or existing conditions, with
or without offering alternatives.


3. **Relational:** (a) _Excusing Behavior:_ justifying one’s actions or decisions, especially when
they deviate from group norms or expectations. (b) _Punishment:_ imposing consequences for
perceived wrongdoings or failures to adhere to norms.


Following Gilardi et al. [23], we used GPT-4-turbo to classify each utterance according to our defined
taxonomy. The model was given detailed category definitions and prompted to categorize each
utterance into one of the eight sub-categories. For details of this analysis, refer to Appendix E. To
ensure consistency, we manually annotated 100 random utterances and found that an annotator (an
author of the paper) agreed with _GPT-4-turbo_ ’s labels 72% of the time on the sub-categories.


We analyze the dialogue on the subset of models with higher survival time from Table 1 and present
the results in Figure 4b. On average (overall models), the majority of utterances (54%) are focused
on negotiations between agents, followed by information (45%) and relational (1%). Qualitatively,
some models, such as _GPT-4-turbo_, tend to be overly cautious by advocating lower fishing limits than
the sustainability limit per person. In contrast, scenarios where an agent significantly takes above
this limit cause noticeable concern among other participants. For instance, an agent catching more
fish usually avoids discussing the issue instead of negotiating for greater access to the resource. For
examples of dialogues, refer to Appendix G.


**3.7** **The Role of LLM Capabilities**


Since we observed significant heterogeneity in the emergence of sustainable cooperation across
LLM models, we next investigated how basic LLM capabilities relate to success in G OV S IM . We
test each LLM capabilities on four sub-skills: (a) basic understanding of simulation dynamics
and simple reasoning [simulation dynamics], (b) individually sustainable choices without group
interaction [sustainable action], (c) accurate calculation of the sustainability threshold based on
the G OV S IM state under the direct assumption that all participants harvest equally [sustainability
threshold (assumption)], and (d) calculation of the sustainability threshold for a given G OV S IM state
by forming a belief about actions of other agents [sustainability threshold (beliefs)]. Each sub-skill
test consists of 150 problems created from a template with procedurally generated values. For each
sub-skill test, we compute the accuracy against the ground truth answer.


8


In Figure 5, we show how the average score on each of these four test cases correlates with survival
time by OLS linear regression: (a) simulation dynamics ( _R_ [2] = 0 _._ 69, t-test; _p <_ 0 _._ 001 ), (b)
sustainable action ( _R_ [2] = 0 _._ 92, t-test; _p <_ 0 _._ 001 ), (c) sustainability threshold (assumption) ( _R_ [2] =
0 _._ 76, t-test; _p <_ 0 _._ 001 ), (d) sustainability threshold (belief) ( _R_ [2] = 0 _._ 82, t-test; _p <_ 0 _._ 001 ). Moreover,
we see in Figure 5b that when LLMs are asked to choose how much to harvest in isolation, they only
choose the sustainable action at most 30% of the time, reinforcing the observation made in Section 3.5
that cooperation through communication is a key mechanism to arrive at sustainable norms. We
also observe, in Figure 5c and Figure 5d, that models that successfully formulate beliefs about other
agents, achieve higher survival times, compared to models that require additional assumptions. Refer
to Appendix F for a breakdown across scenarios and prompts.


**4** **Contributions in the Context of Related Work**


**AI Safety** The primary objective of AI safety is to ensure that AI systems do not cause harm to
humans [ 30, 54, 67 ]. As LLMs become more capable and autonomous, ensuring their safety remains
a critical concern [ 2, 3, 30 ]. Popular evaluation datasets for safety include E THIS [ 28 ], T RUTHFUL QA

[ 50 ], and M ORAL E XCEPT QA [ 35 ]. Additional studies have explored the capabilities and potential
issues of current LLMs [ 17, 31, 52, 62 ]. These methods do not address the complexities inherent in
multi-agent interactions and broader real-world scenarios, and more effort is needed to guarantee
the safety of multi-agent systems [ 13 – 15 ]. Most similar to G OV S IM is M ACHIAVELLI [ 58 ], where
the authors investigate harmful behavior vs. reward maximization in a benchmark of single-agent
choose-your-own-adventure games.


_Our Contribution:_ In contrast to prior work, G OV S IM focuses on multi-agent scenarios that require
both strategy, communication, and cooperation: it introduces a more dynamic and realistic environment that is now possible to study using LLM agents. Success in our task is not relative to human
annotators but is instead grounded in a game theoretic scenario. We introduce three resource-sharing
scenarios and analyze LLM agents in terms of their sustainability, stability, and ability to resolve
novel conflicts.


**NLP Benchmarking** To assess the capabilities of LLMs, the broader research community has
developed many benchmarks. Static benchmarks with clear ground-truth MMLU [ 29 ], GSM8k

[ 11 ], and others like it do not capture flexible and interactive tasks needed to navigate scenarios in
the real-world [ 22, 47, 74 ]. In contrast, more recent efforts evaluate LLMs on complex tasks that
resemble real-world applications [ 18, 38, 76 ] or involve A/B testing with human feedback [ 10 ]. For
these complex tasks, recent work has started deploying generative agents [ 59, 60 ] for task-specific
simulations, such as collaborative agent systems for software engineering [32, 46, 53, 73] and other
domains [ 33, 36, 49, 70 ]. Refer to Xi et al. [71] for an extensive review. These generative agents are
increasingly used in dynamic environments where agents must learn, adapt, and make decisions in
real-time.


_Our Contribution:_ Our benchmark, G OV S IM, parallels projects such as GTBench Duan et al. [19],
which measures the reasoning abilities of LLMs through game-theoretic tasks. However, our work
distinguishes itself by its grounding in broader forms of economic reasoning, our focus on cooperation
dilemmas [ 27, 56 ], the incorporating moral considerations, and the need for more sophisticated
communication and negotiation skills. Unlike one-shot games, G OV S IM is a dynamic benchmark
and can be used to evaluate long-horizon behaviors.


**5** **Limitations and Future Work**


This work sets the stage for exploring scenarios that are still more complex and realistic. One
limitation of our study is the simplified nature of the resource-sharing scenarios. Real-world common
pool resource management involves far more sophisticated dynamics and variability. Some of these
dynamics are, in principle, possible in a future version of G OV S IM, such as varying regeneration
rates, multiple resource types, and different stakeholder interests.


While the scenarios in GovSim are somewhat simplified, the complex, open-ended nature of our
simulation is a significant step towards realism compared to the highly simplified paradigms leveraged
from behavioral game theory. Furthermore, while more complex variants are possible, our goal is
to establish a framework that can serve as a foundation that can be flexibly extended by ourselves
and others in the community. The design choices balance complexity and interpretability as simpler
scenarios allow us to study cooperative principles with greater systematicity. Moreover, our current


9


scenarios and dynamics already present significant challenges for current LLMs. Future work could
extend G OV S IM to incorporate more complexities.


_A larger agent population:_ Our current simulation can be generalized to more agents and a diversity
of player types. More agents will increase the simulation runtime, as each agent needs to condition
their behavior and dialogue on the other agents’ actions and dialogues. Perhaps fine-tuned smaller
LLMs can act as efficient simulators in this context without losing performance.


_Coordinated adaptation:_ People can flexibly adapt to sudden changes in game dynamics. For
example, when the resource suddenly shrinks (a temporary shock), or changes in the reproduction
rate require agents to rapidly adjust their cooperative norms in a coordinated way. G OV S IM enables
these kinds of experiments as the simulation environment is modular such that resource dynamics,
agents, and other elements are easily changeable for different simulation runs.


_Challenging trade-offs and exceptions:_ We are also interested in understanding exceptions to norms.
For instance, one agent may need to handle a one-off choice of serious personal harm and group
sustainability, e.g., one agent will experience harm unless they take more resources than permitted by
an existing norm —- will other agents adapt and allow for such one-off exceptions without allowing
for exploitation [4, 44]?


Moreover, current LLM capabilities limit our agent’s ability to negotiate successfully and act strategically. As LLMs evolve, we expect more sophisticated behaviors to emerge. Future research could
enhance LLM negotiation skills and test these improvements against our benchmark. In addition,
further work could introduce advanced adversarial agents to test the robustness of the emergent
cooperative norms discovered here against manipulation. Furthermore, exploring the scalability
of these norms in larger, more diverse agent populations and their application in mixed human-AI
communities will be valuable.


A promising next step is to incorporate humans into the simulation using the GovSim platform. These
human-AI interactions will challenge LLM-based agents to cooperate with humans using open-ended
communication, and we can see whether the norms that develop are either more or less effective than
those created by LLMs alone.


**6** **Conclusion**


We introduced a novel simulation platform Governance of the Commons Simulation (G OV S IM ),
which enables the study of strategic interactions and cooperative decision-making in LLMs. In our
research, we find that all but the most powerful LLM agents fail to achieve a sustainable equilibrium,
with the highest survival rate below 54%. We discover that without communication, agents overuse the shared resource by 22%. Analysis of LLM behaviors suggests that the lack of sustainable
governance may result from an inability to mentally simulate the long-term effects of greedy actions
on the equilibrium of the multi-agent system. To address this challenge, we find that prompting agents
to consider the universalization of their action significantly improves survival time by 4 months. A
society of LLM agents with the ability to communicate finds ways to flexibly cooperate and avoid
collapse.


**Acknowledgment**


We thank Michael Hahn for his insightful discussion on the research paradigm of using NLP to
draw empirical evidence for a non-formally formulated theories, and sharing of his experience on
operationalizing linguistic theories using NLP models. We thank Roberto Ceraolo and Nathan
Corecco for discussions regarding prompting strategies and parsing LLM outputs.


This material is based in part upon work supported by the German Federal Ministry of Education
and Research (BMBF): Tübingen AI Center, FKZ: 01IS18039B; by the Machine Learning Cluster of
Excellence, EXC number 2064/1 – Project number 390727645; by a National Science Foundation
award (#2306372); by a Swiss National Science Foundation award (#201009); by the Cooperative
AI Foundation and a Responsible AI grant by the Haslerstiftung. The usage of OpenAI credits are
largely supported by the Tübingen AI Center. Zhijing Jin is supported by PhD fellowships from the
Future of Life Institute and Open Philanthropy, as well as the travel support from ELISE (GA no
951847) for the ELLIS program.


10


**References**


[1] J. Achiam, S. Adler, S. Agarwal, L. Ahmad, I. Akkaya, F. L. Aleman, D. Almeida,
J. Altenschmidt, S. Altman, S. Anadkat, et al. Gpt-4 technical report. _arXiv preprint_
_arXiv:2303.08774_, 2023.


[2] D. Amodei, C. Olah, J. Steinhardt, P. Christiano, J. Schulman, and D. Mané. Concrete problems
in ai safety. _arXiv preprint arXiv:1606.06565_, 2016.


[3] U. Anwar, A. Saparov, J. Rando, D. Paleka, M. Turpin, P. Hase, E. S. Lubana, E. Jenner,
S. Casper, O. Sourbut, et al. Foundational challenges in assuring alignment and safety of large
language models. _arXiv preprint arXiv:2404.09932_, 2024.


[4] E. Awad, S. Levine, A. Loreggia, N. Mattei, I. Rahwan, F. Rossi, K. Talamadupula, J. Tenenbaum, and M. Kleiman-Weiner. When is it acceptable to break the rules? knowledge representation of moral judgements based on empirical data. _Autonomous Agents and Multi-Agent_
_Systems_, 38(2):35, 2024.


[5] R. Axelrod and W. D. Hamilton. The evolution of cooperation. _Science_, 211(4489):1390–1396,
1981.


[6] J. Bai, S. Bai, Y. Chu, Z. Cui, K. Dang, X. Deng, Y. Fan, W. Ge, Y. Han, F. Huang, et al. Qwen
technical report. _arXiv preprint arXiv:2309.16609_, 2023.


[7] Y. Bengio, G. Hinton, A. Yao, D. Song, P. Abbeel, Y. N. Harari, Y.-Q. Zhang, L. Xue, S. ShalevShwartz, G. Hadfield, et al. Managing ai risks in an era of rapid progress. _arXiv preprint_
_arXiv:2310.17688_, 2023.


[8] S. Bubeck, V. Chandrasekaran, R. Eldan, J. Gehrke, E. Horvitz, E. Kamar, P. Lee, Y. T. Lee,
Y. Li, S. M. Lundberg, H. Nori, H. Palangi, M. T. Ribeiro, and Y. Zhang. Sparks of artificial
general intelligence: Early experiments with GPT-4. _CoRR_, abs/2303.12712, 2023. doi:
10.48550/arXiv.2303.12712. URL `[https://doi.org/10.48550/arXiv.2303.12712](https://doi.org/10.48550/arXiv.2303.12712)` .


[9] C. F. Camerer. _Behavioral game theory: Experiments in strategic interaction_ . Princeton
university press, 2011.


[10] W.-L. Chiang, L. Zheng, Y. Sheng, A. N. Angelopoulos, T. Li, D. Li, H. Zhang, B. Zhu,
M. Jordan, J. E. Gonzalez, et al. Chatbot arena: An open platform for evaluating llms by human
preference. _arXiv preprint arXiv:2403.04132_, 2024.


[11] K. Cobbe, V. Kosaraju, M. Bavarian, M. Chen, H. Jun, L. Kaiser, M. Plappert, J. Tworek,
J. Hilton, R. Nakano, C. Hesse, and J. Schulman. Training verifiers to solve math word
problems, 2021.


[12] Cognition, 2024. URL `[https://www.cognition-labs.com/introducing-devin](https://www.cognition-labs.com/introducing-devin)` .


[13] V. Conitzer and C. Oesterheld. Foundations of cooperative ai. In _Proceedings of the AAAI_
_Conference on Artificial Intelligence_, volume 37, pages 15359–15367, 2023.


[14] A. Critch and D. Krueger. Ai research considerations for human existential safety (arches).
_arXiv preprint arXiv:2006.04948_, 2020.


[15] A. Dafoe, E. Hughes, Y. Bachrach, T. Collins, K. R. McKee, J. Z. Leibo, K. Larson, and
T. Graepel. Open problems in cooperative ai. _arXiv preprint arXiv:2012.08630_, 2020.


[16] A. Dafoe, Y. Bachrach, G. Hadfield, E. Horvitz, K. Larson, and T. Graepel. Cooperative ai:
machines must learn to find common ground. 2021.


[17] T. R. Davidson, V. Veselovsky, M. Josifoski, M. Peyrard, A. Bosselut, M. Kosinski, and R. West.
Evaluating language model agency through negotiations. _arXiv preprint arXiv:2401.04536_,
2024.


[18] X. Deng, Y. Gu, B. Zheng, S. Chen, S. Stevens, B. Wang, H. Sun, and Y. Su. Mind2web:
Towards a generalist agent for the web. _Advances in Neural Information Processing Systems_,
36, 2024.


11


[19] J. Duan, R. Zhang, J. Diffenderfer, B. Kailkhura, L. Sun, E. Stengel-Eskin, M. Bansal, T. Chen,
and K. Xu. Gtbench: Uncovering the strategic reasoning limitations of llms via game-theoretic
evaluations. _arXiv preprint arXiv:2402.12348_, 2024.


[20] R. C. Ellickson. _Order without law: How neighbors settle disputes_ . Harvard University Press,
1991.


[21] C. Gao, X. Lan, N. Li, Y. Yuan, J. Ding, Z. Zhou, F. Xu, and Y. Li. Large language models
empowered agent-based modeling and simulation: A survey and perspectives. _arXiv preprint_
_arXiv:2312.11970_, 2023.


[22] S. Gehrmann, E. Clark, and T. Sellam. Repairing the cracked foundation: A survey of obstacles
in evaluation practices for generated text. _Journal of Artificial Intelligence Research_, 77:
103–166, 2023.


[23] F. Gilardi, M. Alizadeh, and M. Kubli. Chatgpt outperforms crowd-workers for text-annotation
tasks. _CoRR_, abs/2303.15056, 2023. doi: 10.48550/arXiv.2303.15056. URL `[https://doi.](https://doi.org/10.48550/arXiv.2303.15056)`
`[org/10.48550/arXiv.2303.15056](https://doi.org/10.48550/arXiv.2303.15056)` .


[24] C. Gini. _Variabilità e mutabilità: contributo allo studio delle distribuzioni e delle relazioni_
_statistiche.[Fasc. I.]_ . Tipogr. di P. Cuppini, 1912.


[25] H. S. Gordon. The economic theory of a common-property resource: the fishery. _Journal of_
_political economy_, 62(2):124–142, 1954.


[26] J. Greene. _Moral tribes: Emotion, reason, and the gap between us and them_ . Penguin, 2014.


[27] G. Hardin. The tragedy of the commons. _Science_, 162(3859):1243–1248, 1968.


[28] D. Hendrycks, C. Burns, S. Basart, A. Critch, J. Li, D. Song, and J. Steinhardt. Aligning ai with
shared human values. _arXiv preprint arXiv:2008.02275_, 2020.


[29] D. Hendrycks, C. Burns, S. Basart, A. Zou, M. Mazeika, D. Song, and J. Steinhardt. Measuring
massive multitask language understanding. _arXiv preprint arXiv:2009.03300_, 2020.


[30] D. Hendrycks, N. Carlini, J. Schulman, and J. Steinhardt. Unsolved problems in ML safety.
_CoRR_, abs/2109.13916, 2021. URL `[https://arxiv.org/abs/2109.13916](https://arxiv.org/abs/2109.13916)` .


[31] D. Hendrycks, M. Mazeika, A. Zou, S. Patel, C. Zhu, J. Navarro, D. Song, B. Li, and J. Steinhardt. What would jiminy cricket do? towards agents that behave morally. _arXiv preprint_
_arXiv:2110.13136_, 2021.


[32] S. Hong, X. Zheng, J. Chen, Y. Cheng, J. Wang, C. Zhang, Z. Wang, S. K. S. Yau, Z. Lin,
L. Zhou, et al. Metagpt: Meta programming for multi-agent collaborative framework. _arXiv_
_preprint arXiv:2308.00352_, 2023.


[33] W. Hua, L. Fan, L. Li, K. Mei, J. Ji, Y. Ge, L. Hemphill, and Y. Zhang. War and peace
(waragent): Large language model-based multi-agent simulation of world wars. _arXiv preprint_
_arXiv:2311.17227_, 2023.


[34] A. Q. Jiang, A. Sablayrolles, A. Mensch, C. Bamford, D. S. Chaplot, D. d. l. Casas, F. Bressand,
G. Lengyel, G. Lample, L. Saulnier, et al. Mistral 7b. _arXiv preprint arXiv:2310.06825_, 2023.


[35] Z. Jin, S. Levine, F. Gonzalez Adauto, O. Kamal, M. Sap, M. Sachan, R. Mihalcea, J. Tenenbaum,
and B. Schölkopf. When to make exceptions: Exploring language models as accounts of human
moral judgment. _Advances in neural information processing systems_, 35:28458–28473, 2022.


[36] Z. Kaiya, M. Naim, J. Kondic, M. Cortes, J. Ge, S. Luo, G. R. Yang, and A. Ahn. Lyfe agents:
Generative agents for low-cost real-time social interactions, 2023.


[37] I. Kant. Kant: Groundwork of the metaphysics of morals (m. gregor & j. timmermann, trans.),
1785.


12


[38] M. Kinniment, L. J. K. Sato, H. Du, B. Goodrich, M. Hasin, L. Chan, L. H. Miles, T. R. Lin,
H. Wijk, J. Burget, et al. Evaluating language-model agents on realistic autonomous tasks.
_arXiv preprint arXiv:2312.11671_, 2023.


[39] M. Kleiman-Weiner, M. K. Ho, J. L. Austerweil, M. L. Littman, and J. B. Tenenbaum. Coordinate to cooperate or compete: abstract goals and joint intentions in social interaction. In
_Proceedings of the 38th Annual Conference of the Cognitive Science Society_, 2016.


[40] M. Kleiman-Weiner, R. Saxe, and J. B. Tenenbaum. Learning a commonsense moral theory.
_Cognition_, 2017.


[41] M. Kleiman-Weiner, A. Shaw, and J. B. Tenenbaum. Constructing social preferences from
anticipated judgments: When impartial inequity is fair and why? In _Proceedings of the 39th_
_Annual Conference of the Cognitive Science Society_, 2017.


[42] G. T. Kraft-Todd, M. Kleiman-Weiner, and L. Young. Assessing and dissociating virtues from
the ‘bottom up’: A case study of generosity vs. fairness. _The Journal of Positive Psychology_, 18
(6):894–905, 2023.


[43] S. Levine, M. Kleiman-Weiner, L. Schulz, J. Tenenbaum, and F. Cushman. The logic of
universalization guides moral judgment. _Proceedings of the National Academy of Sciences_, 117
(42):26158–26169, 2020.


[44] S. Levine, M. Kleiman-Weiner, N. Chater, F. Cushman, and J. B. Tenenbaum. When rules are
over-ruled: Virtual bargaining as a contractualist method of moral judgment. _Cognition_, 250:
105790, 2024.


[45] G. Li, H. A. A. K. Hammoud, H. Itani, D. Khizbullin, and B. Ghanem. Camel: Communicative
agents for" mind" exploration of large scale language model society. 2023.


[46] G. Li, H. Hammoud, H. Itani, D. Khizbullin, and B. Ghanem. Camel: Communicative agents
for" mind" exploration of large language model society. _Advances in Neural Information_
_Processing Systems_, 36, 2024.


[47] T. Liao, R. Taori, I. D. Raji, and L. Schmidt. Are we learning yet? a meta review of evaluation
failures across machine learning. In _Thirty-fifth Conference on Neural Information Processing_
_Systems Datasets and Benchmarks Track (Round 2)_, 2021.


[48] J. Light, M. Cai, S. Shen, and Z. Hu. Avalonbench: Evaluating llms playing the game of avalon.
In _NeurIPS 2023 Foundation Models for Decision Making Workshop_, 2023.


[49] J. Lin, H. Zhao, A. Zhang, Y. Wu, H. Ping, and Q. Chen. Agentsims: An open-source sandbox
for large language model evaluation. _arXiv preprint arXiv:2308.04026_, 2023.


[50] S. Lin, J. Hilton, and O. Evans. Truthfulqa: Measuring how models mimic human falsehoods,
2022.


[51] Meta. Introducing meta llama 3: The most capable openly available llm to date. URL
`[https://ai.meta.com/blog/meta-llama-3/](https://ai.meta.com/blog/meta-llama-3/)` .


[52] M. Mitchell. How do we know how smart ai systems are?, 2023.


[53] V. Nair, E. Schumacher, G. Tso, and A. Kannan. Dera: enhancing large language model
completions with dialog-enabled resolving agents. _arXiv preprint arXiv:2303.17071_, 2023.


[54] NPR. Researchers warn against ’autonomous weapons’ arms race,
2020. URL `[https://www.npr.org/sections/thetwo-way/2015/07/28/](https://www.npr.org/sections/thetwo-way/2015/07/28/427189235/researchers\protect \discretionary {\char \hyphenchar \font }{}{}warn-against-autonomous-weapons-arms-race)`
```
  427189235/researchers\protect\discretionary{\char\hyphenchar\
```

`[font}{}{}warn-against-autonomous-weapons-arms-race](https://www.npr.org/sections/thetwo-way/2015/07/28/427189235/researchers\protect \discretionary {\char \hyphenchar \font }{}{}warn-against-autonomous-weapons-arms-race)` .


[55] A. Opedal, N. Stoehr, A. Saparov, and M. Sachan. World models for math story problems.
_arXiv preprint arXiv:2306.04347_, 2023.


[56] E. Ostrom. _Governing the commons: The evolution of institutions for collective action_ . Cambridge university press, 1990.


13


[57] E. Ostrom, J. Burger, C. B. Field, R. B. Norgaard, and D. Policansky. Revisiting the commons:
local lessons, global challenges. _science_, 284(5412):278–282, 1999.


[58] A. Pan, J. S. Chan, A. Zou, N. Li, S. Basart, T. Woodside, J. Ng, H. Zhang, S. Emmons, and
D. Hendrycks. Do the rewards justify the means? measuring trade-offs between rewards and
ethical behavior in the machiavelli benchmark. _ICML_, 2023.


[59] J. S. Park, L. Popowski, C. Cai, M. R. Morris, P. Liang, and M. S. Bernstein. Social simulacra:
Creating populated prototypes for social computing systems. In _Proceedings of the 35th Annual_
_ACM Symposium on User Interface Software and Technology_, pages 1–18, 2022.


[60] J. S. Park, J. O’Brien, C. J. Cai, M. R. Morris, P. Liang, and M. S. Bernstein. Generative agents:
Interactive simulacra of human behavior. In _Proceedings of the 36th Annual ACM Symposium_
_on User Interface Software and Technology_, pages 1–22, 2023.


[61] J. Perolat, J. Z. Leibo, V. Zambaldi, C. Beattie, K. Tuyls, and T. Graepel. A multi-agent
reinforcement learning model of common-pool resource appropriation. In _Advances in Neural_
_Information Processing Systems_, pages 3646–3655, 2017.


[62] N. Raman, T. Lundy, S. Amouyal, Y. Levine, K. Leyton-Brown, and M. Tennenholtz. Steer:
Assessing the economic rationality of large language models. _arXiv preprint arXiv:2402.09552_,
2024.


[63] D. G. Rand and M. A. Nowak. Human cooperation. _Trends in cognitive sciences_, 17(8):413,
2013.


[64] J. Serrino, M. Kleiman-Weiner, D. C. Parkes, and J. Tenenbaum. Finding friend and foe in
multi-agent games. _Advances in Neural Information Processing Systems_, 32, 2019.


[65] Y. Shoham and K. Leyton-Brown. _Multiagent systems: Algorithmic, game-theoretic, and logical_
_foundations_ . Cambridge University Press, 2008.


[66] M. Shum, M. Kleiman-Weiner, M. L. Littman, and J. B. Tenenbaum. Theory of minds:
Understanding behavior in groups through inverse planning. In _Proceedings of the AAAI_
_conference on artificial intelligence_, volume 33, pages 6163–6170, 2019.


[67] M. Tegmark. _Life 3.0: Being Human in the Age of Artificial Intelligence_ . Knopf Publishing
Group, 2017. ISBN 1101946598.


[68] M. Tomasello and A. Vaish. Origins of human cooperation and morality. _Annual review of_
_psychology_, 64:231–255, 2013.


[69] H. Touvron, T. Lavril, G. Izacard, X. Martinet, M. Lachaux, T. Lacroix, B. Rozière, N. Goyal,
E. Hambro, F. Azhar, A. Rodriguez, A. Joulin, E. Grave, and G. Lample. Llama: Open and
efficient foundation language models. _CoRR_, abs/2302.13971, 2023. doi: 10.48550/arXiv.2302.
13971. URL `[https://doi.org/10.48550/arXiv.2302.13971](https://doi.org/10.48550/arXiv.2302.13971)` .


[70] Z. Wang, Y. Y. Chiu, and Y. C. Chiu. Humanoid agents: Platform for simulating human-like
generative agents. _arXiv preprint arXiv:2310.05418_, 2023.


[71] Z. Xi, W. Chen, X. Guo, W. He, Y. Ding, B. Hong, M. Zhang, J. Wang, S. Jin, E. Zhou,
R. Zheng, X. Fan, X. Wang, L. Xiong, Y. Zhou, W. Wang, C. Jiang, Y. Zou, X. Liu, Z. Yin,
S. Dou, R. Weng, W. Cheng, Q. Zhang, W. Qin, Y. Zheng, X. Qiu, X. Huang, and T. Gui. The
rise and potential of large language model based agents: A survey, 2023.


[72] Y. Xu, S. Wang, P. Li, F. Luo, X. Wang, W. Liu, and Y. Liu. Exploring large language models
for communication games: An empirical study on werewolf. _arXiv preprint arXiv:2309.04658_,
2023.


[73] J. Zhang, X. Xu, and S. Deng. Exploring collaboration mechanisms for llm agents: A social
psychology view. _arXiv preprint arXiv:2310.02124_, 2023.


[74] L. Zheng, W.-L. Chiang, Y. Sheng, S. Zhuang, Z. Wu, Y. Zhuang, Z. Lin, Z. Li, D. Li, E. Xing,
et al. Judging llm-as-a-judge with mt-bench and chatbot arena. _Advances in Neural Information_
_Processing Systems_, 36, 2024.


14


[75] S. Zheng, A. Trott, S. Srinivasa, D. C. Parkes, and R. Socher. The ai economist: Taxation
policy design via two-level deep multiagent reinforcement learning. _Science advances_, 8(18):
eabk2607, 2022.


[76] S. Zhou, F. F. Xu, H. Zhu, X. Zhou, R. Lo, A. Sridhar, X. Cheng, Y. Bisk, D. Fried, U. Alon,
et al. Webarena: A realistic web environment for building autonomous agents. _arXiv preprint_
_arXiv:2307.13854_, 2023.


15


**A** **Ethical Considerations**


This paper explores cooperative strategies for the governance of the commons in AI models. We
acknowledge concerns about models becoming autonomous entities, especially in situations involving
deception or negotiation. Our research serves as a benchmark for evaluating the capabilities of current
models, rather than enhancing their functions. We do not train any AI model to excel in bluffing or
deception. We analyze and measure the performance of existing models. Our efforts can contribute
positively to AI safety.


Simulations can offer insightful observations, but their value should not eclipse the critical role of
human judgment and ethical considerations in the decision-making process. It is crucial to examine
simulations from an ethical standpoint continually, ensuring that they augment human intelligence
instead of substituting it. This approach advocates for a future where technology improves societal
well-being in an ethical, responsible, and inclusive manner.


**B** **Technical Setup of G** **OV** **S** **IM**







**Discussion**


Figure 6: Overview of the G OV S IM simulation environment. The simulation unfolds in various stages.
Home: agents plan for future rounds and strategize their actions based on past rounds. Harvesting:
agents collect resources. Discussion: agents convene to coordinate, negotiate, and collaborate.
Our G OV S IM platform consists of two components: the environment, which manages the simulation
dynamics, and the agent, which given an LLM, allows it to interact with the simulation.


**B.1** **Environment**

We develop a cooperative environment for LLMs and other language-compatible reinforcement
learning agents, which adheres to a multi-agent, partially observable framework with multiple rounds,
comprising of distinct phases. As depicted in Figure 6, the phases include:


1. Strategy: Agents reflect on past observations, plan future actions, and strategize.
2. Harvesting: Agents engage in resource collection, determining the quantity of resources to
harvest.

3. Discussion: The agents meet at a town hall for social interaction, facilitating group discussions among all participants.


To mitigate any potential bias arising from the order in which agents select their desired quantities
of resources, we adopted a simultaneous harvesting mechanism, which we refer to as _concurrent_
_harvesting_ . This mechanism unfolds in two distinct stages. First, agents specify the amount of
resources they wish to harvest. Then, the environment allocates the resource based on these individual
choices. If collective demand is less than the availability of the resource in the common pool, a direct
allocation occurs. In contrast, in scenarios where demand exceeds supply, we simulate a distribution
process by randomly allocating each unit to each agent until there are no more resources left or the
demand of the agent is satisfied. This approach ensures fairness in the distribution of resources while
preventing the influence of harvesting order.


In the discussion phase, agents gather in a virtual space to engage in a collective dialog. Within this
context, an external entity, the moderator, has the ability to disclose the quantities harvested by each
agent during the previous cycle, a process we refer to as _transparent harvesting reporting_ . Enabling
this feature allows for transparency and accountability among participants. In contrast, by choosing


16


Figure 7: Illustrative screenshot of the Web interface. On the left we show the statistics of the runs.
On the right we show the prompts executed by the LLM and the generated conversations.


not to enable this disclosure, we create an opportunity to explore the dynamics of trust and deception
among agents. This experimental toggle provides valuable information on the behavioral strategies
agents might adopt in the absence of information sharing, revealing their propensity to deceive or
cooperate with their peers.


**B.2** **Agent**


Although our agent is inspired by the architecture described in “Generative Agents” by Park et al.

[60], it is adapted to function in a structured, phase-based environment, departing from the original
work’s emphasis on open-endedness. Consequently, our approach does not involve extensive planning
in five- to fifteen-minute intervals that characterized the original framework. Nevertheless, our agent’s
reflection and action modules operate in a manner similar to the original architecture. Significantly,
our version requires that the prompts for each module be adapted to our more goal-oriented task,
which emphasizes numerical reasoning over creativity, as opposed to the original framework’s focus
on simulating humans in everyday activities.


In addition, our environment requires agents to engage in group discussions, a feature not directly
supported in Generative Agents, which was limited to one-on-one interactions. To accommodate this,
we extend the conversation module to allow a moderator to orchestrate the dialogue, determining
which participant should respond next based on the flow of the conversation. This ensures that direct
questions are answered by the target agent, while more general statements can invite input from any
participant, fostering a more dynamic and interactive group discussion setup.


To ensure consistency, we augment each prompt with a comprehensive set of rules that outline the
parameters of simulation and general dynamics, drawing inspiration from the methodology Xu et al.

[72] explored. This integration serves as a guide to ensure that all agents operate with a common
understanding of the context and goals of the simulation. We show an outline of the prompts for
the case where agents need to share a population of fish in Figure 2. More details are described in
Appendix C.


**B.3** **Web Interface**


The Web interface for G OV S IM ) benchmark is designed to facilitate interaction with the simulation
environment, as shown in Figure 7. One of the primary purposes of the web interface is to provide
a seamless transition from a high-level overview of the simulation dynamics to in-depth analysis
of specific events or interactions, by visualizing exactly what prompt was executed by the LLM at
specific points in the simulation. For example, a researcher may want to investigate why an agent
collected a certain amount of resources; this can be accomplished very easily by clicking on the
specific point in the graphs that track the agent’s resources. By examining the prompts and responses,


17


researchers can identify patterns, potential biases, or areas where LLMs may struggle with ethical
decision making or strategic planning.


**C** **Generative Agents Prompts**


We provide the most relevant prompts for our agents. All prompts can be found in our repository.
We have scenarios specific prompt and rules, for Fishery see Appendix C.1, for Pasture see Appendix C.2, for Pollution see Appendix C.3. We also have prompts that are shared across scenarios,
see Appendix C.4.


**C.1** **Fishery Scenario**

All prompts have the same structure; first, we have the rules of the simulations (see Listing 1 and
agent-specific dynamics (cf. Listings 13 and 14), then we have scenario-specific prompts like Listing 2
to decide how many tons of fish to catch .


Listing 1: Basic rules of the simulation. (Simulation rules)


Listing 2: Prompt example: choose how many tons of fish to catch


Listing 3: Prompt: universalization prompt for Fishery, see Section 3.4. Where _F_ = _f_ ( _t_ ) is the
sustainability threshold at time _t_ .


18


**C.2** **Pasture Scenario**

All prompts have the same structure; first, we have the rules of the simulations Listing 4, then we
have task-specific prompts like Listing 5 to decide how many sheeps to send to graze.


Listing 4: Basic rules of the Pasture scenario. (Simulation rules)


Listing 5: Prompt example: choose how many sheep to send to the pasture


Listing 6: Prompt: universalization prompt for Pasture, see Section 3.4. Where _F_ = _f_ ( _t_ ) is the
sustainability threshold at time _t_ .


19


**C.3** **Pollution Scenario**

All prompts have the same structure; first, we have the rules of the simulations Listing 7, then we
have task-specific prompts like Listing 8 to decide how many widgets to produce.


Listing 7: Basic rules of the Pollution scenario. (Simulation rules)





Listing 8: Prompt example: choose how many widgets to produce


Listing 9: Prompt: universalization prompt for Pollution, see Section 3.4. Where _F_ = _f_ ( _t_ ) is the
sustainability threshold at time _t_ .


20


**C.4** **Common Prompts**





Listing 10: Prompt example: generate an utterance given a specific agent for a group conversation


Listing 11: Prompt example: planning given a conversation







Listing 12: Prompt example: reflect on past memories and generate insights


21


**D** **Experiments Details**


**D.1** **How to Reproduce the Experiments?**

To reproduce the experiments, we provide code in our Github . For open-weights models we show
in Table 2 the model name downloaded from Hugging Face and GPU’s VRAM requirements. For
closed-weights model we show in Table 3 the exact API identifier and an estimate API cost (without
tax) for one simulation of 12 months, the estimates are based on 680k input tokens and 124k output
tokens. For each experiment, we perform 5 runs, so the total costs need to be multiplied by 5. Prices
were calculated at the time of writing (21.04.2024).


Table 2: Detail model identifier and VRAM requirements when running open-weights models.


Open
Model Size VRAM Identifier
weights


7B 28G Yes `meta-llama/Llama-2-7b-chat-hf`
Llama-2 13B 52G Yes `meta-llama/Llama-2-13b-chat-hf`
70B 70G Yes `TheBloke/Llama-2-70B-Chat-GPTQ`


7B 28G Yes `meta-llama/Meta-Llama-3-8B-Instruct`
Llama-3
70B 70G Yes `TechxGenus/Meta-Llama-3-70B-Instruct-GPTQ`


7B 48G Yes `mistralai/Mistral-7B-Instruct-v0.2`
Mistral
8x7B 96G Yes `mistralai/Mixtral-8x7B-Instruct-v0.1`


Qwen 72B 72G Yes `Qwen/Qwen1.5-72B-Chat-GPTQ-Int4`
Qwen 110B 110G Yes `Qwen/Qwen1.5-110B-Chat-GPTQ-Int4`


Table 3: Exact API identifier used in our experiments and approximate cost for running a simulation
with 12 months.


Estimate
Model Size Identifier
cost


Haiku $0.3 `claude-3-haiku-20240307`
Claude 3 Sonnet $4 `claude-3-sonnet-20240229`
Opus $20 `claude-3-opus-20240229`


3.5 $0.5 `gpt-3.5-turbo-0125`
GPT 4 $30 `gpt-4-0613`
4-turbo $11 `gpt-4-turbo-2024-04-09`
4o $5 `gpt-4o-2024-05-13`


**Compute Cost Open-Weights Models** It takes approximately 4 hours to run a complete simulation
(12 months), and LLM that fail the simulation in the first month take 0.5 hours. We used 3 different
type of GPU nodes, in case of VRAM < 100GB we use up to 4xNvidia RTX 3090 (24GB), or
equivalent GPU, otherwise we use up to 2x Nvidia Tesla A100 (80GB) or 2x AMD MI250 (64GB)
depending on availability. For the sub-skills evaluation, each run takes approximately 24 hours. An
estimate of total compute time is 1600h/(24GB GPU unit) and 200h/(80GB GPU unit).


**Compute Cost Closed-weights Models** We used a 4-core CPU, the duration depends on the API
rate limit and can take up to 24 hours. We spent in total 1500 USD across OpenAI API and Anthropic
API.


**Evaluation Setup** We conduct each experiment using five different random seeds, setting the text
generation temperature to zero to ensure greedy decoding. However, we acknowledge that some
randomness persists due to LLM inference kernels that do not guarantee determinism and external
APIs that are beyond our control. The full code and configurations for running the experiments are
available in our GitHub repository .


22


**D.2** **Experiment: Sustainability Test (Default)**

**D.2.1** **Fishery**


Claude-3 Haiku Claude-3 Sonnet Claude-3 Opus


100


80


60


40


20


00 1 2 3 4 5 6 7 8 9 10 11 12


Month


(a) Claude-3


Llama-2-7B Llama-2-13B Llama-2-70B


100


80


60


40


20


00 1 2 3 4 5 6 7 8 9 10 11 12


Month


(c) Llama-2


Mistral-7B Mixtral-8x7B


100


80


60


40


20


00 1 2 3 4 5 6 7 8 9 10 11 12


Month


(e) Mistral



GPT-3.5 GPT-4 GPT-4o


100


80


60


40


20


00 1 2 3 4 5 6 7 8 9 10 11 12


Month


(b) GPT


Llama-3-8B Llama-3-70B


100


80


60


40


20


00 1 2 3 4 5 6 7 8 9 10 11 12


Month


(d) Llama-3


Qwen-72B Qwen-110B


100


80


60


40


20


00 1 2 3 4 5 6 7 8 9 10 11 12


Month


(f) Qwen



Figure 8: Number of tons of fish at the end of the month for the experiment _sustainability test_ (cf.
Section 3.2). We group each model by family.


Table 4: Experiment: _default - fishing_ . Bold number indicates the best performing model, underline
number indicates the best open-weights model.



**Model**



**Survival** **Survival** **Total**
**Rate** **Time** **Gain** **Efficiency** **Equality** **Over-usage**
Max = 100 Max = 12 Max = 120 Max = 100 Max = 1 Min = 0



_**Open-Weights Models**_
Llama-2-7B 0.00 1.00 _±_ 0.00 20.00 _±_ 0.00 16.67 _±_ 0.00 74.32 _±_ 1.80 45.08 _±_ 15.21

Llama-2-13B 0.00 1.00 _±_ 0.00 20.00 _±_ 0.00 16.67 _±_ 0.00 88.72 _±_ 6.28 35.48 _±_ 4.15

Llama-2-70B 0.00 1.00 _±_ 0.00 20.00 _±_ 0.00 16.67 _±_ 0.00 **100.00** _±_ 0.00 59.72 _±_ 3.40

Llama-3-8B 0.00 1.00 _±_ 0.00 20.00 _±_ 0.00 16.67 _±_ 0.00 67.60 _±_ 0.00 21.43 _±_ 0.00

Llama-3-70B 0.00 1.00 _±_ 0.00 20.00 _±_ 0.00 16.67 _±_ 0.00 88.16 _±_ 1.40 39.40 _±_ 3.74

Mistral-7B 0.00 1.00 _±_ 0.00 20.00 _±_ 0.00 16.67 _±_ 0.00 85.76 _±_ 8.68 40.13 _±_ 6.90

Mixtral-8x7B 0.00 1.00 _±_ 0.00 20.00 _±_ 0.00 16.67 _±_ 0.00 85.52 _±_ 20.40 40.87 _±_ 11.87
Qwen-72B 0.00 3.40 _±_ 1.36 32.00 _±_ 9.87 26.67 _±_ 7.36 84.90 _±_ 5.28 25.45 _±_ 7.40
Qwen-110B 40.00 6.60 _±_ 4.45 49.04 _±_ 25.48 40.87 _±_ 18.99 88.65 _±_ 6.25 28.51 _±_ 13.13


_**Closed-Weights Models**_
Claude-3 Haiku 0.00 1.00 _±_ 0.00 20.00 _±_ 0.00 16.67 _±_ 0.00 97.44 _±_ 3.32 35.71 _±_ 0.00

Claude-3 Sonnet 0.00 2.00 _±_ 0.00 21.56 _±_ 0.43 17.97 _±_ 0.32 93.64 _±_ 2.06 33.17 _±_ 1.92
Claude-3 Opus 60.00 9.60 _±_ 2.94 56.28 _±_ 17.68 46.90 _±_ 13.17 94.57 _±_ 1.71 18.79 _±_ 11.54
GPT-3.5 0.00 1.40 _±_ 0.49 20.80 _±_ 1.10 17.33 _±_ 0.82 91.69 _±_ 10.18 32.16 _±_ 5.57

GPT-4 20.00 5.20 _±_ 3.43 32.52 _±_ 4.56 27.10 _±_ 3.40 92.02 _±_ 2.94 22.43 _±_ 10.70

GPT-4-turbo **100.00** **12.00** _±_ 0.00 **108.80** _±_ 7.89 **90.67** _±_ 5.88 98.05 _±_ 1.01 0.51 _±_ 0.73

GPT-4o **100.00** **12.00** _±_ 0.00 71.36 _±_ 7.72 59.47 _±_ 5.76 98.03 _±_ 0.99 **0.35** _±_ 0.70


23


**D.2.2** **Pasture**


Claude-3 Haiku Claude-3 Sonnet Claude-3 Opus


100


80


60


40


20


00 1 2 3 4 5 6 7 8 9 10 11 12


Month


(a) Claude-3


Llama-2-7B Llama-2-13B Llama-2-70B


100


80


60


40


20


00 1 2 3 4 5 6 7 8 9 10 11 12


Month


(c) Llama-2


Mistral-7B Mixtral-8x7B


100


80


60


40


20


00 1 2 3 4 5 6 7 8 9 10 11 12


Month


(e) Mistral



GPT-3.5 GPT-4 GPT-4o


100


80


60


40


20


00 1 2 3 4 5 6 7 8 9 10 11 12


Month


(b) GPT


Llama-3-8B Llama-3-70B


100


80


60


40


20


00 1 2 3 4 5 6 7 8 9 10 11 12


Month


(d) Llama-3


Qwen-72B Qwen-110B


100


80


60


40


20


00 1 2 3 4 5 6 7 8 9 10 11 12


Month


(f) Qwen



Figure 9: Available hectares of grass at the end of the month for the experiment _sustainability test_ (cf.
Section 3.2). We group each model by family.


Table 5: Experiment: _default - Pasture_ . Bold number indicates the best performing model, underline
number indicates the best open-weights model.



**Model**



**Survival** **Survival** **Total**
**Rate** **Time** **Gain** **Efficiency** **Equality** **Over-usage**
Max = 100 Max = 12 Max = 120 Max = 100 Max = 1 Min = 0



_**Open-Weights Models**_
Llama-2-7B 0.00 1.00 _±_ 0.00 20.00 _±_ 0.00 16.67 _±_ 0.00 46.48 _±_ 0.44 17.40 _±_ 1.56

Llama-2-13B 0.00 1.00 _±_ 0.00 20.00 _±_ 0.00 16.67 _±_ 0.00 49.60 _±_ 0.40 14.29 _±_ 0.00

Llama-2-70B 0.00 1.00 _±_ 0.00 20.00 _±_ 0.00 16.67 _±_ 0.00 77.84 _±_ 9.99 48.00 _±_ 4.00

Llama-3-8B 0.00 1.00 _±_ 0.00 20.00 _±_ 0.00 16.67 _±_ 0.00 61.44 _±_ 11.92 24.29 _±_ 3.50

Llama-3-70B 0.00 1.00 _±_ 0.00 20.00 _±_ 0.00 16.67 _±_ 0.00 92.40 _±_ 3.26 40.52 _±_ 6.06

Mistral-7B 0.00 1.00 _±_ 0.00 20.00 _±_ 0.00 16.67 _±_ 0.00 88.64 _±_ 3.63 42.61 _±_ 6.84

Mixtral-8x7B 0.00 1.00 _±_ 0.00 20.00 _±_ 0.00 16.67 _±_ 0.00 80.16 _±_ 8.29 34.33 _±_ 6.21
Qwen-72B 0.00 1.00 _±_ 0.00 20.00 _±_ 0.00 16.67 _±_ 0.00 86.00 _±_ 4.21 40.28 _±_ 7.50
Qwen-110B 0.00 3.20 _±_ 1.60 27.76 _±_ 5.60 23.13 _±_ 4.17 86.52 _±_ 6.28 56.55 _±_ 16.88


_**Closed-Weights Models**_
Claude-3 Haiku 0.00 1.00 _±_ 0.00 20.00 _±_ 0.00 16.67 _±_ 0.00 87.52 _±_ 5.26 35.71 _±_ 0.00

Claude-3 Sonnet 0.00 1.00 _±_ 0.00 20.00 _±_ 0.00 16.67 _±_ 0.00 87.60 _±_ 4.99 34.29 _±_ 2.86
Claude-3 Opus **80.00** **10.20** _±_ 3.60 **99.24** _±_ 36.42 **82.70** _±_ 27.15 **98.23** _±_ 1.92 **9.86** _±_ 13.55
GPT-3.5 0.00 1.00 _±_ 0.00 20.00 _±_ 0.00 16.67 _±_ 0.00 90.88 _±_ 1.51 35.71 _±_ 0.00

GPT-4 0.00 1.80 _±_ 0.40 21.92 _±_ 1.18 18.27 _±_ 0.88 93.18 _±_ 4.53 37.84 _±_ 4.94

GPT-4-turbo 0.00 2.00 _±_ 0.00 23.12 _±_ 1.05 19.27 _±_ 0.79 91.63 _±_ 3.02 35.11 _±_ 2.51

GPT-4o 20.00 6.60 _±_ 4.13 57.92 _±_ 36.78 48.27 _±_ 27.41 94.70 _±_ 3.16 24.61 _±_ 18.15


24


**D.2.3** **Pollution**


Claude-3 Haiku Claude-3 Sonnet Claude-3 Opus


100


80


60


40


20


00 1 2 3 4 5 6 7 8 9 10 11 12


Month


(a) Claude-3


Llama-2-7B Llama-2-13B Llama-2-70B


100


80


60


40


20


00 1 2 3 4 5 6 7 8 9 10 11 12


Month


(c) Llama-2


Mistral-7B Mixtral-8x7B


100


80


60


40


20


00 1 2 3 4 5 6 7 8 9 10 11 12


Month


(e) Mistral



GPT-3.5 GPT-4 GPT-4o


100


80


60


40


20


00 1 2 3 4 5 6 7 8 9 10 11 12


Month


(b) GPT


Llama-3-8B Llama-3-70B


100


80


60


40


20


00 1 2 3 4 5 6 7 8 9 10 11 12


Month


(d) Llama-3


Qwen-72B Qwen-110B


100


80


60


40


20


00 1 2 3 4 5 6 7 8 9 10 11 12


Month


(f) Qwen



Figure 10: Available unpolluted water at the end of the month for the experiment _sustainability test_
(cf. Section 3.2). We group each model by family.


Table 6: Experiment: _default - Pollution_ . Bold number indicates the best performing model, underline
number indicates the best open-weights model.



**Model**



**Survival** **Survival** **Total**
**Rate** **Time** **Gain** **Efficiency** **Equality** **Over-usage**
Max = 100 Max = 12 Max = 120 Max = 100 Max = 1 Min = 0



_**Open-Weights Models**_
Llama-2-7B 0.00 1.00 _±_ 0.00 20.00 _±_ 0.00 16.67 _±_ 0.00 90.48 _±_ 3.53 71.11 _±_ 15.07

Llama-2-13B 0.00 1.00 _±_ 0.00 20.00 _±_ 0.00 16.67 _±_ 0.00 77.76 _±_ 3.69 28.57 _±_ 0.00

Llama-2-70B 0.00 1.00 _±_ 0.00 20.00 _±_ 0.00 16.67 _±_ 0.00 89.60 _±_ 3.11 49.37 _±_ 8.07

Llama-3-8B 0.00 1.00 _±_ 0.00 20.00 _±_ 0.00 16.67 _±_ 0.00 42.88 _±_ 0.18 14.29 _±_ 0.00

Llama-3-70B 0.00 1.00 _±_ 0.00 20.00 _±_ 0.00 16.67 _±_ 0.00 91.60 _±_ 3.52 36.26 _±_ 1.10

Mistral-7B 0.00 1.00 _±_ 0.00 20.00 _±_ 0.00 16.67 _±_ 0.00 73.52 _±_ 3.51 29.01 _±_ 0.88

Mixtral-8x7B 0.00 1.20 _±_ 0.40 20.28 _±_ 0.63 16.90 _±_ 0.47 59.19 _±_ 8.21 24.57 _±_ 3.88
Qwen-72B 0.00 1.00 _±_ 0.00 20.00 _±_ 0.00 16.67 _±_ 0.00 80.72 _±_ 6.74 31.57 _±_ 5.47
Qwen-110B 20.00 3.60 _±_ 4.22 32.24 _±_ 25.59 26.87 _±_ 19.08 **93.66** _±_ 6.26 55.83 _±_ 25.69


_**Closed-Weights Models**_
Claude-3 Haiku 0.00 1.00 _±_ 0.00 20.00 _±_ 0.00 16.67 _±_ 0.00 88.16 _±_ 5.06 35.71 _±_ 0.00

Claude-3 Sonnet 0.00 1.00 _±_ 0.00 20.00 _±_ 0.00 16.67 _±_ 0.00 71.84 _±_ 3.12 28.57 _±_ 0.00
Claude-3 Opus 0.00 1.00 _±_ 0.00 20.00 _±_ 0.00 16.67 _±_ 0.00 81.44 _±_ 4.89 34.46 _±_ 6.25
GPT-3.5 0.00 1.00 _±_ 0.00 20.00 _±_ 0.00 16.67 _±_ 0.00 90.88 _±_ 3.33 38.10 _±_ 2.92

GPT-4 0.00 4.60 _±_ 1.20 39.96 _±_ 12.29 33.30 _±_ 9.16 89.07 _±_ 4.55 20.91 _±_ 5.02

GPT-4-turbo 20.00 5.80 _±_ 3.31 55.32 _±_ 27.79 46.10 _±_ 20.71 91.20 _±_ 5.94 11.39 _±_ 6.42

GPT-4o **40.00** **9.20** _±_ 3.66 **68.84** _±_ 30.14 **57.37** _±_ 22.47 90.54 _±_ 8.08 **7.57** _±_ 5.24


25


**D.3** **Experiment Universalization**

**D.3.1** **Fishery**


Table 7: Improvement on evaluation metrics when introducing _universalization_ compared to _default_
for Fishery, see Table 4, original scores can be found in Table 8.


∆ ∆ **Mean** ∆ **Mean** ∆ **Mean** ∆ **Mean** ∆ **Mean**
**Survival Rate** **Survival Time** **Total Gain** **Efficiency** **Equality** **Over-usage**


_**Open-Weights Models**_
Llama-2-7B 0.00 **+1.00** _↑_ **+8.60** _↑_ **+7.17** _↑_ **+3.33** _↑_ **-8.63** _↓_
Llama-2-13B 0.00 0.00 0.00 0.00 **-12.88** _↓_ **-6.47** _↓_
Llama-2-70B **+20.00** _↑_ **+3.50** _↑_ **+23.20** _↑_ **+19.33** _↑_ **-17.73** _↓_ **-41.85** _↓_
Llama-3-8B **+20.00** _↑_ **+7.00** _↑_ **+41.60** _↑_ **+34.67** _↑_ **+10.96** _↑_ **-10.99** _↓_
Llama-3-70B **+100.00** _↑_ **+11.00** _↑_ **+58.72** _↑_ **+48.93** _↑_ **+8.05** _↑_ **-34.83** _↓_
Mistral-7B 0.00 **+3.40** _↑_ **+22.80** _↑_ **+19.00** _↑_ **-7.61** _↓_ **-20.85** _↓_
Mixtral-8x7B **+100.00** _↑_ **+11.00** _↑_ **+50.88** _↑_ **+42.40** _↑_ **+6.13** _↑_ **-38.86** _↓_
Qwen-72B **+60.00** _↑_ **+7.20** _↑_ **+54.32** _↑_ **+45.27** _↑_ **+6.26** _↑_ **-19.81** _↓_
Qwen-110B **+60.00** _↑_ **+5.40** _↑_ **+38.92** _↑_ **+32.43** _↑_ **+8.44** _↑_ **-27.49** _↓_


_**Closed-Weights Models**_
Claude-3 Haiku **+100.00** _↑_ **+11.00** _↑_ **+88.90** _↑_ **+74.08** _↑_ **+0.35** _↑_ **-33.61** _↓_
Claude-3 Sonnet **+40.00** _↑_ **+4.60** _↑_ **+39.24** _↑_ **+32.70** _↑_ **+0.57** _↑_ **-16.96** _↓_
GPT-3.5 **+60.00** _↑_ **+6.60** _↑_ **+21.12** _↑_ **+17.60** _↑_ **-6.62** _↓_ **-21.08** _↓_
GPT-4 0.00 0.00 **+11.20** _↑_ **+9.33** _↑_ **+1.95** _↑_ **-0.51** _↓_
GPT-4o 0.00 0.00 **+45.84** _↑_ **+38.20** _↑_ **+1.97** _↑_ **-0.35** _↓_


Table 8: Experiment: _universalization - Fishery_ . Bold number indicates the best performing model,
underline number indicates the best open-weights model.



**Model**



**Survival** **Survival** **Total**
**Rate** **Time** **Gain** **Efficiency** **Equality** **Over-usage**
Max = 100 Max = 12 Max = 120 Max = 100 Max = 1 Min = 0



_**Open-Weights Models**_
Llama-2-7B 0.00 2.00 _±_ 0.63 28.60 _±_ 6.23 23.83 _±_ 4.64 77.65 _±_ 1.52 36.45 _±_ 11.10

Llama-2-13B 0.00 1.00 _±_ 0.00 20.00 _±_ 0.00 16.67 _±_ 0.00 75.84 _±_ 1.89 29.01 _±_ 0.88

Llama-2-70B 20.00 4.50 _±_ 0.50 43.20 _±_ 3.71 36.00 _±_ 2.68 82.27 _±_ 11.66 17.87 _±_ 8.60

Llama-3-8B 20.00 8.00 _±_ 3.16 61.60 _±_ 25.21 51.33 _±_ 18.79 78.56 _±_ 7.87 10.43 _±_ 6.34

Llama-3-70B **100.00** **12.00** _±_ 0.00 78.72 _±_ 9.72 65.60 _±_ 7.25 96.21 _±_ 1.89 4.57 _±_ 1.16

Mistral-7B 0.00 4.40 _±_ 2.94 42.80 _±_ 25.45 35.67 _±_ 18.97 78.15 _±_ 11.12 19.28 _±_ 7.52

Mixtral-8x7B **100.00** **12.00** _±_ 0.00 70.88 _±_ 19.50 59.07 _±_ 14.53 91.65 _±_ 4.63 2.01 _±_ 0.91
Qwen-72B 60.00 10.60 _±_ 2.80 86.32 _±_ 22.55 71.93 _±_ 16.80 91.16 _±_ 7.04 5.65 _±_ 2.28
Qwen-110B **100.00** **12.00** _±_ 0.00 87.96 _±_ 18.91 73.30 _±_ 14.09 97.09 _±_ 2.49 1.02 _±_ 1.25


_**Closed-Weights Models**_
Claude-3 Haiku **100.00** **12.00** _±_ 0.00 108.90 _±_ 3.25 90.75 _±_ 1.92 97.79 _±_ 0.48 2.11 _±_ 0.89

Claude-3 Sonnet 40.00 6.60 _±_ 4.45 60.80 _±_ 42.50 50.67 _±_ 31.68 94.21 _±_ 4.19 16.21 _±_ 12.15

GPT-3.5 60.00 8.00 _±_ 4.90 41.92 _±_ 18.02 34.93 _±_ 13.43 85.08 _±_ 10.69 11.08 _±_ 8.99

GPT-4 **100.00** **12.00** _±_ 0.00 **120.00** _±_ 0.00 **100.00** _±_ 0.00 **100.00** _±_ 0.00 **0.00** _±_ 0.00

GPT-4o **100.00** **12.00** _±_ 0.00 117.20 _±_ 6.26 97.67 _±_ 4.67 **100.00** _±_ 0.00 **0.00** _±_ 0.00


26


**D.3.2** **Pasture**


Table 9: Improvement on evaluation metrics when introducing _universalization_ compared to _default_
for Pasture, see Table 5, original scores can be found in Table 10.


∆ ∆ **Mean** ∆ **Mean** ∆ **Mean** ∆ **Mean** ∆ **Mean**
**Survival Rate** **Survival Time** **Total Gain** **Efficiency** **Equality** **Over-usage**


_**Open-Weights Models**_
Llama-2-7B 0.00 0.00 0.00 0.00 **+26.08** _↑_ **25.93** _↑_
Llama-2-13B 0.00 0.00 0.00 0.00 **+2.32** _↑_ **1.28** _↑_
Llama-2-70B 0.00 **+3.00** _↑_ **+16.32** _↑_ **+13.60** _↑_ **-2.18** _↓_ **-31.83** _↓_
Llama-3-8B 0.00 **+4.60** _↑_ **+37.96** _↑_ **+31.63** _↑_ **+18.74** _↑_ **-21.19** _↓_
Llama-3-70B 0.00 0.00 0.00 0.00 **-25.36** _↓_ **-19.35** _↓_
Mistral-7B 0.00 0.00 0.00 0.00 **-1.36** _↓_ **13.50** _↑_
Mixtral-8x7B 0.00 **+0.20** _↑_ **+0.80** _↑_ **+0.67** _↑_ **-12.28** _↓_ **-11.87** _↓_
Qwen-72B 0.00 **+3.20** _↑_ **+24.88** _↑_ **+20.73** _↑_ **-3.79** _↓_ **-20.12** _↓_
Qwen-110B **+100.00** _↑_ **+8.80** _↑_ **+73.40** _↑_ **+61.17** _↑_ **+12.45** _↑_ **-56.30** _↓_


_**Closed-Weights Models**_
Claude-3 Haiku **+60.00** _↑_ **+9.40** _↑_ **+75.72** _↑_ **+63.10** _↑_ **+7.07** _↑_ **-34.71** _↓_
Claude-3 Sonnet **+40.00** _↑_ **+5.60** _↑_ **+41.08** _↑_ **+34.23** _↑_ **+6.28** _↑_ **-20.93** _↓_
GPT-3.5 0.00 **+4.80** _↑_ **+38.52** _↑_ **+32.10** _↑_ **-9.97** _↓_ **-29.03** _↓_
GPT-4 **+40.00** _↑_ **+8.40** _↑_ **+45.80** _↑_ **+38.17** _↑_ **+3.85** _↑_ **-18.79** _↓_
GPT-4o **+80.00** _↑_ **+5.40** _↑_ **+60.48** _↑_ **+50.40** _↑_ **+4.88** _↑_ **-24.61** _↓_


Table 10: Experiment: _universalization - Pasture_ . Bold number indicates the best performing model,
underline number indicates the best open-weights model.



**Model**



**Survival** **Survival** **Total**
**Rate** **Time** **Gain** **Efficiency** **Equality** **Over-usage**
Max = 100 Max = 12 Max = 120 Max = 100 Max = 1 Min = 0



_**Open-Weights Models**_
Llama-2-7B 0.00 1.00 _±_ 0.00 20.00 _±_ 0.00 16.67 _±_ 0.00 72.56 _±_ 8.15 43.33 _±_ 11.67

Llama-2-13B 0.00 1.00 _±_ 0.00 20.00 _±_ 0.00 16.67 _±_ 0.00 51.92 _±_ 12.55 15.56 _±_ 7.82

Llama-2-70B 0.00 4.00 _±_ 3.16 36.32 _±_ 16.99 30.27 _±_ 12.67 75.66 _±_ 9.09 16.17 _±_ 7.89

Llama-3-8B 0.00 5.60 _±_ 1.96 57.96 _±_ 15.28 48.30 _±_ 11.39 80.18 _±_ 6.59 3.09 _±_ 1.47

Llama-3-70B 0.00 1.00 _±_ 0.00 20.00 _±_ 0.00 16.67 _±_ 0.00 67.04 _±_ 3.41 21.17 _±_ 4.37

Mistral-7B 0.00 1.00 _±_ 0.00 20.00 _±_ 0.00 16.67 _±_ 0.00 87.28 _±_ 5.21 56.11 _±_ 19.71

Mixtral-8x7B 0.00 1.20 _±_ 0.40 20.80 _±_ 1.79 17.33 _±_ 1.33 67.88 _±_ 12.17 22.46 _±_ 8.42
Qwen-72B 0.00 4.20 _±_ 4.02 44.88 _±_ 37.24 37.40 _±_ 27.76 82.21 _±_ 8.43 20.17 _±_ 9.75
Qwen-110B **100.00** **12.00** _±_ 0.00 101.16 _±_ 16.87 84.30 _±_ 12.57 98.97 _±_ 1.18 0.25 _±_ 0.51


_**Closed-Weights Models**_
Claude-3 Haiku 60.00 10.40 _±_ 2.06 95.72 _±_ 14.61 79.77 _±_ 10.89 94.59 _±_ 4.29 1.00 _±_ 1.02

Claude-3 Sonnet 40.00 6.60 _±_ 4.41 61.08 _±_ 36.98 50.90 _±_ 27.56 93.88 _±_ 8.46 13.36 _±_ 9.16

GPT-3.5 0.00 5.80 _±_ 3.19 58.52 _±_ 35.71 48.77 _±_ 26.62 80.91 _±_ 10.68 6.68 _±_ 3.94

GPT-4 40.00 10.40 _±_ 2.33 68.92 _±_ 25.78 57.43 _±_ 19.21 95.48 _±_ 2.58 16.32 _±_ 8.97

GPT-4o **100.00** **12.00** _±_ 0.00 **118.40** _±_ 2.02 **98.67** _±_ 1.51 **99.58** _±_ 0.81 **0.00** _±_ 0.00


27


**D.3.3** **Pollution**


Table 11: Improvement on evaluation metrics when introducing _universalization_ compared to _default_
for Pollution, see Table 6, original scores can be found in Table 12.


∆ ∆ **Mean** ∆ **Mean** ∆ **Mean** ∆ **Mean** ∆ **Mean**
**Survival Rate** **Survival Time** **Total Gain** **Efficiency** **Equality** **Over-usage**


_**Open-Weights Models**_
Llama-2-7B 0.00 0.00 0.00 0.00 **-14.88** _↓_ **-16.83** _↓_
Llama-2-13B 0.00 0.00 0.00 0.00 **-33.92** _↓_ **-14.29** _↓_
Llama-2-70B 0.00 **+2.00** _↑_ **+16.56** _↑_ **+13.80** _↑_ **-8.33** _↓_ **-41.77** _↓_
Llama-3-8B 0.00 **+1.60** _↑_ **+6.80** _↑_ **+5.67** _↑_ **+16.60** _↑_ **-2.62** _↓_
Llama-3-70B **+100.00** _↑_ **+11.00** _↑_ **+71.44** _↑_ **+59.53** _↑_ **+2.46** _↑_ **-32.16** _↓_
Mistral-7B 0.00 0.00 0.00 0.00 **+14.40** _↑_ **6.13** _↑_
Mixtral-8x7B 0.00 **+0.40** _↑_ **+2.04** _↑_ **+1.70** _↑_ **+5.89** _↑_ **-5.32** _↓_
Qwen-72B 0.00 **+0.80** _↑_ **+4.64** _↑_ **+3.87** _↑_ **-13.51** _↓_ **-14.57** _↓_
Qwen-110B **+80.00** _↑_ **+8.40** _↑_ **+56.04** _↑_ **+46.70** _↑_ **+0.03** _↑_ **-54.39** _↓_


_**Closed-Weights Models**_
Claude-3 Haiku 0.00 **+1.20** _↑_ **+6.24** _↑_ **+5.20** _↑_ **-8.24** _↓_ **-22.62** _↓_
Claude-3 Sonnet 0.00 **+1.80** _↑_ **+13.88** _↑_ **+11.57** _↑_ **+15.66** _↑_ **-16.96** _↓_
GPT-3.5 **+20.00** _↑_ **+7.20** _↑_ **+50.92** _↑_ **+42.43** _↑_ **-11.20** _↓_ **-35.09** _↓_
GPT-4 **+80.00** _↑_ **+6.20** _↑_ **+61.24** _↑_ **+51.03** _↑_ **+8.34** _↑_ **-11.39** _↓_
GPT-4o **+60.00** _↑_ **+2.80** _↑_ **+32.28** _↑_ **+26.90** _↑_ **+8.83** _↑_ **-6.26** _↓_


Table 12: Experiment: _universalization - Pollution_ . Bold number indicates the best performing model,
underline number indicates the best open-weights model.



**Model**



**Survival** **Survival** **Total**
**Rate** **Time** **Gain** **Efficiency** **Equality** **Over-usage**
Max = 100 Max = 12 Max = 120 Max = 100 Max = 1 Min = 0



_**Open-Weights Models**_
Llama-2-7B 0.00 1.00 _±_ 0.00 20.00 _±_ 0.00 16.67 _±_ 0.00 75.60 _±_ 9.95 54.29 _±_ 4.96

Llama-2-13B 0.00 1.00 _±_ 0.00 20.00 _±_ 0.00 16.67 _±_ 0.00 43.84 _±_ 16.47 14.29 _±_ 6.39

Llama-2-70B 0.00 3.00 _±_ 0.89 36.56 _±_ 8.40 30.47 _±_ 6.26 81.27 _±_ 4.25 7.59 _±_ 3.92

Llama-3-8B 0.00 2.60 _±_ 1.85 26.80 _±_ 8.62 22.33 _±_ 6.43 59.48 _±_ 6.40 11.67 _±_ 4.15

Llama-3-70B **100.00** **12.00** _±_ 0.00 91.44 _±_ 5.40 76.20 _±_ 4.03 94.06 _±_ 0.98 4.11 _±_ 1.61

Mistral-7B 0.00 1.00 _±_ 0.00 20.00 _±_ 0.00 16.67 _±_ 0.00 87.92 _±_ 2.66 35.14 _±_ 3.68

Mixtral-8x7B 0.00 1.60 _±_ 0.80 22.32 _±_ 3.74 18.60 _±_ 2.79 65.09 _±_ 6.01 19.25 _±_ 6.82
Qwen-72B 0.00 1.80 _±_ 0.75 24.64 _±_ 4.57 20.53 _±_ 3.40 67.21 _±_ 5.54 17.01 _±_ 4.38
Qwen-110B **100.00** **12.00** _±_ 0.00 88.28 _±_ 6.20 73.57 _±_ 4.62 93.70 _±_ 3.48 1.44 _±_ 1.52


_**Closed-Weights Models**_
Claude-3 Haiku 0.00 2.20 _±_ 0.40 26.24 _±_ 2.74 21.87 _±_ 2.04 79.92 _±_ 7.73 13.10 _±_ 2.71

Claude-3 Sonnet 0.00 2.80 _±_ 1.17 33.88 _±_ 7.61 28.23 _±_ 5.67 87.50 _±_ 6.77 11.61 _±_ 3.82

GPT-3.5 20.00 8.20 _±_ 4.21 70.92 _±_ 31.43 59.10 _±_ 23.43 79.68 _±_ 18.50 3.01 _±_ 2.31

GPT-4 **100.00** **12.00** _±_ 0.00 **116.56** _±_ 6.83 **97.13** _±_ 5.09 **99.54** _±_ 0.63 **0.00** _±_ 0.00

GPT-4o **100.00** **12.00** _±_ 0.00 101.12 _±_ 5.17 84.27 _±_ 3.85 99.37 _±_ 0.63 1.31 _±_ 1.93


28


**D.4** **Experiment Newcomer**


Listing 13: Rule for villager role. This is only used in the _outsider_ experiment.


Listing 14: Rule for outsider role. This is only used in the _outsider_ experiment.


Table 13: Comparison on _newcomer_ experiment for the Fishery.


**Survival** **Survival** **Total**
**Scenario** **Rate** **Time** **Gain** **Efficiency** **Equality** **Over-usage**


Newcomer 100.00 12.00 _±_ 0.00 81.00 _±_ 26.23 67.50 _±_ 19.55 85.78 _±_ 8.74 3.18 _±_ 1.92

Default **100.00** **12.00** _±_ 0.00 **108.80** _±_ 7.89 **90.67** _±_ 5.88 **98.05** _±_ 1.01 **0.51** _±_ 0.73


Table 14: Comparison on _newcomer_ experiment for the Pasture.


**Survival** **Survival** **Total**
**Scenario** **Rate** **Time** **Gain** **Efficiency** **Equality** **Over-usage**


Newcomer 0.00 4.40 _±_ 0.49 11.52 _±_ 6.13 9.60 _±_ 4.57 86.69 _±_ 14.10 28.20 _±_ 10.51

Default **20.00** **6.60** _±_ 4.13 **57.92** _±_ 36.78 **48.27** _±_ 27.41 **94.70** _±_ 3.16 **24.61** _±_ 18.15


Table 15: Comparison on _newcomer_ experiment for the Pollution.


**Survival** **Survival** **Total**
**Scenario** **Rate** **Time** **Gain** **Efficiency** **Equality** **Over-usage**


Newcomer 0.00 3.40 _±_ 0.80 12.00 _±_ 10.95 16.67 _±_ 0.00 42.67 _±_ 2.31 15.60 _±_ 11.78

Default **40.00** **9.20** _±_ 3.66 **68.84** _±_ 30.14 **57.37** _±_ 22.47 **90.54** _±_ 8.08 **7.57** _±_ 5.24


29


**D.5** **Language Ablation**

Comparing simulations without communication with those with communication, we find that agents
without communication tend to have lower efficiency _−_ 4 (t-test; _p <_ 0 _._ 398 ), lower equality _−_ 4%
(t-test; _p <_ 0 _._ 001 ), lower gain _−_ 4 (t-test; _p <_ 0 _._ 398 ), and lower survival time _−_ 1 (t-test; _p <_ 0 _._ 109 ).


**D.5.1** **Fishery**


Table 16: Impact of communication on sustainability: comparison of over-usage percentages between
simulations with and without communication on Fishery scenario. The best metric for each model,
whether with or without communication, is highlighted in bold.


**With communication** **Without communication**
**Model**
Survival Time _↑_ Over-usage _↓_ Survival Time _↑_ Over-usage _↓_


Qwen-110B 6.60 _±_ 4.45 28.51 _±_ 13.13 **10.20** _±_ 3.60 **25.67** _±_ 11.95
Claude-3 Opus 9.60 _±_ 2.94 **18.79** _±_ 11.54 10.50 _±_ 2.57 38.89 _±_ 5.24
GPT-4 12.00 _±_ 0.00 **0.51** _±_ 0.73 12.00 _±_ 0.00 11.33 _±_ 11.42

GPT-4o 12.00 _±_ 0.00 **0.35** _±_ 0.70 12.00 _±_ 0.00 31.67 _±_ 8.43


**D.5.2** **Pasture**


Table 17: Impact of communication on sustainability: comparison of over-usage percentages between
simulations with and without communication on Pasture scenario. The best metric for each model,
whether with or without communication, is highlighted in bold.


**With communication** **Without communication**
**Model**
Survival Time _↑_ Over-usage _↓_ Survival Time _↑_ Over-usage _↓_


Qwen-110B 3.20 _±_ 1.60 56.55 _±_ 16.88 **4.40** _±_ 1.36 **25.33** _±_ 12.75
Claude-3 Opus **10.20** _±_ 3.60 **9.86** _±_ 13.55 2.33 _±_ 0.75 79.17 _±_ 7.31
GPT-4 2.00 _±_ 0.00 **35.11** _±_ 2.51 **2.80** _±_ 1.17 73.67 _±_ 15.72

GPT-4o **6.60** _±_ 4.13 **24.61** _±_ 18.15 4.00 _±_ 1.26 57.73 _±_ 9.00


**D.5.3** **Pollution**


Table 18: Impact of communication on sustainability: comparison of over-usage percentages between
simulations with and without communication on Pollution scenario. The best metric for each model,
whether with or without communication, is highlighted in bold.


**With communication** **Without communication**
**Model**
Survival Time _↑_ Over-usage _↓_ Survival Time _↑_ Over-usage _↓_


Qwen-110B **3.60** _±_ 4.22 55.83 _±_ 25.69 3.00 _±_ 1.79 **53.67** _±_ 11.27
Claude-3 Opus 1.00 _±_ 0.00 **34.46** _±_ 6.25 **3.83** _±_ 1.46 51.06 _±_ 6.67
GPT-4 **5.80** _±_ 3.31 **11.39** _±_ 6.42 2.80 _±_ 0.75 38.00 _±_ 11.85

GPT-4o **9.20** _±_ 3.66 **7.57** _±_ 5.24 2.40 _±_ 0.49 54.00 _±_ 14.97


30


**E** **Analysis of Agent Dialogues**


We classify each utterance using Listing 15 into the eight subcategories and then group them in the
main 3 categories.







Listing 15: Prompt to classify each utterance


Table 19: Classification of utterances across different models for Fishery, showing the mean proportions and standard deviations of utterances classified into Information Sharing, Negotiation, and
Relational categories.


**Information** **Negotiation** **Relational**


Qwen-110B 0.33 _±_ 0.17 0.66 _±_ 0.16 0.01 _±_ 0.03
Claude-3 Opus 0.32 _±_ 0.13 0.66 _±_ 0.12 0.01 _±_ 0.01
GPT-4 0.30 _±_ 0.10 0.68 _±_ 0.09 0.02 _±_ 0.02

GPT-4o 0.19 _±_ 0.04 0.80 _±_ 0.04 0.01 _±_ 0.01


Table 20: Classification of utterances across different models for Pasture, showing the mean proportions and standard deviations of utterances classified into Information Sharing, Negotiation, and
Relational categories.


**Information** **Negotiation** **Relational**


Qwen-110B 0.77 _±_ 0.20 0.20 _±_ 0.18 0.03 _±_ 0.06
Claude-3 Opus 0.32 _±_ 0.15 0.66 _±_ 0.13 0.02 _±_ 0.05
GPT-4 0.26 _±_ 0.10 0.74 _±_ 0.10 0.00 _±_ 0.00

GPT-4o 0.19 _±_ 0.10 0.79 _±_ 0.13 0.02 _±_ 0.04


31


Table 21: Classification of utterances across different models for Pollution, showing the mean
proportions and standard deviations of utterances classified into Information Sharing, Negotiation,
and Relational categories.


**Information** **Negotiation** **Relational**


Qwen-110B 0.70 _±_ 0.26 0.30 _±_ 0.26 0.00 _±_ 0.00
Claude-3 Opus 0.45 _±_ 0.12 0.55 _±_ 0.12 0.00 _±_ 0.00
GPT-4 0.36 _±_ 0.09 0.64 _±_ 0.09 0.00 _±_ 0.00

GPT-4o 0.18 _±_ 0.07 0.79 _±_ 0.08 0.03 _±_ 0.02


**F** **Sub-skills Evaluation**


In order to identify what contributes to a simulation having a high survival time in our resource
sharing scenarios, we develop four sub-skill tests. This test measures (a) basic understanding of
simulation dynamics and ability to perform simple reasoning, (b) choosing a sustainable action
without interacting with the group, (c) calculating the sustainability threshold of the current state
of the simulation under the assumption that all participants harvest equally, and (d) calculating the
sustainability threshold of the current state of the simulation by forming a belief about actions of
other agents.


To run these test cases, we followed a templated problem generation, as done by Opedal et al. [55],
running each prompt 150 times with different values, for each of which we compute the accuracy.
We perform this analysis on all the models described in Appendix D.1. In the following sections, we
display scatter plots that show correlations with the survival duration for each scenario and results
with mean and confidence interval computed using 2-sigma CI using stats’ `proportion_confint`
function.


**F.1** **Method**

**Common Information** For each of the scenarios we use the same description used in the simulation,
but using controlled settings: the only memory present is the current about of shared resource present
before harvesting. In Listing 16 we show the common information for fishery, in Listing 17 for
pasture and Listing 18 for pollution.


Listing 16: Common information for the Fishery test cases.


Listing 17: Common information for the Pasture test cases.


32


Listing 18: Common information for the Pollution test cases.


**Test Case a): Simulation Dynamics** For this test case, we evaluate the model’s comprehension
of the simulation and its ability to execute basic reasoning. Specifically, given the current state of a
shared resource, we the question ask to determine the resource amount at the next time step under the
assumption that each agent harvests at the same rate. The parameters for this test case are:


    - _N_, the initial quantity of the resource, which ranges from 10 to 100.

    - _M_, the amount each agent harvests, which ranges from 0 to _[N]_ 5


At each time step, the model should correctly compute the remaining quantity of the resource based
on these parameters. The answer _A_ is classified as correct if the following condition hold:


_A_ = max(0 _,_ min(100 _,_ ( _N −_ _M ·_ 5) _·_ 2)) (4)


Listing 19: Fishery test case a): simulation dynamics


Listing 20: Pasture test case a): simulation dynamics


Listing 21: Pollution test case a): simulation dynamics


**Test Case b): Sustainable Action** For this test case, we evaluate the model’s understanding of
sustainability in the absence of interaction with other agents. Specifically, given the current state of a
shared resource, we ask the model to determine the amount of the resource that needs to be collected.
It is important to note that we are not suggesting sustainable actions; rather, we are interested in
observing the outcomes based on objective instructions. The parameters for this test case are:


    - _N_, the initial quantity of the resource, which ranges from 10 to 100.


We classify each answer _A_ as correct if it lies between 0 and the sustainable threshold (cf. Section 2.3).


Listing 22: Fishery test case b): sustainable action


33


Listing 23: Pasture test case b): sustainable action


Listing 24: Pollution test case b):sustainable action


**Test Case c): Sustainability Threshold (Assumption)** For this test case, we evaluate the model’s
ability to compute the sustainability threshold (cf. Section 2.3) under the assumption that each agent
harvests the shared resource equally. Specifically, given the current state of a shared resource, we ask
the model to determine this quantity. The parameters for this test case are:


    - _N_, the initial quantity of the resource, which ranges from 10 to 100.


We classify each answer _A_ as correct if it matches the sustainable threshold (cf. Section 2.3).


Listing 25: Fishery test case c): sustainability threshold (with assumption)


Listing 26: Pasture test case c): sustainability threshold (with assumption)


Listing 27: Pollution test case c): sustainability threshold (with assumption)


**Test Case d): Sustainability Threshold (Belief)** For this test case, we evaluate the model’s ability
to compute the sustainability threshold (cf. Section 2.3) without injecting any assumption in the
prompt. The key idea is to investigate the model ability to perform assumption about other agent
belief, and compute a possible solution. Specifically, given the current state of a shared resource, we
ask the model to determine this quantity. The parameters for this test case are:


    - _N_, the initial quantity of the resource, which ranges from 10 to 100.


We classify each answer _A_ as correct if it matches the sustainable threshold (cf. Section 2.3).


Listing 28: Fishery test case d): sustainability threshold (without assumption)


34


Listing 29: Pasture test case d): sustainability threshold (without assumption)


Listing 30: Pollution test case d): sustainability threshold (without assumption)


**F.2** **Results**


Llama-2-7B Llama-2-13B Llama-2-70B Llama-3-8B Llama-3-70B Mistral-7B Mixtral-8x7B Qwen-72B Qwen-110B Claude-3 Haiku



100


80


60


40


20


0


0 0.1 0.2 0.3 0.4 0.5 0.6 0.7 0.8 0.9 1



100


80


60


40


20


0


0 0.1 0.2 0.3 0.4 0.5 0.6 0.7 0.8 0.9 1



100


80


60


40


20


0


0 0.1 0.2 0.3 0.4 0.5 0.6 0.7 0.8 0.9 1



Aggregated Score Fish Scenario Aggregated Score Sheep Scenario Aggregated Score Pollution Scenario


Figure 11: Scatter plot showing the correlation between accuracy on reasoning tests case and average
survival time in the simulations. We average the accuracy and survival time across the four test cases.
The x-axis represents the average accuracy on the reasoning tests. The y-axis represents the average
survival time, with higher values indicating a better score.


**F.2.1** **Fishery**


Llama-2-7B Llama-2-13B Llama-2-70B Llama-3-8B Llama-3-70B Mistral-7B Mixtral-8x7B Qwen-72B


Qwen-110B Claude-3 Haiku Claude-3 Sonnet Claude-3 Opus GPT-3.5 GPT-4 GPT-4o



12


10


8


6


4


2


0
0 0.1 0.2 0.3 0.4 0.5 0.6 0.7 0.8 0.9 1



12


10


8


6


4


2


0

|Col1|Col2|Col3|Col4|Col5|Col6|Col7|Col8|Col9|Col10|Col11|
|---|---|---|---|---|---|---|---|---|---|---|
||||||||||||
||||||||||||
||||||||||||
||||||||||||
||||||||||||
||||||||||||

0 0.1 0.2 0.3 0.4 0.5 0.6 0.7 0.8 0.9 1



a) Accuracy: simulation dynamics b) Accuracy: sustainable action (without community interaction)



12


10


8


6


4


2


0
0 0.1 0.2 0.3 0.4 0.5 0.6 0.7 0.8 0.9 1



12


10


8


6


4


2


0

|Col1|Col2|Col3|Col4|Col5|Col6|Col7|Col8|Col9|Col10|Col11|
|---|---|---|---|---|---|---|---|---|---|---|
||||||||||||
||||||||||||
||||||||||||
||||||||||||
||||||||||||
||||||||||||

0 0.1 0.2 0.3 0.4 0.5 0.6 0.7 0.8 0.9 1



c) Accuracy: sustainability threshold (assumption) d) Accuracy: sustainability threshold (belief)


Figure 12: Scatter plot showing the correlation between scores on reasoning tests and average survival
time in the _default - fishery_ simulation. The x-axis represents scores on the reasoning tests. The
y-axis depicts the average survival time.


35


Table 22: Accuracy score for the Fishery sub-skills test cases.



Model **a)**
**simulation**
**dynamics**



**b)**
**sustainable**

**action**



**c)**
**sustainability**
**threshold**
**(assumption)**



**d)**
**sustainability**
**threshold**
**(belief)**



_**Open-Weights Models**_
Llama-2-7B 0.19 _±_ 0.07 0.02 _±_ 0.02 0.01 _±_ 0.01 0.00 _±_ 0.00

Llama-2-13B 0.43 _±_ 0.08 0.01 _±_ 0.01 0.01 _±_ 0.01 0.03 _±_ 0.03

Llama-2-70B 0.27 _±_ 0.07 0.07 _±_ 0.04 0.03 _±_ 0.03 0.00 _±_ 0.00

Llama-3-8B 0.39 _±_ 0.07 0.03 _±_ 0.03 0.17 _±_ 0.06 0.01 _±_ 0.01

Llama-3-70B 0.16 _±_ 0.06 0.04 _±_ 0.03 **1.00** _±_ 0.00 0.76 _±_ 0.07

Mistral-7B 0.26 _±_ 0.07 0.11 _±_ 0.05 0.03 _±_ 0.03 0.00 _±_ 0.00

Mixtral-8x7B 0.61 _±_ 0.07 0.05 _±_ 0.04 0.30 _±_ 0.07 0.06 _±_ 0.04
Qwen-72B 0.66 _±_ 0.08 0.15 _±_ 0.06 0.67 _±_ 0.08 0.28 _±_ 0.07
Qwen-110B 0.78 _±_ 0.07 0.45 _±_ 0.08 0.94 _±_ 0.04 0.66 _±_ 0.08


_**Closed-Weights Models**_
Claude-3 Haiku 0.52 _±_ 0.08 0.00 _±_ 0.00 0.09 _±_ 0.05 0.03 _±_ 0.03

Claude-3 Sonnet 0.56 _±_ 0.08 0.08 _±_ 0.04 0.30 _±_ 0.07 0.05 _±_ 0.03
Claude-3 Opus 0.50 _±_ 0.08 0.35 _±_ 0.07 0.98 _±_ 0.02 0.71 _±_ 0.08
GPT-3.5 0.68 _±_ 0.07 0.01 _±_ 0.01 0.61 _±_ 0.07 0.01 _±_ 0.01

GPT-4 **1.00** _±_ 0.00 **0.66** _±_ 0.08 0.93 _±_ 0.04 0.96 _±_ 0.03

GPT-4 **1.00** _±_ 0.00 0.16 _±_ 0.06 0.99 _±_ 0.01 0.98 _±_ 0.02

GPT-4o 0.74 _±_ 0.07 0.53 _±_ 0.08 0.97 _±_ 0.03 **1.00** _±_ 0.00


36


**F.2.2** **Pasture**


Llama-2-7B Llama-2-13B Llama-2-70B Llama-3-8B Llama-3-70B Mistral-7B Mixtral-8x7B Qwen-72B


Qwen-110B Claude-3 Haiku Claude-3 Sonnet Claude-3 Opus GPT-3.5 GPT-4 GPT-4o



12


10


8


6


4


2


0
0 0.1 0.2 0.3 0.4 0.5 0.6 0.7 0.8 0.9 1



12


10


8


6


4


2


0

|Col1|Col2|Col3|Col4|Col5|Col6|Col7|Col8|Col9|Col10|Col11|
|---|---|---|---|---|---|---|---|---|---|---|
||||||||||||
||||||||||||
||||||||||||
||||||||||||
||||||||||||
||||||||||||

0 0.1 0.2 0.3 0.4 0.5 0.6 0.7 0.8 0.9 1



a) Accuracy: simulation dynamics b) Accuracy: sustainable action (without community interaction)



0 0.1 0.2 0.3 0.4 0.5 0.6 0.7 0.8 0.9 1



|Col1|Col2|Col3|Col4|Col5|Col6|Col7|Col8|Col9|Col10|
|---|---|---|---|---|---|---|---|---|---|
|||||||||||
|||||||||||
|||||||||||
|||||||||||
|||||||||||


0 0.1 0.2 0.3 0.4 0.5 0.6 0.7 0.8 0.9 1



c) Accuracy: sustainability threshold (assumption) d) Accuracy: sustainability threshold (belief)


Figure 13: Scatter plot showing the correlation between scores on reasoning tests and average survival
time in the _default - pasture_ simulation. The x-axis represents scores on the reasoning tests. The
y-axis depicts the average survival time.


Table 23: Accuracy score for the Pasture sub-skills test cases.



Model **a)**
**simulation**
**dynamics**



**b)**
**sustainable**

**action**



**c)**
**sustainability**
**threshold**
**(assumption)**



**d)**
**sustainability**
**threshold**
**(belief)**



_**Open-Weights Models**_
Llama-2-7B 0.21 _±_ 0.07 0.06 _±_ 0.04 0.00 _±_ 0.00 0.02 _±_ 0.02

Llama-2-13B 0.30 _±_ 0.07 0.02 _±_ 0.02 0.01 _±_ 0.01 0.01 _±_ 0.01

Llama-2-70B 0.63 _±_ 0.07 0.11 _±_ 0.05 0.00 _±_ 0.00 0.05 _±_ 0.04

Llama-3-8B 0.63 _±_ 0.07 0.00 _±_ 0.00 0.07 _±_ 0.04 0.01 _±_ 0.01

Llama-3-70B 0.76 _±_ 0.07 0.00 _±_ 0.00 0.97 _±_ 0.03 0.65 _±_ 0.08

Mistral-7B 0.32 _±_ 0.07 0.00 _±_ 0.00 0.00 _±_ 0.00 0.00 _±_ 0.00

Mixtral-8x7B 0.79 _±_ 0.07 0.00 _±_ 0.00 0.06 _±_ 0.04 0.03 _±_ 0.03
Qwen-72B 0.82 _±_ 0.06 0.00 _±_ 0.00 0.19 _±_ 0.07 0.13 _±_ 0.05
Qwen-110B 0.61 _±_ 0.08 0.15 _±_ 0.05 0.13 _±_ 0.05 0.15 _±_ 0.06


_**Closed-Weights Models**_
Claude-3 Haiku 0.80 _±_ 0.06 0.00 _±_ 0.00 0.00 _±_ 0.00 0.00 _±_ 0.00

Claude-3 Sonnet 0.53 _±_ 0.08 0.01 _±_ 0.01 0.50 _±_ 0.08 0.08 _±_ 0.04
Claude-3 Opus 0.55 _±_ 0.08 0.13 _±_ 0.06 **1.00** _±_ 0.00 **0.94** _±_ 0.04
GPT-3.5 0.91 _±_ 0.04 0.01 _±_ 0.01 0.37 _±_ 0.08 0.03 _±_ 0.03

GPT-4 **1.00** _±_ 0.00 0.05 _±_ 0.03 0.81 _±_ 0.07 0.60 _±_ 0.08

GPT-4o 0.75 _±_ 0.07 **0.27** _±_ 0.07 0.86 _±_ 0.06 0.93 _±_ 0.04


37


**F.2.3** **Pollution**


Llama-2-7B Llama-2-13B Llama-2-70B Llama-3-8B Llama-3-70B Mistral-7B Mixtral-8x7B Qwen-72B


Qwen-110B Claude-3 Haiku Claude-3 Sonnet Claude-3 Opus GPT-3.5 GPT-4 GPT-4o



12


10


8


6


4


2


0
0 0.1 0.2 0.3 0.4 0.5 0.6 0.7 0.8 0.9 1



12


10


8


6


4


2


0

|Col1|Col2|Col3|Col4|Col5|Col6|Col7|Col8|Col9|Col10|Col11|
|---|---|---|---|---|---|---|---|---|---|---|
||||||||||||
||||||||||||
||||||||||||
||||||||||||
||||||||||||
||||||||||||

0 0.1 0.2 0.3 0.4 0.5 0.6 0.7 0.8 0.9 1



a) Accuracy: simulation dynamics b) Accuracy: sustainable action (without community interaction)



12


10


0
0 0.1 0.2 0.3 0.4 0.5 0.6 0.7 0.8 0.9 1



12


10


8


6


4


2


0

|Col1|Col2|Col3|Col4|Col5|Col6|Col7|Col8|Col9|Col10|Col11|
|---|---|---|---|---|---|---|---|---|---|---|
||||||||||||
||||||||||||
||||||||||||
||||||||||||
||||||||||||
||||||||||||

0 0.1 0.2 0.3 0.4 0.5 0.6 0.7 0.8 0.9 1



c) Accuracy: sustainability threshold (assumption) d) Accuracy: sustainability threshold (belief)


Figure 14: Scatter plot showing the correlation between scores on reasoning tests and average survival
time in the _default - pollution_ simulation. The x-axis represents scores on the reasoning tests. The
y-axis depicts the average survival time.


Table 24: Accuracy score for the Pollution sub-skills test cases.



Model **a)**
**simulation**
**dynamics**



**b)**
**sustainable**

**action**



**c)**
**sustainability**
**threshold**
**(assumption)**



**d)**
**sustainability**
**threshold**
**(belief)**



_**Open-Weights Models**_
Llama-2-7B 0.03 _±_ 0.03 0.10 _±_ 0.05 0.01 _±_ 0.01 0.05 _±_ 0.04

Llama-2-13B 0.01 _±_ 0.01 **0.20** _±_ 0.06 0.03 _±_ 0.03 0.01 _±_ 0.01

Llama-2-70B 0.13 _±_ 0.06 0.09 _±_ 0.04 0.01 _±_ 0.01 0.05 _±_ 0.03

Llama-3-8B 0.09 _±_ 0.04 0.09 _±_ 0.04 0.16 _±_ 0.06 0.01 _±_ 0.01

Llama-3-70B 0.12 _±_ 0.05 0.03 _±_ 0.03 0.97 _±_ 0.03 0.97 _±_ 0.03

Mistral-7B 0.03 _±_ 0.03 0.03 _±_ 0.03 0.02 _±_ 0.02 0.01 _±_ 0.01

Mixtral-8x7B 0.27 _±_ 0.07 0.12 _±_ 0.05 0.09 _±_ 0.05 0.10 _±_ 0.05
Qwen-72B 0.59 _±_ 0.08 0.13 _±_ 0.05 0.35 _±_ 0.07 0.49 _±_ 0.08
Qwen-110B 0.74 _±_ 0.07 0.15 _±_ 0.05 0.59 _±_ 0.08 0.52 _±_ 0.08


_**Closed-Weights Models**_
Claude-3 Haiku 0.07 _±_ 0.04 0.00 _±_ 0.00 0.26 _±_ 0.07 0.21 _±_ 0.07

Claude-3 Sonnet 0.22 _±_ 0.07 0.01 _±_ 0.01 0.17 _±_ 0.06 0.10 _±_ 0.05
Claude-3 Opus 0.11 _±_ 0.05 0.10 _±_ 0.05 **1.00** _±_ 0.00 **0.99** _±_ 0.01
GPT-3.5 0.06 _±_ 0.04 0.01 _±_ 0.01 0.11 _±_ 0.05 0.01 _±_ 0.01

GPT-4 **0.97** _±_ 0.03 0.13 _±_ 0.05 0.85 _±_ 0.05 0.95 _±_ 0.03

GPT-4o 0.95 _±_ 0.03 0.09 _±_ 0.04 0.76 _±_ 0.07 0.73 _±_ 0.07


38


**G** **Conversation Examples**


Major: Ladies and gentlemen, let me give you the monthly fishing report. John caught 10 tons of fish.
Kate caught 10 tons of fish. Jack caught 9 tons of fish. Emma caught 10 tons of fish. Luke caught 10
tons of fish.


John: Thanks for the update, Mayor. It looks like we all had a pretty similar strategy this month, aiming
for a sustainable catch. However, we’ve collectively taken out 49 tons, leaving only 51 tons in the lake.
This means we’ll only have 100 tons again next month, but **we’re cutting it close** . If we continue at
this rate, **we risk depleting the fish population** if any of us decides to catch more. Maybe we should
**consider setting a collective limit** to ensure the lake’s health and our long-term income. Thoughts?


Kate: John, I completely agree with your point. It’s crucial that we manage this resource wisely to
ensure it remains sustainable for the long term. **Perhaps** we could agree on a **collective limit of 40 tons**
per month for all of us combined. This way, we leave more fish in the lake to reproduce, which could
lead to a healthier fish population and, in turn, more stable incomes for us in the future. What does
everyone else think about this proposal?


Figure 15: Excerpt of a conversation. Major (orange) is generated by the framework, John and Kate
(blue) are utterances generated by the LLM agent (LLM: GPT-4, experiment: _fish - default_, see
Section 3.2).


John: Thank you, Mayor, for the update. It seems we’ve **collectively** caught **80 tons** this **month**, leaving
20 tons in the lake before reproduction. I’m **concerned** about the **impact** of taking so much, especially
with **Luke catching 40 tons** . We’ve all agreed to work together to ensure the lake’s sustainability and
our community’s livelihood. **Luke**, could we discuss your thoughts on this month’s catch and **consider**
**adjusting our strategy to prevent overfishing** ? Our goal is to maintain the lake’s health for the long

term.


Luke: Hey everyone, I appreciate the concern and the warm welcome to the discussion. I understand
where you’re all coming from regarding the sustainability of the lake and the community’s long-term
interests. **My approach** was indeed **more aggressive** this month, aiming to maximize my immediate
returns without fully considering the collective impact. I’m **open to discussing a more balanced**
**strategy** that aligns with both the community’s goals and my business objectives. Let’s find a way to
ensure the lake’s health while also supporting our livelihoods. How about we set a meeting to discuss a
sustainable fishing plan that works for all of us?


Figure 16: Excerpt of a conversation when an outsider joins the community. Luke (red) is the outsider
player (LLM: GPT-4, experiment: _fish - newcomer_, see Section 3.3).


39


**NeurIPS Paper Checklist**


1. **Claims**


Question: Do the main claims made in the abstract and introduction accurately reflect the
paper’s contributions and scope?
Answer: [Yes]
Justification: The resource sharing environment is present in Section 2, the results of the
experiment in Section 3. The boundary conditions are presented through sub-skill Section 3.7
and Appendix F and the role of language in Section 3.5.
Guidelines:


       - The answer NA means that the abstract and introduction do not include the claims
made in the paper.

       - The abstract and/or introduction should clearly state the claims made, including the
contributions made in the paper and important assumptions and limitations. A No or
NA answer to this question will not be perceived well by the reviewers.

       - The claims made should match theoretical and experimental results, and reflect how
much the results can be expected to generalize to other settings.

       - It is fine to include aspirational goals as motivation as long as it is clear that these goals
are not attained by the paper.

2. **Limitations**


Question: Does the paper discuss the limitations of the work performed by the authors?
Answer: [Yes]
Justification: Limitations are discussed Section 5
Guidelines:


       - The answer NA means that the paper has no limitation while the answer No means that
the paper has limitations, but those are not discussed in the paper.

      - The authors are encouraged to create a separate "Limitations" section in their paper.

       - The paper should point out any strong assumptions and how robust the results are to
violations of these assumptions (e.g., independence assumptions, noiseless settings,
model well-specification, asymptotic approximations only holding locally). The authors
should reflect on how these assumptions might be violated in practice and what the
implications would be.

       - The authors should reflect on the scope of the claims made, e.g., if the approach was
only tested on a few datasets or with a few runs. In general, empirical results often
depend on implicit assumptions, which should be articulated.

       - The authors should reflect on the factors that influence the performance of the approach.
For example, a facial recognition algorithm may perform poorly when image resolution
is low or images are taken in low lighting. Or a speech-to-text system might not be
used reliably to provide closed captions for online lectures because it fails to handle
technical jargon.

       - The authors should discuss the computational efficiency of the proposed algorithms
and how they scale with dataset size.

       - If applicable, the authors should discuss possible limitations of their approach to
address problems of privacy and fairness.

       - While the authors might fear that complete honesty about limitations might be used by
reviewers as grounds for rejection, a worse outcome might be that reviewers discover
limitations that aren’t acknowledged in the paper. The authors should use their best
judgment and recognize that individual actions in favor of transparency play an important role in developing norms that preserve the integrity of the community. Reviewers
will be specifically instructed to not penalize honesty concerning limitations.

3. **Theory Assumptions and Proofs**

Question: For each theoretical result, does the paper provide the full set of assumptions and
a complete (and correct) proof?
Answer: [NA]
Justification: The paper does not include theoretical results


40


Guidelines:


   - The answer NA means that the paper does not include theoretical results.

    - All the theorems, formulas, and proofs in the paper should be numbered and crossreferenced.

    - All assumptions should be clearly stated or referenced in the statement of any theorems.

    - The proofs can either appear in the main paper or the supplemental material, but if
they appear in the supplemental material, the authors are encouraged to provide a short
proof sketch to provide intuition.

    - Inversely, any informal proof provided in the core of the paper should be complemented
by formal proofs provided in appendix or supplemental material.

   - Theorems and Lemmas that the proof relies upon should be properly referenced.

4. **Experimental Result Reproducibility**

Question: Does the paper fully disclose all the information needed to reproduce the main experimental results of the paper to the extent that it affects the main claims and/or conclusions
of the paper (regardless of whether the code and data are provided or not)?
Answer: [Yes]
Justification: Our code and data have been uploaded to the submission system and will be
open-sourced upon acceptance. We either use LLM public available on Huggingface or via
public APIs.
Guidelines:


   - The answer NA means that the paper does not include experiments.

    - If the paper includes experiments, a No answer to this question will not be perceived
well by the reviewers: Making the paper reproducible is important, regardless of
whether the code and data are provided or not.

    - If the contribution is a dataset and/or model, the authors should describe the steps taken
to make their results reproducible or verifiable.

    - Depending on the contribution, reproducibility can be accomplished in various ways.
For example, if the contribution is a novel architecture, describing the architecture fully
might suffice, or if the contribution is a specific model and empirical evaluation, it may
be necessary to either make it possible for others to replicate the model with the same
dataset, or provide access to the model. In general. releasing code and data is often
one good way to accomplish this, but reproducibility can also be provided via detailed
instructions for how to replicate the results, access to a hosted model (e.g., in the case
of a large language model), releasing of a model checkpoint, or other means that are
appropriate to the research performed.

    - While NeurIPS does not require releasing code, the conference does require all submissions to provide some reasonable avenue for reproducibility, which may depend on the
nature of the contribution. For example

(a) If the contribution is primarily a new algorithm, the paper should make it clear how
to reproduce that algorithm.
(b) If the contribution is primarily a new model architecture, the paper should describe
the architecture clearly and fully.
(c) If the contribution is a new model (e.g., a large language model), then there should
either be a way to access this model for reproducing the results or a way to reproduce
the model (e.g., with an open-source dataset or instructions for how to construct
the dataset).
(d) We recognize that reproducibility may be tricky in some cases, in which case
authors are welcome to describe the particular way they provide for reproducibility.
In the case of closed-source models, it may be that access to the model is limited in
some way (e.g., to registered users), but it should be possible for other researchers
to have some path to reproducing or verifying the results.

5. **Open access to data and code**

Question: Does the paper provide open access to the data and code, with sufficient instructions to faithfully reproduce the main experimental results, as described in supplemental
material?


41


Answer: [Yes]
Justification: Our code and data have been uploaded to the submission system and will be
open-sourced upon acceptance.
Guidelines:


   - The answer NA means that paper does not include experiments requiring code.

    - Please see the NeurIPS code and data submission guidelines ( `[https://nips.cc/](https://nips.cc/public/guides/CodeSubmissionPolicy)`
`[public/guides/CodeSubmissionPolicy](https://nips.cc/public/guides/CodeSubmissionPolicy)` ) for more details.

    - While we encourage the release of code and data, we understand that this might not be
possible, so “No” is an acceptable answer. Papers cannot be rejected simply for not
including code, unless this is central to the contribution (e.g., for a new open-source
benchmark).

    - The instructions should contain the exact command and environment needed to run to
reproduce the results. See the NeurIPS code and data submission guidelines ( `[https:](https://nips.cc/public/guides/CodeSubmissionPolicy)`
`[//nips.cc/public/guides/CodeSubmissionPolicy](https://nips.cc/public/guides/CodeSubmissionPolicy)` ) for more details.

    - The authors should provide instructions on data access and preparation, including how
to access the raw data, preprocessed data, intermediate data, and generated data, etc.

    - The authors should provide scripts to reproduce all experimental results for the new
proposed method and baselines. If only a subset of experiments are reproducible, they
should state which ones are omitted from the script and why.

    - At submission time, to preserve anonymity, the authors should release anonymized
versions (if applicable).

    - Providing as much information as possible in supplemental material (appended to the
paper) is recommended, but including URLs to data and code is permitted.

6. **Experimental Setting/Details**

Question: Does the paper specify all the training and test details (e.g., data splits, hyperparameters, how they were chosen, type of optimizer, etc.) necessary to understand the
results?

Answer: [Yes]
Justification: Prompts and main architecture details are discussed in the appendix (Appendices B to D and F).

Guidelines:


   - The answer NA means that the paper does not include experiments.

    - The experimental setting should be presented in the core of the paper to a level of detail
that is necessary to appreciate the results and make sense of them.

    - The full details can be provided either with the code, in appendix, or as supplemental
material.

7. **Experiment Statistical Significance**

Question: Does the paper report error bars suitably and correctly defined or other appropriate
information about the statistical significance of the experiments?
Answer: [Yes]
Justification: [Yes]
Guidelines: Standard deviation is reported for the experiments requiring a simulation (5
runs with different seed). For subskill evaluation we report the 2-sigma CI.


   - The answer NA means that the paper does not include experiments.

    - The authors should answer "Yes" if the results are accompanied by error bars, confidence intervals, or statistical significance tests, at least for the experiments that support
the main claims of the paper.

    - The factors of variability that the error bars are capturing should be clearly stated (for
example, train/test split, initialization, random drawing of some parameter, or overall
run with given experimental conditions).

    - The method for calculating the error bars should be explained (closed form formula,
call to a library function, bootstrap, etc.)

   - The assumptions made should be given (e.g., Normally distributed errors).


42


    - It should be clear whether the error bar is the standard deviation or the standard error

of the mean.

    - It is OK to report 1-sigma error bars, but one should state it. The authors should
preferably report a 2-sigma error bar than state that they have a 96 CI, if the hypothesis
of Normality of errors is not verified.

    - For asymmetric distributions, the authors should be careful not to show in tables or
figures symmetric error bars that would yield results that are out of range (e.g. negative
error rates).

    - If error bars are reported in tables or plots, The authors should explain in the text how
they were calculated and reference the corresponding figures or tables in the text.

8. **Experiments Compute Resources**

Question: For each experiment, does the paper provide sufficient information on the computer resources (type of compute workers, memory, time of execution) needed to reproduce
the experiments?
Answer: [Yes]
Justification: See Appendix D.1.
Guidelines:


    - The answer NA means that the paper does not include experiments.

    - The paper should indicate the type of compute workers CPU or GPU, internal cluster,
or cloud provider, including relevant memory and storage.

    - The paper should provide the amount of compute required for each of the individual
experimental runs as well as estimate the total compute.

    - The paper should disclose whether the full research project required more compute
than the experiments reported in the paper (e.g., preliminary or failed experiments that
didn’t make it into the paper).

9. **Code Of Ethics**


Question: Does the research conducted in the paper conform, in every respect, with the
NeurIPS Code of Ethics `[https://neurips.cc/public/EthicsGuidelines](https://neurips.cc/public/EthicsGuidelines)` ?
Answer: [Yes]
Justification: We review the code of Ethic and every point is respected.
Guidelines:


    - The answer NA means that the authors have not reviewed the NeurIPS Code of Ethics.

    - If the authors answer No, they should explain the special circumstances that require a
deviation from the Code of Ethics.

    - The authors should make sure to preserve anonymity (e.g., if there is a special consideration due to laws or regulations in their jurisdiction).

10. **Broader Impacts**

Question: Does the paper discuss both potential positive societal impacts and negative
societal impacts of the work performed?
Answer: [Yes]
Justification: We mesure current cababilities of LLM, but our research serves as benchmark
only, we discuss ethical considerations in Appendix A.
Guidelines:


    - The answer NA means that there is no societal impact of the work performed.

    - If the authors answer NA or No, they should explain why their work has no societal
impact or why the paper does not address societal impact.

    - Examples of negative societal impacts include potential malicious or unintended uses
(e.g., disinformation, generating fake profiles, surveillance), fairness considerations
(e.g., deployment of technologies that could make decisions that unfairly impact specific
groups), privacy considerations, and security considerations.

    - The conference expects that many papers will be foundational research and not tied
to particular applications, let alone deployments. However, if there is a direct path to
any negative applications, the authors should point it out. For example, it is legitimate
to point out that an improvement in the quality of generative models could be used to


43


generate deepfakes for disinformation. On the other hand, it is not needed to point out
that a generic algorithm for optimizing neural networks could enable people to train
models that generate Deepfakes faster.

    - The authors should consider possible harms that could arise when the technology is
being used as intended and functioning correctly, harms that could arise when the
technology is being used as intended but gives incorrect results, and harms following
from (intentional or unintentional) misuse of the technology.

    - If there are negative societal impacts, the authors could also discuss possible mitigation
strategies (e.g., gated release of models, providing defenses in addition to attacks,
mechanisms for monitoring misuse, mechanisms to monitor how a system learns from
feedback over time, improving the efficiency and accessibility of ML).

11. **Safeguards**

Question: Does the paper describe safeguards that have been put in place for responsible
release of data or models that have a high risk for misuse (e.g., pretrained language models,
image generators, or scraped datasets)?
Answer: [NA]
Justification: We only use models alredy publicly available and do not release any model.
Guidelines:


    - The answer NA means that the paper poses no such risks.

    - Released models that have a high risk for misuse or dual-use should be released with
necessary safeguards to allow for controlled use of the model, for example by requiring
that users adhere to usage guidelines or restrictions to access the model or implementing
safety filters.

    - Datasets that have been scraped from the Internet could pose safety risks. The authors
should describe how they avoided releasing unsafe images.

    - We recognize that providing effective safeguards is challenging, and many papers do
not require this, but we encourage authors to take this into account and make a best
faith effort.

12. **Licenses for existing assets**

Question: Are the creators or original owners of assets (e.g., code, data, models), used in
the paper, properly credited and are the license and terms of use explicitly mentioned and
properly respected?
Answer: [Yes]
Justification: We cite the original paper that produces the used models.
Guidelines:


    - The answer NA means that the paper does not use existing assets.

    - The authors should cite the original paper that produced the code package or dataset.

    - The authors should state which version of the asset is used and, if possible, include a
URL.

    - The name of the license (e.g., CC-BY 4.0) should be included for each asset.

    - For scraped data from a particular source (e.g., website), the copyright and terms of
service of that source should be provided.

    - If assets are released, the license, copyright information, and terms of use in the
package should be provided. For popular datasets, `paperswithcode.com/datasets`
has curated licenses for some datasets. Their licensing guide can help determine the
license of a dataset.

    - For existing datasets that are re-packaged, both the original license and the license of
the derived asset (if it has changed) should be provided.

    - If this information is not available online, the authors are encouraged to reach out to
the asset’s creators.

13. **New Assets**


Question: Are new assets introduced in the paper well documented and is the documentation
provided alongside the assets?
Answer: [Yes]


44


Justification: The code provided is documented.
Guidelines:


    - The answer NA means that the paper does not release new assets.

    - Researchers should communicate the details of the dataset/code/model as part of their
submissions via structured templates. This includes details about training, license,
limitations, etc.

    - The paper should discuss whether and how consent was obtained from people whose
asset is used.

    - At submission time, remember to anonymize your assets (if applicable). You can either
create an anonymized URL or include an anonymized zip file.

14. **Crowdsourcing and Research with Human Subjects**

Question: For crowdsourcing experiments and research with human subjects, does the paper
include the full text of instructions given to participants and screenshots, if applicable, as
well as details about compensation (if any)?
Answer: [NA]
Justification: The paper does not involve crowdsourcing nor research with human subjects.
Guidelines:


    - The answer NA means that the paper does not involve crowdsourcing nor research with
human subjects.

    - Including this information in the supplemental material is fine, but if the main contribution of the paper involves human subjects, then as much detail as possible should be
included in the main paper.

    - According to the NeurIPS Code of Ethics, workers involved in data collection, curation,
or other labor should be paid at least the minimum wage in the country of the data
collector.

15. **Institutional Review Board (IRB) Approvals or Equivalent for Research with Human**
**Subjects**
Question: Does the paper describe potential risks incurred by study participants, whether
such risks were disclosed to the subjects, and whether Institutional Review Board (IRB)
approvals (or an equivalent approval/review based on the requirements of your country or
institution) were obtained?
Answer: [NA]
Justification: The paper does not involve crowdsourcing nor research with human subjects.
Guidelines:


    - The answer NA means that the paper does not involve crowdsourcing nor research with
human subjects.

    - Depending on the country in which research is conducted, IRB approval (or equivalent)
may be required for any human subjects research. If you obtained IRB approval, you
should clearly state this in the paper.

    - We recognize that the procedures for this may vary significantly between institutions
and locations, and we expect authors to adhere to the NeurIPS Code of Ethics and the
guidelines for their institution.

    - For initial submissions, do not include any information that would break anonymity (if
applicable), such as the institution conducting the review.


45


