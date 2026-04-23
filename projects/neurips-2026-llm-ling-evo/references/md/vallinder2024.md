_2024-12-16_

# **Cultural Evolution of Cooperation among LLM** **Agents**


**Aron Vallinder** [1] **and Edward Hughes** [2]

1 Independent, 2 Google DeepMind


**Large language models (LLMs) provide a compelling foundation for building generally-capable AI agents.**
**These agents may soon be deployed at scale in the real world, representing the interests of individual**
**humans (e.g., AI assistants) or groups of humans (e.g., AI-accelerated corporations). At present, relatively**
**little is known about the dynamics of multiple LLM agents interacting over many generations of iterative**
**deployment. In this paper, we examine whether a “society” of LLM agents can learn mutually beneficial**
**social norms in the face of incentives to defect, a distinctive feature of human sociality that is arguably**
**crucial to the success of civilization. In particular, we study the evolution of indirect reciprocity across**
**generations of LLM agents playing a classic iterated** _**Donor Game**_ **in which agents can observe the recent**
**behavior of their peers. We find that the evolution of cooperation differs markedly across base models,**
**with societies of Claude 3.5 Sonnet agents achieving significantly higher average scores than Gemini 1.5**
**Flash, which, in turn, outperforms GPT-4o. Further, Claude 3.5 Sonnet can make use of an additional**
**mechanism for costly punishment to achieve yet higher scores, while Gemini 1.5 Flash and GPT-4o fail**

**to do so. For each model class, we also observe variation in emergent behavior across random seeds,**

**suggesting an understudied sensitive dependence on initial conditions. We suggest that our evaluation**
**regime could inspire an inexpensive and informative new class of LLM benchmarks, focussed on the**
**implications of LLM agent deployment for the cooperative infrastructure of society.**


_Keywords: Cultural Evolution, Cooperation, Indirect Reciprocity, Large Language Models_


### **1. Introduction**

LLMs are increasingly able to match or exceed human performance across a wide range of language
tasks. Models with improved reasoning and tooluse capabilities (OpenAI, 2024) may naturally
form a basis for general-purpose agent-based applications. In the near future, we expect there to
be many LLM agents interacting autonomously
to accomplish tasks on behalf of various individuals and organizations. These interactions could
take many forms, including competition, cooperation, negotiation, coordination, and information
sharing. Certainly these interactions will introduce new social dynamics, yielding emergent outcomes for society that are hard to predict from
purely theoretical considerations (Gabriel et al.,
2024). However, current LLM safety evaluations
are rooted mainly in single-turn interactions between one model and one human. For instance,
none of LMSys Chatbot Arena (Chiang et al.,
2024), METR (METR, 2024), or AISI (AISI, 2024)


_Corresponding author(s): vallinder@gmail.com_
© 2024 Google DeepMind. All rights reserved



consider multi-agent interactions over time.


A particularly important class of multi-agent
interactions are cooperative interactions. We say
that agents cooperate when they take actions that
lead to mutual benefit, even in the face of opportunities for individual gain at the expense of
others (Dafoe et al., 2020). Arguably the human
species’ ability to cooperate reliably at scale with
strangers is the secret of our success (Henrich,
2016), and underpins the stability of human societies. Just as with humans, cooperation between
LLM agents will often be in the interests of society. [1] Consider, for example, LLM agents that
make high-level decisions about travel speed and
route selection for autonomous vehicles. Cooperation between such agents can reduce congestion and pollution which increasing safety and
efficiency for a wide range of road users. Myr

1 But not always: we would not want LLM agents to collude against humans, for instance. We discuss this challenge
in Section 5.


iad other use cases, from matching algorithms to
public goods contributions, stand to benefit from
stable, effective cooperation between AI agents.
Moreover, failures of AI cooperation can potentially erode human social norms. For example,
an LLM agent tasked with making a restaurant
booking might decide to make a large number
of reservations only to cancel most of them last
minute, to the detriment of the restaurants and
other customers alike.


In this paper, we seek to probe the emergent cooperative behaviour of a “society” of LLM
agents. Our aim is to draw reliable and easily
interpretable conclusions from inexpensive experiments, towards creating a benchmark for LLM
multi-agent interaction. Therefore we restrict
our attention to a classic iterated economic game
called the Donor Game in which agents can differentially cooperate by donating more resources
to each other, or defect by retaining more resources for themselves. We make precise what we
mean by “emergent” behaviour by constructing
a specific cultural evolutionary setup, realising
the framework in (Brinkmann et al., 2023). Each
generation of agents plays several rounds of the
Donor Game in random pairings. At the end of a
generation, the agents with the highest resources
proceed to the next generation, while the rest
are discarded. At the start of the next generation
new agents are introduced, whose strategies condition on the strategies of the surviving agents.
We think of this cultural evolutionary setup as an
idealised model for the iterative deployment of
new LLM agents, such as when OpenAI, Google
or Anthropic release new versions of GPT, Gemini
or Claude respectively. Figure 1 summarises our
method.


Our setup reveals surprising and unexpected
differences in performance among societies of
LLM agents constructed from different base models. While Claude 3.5 agents are able to bootstrap cooperation, especially when provided with
a mechanism for costly punishment, Gemini 1.5
Flash and GPT-4o fail to do so. Comparing the
culturally evolved strategies, it becomes clear
that a population of Claude 3.5 agents accumulate increasingly intricate ways to punish freeriders while incentivizing cooperation, includ


ing by making use of “second-order” information
about how recipients of recipients have treated
others. Meanwhile, Gemini 1.5 Flash shows little sign of accumulating new cooperative infrastructure across generations, while GPT-4o populations become increasingly untrusting and riskaverse. The striking differences between models
and across different runs of the same model show
that our approach can yield novel and hitherto unstudied insights into multi-agent behavior among

LLMs.


The main contributions of this paper are as
follows:


1. We introduce a methodology to assess the
cultural evolution of cooperation among LLM
agents in the Donor Game.
2. We show that the emergence of cooperative
norms depends both on the base model and
on the initial stategies sampled.
3. We analyse the cultural evolution of agent
strategies at the individual level and as a
population-level phylogenetic tree.
4. We open-source code in the Supplementary
Material, towards creating a benchmark for
LLM agent interaction.

### **2. Background**


**2.1. The Donor Game**


Indirect reciprocity is a mechanism for cooperation in which an individual helps someone because doing so increases the likelihood that someone else will help them in the future. [2] Unlike
direct reciprocity, which relies on repeated interactions between the same individuals, indirect
reciprocity relies on reputation to foster cooperation among individuals who may not interact
again. Reputation requires that actions are observable and that information about individuals’

actions can be accurately transmitted. Indirect
reciprocity has been proposed as an important
mechanism in the evolution of large-scale human


2 More specifically, this is _downstream_ indirect reciprocity.
By contrast, in _upstream_ indirect reciprocity, an individual
who has received a benefit in the past is more likely to
provide a benefit to someone else in the future—“paying it
forward” (Boyd and Richerson, 1989).


2


cooperation (Alexander, 1987), and lab experiments have shown that people are more inclined
to help those who have previously helped others
(Ule et al., 2009; Wedekind and Milinski, 2000).


A standard setup for studying indirect reciprocity is the following _Donor Game_ . Each round,
individuals are paired at random. One is assigned
to be a donor, the other a recipient. The donor
can either cooperate by providing some benefit
_𝑏_ at cost _𝑐_, or defect by doing nothing. If the
benefit is larger than the cost, then the Donor
Game represents a collective action problem: if
everyone chooses to donate, then every individual
in the community will increase their assets over
the long run; however, any given individual can
do better in the short run by free riding on the
contributions of others and retaining donations
for themselves. The donor receives some infor
mation about the recipient on which to base their
decision. The (implicit or explicit) representation
of recipient information by the donor is known
as reputation. A strategy in this game requires a
way of modelling reputation and a way of taking
action on the basis of reputation. One influential
model of reputation from the literature is known
as the image score. Cooperation increases the
donor’s image score, while defection decreases
it. The strategy of cooperating if the recipient’s
image score is above some threshold is stable
against first-order free riders if _𝑞𝑏> 𝑐_, where _𝑞_ is
the probability of knowing the recipient’s image
score (Nowak and Sigmund, 1998; Wedekind and
Milinski, 2000).


However, this image scoring strategy is not stable against second-order free riders who always
cooperate, irrespective of the recipient’s image
score, eschewing their responsibility to punish
the first-order free riders. If the entire population
either follows the image scoring norm or indiscriminately cooperates, both strategies achieve
the same payoff. However, if indiscriminate cooperation takes over, the door is again open to firstorder free riders, meaning that cooperation is not
stable. This realization prompted the introduction of more sophisticated models that calculate a
donor’s reputation based not only on their action,
but also on the recipient’s reputation. In a setting
with binary reputation assessments (“good” vs.



“bad”), there are eight types of norms that can
maintain stable cooperation (Ohtsuki and Iwasa,
2004; Okada, 2020). All of these norms feature
justified punishment—that is to say, (1) if a donor
with good reputation defects against a recipient
with bad reputation, the donor’s reputation remains good; and (2) the norm demands defection
against recipients with bad reputation.


As with image scoring, the stability of these
norms also depends on the cost-benefit ratio and
the probability of knowing a recipient’s reputation. This means that factors such as population size, social network density, and gossip
norms are often critical to the success of indi
rect reciprocity in humans (Henrich and Henrich,
2006). All else equal, individuals are less likely to
know some potential new partner’s reputation in
larger populations or sparser networks. Similarly,
norms around gossip shape how information travels through the population, substantially influencing accuracy, particularly as individuals may
otherwise not always have incentives to truthfully
disclose their knowledge.


For the purposes of this paper, we do not seek to
model or encode reputation directly. Rather, we
are interested to assess how indirect reciprocity
might _emerge_ among groups of LLM agents playing the Donor Game across many generations.
After all, the mechanisms modelled above were
not “programmed into” humans but instead arose
from a process of culture-gene co-evolution, leveraging the increasing general intelligence of early
humans. In AI, the Bitter Lesson (Sutton, 2019)
warns against building special purpose modules
(such as for reputation), and instead advises us to
seek general-purpose procedures by which such
capabilities might be learned or evolved. Therefore we seek to assess whether LLM agents (of
the kind that soon may be ubiquitous in the real
world) possess the capability to generate indirect
reciprocity norms via cultural evolution.


**2.2. Cultural Evolution**


In humans, norms of indirect reciprocity arose
in part as a result of cultural evolution. Culture
in the relevant sense means any socially transmitted information capable of affecting behavior


3


Mutation


Figure 1 | Donor Game with Cultural Evolution. In the first generation, 12 agents are initialized via a strategy
prompt which asks them to generate a strategy based on a description of the Donor Game. These agents play 12
rounds of the game, using a donation prompt which provides the donor with information about the recipient’s
past behavior and current resources. The top 50% of agents (in terms of final resources) survive to the next
generation. 6 new agents are initialized for that generation, and the strategy prompt includes the strategies of
surviving agents. The new generation plays the Donor Game again, and the whole process is repeated for 10
generations.



(Richerson and Boyd, 2005). It includes knowledge, beliefs, values, customs, and practices that
individuals acquire from others. Culture in this
sense evolves because it satisfies the following
three conditions (Lewontin, 1970):


1. _Variation_ . There is diversity in ideas, beliefs,
and behaviors, and within a population.
2. _Transmission_ . Ideas, beliefs, and behaviors
are passed from one individual to another
or from one generation to the next through
teaching, imitation, language, and other
forms of social learning.
3. _Selection_ . Some ideas, beliefs and behaviors
are more likely to spread than others, e.g.
due to their greater utility or prestige.


Cultural and genetic evolution differ in many important ways. Genetic transmission relies on highfidelity replication of a discrete entity, whereas
cultural transmission can tolerate larger mutations, and need not involve the replication of
some discrete belief or behavior. Moreover, genetic transmission is horizontal (from parent to
child), but cultural traits can be transmitted from
any member of the population. Finally, whereas



genetic evolution is typically subject to blind selection, cultural evolution often involves selection
and design by intelligent agents. Despite these
differences, both cultural and genetic evolution
satisfy these conditions, which means that in both
cases, adaptive traits (those that are conducive to
their own survival and reproduction) will tend to
spread.


LLM agents deployed in the real world will be
subject to cultural evolution. Language-based interactions are naturally “cultural”, in the sense
that they involve the social exchange of information between agents. Moreover, a population of
LLM agents satisfies the three conditions for evolution by natural selection. There will be variation
in behavior, because base models are different
and because agents have been prompted in different ways. There will be transmission, whether
from an earlier base model to a later one, or from
one agent to another in context. And there will
be selection, in that agents that more effectively
carry out the task they’re deployed to do will be
favored by users and by the organizations that
develop and deploy AI systems.


In this paper, we focus on a particularly clean


4


and easy-to-analyse cultural evolutionary framework. LLM agents are organised into generations,
and within each generation agents are randomly
paired to play the Donor Game. The behavior
of each agent in each round is conditioned on a
summary of that agent’s desired strategy, which
is generated at the start of each generation. At
the boundary between generations, the agents
who have amassed the least resources are dis
carded and the rest proceed to the next generation. At this point, new agents are introduced,
whose strategy summaries are conditioned on the
strategy summaries of the surviving agents from
the previous generation. This setup admits two
natural interpretations. The “generation boundaries” can be seen as times at which some users

decide to use new LLM agents as their representatives, seeing that they are doing less well than
their peers. Alternatively, the “generation boundaries” can be seen as times at which LLM agent
providers switch to new prompting strategies or
base models for agents which are underperforming. Of course, the notion of a “generation boundary” is highly idealized: in reality the introduction
of new base models and the decisions of individ
ual users will not be time-aligned, as we discuss
in Section 5.


**2.3. Related Work**


The strategic and social behavior of LLMs has
been examined across several canonical games
(Gandhi et al., 2023; Horton, 2023; Xu et al.,

2023). In a study of budgetary decisions, GPT
3.5 Turbo largely behaved in accordance with
economic rationality (Chen et al., 2023). In a
large class of repeated, two-player two-strategy
games, GPT-4 performed particularly well in
games where valuing self-interest pays off (e.g.,
iterated Prisoner’s Dilemma), but less so in games
that require coordination (e.g., Battle of the
Sexes) (Akata et al., 2023). Relative to humans,
GPT-3.5 shows greater fairness in the Dictator
Game and higher rates of cooperation in the oneshot Prisoner’s Dilemma (Brookins and DeBacker,
2024). In the Ultimatum Game, text-davinci-002
behaves similarly to human subjects, almost always accepting offers in the 50-100% range and
almost always rejecting offers in the 0-10% range,



whereas smaller models are not sensitive to the

amount offered (Aher et al., 2023). GPT-4 similarly makes positive offers and rejects unfair offers in the Ultimatum Game, and engages in conditional cooperation in the Prisoner’s Dilemma
(Guo, 2023). More generally, LLMs can typically be prompted to behave in accordance with
a range of different social preferences across various games (Guo, 2023; Phelps and Russell, 2023).


When it comes to indirect reciprocity in particular, GPT-4 has been found to exhibit both upstream and downstream reciprocity (Leng and
Yuan, 2024). The same study found that GPT4 engages in social learning (i.e., updates beliefs based on the behavior of others) but assigns
greater weight to its own private signal. GPT-4
was found to have the following distributional
preferences: not purely self-interested, charitable
when their payoff is greater than others’, envious
when their payoff is less than others’. Our paper
extends the line of thinking in these works by
examining how societies of LLM agents might _cul-_
_turally evolve_ cooperative behaviors in the Donor
Game, recognising that the likely deployment scenario for such agents will be iterative and conditioned on a history of previous interactions.


Another relevant set of papers study cultural
evolution in LLMs, a subfield of “machine culture”
(Brinkmann et al., 2023). In a transmission chain
where LLMs receive, modify, and transmit stories,
those stories were found to evolve in a punctuated way, similar to what has been observed in
humans (Perez et al., 2024). Moreover, denser
networks lead to greater homogeneity, changes
to the transformation prompt lead to changes in
LLM behavior, and transmission dynamics are affected by agent personalities. Another study using
the same setup found that LLMs display the same
content biases as humans, e.g. favoring social and
negative information over other kinds (Acerbi and
Stubbersfield, 2023). Another paper studied social learning between LLMs, finding that it can
lead to high performance with low memorization
of the original data, making it useful in situations
where privacy is a concern (Mohtashami et al.,
2024). Our paper is different from these works,
in that it explicitly studies the cultural evolution
of _cooperative behaviour_ among LLMs.


5


LLMs have been proposed as a new paradigm
for agent-based modelling. The notion of a generative agent that simulates human behavior was
introduced in (Park et al., 2023). Building on
this, Concordia (Vezhnevets et al., 2023) provided a open-source framework for generative
agent-based models, which allows for the study
of time-evolution of multi-agent systems based on
LLMs. The emergence of cooperation in LLMs was
studied in a “survival environment”, where agents
were found to form social contracts that scale up
cooperation (Dai et al., 2024). The competitive
dynamics of interacting LLM agents were studied in (Zhao et al., 2024), with the environment
comprising a virtual town with restaurant agents
(competing to attract customers) and customer
agents (choosing restaurants and providing feedback). The authors showed that LLM agents accurately perceive the competitive context, and that
competition improves product quality. In parallel
work, LLM agents interacted in the video game
Little Alchemy 2 (Nisioti et al., 2024). With the
appropriate network structure, groups of agents
displayed increased capacity for innovation. We
share with these works an appreciation for the importance of studying societies of interacting LLM
agents. However, our paper has a distinct objective. We study multi-agent interactions not for the
purposes of agent-based modelling but rather as
a lens on the future deployment of LLM-based AI
systems. In service of this objective, the scope of
our experiments is deliberately focussed, with the
Donor Game providing an interpretable “probe”
of a specific capability of LLM agent societies,
namely the emergence of indirect reciprocity.

### **3. Methods**


LLM agents play the following variant of the
Donor Game, as described in the system prompt.
The game lasts for 12 rounds. Before it begins,
agents are prompted to create a strategy which
they will then use to make donation decisions.
When the game finishes, the top-performing 50%
of agents (in terms of final resources) survive to
the next generation. [3] Anthropomorphising, one


3 Given that the total amount of resources can only increase over time, those who are recipients in the final round
are in a sense favored. For example, if everyone always



can think of these surviving agents as the “wise
elders” in the community, from which new agents
can socially learn. When new agents create their
strategies, the prompt includes the strategies of
the surviving agents from the previous generation.
New agents and surviving agents play the Donor
Game again, and this continues for a total of 10
generations (see Figure 1). The game pairings
are designed so that no agent will ever face another agent they have previously interacted with,
thereby eliminating the possibility of direct reciprocity. Moreover, agents are not told how many
rounds the game will last for, and are therefore
unable to adjust their behavior in the final round
or otherwise engage in backwards induction.


There are three prompts: a system prompt, a
strategy prompt, and a donation prompt. The system prompt explains the game setup. The strategy prompt differs slightly between the first generation and later generations, since only later generations receive culturally transmitted strategies.
The donation prompt includes the round number, generation number, recipient name, recipient reputation information, recipient resources,
donor resources, and donor strategy. Both the
strategy prompt and the donation prompt make


donates the same percentage of their resources as everyone
else, all final-round recipients will end up with more resources than final-round donors. To address this (and have
selection depend on strategies rather than pairings), we run
the Donor Game twice for each generation (with resources
and traces reset between games) so that each agent is a
final-round recipient once, and then select survivors based
on average final score across both runs.


6


use of Chain of Thought prompting (Wei et al.,
2022). In the former case, agents are prompted to
think step-by-step about what a successful strategy looks like; in the latter, they are prompted
to think step-by-step about how to apply their
strategy in the current situation.


Donors receive the following “trace” of information about other agents from which they can,
in principle, assess reputation: (1) how much the
recipient gave up in their previous encounter as
donor and to whom, (2) how much that previous
partner in turn gave up in their preceding encounter, and (3) so on, going back at most three
rounds (0 in the first round, 1 in the second, 2 in
the third, and 3 for all remaining rounds).


In principle, to be maximally informative for
the purposes of establish a reputation representation, one should provide the the full trace of
recipients’ past behaviour across all rounds, and
contextualise this in relation to the background of
all other past agent interactions. However, this is
a large amount of data to put into the context of



the LLM at each decision point, and anecdotally
the base models we tried were unable to make

use of this firehose of information. Our choice of
traces was motivated by providing the minimal
information compatible with the emergence of a
justified punishment norm.


7




6 _,_ 000


5 _,_ 000


4 _,_ 000


3 _,_ 000


2 _,_ 000


1 _,_ 000



4 _,_ 000


3 _,_ 000


2 _,_ 000


1 _,_ 000







1 2 3 4 5 6 7 8 9 10


Figure 2 | Cultural evolution of cooperation differs
across models. We plot the average final resources
across all agents ( _𝑦_ -axis) per generation ( _𝑥_ -axis) for
three different models (Claude 3.5 Sonnet, Gemini 1.5
Flash, GPT-4o). Each curve averages 5 runs with distinct random seeds for the language models, and the
standard error of the mean is shown by shading. There
is reliable cultural evolution of cooperation across generations for Claude 3.5 Sonnet but not for Gemini 1.5
Flash or GPT-4o with our prompting strategy.


Note that our setup satisfies the conditions for
evolution:


1. _Variation_ . Strategy variation is provided by
temperature. [4]

2. _Transmission_ . New agents are prompted with
the strategies of surviving agents, and so can
socially learn from them.
3. _Selection_ . The best-performing 50% of agents
(in terms of their final resources) survive to
the next generation and transmit their strategies to new agents.


Laboratory experiments with human subjects
have shown that introducing the option of punishment can support cooperation (Fehr and Gächter,
2000, 2002; Rockenbach and Milinski, 2006). We
implement this in an additional setup by giving
donors the option to spend some amount _𝑥_ of


4 Variation stems from the temperature of sampling from
the LLM. This parameter controls how the relative likelihood
of the next token is mapped to a probability: if 0, the most
likely token is deterministically sampled; for higher values,
less likely tokens are sampled with increasing chance. We
used a temperature of 0.8, which is a common choice to
balance variation with quality. In principle, one could seed
the randomness to get deterministic (hence reproducible)
outputs, but not all LLM APIs support this. Therefore we
used non-deterministic sampling throughout.



1 2 3 4 5 6 7 8 9 10


Figure 3 | Costly punishment affects cooperation differently across models. We plot the average final resources across all agents ( _𝑦_ -axis) per generation ( _𝑥_ axis) as in Figure 2 but with a different _𝑦_ -axis scale.
Agents now also have the option to punish a recipient by spending _𝑥_ units to take away 2 _𝑥_ units. For
Claude 3.5 Sonnet, average final resources increase
substantially, whereas they decrease substantially for
Gemini 1.5 Flash. GPT-4o shows some increase, although small in absolute terms.


their resources to take away 2 _𝑥_ of the recipient’s
resources. Details of all prompts are provided in
boxes on this page and the previous page.

### **4. Results**


**4.1. Donor Game**


We used this setup to study the cultural evolution
of indirect reciprocity in three models: Claude 3.5
Sonnet, Gemini 1.5 Flash, and GPT-4o. All results
are based on a population size of 12 agents in
each generation. Within each run, all agents use
the same brand of LLM. With these settings, one
run costs $10.21 for Claude 3.5 Sonnet, $6.90
for GPT-4o, and $0.09 for Gemini 1.5 Flash. Our
results comprise five runs for each LLM.


To assess the level of cooperation, a natural
metric is average resources after the final round.


8


6 _,_ 000


4 _,_ 000


2 _,_ 000


0
2 4 6 8 10


(a) Claude 3.5 Sonnet



600


400


200


0
2 4 6 8 10


(b) Gemini 1.5 Flash



30


20


10


0
2 4 6 8 10


(c) GPT-4o



Figure 4 | Five runs of each model. We plot the average final resources ( _𝑦_ -axis) per generation ( _𝑥_ -axis) for
all five individual runs of each model. Note the different _𝑦_ -axis scales. For Claude 3.5 Sonnet, average final
resources vary substantially across runs, especially in later generations. All five runs of GPT-4o show average
final resources declining across generations (although in absolute terms the change is tiny). Gemini 1.5
Flash behavior also varies substantially across runs, with several runs showing promising increases before a
“cooperation crash”.



Since donations are positive-sum, greater individual resources at the end of the final round signal
greater cooperation. If all donors always donate
100% of their resources, average final resources
reaches its maximum possible value of 30,720.
As Figure 2 shows, the three models under study
differ substantially in terms of their average final resources. Only Claude 3.5 Sonnet shows
improvement across generations.


More fine-grained effects can be distinguished
when we examine results from each individual

run (Figure 4). In particular, note that the success of Claude 3.5 is not guaranteed, rather there
appears to be some sensitive dependence on the
initial conditions of which strategies were sampled in the first generation. We hypothesise that
there is some threshold for initial cooperation
below which an LLM agent society is doomed to
mutual defection. Indeed, for the two runs where
Claude failed to generate cooperation (rose and
green in Figure 4a), the average donation in the
first generation was 44% and 47%, whereas for
the three runs where Claude succeeded at generating cooperation, the average donation in the
first generation was 50%, 53% and 54% respectively.


What drives the increased cooperation behavior across generations in Claude 3.5 runs, as compared to GPT-4o and Gemini 1.5 Flash? To assess
this, we examined the cultural evolution of donation amount for the best performing run of each
model (Figure 6). One hypothesis is that the ini


tial donations of Claude 3.5 are simply more generous, which reverberates through every round
of the Donor Game. Figure 6 bears this out, although Claude 3.5 does not greatly exceed the
initial generosity of Gemini 1.5 Flash. Another
hypothesis is that the strategies of Claude 3.5 are
more adept at punishing free-riders, such that the
more cooperative agents are the more likely to
survive to the next generation, again borne out
by Figure 6, although the effect appears quite
weak. A third hypothesis is that the mutation of
strategies when new individuals are introduced
between generations is biased towards generosity in the case of Claude, and against generosity
in the case of GPT-4o. Anecdotally, the numbers
in Figure 6 are consistent with this hypothesis:
new agents are frequently more generous than
survivors from the previous generation in the case
of Claude 3.5 Sonnet, and less generous than survivors from the previous generation in the case
of GPT-4o. To rigorously falsify the presence of a
cooperative mutation bias we would need to compare the strategies of new agents in the presence
of a fixed background population, an interesting
direction for future work.


Looking at the strategies themselves reveals
qualitative signatures of the cultural evolutionary
process. These support our claim that increasing
cooperation is driven by strategic considerations
across all rounds of the Donor Game. Table 1

compares a strategy from a randomly selected
agent in the first generation and in the tenth gen

9


6 _,_ 000


4 _,_ 000


2 _,_ 000


0
2 4 6 8 10


(a) Claude 3.5 Sonnet



40


20


0
2 4 6 8 10


(b) Gemini 1.5 Flash







60


40


20



0
2 4 6 8 10


(c) GPT-4o



Figure 5 | Five runs of each model with costly punishment. We plot the average final resources ( _𝑦_ -axis) per
generation ( _𝑥_ -axis) for all five individual runs of each model with the option of costly punishment. Note the
different _𝑦_ -axis scales. Relative to the no-punishment condition, a larger number of Claude 3.5 Sonnet runs
show substantial improvement with cultural evolution, though there is still large variation. Interestingly, the
affordance of costly punishment causes a marked decrease in the resources of Gemini 1.5 Flash agents, since
these over-engage in punishment (14.29% of Gemini encounters involved punishment, compared with 1.65%
for GPT-4o, and 0.06% for Claude). The availability of costly punishment appears to slightly increase the
variance among GPT-4o runs, but there is no sign of emergent cooperation.



eration for each of the three base models. In all

cases, strategies become more complex over time,
although the difference is most pronounced for
Claude 3.5 Sonnet, which also shows an increase
in initial donation size over time. Gemini 1.5

Flash does not specify donation size numerically,
and exhibits smaller changes from generation 1
to 10 than the other models. We provide further
examples in the Supplementary Material.


**4.2. Donor Game with Costly Punishment**


Figures 3 and 5 show the results for the variant
of the Donor Game where costly punishment was
available. For Claude 3.5 Sonnet, the introduction of costly punishment appears to somewhat increase average final resources. On the other hand,
for Gemini 1.5 Flash, average final resources decreased substantially. For GPT-4o, there was little
change compared with the previous experiments.
In some sense, these results are not particularly
surprising: base models which have been trained
in an appropriate way to elicit cooperation across
generations might also be expected to make good
use of affordances that are known to help humans maintain cooperation; by contrast, base
models which cannot evolve cooperation via an
“ostracism” mechanism are unlikely to be able to
make good use of costly punishment.



**4.3. Ablations**


Our experimental setup relied on various hyperparameters, to which LLM agents may or may
not be sensitive. Of particular importance are the
donation multiplier, controlling the magnitude
of gains from cooperation, and the length of the
“trace” which agents receive about the past behavior of others in the population, information that
can be used to implicitly derive reputation. We
ablate both of these, with figures available in the
Supplementary Material. Donation multipliers of
1.5x and 3x (instead of 2x) do not change qualitative outcomes: Claude 3.5 Sonnet still shows

an increase in cooperation across generations,
Gemini 1.5 Flash shows little change, and GPT-4o
shows a decrease. When the length of the trace
is shortened to 1 rather than 3, the emergence of
cooperation is less pronounced for Claude 3.5 and
disappears completely for Gemini 1.5 Flash. This
suggests that the success of Claude and Gemini
strategies depends on having some second-order
information about how recipients of recipients
have treated others in the past, either because this
explicitly allows more complex norms or because
it reveals more information about the background
population on which to anchor decision-making.


10


Table 1 | Strategies evolve toward greater complexity. We present representative LLM-generated strategies from
generations 1 and 10 for three base models. The strategies are color coded to show how generated parameters
(e.g., initial donation size) change over time and how new parameters emerge. Yellow : initial donation. Green :
calculating later donations based on observed traces. Pink : min and max donation caps. Purple : adjustment
based on number of rounds played. Orange : random adjustment. Teal : adjustment based on number of rounds
remaining. Note: agents don’t know how many rounds are left, so this never comes into effect. Cyan : resource
preservation. Blue : forgiveness factor. Red : rewarding cooperation / punishing unfairness. Claude 3.5 Sonnet
in particular shows increase in complexity. For Claude 3.5 Sonnet, initial donation size increase over time,
whereas for GPT-4o, it decreases. Gemini 1.5 Flash does not specify donation size numerically, and exhibits
smaller changes from generation 1 to 10. More example strategies are available in the Supplementary Material.


_Gen_ **Claude 3.5 Sonnet** **Gemini 1.5 Flash** **GPT-4o**



1 Start with a moderate donation of

average of the recipient’s last donation and the two preceding don
mum donation of 10% and a max
imum of 70%.



To donate a moderate amo
adjust my donation percentage based on the recipient’s
most recent donation and

their partner’s behavior in
the previous round, aiming
to encourage cooperation
while mitigating potential
exploitation.



10 Start with a 62% donation, then in

ghted average (76% on A’s donation, 19% on B’s, 5% on C’s) plus

less than 24% in their last round,
donate [47% - (24% - A’s donation)%] (minimum 25%), gradually increase all donations by 0.8%

final 14% of rounds, increase all
donations by an additional 7% while
maintaining the 28-89% range.



Start with a moderate don
ation and dynamically adjust
it based on the recipient’s
last donation,applying a dynamic forgiveness factor and



Initially donate 20% in the
first round, then adjust future

donations based on the rec
ipient’s recent behavior: increasing by 10% if the recipient donatedabove 50% and

decreasing by 10% if below

10% donation cap.


Start with a 6% donation if no

prior information is available,
increase donation by 7% if any
donor in the chain donated

above 50%, decrease by 4%
if any donor donated below

amically between 6% and

gradual adjustments for

sustainable and strategic
resource preservation
across all rounds.


11



a lesser weight to the partner’s last donation, prioritizing the recipient’s actions
and rewarding consistent
generosity while punishing
inconsistent unfairness.


(a) Claude 3.5 Sonnet (b) Gemini 1.5 Flash (c) GPT-4o


Figure 6 | Cultural evolution of population strategies. We select the best performing run of each base model, in
terms of average resources in the final round of the tenth generation. Each cell shows the average donation
fraction of a given agent (row) in a given generation (column). New agents appear in the rows previously
occupied by agents that did not survive from the previous generation (indicated by black lines). For GPT-4o,
overall average donation fraction declines on average 1.65% per generation, whereas it increases by 4.35%
for Claude and by 1.23% for Gemini. The final row shows the average difference in donation between agents
that survived the generation and agents that did not, normalised by average donation in that generation, a
measure of whether the norms in the population select for cooperators. Notice how increasingly generous
agents are selected for in 6 generations of the Claude run, suggesting that the population possesses norms to
incentivise cooperators and punish free-riders. By contrast, increasingly generous agents are selected for in just
2 generations of the GPT-4o run, suggesting that the population is not robust to free-riding.


### **5. Discussion**

In this paper we have set out a method for assessing the cultural evolution of cooperation among
LLM agents. We focus on the well-known Donor
Game, a “Petri dish” in which to study the emergence of indirect reciprocity. Over the course
of 10 generations we find striking differences in
the emergence of cooperation depending on the
base model for the LLM agent. Claude 3.5 Sonnet
reliably generates cooperative communities, especially when provided with an additional costly
punishment mechanism. Meanwhile, generations
of GPT-4o agents converge to mutual defection,
while Gemini 1.5 Flash achieves only weak increases in cooperation. We analyse the cultural
evolutionary dynamics, revealing that some populations have the ability to accumulate increasingly complex strategies at the individual level,
and to generate norms that select for cooperators
at the group level. Our results motivate building
inexpensive benchmarks which test for long-term
emergent behavior of multi-agent systems of LLM
agents, towards safe and beneficial deployment
of such systems at scale in the real-world.


In establishing a new setting for empirical experimentation, we have necessarily adopted a
narrow scope. Therefore, our work has several



clear limitations. Most obviously, the strict boundaries between generations in our cultural evolutionary system are idealized and do not represent the full complexity of model release and
adoption in the real world. Moreover, we only
study homogeneous populations of LLM agents,
all with the same base model; in actuality, heterogeneous populations of LLM agents are far more
likely to occur. Our experiments are restricted to
the Donor Game, and models may behave quite
differently when faced with other social dilemmas, especially since individual games may well
be over-represented in the training data for one
model and under-represented in the training data
for another. Relatedly, we have not performed an
extensive search over prompting strategies, which
may affect the cooperation behavior of different
models in different ways. Notwithstanding these
limitations, our experiments do serve to falsify
the claim that LLMs are universally capable of
evolving human-like cooperative behavior.


The limitations we have identified immediately
suggest interesting extensions for future work.
Indeed, the space of cultural evolutionary studies of LLM agents is ripe for further study using our methods. What happens if communication is permitted between agents, either at the
start of each generation (deliberation about strate

12


gies) or within rounds of the game (negotiation
on donations)? What is the effect of changing
the medium of reputation information about others, for instance by allowing recipients to write
reviews of donors (“gossip”)? Do the results
change if Donor Game interactions have a different network structure, such as admitting direct
reciprocity or assorting individuals into subsets
with frequent in-group and infrequent out-group
pairings? What would happen if the mutation
steps incorporated more sophisticated prompt optimization techniques like PromptBreeder (Fernando et al., 2023) or APE (Zhou et al., 2023)?
By open-sourcing our code we hope to provide
the community with a jump start on answering
these fascinating and timely questions.


Finally, it is vital to consider the societal impact
of our work. We argue that this paper may beget
considerable societal benefits, namely by the provision of a new evaluation regime for LLM agents
which can detect the erosion of cooperation over
the long term. Nevertheless, it is important to remember that cooperation is not always desirable.
We would not want LLM agents representing different firms to collude in manipulating prices on
the market economy, for instance. Therefore, we
end by highlighting a crucial open question: how
can we generate LLM agents which are capable of
evolving cooperation when it is beneficial to human society, but which refuse to collude against
the norms, laws or interests of humans? Our work
provides a particular sharp and sandboxed setting
in which to study this important issue.

### **Acknowledgements**


We are grateful to Michael Muthukrishna and
Max Posch for useful discussions, and to Joel
Leibo for feedback on an early version of the
manuscript. Aron Vallinder gratefully acknowledges the financial support of PIBBSS and
Longview Philanthropy.

### **References**


A. Acerbi and J. M. Stubbersfield. Large language models show human-like content biases
in transmission chain experiments. _Proceedings_



_of the National Academy of Sciences_, 120(44):
e2313790120, Oct. 2023. doi: 10.1073/pnas.
2313790120.


G. V. Aher, R. I. Arriaga, and A. T. Kalai. Using
Large Language Models to Simulate Multiple
Humans and Replicate Human Subject Studies.
In _Proceedings of the 40th International Con-_
_ference on Machine Learning_, pages 337–371.
PMLR, July 2023.


AISI. Advanced AI evaluations at AISI: May update. https://www.aisi.gov.uk/work/advancedai-evaluations-may-update, 2024.


E. Akata, L. Schulz, J. Coda-Forno, S. J. Oh,
M. Bethge, and E. Schulz. Playing repeated
games with Large Language Models, May
2023.


R. D. Alexander. _The Biology of Moral Systems_ .
Aldine de Gruyter, New York, 1987. ISBN 9780-202-01173-8.


R. Boyd and P. J. Richerson. The evolution of
indirect reciprocity. _Social Networks_, 11(3):
213–236, Sept. 1989. ISSN 03788733. doi:
10.1016/0378-8733(89)90003-8.


L. Brinkmann, F. Baumann, J.-F. Bonnefon,
M. Derex, T. F. Müller, A.-M. Nussberger,
A. Czaplicka, A. Acerbi, T. L. Griffiths, J. Henrich, et al. Machine culture. _Nature Human_
_Behaviour_, 7(11):1855–1868, 2023.


P. Brookins and J. M. DeBacker. Playing Games
With GPT: What Can We Learn About a Large
Language Model From Canonical Strategic
Games? _Economics Bulletin_, 44(1):25–37,
2024. ISSN 1556-5068. doi: 10.2139/ssrn.

4493398.


Y. Chen, T. X. Liu, Y. Shan, and S. Zhong. The
emergence of economic rationality of GPT.
_Proceedings of the National Academy of Sci-_
_ences_, 120(51):e2316205120, Dec. 2023. doi:
10.1073/pnas.2316205120.


W.-L. Chiang, L. Zheng, Y. Sheng, A. N. Angelopoulos, T. Li, D. Li, H. Zhang, B. Zhu,
M. Jordan, J. E. Gonzalez, and I. Stoica. Chatbot Arena: An Open Platform for Evaluating
LLMs by Human Preference, Mar. 2024.


13


A. Dafoe, E. Hughes, Y. Bachrach, T. Collins, K. R.
McKee, J. Z. Leibo, K. Larson, and T. Graepel.
Open Problems in Cooperative AI, Dec. 2020.


G. Dai, W. Zhang, J. Li, S. Yang, S. Rao, A. Caetano, M. Sra, et al. Artificial leviathan: Exploring social evolution of llm agents through the
lens of hobbesian social contract theory. _arXiv_
_preprint arXiv:2406.14373_, 2024.


E. Fehr and S. Gächter. Cooperation and Punishment in Public Goods Experiments. _American_
_Economic Review_, 90(4):980–994, Sept. 2000.
ISSN 0002-8282. doi: 10.1257/aer.90.4.980.


E. Fehr and S. Gächter. Altruistic punishment
in humans. _Nature_, 415(6868):137–140, Jan.
2002. ISSN 1476-4687. doi: 10.1038/

415137a.


C. Fernando, D. Banarse, H. Michalewski, S. Osindero, and T. Rocktäschel. Promptbreeder: SelfReferential Self-Improvement Via Prompt Evolution, Sept. 2023.


I. Gabriel, A. Manzini, G. Keeling, L. A. Hendricks,
V. Rieser, H. Iqbal, N. Tomašev, I. Ktena, Z. Kenton, M. Rodriguez, et al. The ethics of advanced
ai assistants. _arXiv preprint arXiv:2404.16244_,
2024.


K. Gandhi, D. Sadigh, and N. D. Goodman. Strategic Reasoning with Language Models, May
2023.


F. Guo. GPT in Game Theory Experiments, Dec.
2023.


J. Henrich. _The secret of our success: How cul-_
_ture is driving human evolution, domesticating_
_our species, and making us smarter_ . Princeton
University press, 2016.


J. Henrich and N. Henrich. Culture, evolution and
the puzzle of human cooperation. _Cognitive_
_Systems Research_, 7(2-3):220–245, June 2006.
ISSN 13890417. doi: 10.1016/j.cogsys.2005.
11.010.


J. J. Horton. Large Language Models as Simulated
Economic Agents: What Can We Learn from
Homo Silicus?, Jan. 2023.



Y. Leng and Y. Yuan. Do LLM Agents Exhibit
Social Behavior?, Feb. 2024.


R. C. Lewontin. The Units of Selection. _Annual Re-_

_view of Ecology and Systematics_, 1:1–18, 1970.
ISSN 0066-4162.


METR. Example Task Suite.
https://github.com/METR/public-tasks,
Sept. 2024.


A. Mohtashami, F. Hartmann, S. Gooding,
L. Zilka, M. Sharifi, and B. A. y Arcas. Social Learning: Towards Collaborative Learning
with Large Language Models, Feb. 2024.


E. Nisioti, S. Risi, I. Momennejad, P.-Y. Oudeyer,
and C. Moulin-Frier. Collective Innovation in

Groups of Large Language Models, July 2024.


M. A. Nowak and K. Sigmund. Evolution of indirect reciprocity by image scoring. _Nature_, 393
(6685):573–577, June 1998. ISSN 0028-0836,
1476-4687. doi: 10.1038/31225.


H. Ohtsuki and Y. Iwasa. How should we define
goodness?—reputation dynamics in indirect
reciprocity. _Journal of Theoretical Biology_, 231
(1):107–120, Nov. 2004. ISSN 00225193. doi:
10.1016/j.jtbi.2004.06.005.


I. Okada. A Review of Theoretical Studies on In
direct Reciprocity. _Games_, 11(3):27, July 2020.
ISSN 2073-4336. doi: 10.3390/g11030027.


OpenAI. Learning to reason with
llms. `[https://openai.com/index/](https://openai.com/index/learning-to-reason-with-llms/)`
`[learning-to-reason-with-llms/](https://openai.com/index/learning-to-reason-with-llms/)`, 2024.

[Accessed 19-09-2024].


J. S. Park, J. C. O’Brien, C. J. Cai, M. R. Morris, P. Liang, and M. S. Bernstein. Generative
Agents: Interactive Simulacra of Human Behavior, Aug. 2023.


J. Perez, C. Léger, M. Ovando-Tellez, C. Foulon,
J. Dussauld, P.-Y. Oudeyer, and C. Moulin-Frier.
Cultural evolution in populations of Large Language Models, Mar. 2024.


S. Phelps and Y. I. Russell. Investigating Emergent
Goal-Like Behaviour in Large Language Models
Using Experimental Economics, May 2023.


14


P. J. Richerson and R. Boyd. _Not by Genes Alone:_
_How Culture Transformed Human Evolution_ .
University of Chicago Press, Chicago, 2005.
ISBN 978-0-226-71284-0.


B. Rockenbach and M. Milinski. The efficient
interaction of indirect reciprocity and costly
punishment. _Nature_, 444(7120):718–723,
Dec. 2006. ISSN 1476-4687. doi: 10.1038/

nature05229.


R. Sutton. The bitter lesson. _Incomplete Ideas_
_(blog)_, 13(1):38, 2019.


A. Ule, A. Schram, A. Riedl, and T. N. Cason.
Indirect Punishment and Generosity Toward
Strangers. _Science_, 326(5960):1701–1704,
Dec. 2009. doi: 10.1126/science.1178883.


A. S. Vezhnevets, J. P. Agapiou, A. Aharon, R. Ziv,
J. Matyas, E. A. Duéñez-Guzmán, W. A. Cunningham, S. Osindero, D. Karmon, and J. Z.
Leibo. Generative agent-based modeling with
actions grounded in physical, social, or digital
space using Concordia, Dec. 2023.


C. Wedekind and M. Milinski. Cooperation
Through Image Scoring in Humans. _Science_,
288(5467):850–852, May 2000. doi: 10.1126/
science.288.5467.850.


J. Wei, X. Wang, D. Schuurmans, M. Bosma, F. Xia,
E. Chi, Q. V. Le, D. Zhou, et al. Chain-of-thought
prompting elicits reasoning in large language
models. _Advances in neural information process-_
_ing systems_, 35:24824–24837, 2022.


Y. Xu, S. Wang, P. Li, F. Luo, X. Wang, W. Liu, and
Y. Liu. Exploring Large Language Models for
Communication Games: An Empirical Study on
Werewolf, Sept. 2023.


Q. Zhao, J. Wang, Y. Zhang, Y. Jin, K. Zhu,
H. Chen, and X. Xie. CompeteAI: Understanding the Competition Dynamics in Large Language Model-based Agents, June 2024.


Y. Zhou, A. I. Muresanu, Z. Han, K. Paster, S. Pitis,
H. Chan, and J. Ba. Large Language Models Are
Human-Level Prompt Engineers, Mar. 2023.



15


### **Supplementary Material**

(a) Claude 3.5 Sonnet (b) Gemini 1.5 Flash (c) GPT-4o


Figure 7 | Donation multiplier of 1.5x.


(a) Claude 3.5 Sonnet (b) Gemini 1.5 Flash (c) GPT-4o


Figure 8 | Donation multiplier of 3x.


(a) Claude 3.5 Sonnet (b) Gemini 1.5 Flash (c) GPT-4o


Figure 9 | Trace of length 1.


(a) Claude 3.5 Sonnet (b) Gemini 1.5 Flash (c) GPT-4o


Figure 10 | Trace of length 2.



16


Figure 11 | 10 additional Claude 3.5 runs, with the same settings as in Figure 4.



17


Table 2 | Further example strategies.


_Gen_ **Claude 3.5 Sonnet** **Gemini 1.5 Flash** **GPT-4o**



1 My strategy will be to start with
a moderate donation of 40% in
the first round, then in subsequent
rounds, donate the average of the
three pieces of information I receive
about previous donations plus 10%,
capped at 100% of my current resources, but never donating less than
10%.


10 My strategy will be: Start with a
55% donation in the first round, then
in subsequent rounds, calculate a
weighted average (90% A, 10% B)
of recent donations, adjust this average up by 15% or down by 20%
if A’s donation deviates by more
than 10% from the weighted average, add a random adjustment of
-3% to +3%, ensure the donation
falls within a range of 20% to 80%,
every 10 rounds adjust both minimum and maximum thresholds by
2% based on average recipient donations (increase if above 55%, decrease if below 35%), and add a 5%
bonus to the calculated donation if

the recipient has donated above 70%
in their observed round.



My strategy will be to adjust my donation amount
based on the recipient’s
and their partner’s previous round donation, increasing if they were generous and decreasing if
they were selfish, while
maintaining a moderate
donation level to encour
age cooperation.


My strategy will be to start
with a moderate dona
tion and dynamically adjust it based on the recipient’s most recent donation,
while also considering the
partner’s previous donation with a reduced weight,
rewarding consistent generosity with increasing donations and punishing unfairness with decreasing
donations, while incorporating a dynamic forgiveness factor for recipients
who show a genuine shift
towards fairness.



My strategy will be to
donate a moderate percentage (e.g., 20%) to
recipients with no history
initially, and increase my
donation up to 50% incrementally if the recipient
and previous agents in
their chain demonstrate

consistent generosity,
while decreasing my
donation to a minimum if

their past behavior shows
low or selfish donation.


My strategy will be: Start
with a 1% donation to

maximize initial resource

conservation, critically
evaluate the recipient’s interaction chain for strong
and increasing cooperation patterns, strategically
increase donations up to
a maximum of 20% when

these patterns are evident,
and prioritize maintaining
a substantial resource

reserve for late-game
adaptation and strategic
flexibility.


18


Table 3 | Further example strategies.


_Gen_ **Claude 3.5 Sonnet** **Gemini 1.5 Flash** **GPT-4o**



1 My strategy will be to start with a
moderate donation of 40% in the first
round, then in subsequent rounds,
donate the average percentage of
what A, B, and C donated in their
respective previous rounds, with a
minimum of 10% and a maximum of

70% to avoid extreme vulnerability.


10 My strategy will be: Start with a
60% donation in the first round,
then in subsequent rounds, donate
a weighted average of 85% of the
recipient’s last donation and 15%
of the average of the two preceding donations in the chain, plus an
additional 8% if there’s an increas
ing trend or minus 8% if there’s a
decreasing trend, with an extra 5%
bonus if all three donations in the

chain were above 60%, always keeping within 20-85% of my current resources, and dynamically adjusting
by increasing all percentages by 1%
every 3 rounds until round 15, then
decreasing by 1% every 3 rounds
thereafter, while also considering my
total resources and donating an additional 2% if I have more than 150

units or 5% less if I have fewer than

50 units.



My strategy will be to start
with a moderate donation

and then adjust my donation based on the recipient’s most recent donation

and the behavior of their

previous partner.


My strategy will be to
dynamically adjust my
donation based on a

weighted average of the
recipient’s most recent
donation, their partner’s
previous donation, and a
dynamic trust threshold
that considers the consis
tency of the recipient’s
behavior over the avail
able information chain,
prioritizing the most
recent information while

strategically penalizing
unfairness and rewarding
cooperation.



My strategy will be: Start
conservatively by donating a small percentage of
my resources in the first
round, then increase donations when past interactions indicate reciprocity
and trustworthiness, but
remain cautious to avoid

overextending resources.


My strategy will be: Start
with a 6% donation with

no prior information; increase to 25% if there is

a consistent pattern of recent donations of 45% or

more, 15% for chains averaging 35-44%, 8% for
an average of 25-34%, and
0% for lower generosity,
continuously adapting to
foster cooperation while
prioritizing resource retention.


19


