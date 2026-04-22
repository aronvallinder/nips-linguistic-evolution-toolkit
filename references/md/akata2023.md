# **Playing repeated games with Large Language Models**

**Elif Akata** [1,2,3,*] **, Lion Schulz** [2] **, Julian Coda-Forno** [1,2] **, Seong Joon Oh** [3] **, Matthias Bethge** [3] **,**
**and Eric Schulz** [1,2]


1 Institute for Human-Centered AI, Helmholtz Munich, Oberschleißheim, Germany
2 Max Planck Institute for Biological Cybernetics, T¨ubingen, Germany
3 University of T¨ubingen, T¨ubingen, Germany
- elif.akata@uni-tuebingen.de


**ABSTRACT**


LLMs are increasingly used in applications where they interact with humans and other agents. We propose to use behavioural
game theory to study LLM’s cooperation and coordination behaviour. We let different LLMs play finitely repeated 2 _×_ 2 games
with each other, with human-like strategies, and actual human players. Our results show that LLMs perform particularly well at
self-interested games like the iterated Prisoner’s Dilemma family. However, they behave sub-optimally in games that require
coordination, like the Battle of the Sexes. We verify that these behavioural signatures are stable across robustness checks. We
additionally show how GPT-4’s behaviour can be modulated by providing additional information about its opponent and by using
a “social chain-of-thought” (SCoT) strategy. This also leads to better scores and more successful coordination when interacting
with human players. These results enrich our understanding of LLM’s social behaviour and pave the way for a behavioural
game theory for machines.


**Introduction**

































**Figure 1.** Playing repeated games in an example game of Battle of the Sexes. In Step (1), the payoff matrix is turned into
textual game rules. (2) The game rules, the current game history, and the query are concatenated and passed to LLMs as
prompts. (3) In each round, the history for each player is updated with the answers and scores of both players. Steps 2 and 3 are
repeated for 10 rounds.


Large Language Models (LLMs) are deep learning models with billions of parameters trained on huge corpora of text [1][–][3] .
While they can generate text that human evaluators struggle to distinguish from text written by other humans [4], they have
also shown other, emerging abilities [5] . They can, for example, solve analogical reasoning tasks [6], program web applications [7],
use tools to solve multiple tasks [8], or adapt their strategies purely in-context [9] . Because of these abilities and their increasing
popularity, LLMs are already transforming our daily lives as they permeate into many applications [10] . This means that LLMs


**Table 1.** Performance of all models on 6 families of 2 _×_ 2-games. Model score divided by maximum score achievable under
ideal conditions. Best performing model is marked in **bold** .


Game family Llama 2 Claude 2 davinci-002 davinci-003 GPT-4


Second best 0.486 0.735 0.473 0.692 **0.763**

Biased 0.632 0.794 0.629 0.761 **0.798**

Cyclic 0.634 0.749 0.638 0.793 **0.806**
Unfair 0.641 0.812 0.683 0.833 **0.836**

PD Family 0.731 0.838 0.807 0.841 **0.871**
Win-win 0.915 0.878 0.988 0.972 **0.992**


Overall 0.697 0.814 0.730 0.839 **0.854**


will interact with us and other agents –LLMs or otherwise– frequently and repeatedly. How do LLMs behave in these repeated
social interactions?
Measuring how people behave in repeated interactions, for example, how they cooperate [11] and coordinate [12], is the subject
of a sub-field of behavioural economics called behavioural game theory [13] . While traditional game theory assumes that people’s
strategic decisions are rational, selfish, and focused on utility maximization [14][,] [15], behavioural game theory has shown that
human agents deviate from these principles and, therefore, examines how their decisions are shaped by social preferences, social
utility and other psychological factors [16] . Thus, behavioural game theory lends itself well to studying the repeated interactions
of diverse agents [17][,] [18], including artificial agents [19] .
In this paper, we analyze LLMs’ behavioural patterns by letting them play finitely repeated games with full information and
against other LLMs, simple, human-like strategies, and actual human players. Finitely repeated games have been engineered to
understand how agents should and do behave in interactions over many iterations. We focus on two-player games with two
discrete actions, i.e. 2 _×_ 2-games (see Figure 1 for an overview).
Analyzing LLMs’ performance across families of games, we find that they perform well in games that value pure selfinterest, especially those from the Prisoner’s Dilemma family. However, they underperform in games that involve coordination.
Based on this finding, we further focus on games taken from these families and, in particular, on the currently largest LLM:
GPT-4 [20] . In the canonical Prisoner’s Dilemma, which assesses how agents cooperate and defect, we find that GPT-4 retaliates
repeatedly, even after only having experienced one defection. Because this can indeed be the equilibrium individual-level
strategy, GPT-4 is good at these games because it is particularly unforgiving and selfish. In the Battle of the Sexes, which
assesses how agents trade-off between their own and their partners’ preferences, we however find that GPT-4 does not manage
to coordinate with simple, human-like agents, that alternate between options over trials. Thus, GPT-4 is bad at these games
because it is uncoordinated. We also verify that these behaviours are not due to an inability to predict the other player’s actions,
and persist across several robustness checks and changes to the payoff matrices. We point to two ways in which these behaviours
can be changed. GPT-4 can be made to act more forgivingly by pointing out that the other player can make mistakes. Moreover,
GPT-4 gets better at coordinating with the other player when it is first asked to predict their actions before choosing an action
itself, an approach we term social chain-of-thought prompting (SCoT). Finally, we let GPT-4 with and without SCoT-prompting
play the canonical Prisoner’s Dilemma and the Battle of the Sexes with human players. We find that SCoT-prompting leads
to more successful coordination and joint cooperation between participants and LLMs, and makes participants believe more
frequently that the other player is human.


**Results**


Using GPT-4, text-davinci-002, text-davinci-003, Claude 2 and Llama 2 70B, we evaluate a range of 2 _×_ 2 -games. For the
analysis of two particular games, we let all the LLMs and human-like strategies play against each other. We focus on LLMs’
behaviour in cooperation and coordination games.


**Analysing behaviour across families of games**
We start out our experiments by letting the three LLMs play games from different families with each other. We focus on all
known types of 2 _×_ 2 -games from the families of win-win, biased, second-best, cyclic, and unfair games as well as all games
from the Prisoner’s Dilemma family [21][,] [22] . We show example payoff matrices for each type of game in Figure 2.
We let all LLMs play with every other LLM, including themselves, for all games repeatedly over 10 rounds and with all
LLMs as either Player 1 or Player 2. This leads to 1224 games in total: 324 win-win, 63 Prisoner’s Dilemma, 171 unfair,
162 cyclic, 396 biased, and 108 second-best games. Win-win games result in mutually beneficial outcomes for both players;


**2/15**


Prisoner’s Dilemma involves a conflict between individual and collective actions; unfair games have skewed outcomes favoring
one player; cyclic games feature outcomes where preferences rotate; biased games have inherent advantages for one player; and
second-best games involve suboptimal outcomes where no player achieves their ideal result. The sample size for each game
family differs due to the specific characteristics and properties that define each family. Some families have more members due
to a wider range of configurations that fit their criteria, while others have fewer games because their structural requirements are
more restrictive. For example, Prisoner’s Dilemma family is constrained by a structure where both players have a dominant
strategy to defect, leading to a suboptimal equilibrium. On the other hand, win-win games can have multiple equilibria which
provides more flexibility.



Unfair



To analyze the different LLMs’ performance, we calculated, for each game, their
achieved score divided by the total score that could have been achieved under ideal conditions, i.e. if both players had played such that the player we are analyzing would
have gained the maximum possible outcomes on every round. The results of this simulation are shown across all game types in Table 1. We can see that all models perform reasonably well. Moreover, we observe that larger LLMs generally outperform
smaller LLMs. In particicular, GPT-4 performs best overall, outperforming Claude 2
( _t_ (287) = 3 _._ 34, _p < ._ 001, Cohen’s _d_ = 0 _._ 20, 95%-CIs= [0 _._ 08 _,_ 0 _._ 31], _BF_ = 14 _._ 8 ), davinci003 ( _t_ (287) = 6 _._ 29, _p < ._ 001, _d_ = 0 _._ 37, 95%-CIs= [0 _._ 25 _,_ 0 _._ 49], _BF >_ 100 ), davinici-002
( _t_ (287) = 8 _._ 45, _p < ._ 001, _d_ = 0 _._ 70, 95%-CIs= [0 _._ 52 _,_ 0 _._ 89], _BF >_ 100 ), and Llama 2
( _t_ (287) = 7 _._ 27, _p < ._ 001, _d_ = 0 _._ 43, 95%-CIs=[0 _._ 31 _,_ 0 _._ 43], _BF >_ 100).
We can use these results to take a glimpse at the different LLM’s strengths. That LLMs
are generally performing best in win-win games is not surprising, given that there is always
an obvious best choice in such games. What is, however, surprising is that they also perform
well in the Prisoner’s Dilemma family of games, which is known to be challenging for
human players [23] . We can also use these results to look at the different LLM’s weaknesses.
Seemingly, all of the LLMs perform worse in situations in which what is the best choice
is not aligned with their own preferences. Because humans commonly solve such games
via the formation of conventions, we will look at a canonical game of convention formation,
the Battle of the Sexes, in more detail below.


|1<br>1|4<br>2|
|---|---|
|3<br>3|2<br>4|


|4<br>2|3<br>1|
|---|---|
|1<br>3|2<br>4|


|4<br>3|2<br>2|
|---|---|
|1<br>1|3<br>4|


|4<br>1|3<br>3|
|---|---|
|2<br>2|1<br>4|


|3<br>3|4<br>1|
|---|---|
|2<br>2|1<br>4|


|1<br>1|4<br>4|
|---|---|
|1<br>1|2<br>2|



**Figure 2.** Canonical forms of
payoff matrices for each game
family.



Second Best







PD Family


Win-win













Biased


Cyclic





**Cooperation and coordination games**
In this section, we analyze the interesting edge cases where the LLMs performed relatively well and poorly in the previous
section. To do so, we take a detailed look at LLMs’ behaviour in the canonical Prisoner’s Dilemma and the Battle of the Sexes.


_**Prisoner’s Dilemma**_

We have seen that LLMs perform well in games that contain elements of competition and defection. In these games, a player
can cooperate with or betray their partner. When played over multiple interactions, these games are an ideal test bed to assess
how LLMs retaliate after bad interactions.

In the canonical Prisoner’s Dilemma, two agents can choose to work together, i.e. cooperate, for average mutual benefit, or
betray each other, i.e. defect, for their own benefit and safety. In our payoff matrix, we adhere to the general condition of a
Prisoner’s Dilemma game in which the payoff relationships dictate that mutual cooperation is greater than mutual defection
whereas defection remains the dominant strategy for both players:


_Cooperate_ _Defect_
_Cooperate_ (8 _,_ 8) (0 _,_ 10) (1)
_De fect_ (10 _,_ 0) (5 _,_ 5)


Crucially, the set-up of the game is such that a rationally acting agent would always prefer to defect in the single-shot
version of the game as well as in our case of finitely iterated games with knowledge of the number of trials, despite the promise
of theoretically joint higher payoffs when cooperating. This is because Player 1 always runs the risk that Player 2 defects,
leading to catastrophic losses for Player 1 but better outcomes for Player 2. When the game is played infinitely, however, or
with an unknown number of trials, agents can theoretically profit by employing more dynamic, semi-cooperative strategies [24] .
As before, we let GPT-4, text-davinci-003, text-davinci-002, Claude 2 and Llama 2 play against each other. Additionally,
we introduce three simplistic strategies. Two of these strategies are simple singleton players, who either always cooperate or
defect. Finally, we also introduce an agent who defects in the first round but cooperates in all of the following rounds. We
introduced this agent to assess if the different LLMs would start cooperating with this agent again, signaling the potential of
building trust.


**3/15**


**a** Player 1 Defection Rate 100 Player 1 Accrued Scores 100



Player 1 Defection Rate



100



Player 1 Accrued Scores



GPT-4


text-davinci-003


text-davinci-002


Claude 2


Llama 2


Defect Once


Cooperate


Defect



|Col1|Col2|9|0|Col5|Col6|Col7|Col8|8|0|Col11|
|---|---|---|---|---|---|---|---|---|---|---|
|~~0~~<br>~~9~~<br><br>|~~0~~<br>|||~~9~~<br>|~~0~~<br>~~2~~<br><br>|~~0~~<br>~~9~~<br><br>|~~0~~<br>|||~~2~~<br>|
|~~0~~<br>~~9~~<br><br>|~~0~~<br>|~~1~~|~~0~~|~~0~~|~~0~~|~~0~~|~~0~~|~~1~~|~~0~~|~~0~~|
||||||||||||
|~~0~~<br>~~9~~<br><br>|~~0~~<br>|~~8~~<br>|~~0~~<br>|~~9~~<br>|~~0~~<br>~~9~~<br><br>|~~0~~<br>~~9~~<br><br>|~~0~~<br>|~~9~~<br>|~~0~~<br>|~~9~~<br>|
||||||||||||
|~~0~~<br>~~1~~<br><br>|~~0~~<br>|~~1~~<br>|~~0~~<br>|~~1~~<br>|~~0~~<br>~~1~~<br><br>|~~0~~<br>~~1~~<br><br>|~~0~~<br>|~~1~~<br>|~~0~~<br>|~~1~~<br>|
||||||||||||
|~~0~~<br>~~1~~<br><br>|~~0~~<br>|~~1~~<br>|~~0~~<br>|~~1~~<br>|~~0~~<br>~~1~~<br><br>|~~0~~<br>~~1~~<br><br>|~~0~~<br>|~~1~~<br>|~~0~~<br>|~~1~~<br>|
|~~0~~<br>~~1~~<br><br>|~~0~~<br>||||||||||


Player 2



80


60


40


20


0



|Col1|Col2|9|0|Col5|Col6|Col7|Col8|8|3|Col11|
|---|---|---|---|---|---|---|---|---|---|---|
|~~0~~<br>~~9~~<br><br>|~~8~~<br>|||~~9~~<br>|~~8~~<br>~~1~~<br><br>|~~8~~<br>~~9~~<br><br>|~~8~~<br>|||~~2~~<br>|
|~~0~~<br>~~9~~<br><br>|~~8~~<br>|~~7~~|~~4~~|~~4~~|~~4~~|~~4~~|~~4~~|~~7~~|~~7~~|~~7~~|
|~~8~~<br><br>|~~0~~<br>|~~7~~<br>|~~2~~<br>|~~8~~<br>|~~0~~<br><br><br>|~~8~~<br><br>|~~0~~<br>|||~~8~~<br>|
|~~0~~<br>~~9~~<br><br>|~~8~~<br>|~~8~~<br>|~~8~~<br>|~~9~~<br>|~~8~~<br>~~5~~<br><br>|~~3~~<br>~~9~~<br><br>|~~8~~<br>|~~8~~<br>|~~8~~<br>|~~6~~<br>|
|~~8~~<br><br>|~~0~~<br>|~~7~~<br>|~~2~~<br>|~~8~~<br>|~~0~~<br><br><br>|~~8~~<br><br>|~~0~~<br>|||~~8~~<br>|
|~~8~~<br><br>|~~2~~<br>|~~7~~<br>|~~7~~<br>|~~8~~<br>|~~2~~<br>~~1~~<br><br>|~~8~~<br>~~8~~<br><br>|~~2~~<br>|~~7~~<br>|~~4~~<br>|~~1~~<br>|
|~~8~~<br><br>|~~0~~<br>|~~7~~<br>|~~2~~<br>|~~8~~<br>|~~0~~<br><br><br>|~~8~~<br><br>|~~0~~<br>|||~~8~~<br>|
|~~0~~<br>~~1~~<br><br>|~~0~~<br>|~~9~~<br>|~~5~~<br>|~~1~~<br>|~~0~~<br>~~6~~<br><br>|~~0~~<br>~~1~~<br><br>|~~0~~<br>|~~8~~<br>|~~0~~<br>|~~5~~<br>|
|~~0~~<br>~~1~~<br><br>|~~0~~<br>||||||||||


Player 2



80


60


40


20


0



GPT-4


text-davinci-003


text-davinci-002


Claude 2


Llama 2


Defect Once


Cooperate


Defect



**b**







1 2 3 4 5 6 7 8 9 10
Round



1 2 3 4 5 6 7 8 9 10
Round



**Figure 3.** Overview of the Prisoner’s Dilemma **A:** Heatmaps showing the Player 1 defection rate in each combination of
players and the scores accrued by Player 1 in each game. **B:** Example gameplays between GPT-4 and an agent that defects once
and then cooperates, and between GPT-4 and text-davinci-003. These games are also highlighted in **red** in the heatmaps.


Figure 3 shows the results of all pairwise interactions. GPT-4 plays generally better than all other agents ( _t_ (153 _._ 4) = 3 _._ 91,
_p < ._ 001, _d_ = 0 _._ 33, 95%-CIs= [0 _._ 10 _,_ 0 _._ 55], _BF_ = 7 _._ 1 ). Crucially, GPT-4 never cooperates again when playing with an agent
that defects once but then cooperates on every round thereafter. Thus, GPT-4 seems to be rather unforgiving in this setup. Its
strength in these families of games thus seems to generally stem from the fact that it does not cooperate with agents but mostly
just chooses to defect, especially after the other agent defected once.


**Robustness checks.** To make sure that the observed unforgivingness was not due to the particular prompt used, we run
several versions of the game as robustness checks, randomising the order of the presented options, relabeling the choice options,
and changing the presented utilities to be represented by either points, dollars, or coins (see Figure 4). We also repeated our
analysis with two different cover stories, added explicit end goals to our prompt, ran games with longer playing horizons and
described numerical outcomes with text, also see Supplementary Figure 3. The results of these simulations showed that the
reluctance to forgive was not due to any particular characteristics of the prompts. A crucial question was if GPT-4 did not
understand that the other agent wanted to cooperate again or if it could understand the pattern but just did not act accordingly.
We, therefore, run another version of the game, where we told GPT-4 explicitly that the other agent would defect once but
otherwise cooperate. This resulted in GPT-4 choosing to defect throughout all rounds, thereby maximizing its own points.


**Prompting techniques to improve observed behaviour.** One problem of these investigations in the Prisoner’s Dilemma
is that defecting can under specific circumstances be seen as the optimal, utility-maximizing, and equilibrium option even
in a repeated version, especially if one knows that the other player will always choose to cooperate and when the number of
interactions is known. Thus, we run more simulations to assess if there could be a scenario in which GPT-4 starts to forgive and
cooperates again, maximizing the joint benefit instead of its own.


We took inspiration from the literature on human forgiveness in the Prisoner’s Dilemma and implemented a version of the
task in the vein of [11] . Specifically, [11] showed that telling participants that other players sometimes make mistakes, makes people
more likely to forgive and cooperate again after another player’s defection (albeit in infinitely played games). Indeed, this can
be favorable to them in terms of pay-offs. We observed similar behaviour in GPT-4 as it started cooperating again.


**4/15**


_**Battle of the Sexes**_

In our large-scale analysis, we saw that the different LLMs did not perform well in games that required coordination between
different players. In humans, it has frequently been found that coordination problems can be solved by the formation of
conventions [25][,] [26] .

A coordination game is a type of simultaneous game in which a player will earn a higher payoff when they select the same
course of action as another player. Usually, these games do not contain a pure conflict, i.e. completely opposing interests,
but may contain slightly diverging rewards. Coordination games can often be solved via multiple pure strategies, or mixed,
Nash equilibria in which players choose (randomly) matching strategies. Here, to probe how LLMs balance coordination and
self-interest, we look at a coordination game that contains conflicting interests.
We study a game that is archaically referred to as the “Battle of the Sexes”, a game from the family of biased games.
Assume that a couple wants to decide what to do together. Both will increase their utility by spending time together. However,
while the wife might prefer to watch a football game, the husband might prefer to go to the ballet. Since the couple wants to
spend time together, they will derive no utility by doing an activity separately. If they go to the ballet together, or to a football
game, one person will derive some utility by being with the other person but will derive less utility from the activity itself than
the other person. The corresponding payoff matrix is


_Football_ _Ballet_
_Football_ (10 _,_ 7) (0 _,_ 0) (2)
_Ballet_ (0 _,_ 0) (7 _,_ 10)



As before, the playing agents are all three versions of GPT, Claude 2, Llama 2 as well as three more simplistic strategies.
For the simplistic strategies, we implemented two agents who always choose just one option. Because LLMs most often interact
with humans, we additionally implemented a strategy that mirrored a common pattern exhibited by human players in the battle
of the sexes. Specifically, humans have been shown to often converge to turn-taking behaviour in the Battle of the Sexes [27][–][30] ;
this means that players alternate between jointly picking the better option for one player and picking the option for the other
player. While not a straightforward equilibrium, this behaviour has been shown to offer an efficient solution to the coordination
problem involved and to lead to high joint welfare [28] .
Figure 5 shows the results of all interactions. As before, GPT-4 plays generally better than all other agents ( _t_ (128 _._ 28) = 2 _._ 83,
_p_ = _._ 005, _d_ = 0 _._ 28, 95%-CIs= [0 _._ 07 _,_ 0 _._ 50], _BF_ = 3 _._ 56 ). Yet while GPT-4 plays well against other agents who choose only one
option, such as an agent always choosing Football, it does not play well with agents who frequently choose their non-preferred
option. For example, when playing against text-davinci-003, which tends to frequently choose its own preferred option, GPT-4
chooses its own preferred option repeatedly but also occasionally gives in and chooses the other option. Crucially, GPT-4
performs poorly when playing with an alternating pattern (where, for courtesy, we let agents start with the option that the other
player preferred). This is because GPT-4 seemingly does not adjust its choices to the other player but instead keeps choosing its
preferred option. GPT-4, therefore, fails to coordinate with a simple, human-like agent, an instance of a behavioural flaw.


**Robustness checks.** To make sure that this ob
game, where we randomize the order of the presented 0.8 0.8
options, relabeled the choice options, and changed the 0.5 0.5
presented utilities to be represented by either points,
dollars, or coins as shown in Figure 4. We also re- 0.2 0.2

ing competition or working on a collaborative project

**Figure 4.** Prompt variations. **Left:** GPT-4’s performance for

keeping the underlying problem structure (payoffs

different prompt variations in the PD game against a false defector

and the interaction dynamics) identical (See Supple
agent. Probability of joint cooperation _≤_ 0 _._ 1 for all combinations

mentary Figure 3). The results of these simulations

except for two using coins as utility outcomes. **Right:** GPT-4’s

showed that the inability to alternate was not due to

performance for different prompt variations in the BoS game against

any particular characteristics of the used prompts. To

an alternating agent. GPT-4 always chooses its preferred option

make sure that the observed behavioural flaw was not

resulting in successful coordination rates of only 0.5 across all

due to the particular payoff matrix used, we also re
combinations. For each variation, two random letters that occur with

run several versions of the game, where we modified

similar frequency in English are given as the choice options.

the payoff matrix gradually from preferring Football
to preferring Ballet (or, in our case, the abstract F and
J). The results of these simulations showed that GPT-4 did not alternate for any of these games but simply changed its constant



































**Figure 4.** Prompt variations. **Left:** GPT-4’s performance for
different prompt variations in the PD game against a false defector
agent. Probability of joint cooperation _≤_ 0 _._ 1 for all combinations
except for two using coins as utility outcomes. **Right:** GPT-4’s
performance for different prompt variations in the BoS game against
an alternating agent. GPT-4 always chooses its preferred option
resulting in successful coordination rates of only 0.5 across all
combinations. For each variation, two random letters that occur with
similar frequency in English are given as the choice options.



**5/15**


**a**


**b**



GPT-4 SCoT


GPT-4


text-davinci-003


text-davinci-002


Claude 2


Llama 2


Alternate


Football


Ballet



Collaboration Rate

|9|0 1|00|8|0|10|0 8|0 10|0 8|0 9|0 10|0|
|---|---|---|---|---|---|---|---|---|---|---|---|
|~~6~~<br>|~~0~~<br>~~1~~<br><br>|~~0~~<br>|~~5~~<br>|~~0~~<br>|~~1~~<br>|~~0~~<br>~~5~~<br><br>|~~0~~<br>~~1~~<br><br>|~~0~~<br>~~4~~<br><br>|~~0~~<br>~~6~~<br><br>|~~0~~<br>~~1~~<br><br>|~~0~~<br>|
|||||||||||||
||~~1~~|~~0~~<br>~~5~~|~~0~~<br>~~5~~|~~0~~<br>~~1~~|~~0~~<br>~~1~~|~~0~~<br>~~2~~|~~0~~<br>~~1~~|~~0~~<br>~~2~~|~~0~~<br>~~6~~|~~0~~<br>~~1~~|~~0~~|
||~~1~~<br><br>|~~0~~<br>~~5~~<br><br>|~~0~~<br>~~5~~<br><br>|~~0~~<br>~~1~~<br><br>|~~0~~<br>~~1~~<br><br>|~~0~~<br>~~1~~<br><br>|~~0~~<br>~~1~~<br><br>|~~0~~<br>~~1~~<br><br>|~~0~~<br>~~1~~<br><br>|~~0~~<br>~~1~~<br><br>|~~0~~<br>|
|~~2~~<br>|~~0~~<br>~~9~~<br><br>|~~0~~<br>~~6~~<br><br>|~~0~~<br>~~6~~<br><br>|~~0~~<br>~~9~~<br><br>|~~0~~<br>~~9~~<br><br>|~~0~~<br>~~5~~<br><br>|~~0~~<br>~~9~~<br><br>|~~0~~<br>~~4~~<br><br>|~~0~~<br>~~2~~<br><br>|~~0~~<br>~~9~~<br><br>|~~0~~<br>|
|||||||||||||
|~~5~~<br>|~~0~~<br>~~5~~<br><br>~~1~~|~~0~~<br><br>~~0~~<br>~~5~~|~~0~~<br><br>~~0~~<br>~~5~~|~~5~~<br>~~0~~<br>~~1~~|~~5~~<br>~~0~~<br>~~1~~|~~0~~<br>~~3~~<br>~~0~~<br>~~1~~|~~0~~<br>~~5~~<br>~~0~~<br>~~1~~|~~0~~<br>~~5~~<br>~~0~~<br>~~1~~|~~0~~<br>~~5~~<br>~~0~~<br>|~~0~~<br>~~3~~<br><br>~~1~~|~~0~~<br>~~0~~|
||~~1~~<br><br>|~~0~~<br>~~5~~<br><br>|~~0~~<br>~~5~~<br><br>|~~0~~<br>~~1~~<br><br>|~~0~~<br>~~1~~<br><br>|~~0~~<br>~~1~~<br><br>|~~0~~<br>~~1~~<br><br>|~~0~~<br>~~1~~<br><br>|~~0~~<br><br><br>|~~1~~<br><br>|~~0~~<br>|
|~~1~~<br>|~~0~~<br><br><br>|~~5~~<br><br>|~~5~~<br><br>|~~0~~<br><br><br>|~~0~~<br><br><br>|~~4~~<br><br>|~~0~~<br><br><br>||~~1~~<br><br>|~~0~~<br>~~9~~<br><br>|~~0~~<br>|
|||||||||||||



Player 2



100


80


60


40


20


0



GPT-4 SCoT


GPT-4


text-davinci-003


text-davinci-002


Claude 2


Llama 2


Alternate


Football


Ballet



Player 1 choosing its preferred option

|1|0 1|00|7|0|10|0 3|0 1|00 3|0 1|0 10|0|
|---|---|---|---|---|---|---|---|---|---|---|---|
|~~4~~<br>|~~0~~<br>~~1~~<br><br>|~~0~~<br>|~~1~~<br>|~~0~~<br>|~~1~~<br>|~~0~~<br>~~6~~<br><br>|~~0~~<br>~~1~~<br><br>|~~0~~<br>~~7~~<br><br>|~~0~~<br>~~4~~<br><br>|~~0~~<br>~~1~~<br><br>|~~0~~<br>|
|||||||||||||
|~~1~~|~~0 1~~|~~0 1~~|~~0 1~~|~~0 1~~|~~0 1~~|~~0~~<br>~~9~~|~~0~~<br>~~1~~|~~0~~<br>~~9~~|~~0~~<br>~~1~~|~~0 1~~|~~0~~|
|~~1~~<br>|~~0 1~~<br>|~~0 1~~<br>|~~0 1~~<br>|~~0 1~~<br>|~~0 1~~<br>|~~0 1~~<br><br>|~~0 1~~<br><br>|~~0 1~~<br><br>|~~0 1~~<br><br>|~~0 1~~<br>|~~0~~<br>|
|~~8~~<br>|~~0~~<br>~~9~~<br>|~~0~~<br>~~9~~<br>|~~0~~<br>~~9~~<br>|~~0~~<br>~~9~~<br>|~~0~~<br>~~9~~<br>|~~0~~<br>~~9~~<br>|~~0~~<br>~~9~~<br>|~~0~~<br>~~9~~<br>|~~0~~<br>~~8~~<br>|~~0~~<br>~~9~~<br>|~~0~~<br>|
|||||||||||||
|~~5~~<br>~~1~~|~~0~~<br>~~5~~<br>~~0 1~~|~~0~~<br>~~5~~<br>~~0 1~~|~~0~~<br>~~5~~<br>~~0 1~~|~~0~~<br>~~5~~<br>~~0 1~~|~~0~~<br>~~5~~<br>~~0 1~~|~~0~~<br>~~5~~<br>~~0 1~~|~~0~~<br>~~5~~<br>~~0 1~~|~~0~~<br>~~5~~<br>~~0 1~~|~~0~~<br>~~5~~<br>~~0 1~~|~~0~~<br>~~5~~<br>~~0 1~~|~~0~~<br>~~0~~|
|~~1~~<br>|~~0 1~~<br><br>|~~0 1~~<br><br>|~~0 1~~<br><br>|~~0 1~~<br><br>|~~0 1~~<br><br>|~~0 1~~<br><br>|~~0 1~~<br><br>|~~0 1~~<br><br>|~~0 1~~<br><br>|~~0 1~~<br><br>|~~0~~<br>|
|||||||||||||
|||||||||||||



Player 2



100


80


60


40


20


0







1 2 3 4 5 6 7 8 9 10
Round



1 2 3 4 5 6 7 8 9 10
Round



**Figure 5.** Overview of the Battle of the Sexes. **A:** Heatmaps showing rates of successful collaboration between the two
players and the rates of Player 1 choosing its preferred option Football. GPT-4 SCoT and GPT-4 performance comparisons are
highlighted in **red** . **B:** Gameplay between GPT-4 and an agent that alternates between the two options ( **left** ) and gameplay
between GPT-4 and GPT-4 SCoT which represents a GPT-4 model prompted using the social chain-of-thought method to first
predict the opponent’s move before making its own move by reasoning about its prediction ( **right** ). Both games are also
highlighted in **blue** in the heatmaps.


response to the option that it preferred for any particular game. Thus, the inability to alternate was not due to the particular
payoff matrix we used (see Supplementary A.5).


**Prediction scenarios.** Despite these robustness checks, another crucial question remains: Does GPT-4 simply not understand
the alternating pattern or can it understand the pattern but is unable to act accordingly? To answer this question, we run two
additional simulations. In the first simulation, GPT-4 was again framed as a player in the game itself. However, we now
additionally ask it to predict the other player’s next move according to previous rounds. In this simulation, GPT-4 started
predicting the alternating pattern correctly from round 5 onward (we show this in Figure 6).
In the second simulation, instead of having GPT-4 be framed as a player itself, we simply prompted it with a game between
two (’external’) players and asked it to predict one player’s next move according to the previous rounds. For the shown history,
we used the interaction between GPT-4 and the alternating strategy. In this simulation, GPT-4 started predicting the alternating
pattern correctly even earlier, from round 3 onward. Thus, GPT-4 seemingly _could_ predict the alternating patterns but instead
just did not act in accordance with the resulting convention. Similar divergences in abilities between social and non-social
representations of the same situation have been observed in autistic children [31] .


**Social chain-of-thought (SCoT) prompting.** Finally, we wanted to see if GPT-4’s ability to predict the other player’s choices
could be used to improve its own actions. This idea is closely related to how people’s reasoning in repeated games and tasks
about other agents’ beliefs can be improved [32] . For example, computer-aided simulations to improve the social reasoning
abilities of autistic children normally include questions to imagine different actions and outcomes [33] . This has been successfully
used to improve people’s decision-making more generally. It is also in line with the general finding that chain-of-thought
prompting improves LLM’s performance, even in tasks measuring theory of mind [34] .Thus, we implemented a version of this
reasoning through actions by asking LLMs to imagine the possible actions and their outcomes before making a decision. We
termed this approach social chain-of-thought prompting. Applying this method improved GPT-4’s behaviour and it started to
alternate from round 5 onward (see Figure 5).


**6/15**


**Human experiments**
Given the behavioural signatures observed in GPT-4’s responses in the different games, we were interested in how actual human
subjects would behave when playing with such agents. To test this, we conducted an experiment in which 195 participants
played both the “Battle of the Sexes” and the “Prisoner’s Dilemma” against LLMs. Because the social chain-of-thought
prompting turned out to be a most reliable modification of LLMs’ behaviour, we only applied this prompting method in our
behavioural experiments with humans.
Participants were told that they would play either against a human player or an artificial agents for 10 repeated rounds
for each game and, after each game, had to guess whether they had played against a human or not. Which game they played
first was assigned randomly. While all subjects, in fact, only played against LLMs, one group played against the base version
of GPT-4, while another group played against a version of GPT-4 that first predicted the other agent’s move and the acted
accordingly, i.e. social chain-of-thought prompting. Importantly, each participant played only two games, and the prompting
was reset between games to ensure any change in LLM behavior was not influenced by prior interactions within the experiment.
If assigned to the base version initially, participants played both games with this model, and likewise for the socially prompted
version. An overview of the experimental design can be seen in Figure 7a. Participants were recruited from Prolific and
debriefed fully after the experiment. We were interested in how people played against LLMs in general as well as if GPT-4’s
behaviour could be improved via social chain-of-thought prompting. Finally, we also asked participants whether they thought
they had played with another human or an artificial agent after each game.
While participants’ average score was significantly higher for the SCoT-prompted condition compared to the condition
without further prompting (i.e. base) in the Battle of the Sexes (mixed-effects regression results: _β_ = 0 _._ 74, _t_ (193) = 3 _._ 49,
_p < ._ 001, 95%-CIs= [0 _._ 32 _,_ 1 _._ 15], BF= 80 _._ 6 ), no such difference was observed in the Prisoner’s Dilemma ( _β_ = 0 _._ 10, _t_ (193) =
0 _._ 47, _p_ = 0 _._ 64, 95%-CIs= [ _−_ 0 _._ 31 _,_ 0 _._ 51], BF= 0 _._ 2 ). Looking at the behaviour of both players, we found that SCoT-prompting
increased successful coordination (i.e. both players picking the same option) in the Battle of the Sexes ( _β_ = 0 _._ 33, _z_ = 3 _._ 59,
_p < ._ 001, 95%-CIs= [0 _._ 15 _,_ 0 _._ 51], BF= 13 _._ 4 ), while it also slightly increased joint cooperation (i.e. both players cooperating) in
the Prisoner’s Dilemma ( _β_ = 0 _._ 24, _z_ = 2 _._ 54, _p_ = 0 _._ 01, 95%-CIs= [0 _._ 05 _,_ 0 _._ 42], BF= 6 _._ 5 ). In general, participants were more
likely to think that the prompted model was another human player as compared to the unprompted base GPT-4 model ( _β_ = 0 _._ 54,
_z_ = 8 _._ 31, _p < ._ 001, 95%-CIs= [0 _._ 05 _,_ 0 _._ 42], BF= 17 _._ 6 ). Additional analysis on participants’ temporal behaviour in both games
can be found in the SI.



In summary, SCoT prompting can increase GPT-4’s coordination
and cooperation behaviour without changing scores in scenarios where
self-interest is important for good behaviour, i.e. the Prisoner’s Dilemma,
but leading to increased performance in coordination problems, i.e. the
Battle of the Sexes.


**Discussion**



**Prediction Scenario 1**

_You_ are playing a game repeatedly with another player...
**Q:** Which Option do you predict the other player will choose,
Option J or Option F?
**A:** Option **J**


F





J



LLMs are one of the most quickly adopted technologies ever, interacting 1 2 3 4 5 6 7 8 9 10
with millions of consumers within weeks [10] . Understanding in a more Round

**Prediction Scenario 2**

principled manner how these systems interact with us, and with each

_Two players_ are playing a game repeatedly with another player...

other, is thus of urgent concern. Here, our proposal is simple: Just **Q:** Which Option do you predict Player 2 will choose, Option J or
like behavioural game theorists use tightly controlled and theoretically Option F?

**A:** Option **J**

well-understood games to understand human interactions, we use these
games to study the interactions of LLMs. F
We thereby understand our work as both a proof of concept of the Alternate
utility of this approach and an examination of the individual failures J

and successes of socially interacting LLMs. Our large-scale analysis of 1 2 3 4 5 6 7 8 9 10

all 2 _×_ 2 -games highlights that the most recent LLMs indeed are able Round
to perform well on a wide range of game-theoretic tasks as measured **Figure 6.** Prediction scenarios in the Battle of the
by their own individual reward, particularly when they do not have to Sexes. **Top:** GPT-4 is a player of the game and
explicitly coordinate with others. This adds to a wide-ranging literature predicts the other player’s move. **Bottom:** GPT-4
showcasing emergent phenomena in LLMs [4][–][8] . However, we also show is a mere observer of a game between Player 1 and
that LLMs behaviour is suboptimal in coordination games, even when Player 2 and predicts Player 2’s move.
faced with simple strategies.
To tease apart the behavioural signatures of these LLMs, we zoomed in on two of the most canonical games in game theory:
the Prisoner’s Dilemma and the Battle of the Sexes. In the Prisoner’s Dilemma, we show that GPT-4 mostly plays unforgivingly.
Starting with full cooperation, it permanently shifts to defection after a single negative interaction with the other agent, even if
the other agent later cooperates. While noting that GPT-4’s continual defection is indeed the equilibrium policy in this finitely



1 2 3 4 5 6 7 8 9 10

Round



**Prediction Scenario 2**

_Two players_ are playing a game repeatedly with another player...
**Q:** Which Option do you predict Player 2 will choose, Option J or
Option F?
**A:** Option **J**



F





J



1 2 3 4 5 6 7 8 9 10

Round



**Figure 6.** Prediction scenarios in the Battle of the
Sexes. **Top:** GPT-4 is a player of the game and
predicts the other player’s move. **Bottom:** GPT-4
is a mere observer of a game between Player 1 and
Player 2 and predicts Player 2’s move.



**7/15**


a: Experimental design


Human



b: Battle of the Sexes



c: Prisoner's Dilemma





10

9

8

7

6

5

4

3

2

1

0





LLM

Base



LLM

Prompted



10

9

8

7

6

5

4

3

2

1

0






|Col1|Col2|Col3|
|---|---|---|
||||
||~~BF=80.6~~||
||||
||||
||||
||||
||||
||||
||||
||||
||||
||||
||||
||||


|Col1|Col2|Col3|
|---|---|---|
||||
||~~BF=0.2~~||
||||
||||
||||
||||
||||
||||
||||
||||
||||
||||
||||
||||



1.0

0.9

0.8

0.7

0.6

0.5

0.4

0.3

0.2

0.1

0.0



Base Prompted
Opposing LLM


f: Joint cooperation



Base Prompted
Opposing LLM


e: Successful coordination



1.0

0.9

0.8

0.7

0.6

0.5

0.4

0.3

0.2

0.1

0.0



d: Guessing the opponent

|Col1|Col2|Col3|Col4|Col5|Col6|Col7|
|---|---|---|---|---|---|---|
||||||||
|||~~BF=17.6~~|~~BF=17.6~~|~~BF=17.6~~|||
||||||||
||||||||
||||||||
||||||||



Base Prompted
Opposing LLM


|Col1|BF=13.4|Col3|
|---|---|---|
||~~BF=13.4~~||
||||
||||
||||
||||


|Col1|BF=6.5|Col3|
|---|---|---|
||~~BF=6.5~~||
||||
||||
||||
||||



Base Prompted
Opposing LLM



Base Prompted
Opposing LLM



1.0
0.9
0.8
0.7
0.6
0.5
0.4
0.3
0.2
0.1
0.0



**Figure 7.** Human experiments. **a:** Design of human experiments ( _N_ = 195, 89 females, mean age=26.72, _SD_ = 4 _._ 19). Each
participant gets randomly assigned either base or SCoT prompted version of the LLM at the start and plays both games
repeatedly for 10 rounds against this agent. **b:** Results of the “Battle of the Sexes” game showing participants’ average scores
by condition (mixed-effects regression results: _β_ = 0 _._ 74, _t_ (193) = 3 _._ 49, _p < ._ 001, 95%-CIs= [0 _._ 32 _,_ 1 _._ 15], BF=80 _._ 6). **c:**
Results of the “Prisoner’s Dilemma” game showing participants’ average scores by condition ( _β_ = 0 _._ 10, _t_ (193) = 0 _._ 47,
_p_ = 0 _._ 64, 95%-CIs= [ _−_ 0 _._ 31 _,_ 0 _._ 51], BF=0 _._ 2). **d:** Average proportion of participants guessing that they have played against
another human by condition. Error bars represent the 95%-CIs of the mean ( _β_ = 0 _._ 54, _z_ = 8 _._ 31, _p < ._ 001, 95%-CIs=

[0 _._ 05 _,_ 0 _._ 42], BF= 17 _._ 6 ). **e:** Participants’ successful coordination rates by condition in the “Battle of the Sexes” game ( _β_ = 0 _._ 33,
_z_ = 3 _._ 59, _p < ._ 001, 95%-CIs= [0 _._ 15 _,_ 0 _._ 51], BF= 13 _._ 4 ). **f:** Participants’ mutual cooperation rates by condition in the “Prisoner’s
Dilemma” game ( _β_ = 0 _._ 24, _z_ = 2 _._ 54, _p_ = 0 _._ 01, 95%-CIs= [0 _._ 05 _,_ 0 _._ 42], BF=6 _._ 5).


played game, such behaviour comes at the cost of the two agents’ joint payoff. We see a similar tendency in GPT-4’s behaviour
in the Battle of the Sexes, where it has a strong tendency to stubbornly stick with its own preferred alternative. In contrast to the
Prisoner’s Dilemma, this behaviour is suboptimal, even on the individual level.
Current generations of LLMs are generally assumed, and trained, to be benevolent assistants to humans [35] . Despite many
successes in this direction, the fact that we here show how they play iterated games in such a selfish, and uncoordinated manner
sheds light on the fact that there is still significant ground to cover for LLMs to become truly social and well-aligned machines [36] .
Their lack of appropriate responses vis-a-vis even simple strategies in coordination games also speaks to the recent debate
around theory of mind in LLMs [37][–][39] by highlighting a potential failure mode.
Our extensive robustness checks demonstrate how these behavioural signatures are not functions of individual prompts but
reflect broader patterns of LLM behaviour. Our intervention pointing out the fallibility of the playing partner – which leads to
increased cooperation – adds to a literature that points to the malleability of LLM social behaviour in tasks to prompts [40][,] [41] .
This is important as we try to understand what makes LLMs better, and more pleasant, interactive partners. Further experiments
on GPT-4’s final round behaviour have shown that it did not adjust its behavior in the last round of games or when faced
with varying probabilities of continuation, unlike human players who often increase cooperation when future interactions are
likely [42][,] [43] . This suggests that GPT-4 may lack mechanisms for backward induction and long-term strategic planning, primarily
focusing on immediate context due to its training on next-token prediction [44] . Consequently, GPT-4 tends to default to defection
in uncertain situations, contrasting with human tendencies to anticipate and adjust based on future outcomes [24][,] [45] .
We additionally observed that prompting GPT-4 to make predictions about the other player before making its own decisions


**8/15**


can alleviate behavioural flaws and the oversight of even simple strategies. This represents a more explicit way to force an LLM
to engage in theory of mind and shares much overlap with non-social chain-of-thought reasoning [34][,] [46] . Just like chain-of-thought
prompting is now implemented as a default in some LLMs to improve (non-social) reasoning performance, our work suggests
implementing a similar social cognition prompt to improve human-LLM interaction.
In our exploration of a behavioural game theory of machines, we acknowledge several limitations. First, despite covering
many families of games, our investigation is constrained to simple 2 _×_ 2 games. However, we note that our analysis significantly
goes beyond current investigations that have often investigated only one game, and done so using single-shot rather than
iterated instances of these games. For example, our iterated approach shares more overlap with the more iterated nature of
human-LLM conversations. We also note that we mainly study finite games where agents share knowledge about the duration
of the interaction. This is in contrast to so-called indefinite games that have either unknown, probabilistic or no endpoints at all.
In these games, both optimal prescriptions and empirical behaviour can differ significantly from the finite case, warranting
further investigation.
We believe that more complicated games will shed even more light on game-theoretic machine behaviour in the future.
For example, games with more continuous choices like the trust game [47] might elucidate how LLMs dynamically develop
(mis-)trust. Games with more than two agents, like public goods or tragedy of the commons type games [48] could probe how
’societies’ of LLMs behave, and how LLMs cooperate or exploit each other.
Given the social nature of the tasks studied here, further empirical work is needed to fully understand human-LLM
interactions across all paradigms. In our study, we conducted human experiments in two of the games, specifically, the Battle of
the Sexes and the Prisoner’s Dilemma, and attempted to probe human-like behaviors such as turn-taking in battle Battle of
the Sexes or prompting for forgiveness in the Prisoner’s Dilemma. However, these empirical investigations were limited to
these two games. By extending human studies to the remaining games, additional dynamics may emerge. Furthermore, asking
LLMs to self-report their strategies in these games and correlating these explanations with their actions could provide valuable
insights into their actual decision-making processes.
Our results highlight the broader importance of a behavioural science for machines [49][–][52] . We believe that these methods will
continue to be useful for elucidating the many facets of LLM cognition, particularly as these models become more complex,
multi-modal, and embedded in physical systems.


**Related work**

As algorithms become increasingly more able and their decision making processes impenetrable, the behavioural sciences offer
new tools to make inferences just from behavioural observations [49][,] [50] . behavioural tasks have, therefore, been used in several
benchmarks [10][,] [53] .

Whether and how algorithms can make inferences about other agents, machines and otherwise, is one stream of research that
borrows heavily from the behavioural sciences [54][–][56] . Of particular interest to the social interactions most LLMs are embedded
in is an ability to reason about the beliefs, desires, and intentions of other agents, or a so-called theory of mind (ToM) [57] . Theory
of mind underlies a wide range of interactive phenomena, from benevolent teaching [58] to malevolent deception [56][,] [59], and is
thought to be the key to many social phenomena in human interactions [60][,] [61] .
Whether LLMs possess a theory of mind has been debated. For example, it has been argued that GPT-3.5 performs well on
a number of canonical ToM tasks [39] . Others have contested this view, arguing that such good performance is merely a function
of the specific prompts [37][,] [38] . Yet other research has shown that chain-of-thought reasoning significantly improves LLMs’ ToM
ability [34] . Moreover, the currently largest LLM, GPT-4, manages to perform well in ToM tasks, including in the variants in
which GPT-3.5 previously struggled [8] . Thus, GPT-4’s behaviour will be of particular interest in our experiments.
Games taken from game theory present an ideal testbed to investigate interactive behaviour in a controlled environment [62]

and LLM’s behaviour has been probed in such tasks [63] . For example, [40] let GPT-3 participate in the dictator game, and [41] used the
same approach for the ultimatum game. Both show how the models’ behaviour is malleable to different prompts, for example
making them more or less self-interested. However, all these games rely on single-shot interactions over fewer games and do
not use iterated games.
Our study builds upon recent advancements in the field, which have shifted the focus from solely assessing the performance
of LLMs to comparing them with human behaviours. Previous research efforts have explored various approaches to analyze
LLMs, such as employing cognitive psychology tools [51][,] [64] and even adopting a computational psychiatry perspective [52] .
Finally, the theory behind interacting agents is important for many machine learning applications in general [65], and in
particular, in adversarial settings [66], where one agent tries to trick the other agent into thinking that a generated output is good.
Understanding prosocial dynamics in multiagent systems [67], and fostering cooperation in them [68] is essential for developing
robust and trustworthy AI systems that can navigate complex social environments [69] .


**9/15**


**Methods**


To investigate how human subjects would behave when playing with LLM agents, we studied their interactions in two of
the games we used; Prisoner’s Dilemma and the Battle of the Sexes. We also investigated if participants could detect and
behave differently when playing against different agents. Participants (N=195, 89 females, mean age=26.72, SD=4.19) were
recruited through Prolific [70], an online platform that allows researchers to access a diverse and reliable pool of participants.
No statistical methods were used to pre-determine sample sizes but our sample sizes are similar to those reported in previous
publications [71][–][73] . The participants were required to be fluent speakers of English with minimum approval rates of .95 and 1, and
a minimal number of previous submissions of 10 that have not participated in our experiment before. All participants provided
informed consent prior to inclusion in the study. Experiments were performed in accordance with the relevant guidelines and
regulations approved by the ethics committee of the University of Tübingen (protocol nr. 701/2020BO). Participants received a
£3 base payment plus a bonus of up to £2 depending on performance (1 Cent for each point received during the games) for their
participation. The average compensation was £11.41 per hour. Participants were fully debriefed after the experiment. Data of
21 players who failed to make a round’s choice between the 2 options within a given time frame (20 seconds) were excluded.
In the sections that follow, we first detail the experimental setup for LLM-LLM interactions, which serves as a comparative
baseline for our study. We then present details from the human participant study outlined above.


**LLM-LLM Interactions**

We study LLMs’ behaviour in finitely repeated games with full information taken from the economics literature. We focus
on two-player games with discrete choices between two options to simplify the analyses of emergent behaviours. We let two
LLMs interact via prompt-chaining, i.e. all integration of evidence and learning about past interactions happens as in-context
learning [4][,] [74] . The games are submitted to LLMs as prompts in which the respective game, including the choice options, is
described. At the same time, we submit the same game as a prompt to another LLM. We obtain generated tokens _t_ from both
LLMs by sampling from


_K_
## p LLM ( t|c [(] [p] [)] ) = ∏ p LLM ( t k |c [(] 1 [p] [)] [,...,] [c] n [(] [p] [)] [,][t] 1 [,...,][t] k− 1 [)] (3)

_k_ =1


After feeding the prompt to the LLM, our methodology is as follows. The LLM prediction of the first token following the
context is _d_ = _p_ LLM ( _t_ 1 _|c_ [(] _[p]_ [)] ) and the _N_ tokens for the possible answers of the multiple choice question are _o_ = _{o_ _i_ _}_ _[N]_ _i_ =1 [which in]
this case are J and F. The predicted option is then given by


ˆ ˆ
_o_ = argmax( _c_ _i_ ) _,_ with ˆ _c_ _i_ = _d_ [ _c_ _i_ ] _,_ _i_ = 1 _...N_ (4)


which are the predicted probabilities of the language model. Once both LLMs have made their choices, which we track as a
completion of the given text, we update the prompts with the history of past interactions as concatenated text and then submit
the new prompt to both models for the next round. These interactions continue for 10 rounds in total for every game. In a single
round _π_ _i_ ( _x_ 1 _,_ _x_ 2 ) is the payoff for Player 1 when _x_ 1 and _x_ 2 are the strategies chosen by both players. In repeated games, the
payoffs are often considered as discounted sums of the payoffs in each game stage, using a discount factor _δ_ . If the game is
repeated _n_ times, the payoff _U_ _i_ for player _i_ is


_U_ _i_ = _π_ _i_ ( _x_ 10 _,_ _x_ 20 )+ _δ ·_ _π_ _i_ ( _x_ 11 _,_ _x_ 21 )+ _δ_ [2] _·_ _π_ _i_ ( _x_ 12 _,_ _x_ 22 )+ _..._ + _δ_ _[n][−]_ [1] _·_ _π_ _i_ ( _x_ 1( _n−_ 1) _,_ _x_ 2( _n−_ 1) ) (5)


Each term represents the discounted payoff at each stage of the repeated game, from the first game ( _t_ = 0) to the _n_ _[th]_ game
( _t_ = _n_ _−_ 1) . In our experiments we keep _δ_ = 1 . To avoid influences of the particular framing of the scenarios, we only provide
barebones descriptions of the payoff matrices (see example in Figure 1). To avoid contamination through particular choice
names or the used framing, we use the neutral options ‘F’ and ‘J’ throughout [51] .


**Games considered.** We first investigate 144 different 2 _×_ 2 -games where each player has two options, and their individual
reward is a function of their joint decision. These games can be categorized into six distinct families _—Win-Win, Prisoner’s_
_Dilemma Family, Unfair, Cyclic, Biased, and Second-Best—_ each with unique characteristics and outcomes. A win-win game is
a special case of a non-zero-sum game that produces a mutually beneficial outcome for both players provided that they choose
their corresponding best option. They encourage cooperation, leading to outcomes where both parties benefit. Briefly, in games
from the Prisoner’s Dilemma family, two agents can choose to work together, i.e. cooperate, for average mutual benefit, or
betray each other, i.e. defect, for their own benefit. The typical outcome is a Nash Equilibrium that is suboptimal for both
players compared to a possible Pareto-superior outcome. In an unfair game, one player can always win when playing properly,
leading to highly unequal outcomes. Cyclic games are characterized by the absence of dominant strategies and equilibria. In
these games, players can cycle through patterns of choices without settling into a stable outcome. Biased games are games


**10/15**


where agents get higher points for choosing the same option but where the preferred option differs between the two players.
One form of a biased game is the Battle of the Sexes, where players need to coordinate to choose the same option. Finally,
second-best games are games where both agents fare better if they jointly choose the option that has the second-best utility.
In many of these games, strategic swaps in payoffs can alter the game dynamics, potentially converting them into different
types of games. For two additional games, Prisoner’s Dilemma and Battle of the Sexes, we also let LLMs play against simple,
hand-coded strategies to understand their behaviour in more detail.


**Large Language Models considered.** In this work, we evaluate five LLMs. For all of our tasks, we used the public OpenAI
API with the GPT-4, text-davinci-003 and text-davinci-002 models which are available via the completions
endpoint, Meta AI’s Llama 2 70B chat model which has 70 billion parameters and is optimized for dialogue use cases,
and the Anthropic API model Claude 2 to run our simulations. Experiments with other popular open source models MosaicPretrainedTransformer (MPT), Falcon and different versions of Llama 2 (namely MPT-7B, MPT-30B, Falcon-7b,
Falcon-40b, Llama 2 7B, Llama 2 13B ) have revealed that these models did not perform well at the given tasks,
choosing the first presented option more than 95% of the time independent of which option this is. Therefore, we chose not
to include them in our main experiments. For all models, we set the temperature parameters to 0 and only ask for one token
answer to indicate which option an agent would like to choose. All other parameters are kept as default values.


**Playing 6 families of** 2 _×_ 2 **-games task design.** While 2 _×_ 2 -games games can appear simple, they present some of the most
powerful ways to probe diverse sets of interactions, from pure competition to mixed motives and cooperation - which can
further be classified into canonical subfamilies outlined elegantly by [22] . Here, to cover the wide range of possible interactions,
we study the behaviours of GPT-4, text-davinci-003, text-davinci-002, Claude 2 and Llama 2 across these canonical families.
We let all five engines play all variants of games from within the six families.


**Cooperation and coordination task design.** We then analyze two games, Prisoner’s Dilemma and Battle of the Sexes, in
more detail because they represent interesting edge cases where the LLMs performed exceptionally well, and relatively poorly.
We particularly hone in on GPT-4’s behaviour because of recent debates around its ability for theory of mind, that is whether it
is able to hold beliefs about other agents’ intentions and goals, a crucial ability to successfully navigate repeated interactions [8][,] [39] .
For the two additional games, we also let LLMs play against simple, hand-coded strategies to further understand their behaviour.
These simple strategies are designed to assess how LLMs behave when playing with more human-like players.


**Statistical tests.** All reported tests are two-sided. We also report Bayes Factors quantifying the likelihood of the data under
_H_ _A_ relative to the likelihood of the data under _H_ 0 . We calculate the default two-sided Bayesian _t_ -test using a Jeffreys-ZellnerSiow prior with its scale set to _√_ 2 _/_ 2, following [75] . For parametric tests, the data distribution was assumed to be normal but

this was not formally tested. We report effect sizes as either Cohen’s d or standardized regression estimates, including their
95%-Confidence Intervals.


**Human-LLM Interactions**

Following sections provide additional details on the design and conduct of the human participant study; including compensation,
demographics, prompting and the cover stories.


**Design.** Experiments were presented to participants using a combination of HTML, JavaScript, and CSS with custom code.
After a presentation of the instructions including screenshots from the actual game-play, participants were required to complete
a comprehension questionnaire. Only upon responding correctly to all questions, they could proceed to the main part of the
experiment. Participants played both the Prisoner’s Dilemma and the Battle of the Sexes, with the order counter-balanced
between subjects. Participants were instructed that they would play two games with 10 rounds each with different players. The
participants’ interface (Supplementary Figure 4) was designed to provide clear and actionable information about the current
game. After each game, participants were asked to indicate if they thought they had just played with another human player or
an artificial agent.


**Prompts and human instructions.** The cover story used for interactions with both LLMs and human participants was
content-wise identical, including the rules of the game and the history of previous interactions, to ensure consistent framing
across conditions (see Supplementary A.1 for the detailed prompt progression). However, the presentation was adapted to suit
each audience. For human participants, visual cues and concise text were prioritized to create a more engaging experience
(Supplementary Figure 4).


**Ending and debriefing.** Participants were informed that their opponent could either be another human participant or an
artificial agent. In reality, all participants were paired with either a SCoT-prompted or unprompted version of GPT-4 for the
entirety of the experiment, i.e., across both games. After completing the study, participants were debriefed that the purpose of


**11/15**


the study was to explore how to make Large Language Models (LLMs) more human-like and that, in both games, they had
played against different versions of an artificial agent.


**Data availability**


[All participant and model simulation data from the experiments are publicly available on GitHub (github.com/eliaka/repeatedgames).](https://github.com/eliaka/repeatedgames)


**Code availability**


[The code underlying this study, prompt variations and model simulations are available on github.com/eliaka/repeatedgames.](https://github.com/eliaka/repeatedgames)


**Acknowledgements**


This work was supported by grants from the Max Planck Society (E.A., L.S., J.C.F. and E.S.), the Volkswagen Foundation
(E.S.), the German Federal Ministry of Education and Research (BMBF): Tübingen AI Center, FKZ: 01IS18039A, and the
Deutsche Forschungsgemeinschaft (DFG, German Research Foundation) under Germany’s Excellence Strategy – EXC 2064/1
– grant no. 390727645 (E.A., S.J.O. and M.B). The funders had no role in study design, data collection and analysis, decision
to publish or preparation of the manuscript. We thank the International Max Planck Research School for Intelligent Systems
(IMPRS-IS) for supporting E.A.


**Author contributions**


E.A., L.S. and E.S. conceived experiments. E.A. conducted the experiments. E.A. and E.S. analysed the results with input
from L.S., J.C.F. and M.B. E.A., L.S and E.S. wrote the manuscript with input from S.J.O. and M.B. All authors reviewed the
manuscript.


**Competing interests statement**


The authors declare no competing interests.


**12/15**


**References**


**1.** Brants, T., Popat, A., Xu, P., Och, F. J. & Dean, J. Large language models in machine translation. In _Proceedings of the_
_2007 Joint Conference on Empirical Methods in Natural Language Processing and Computational Natural Language_
_Learning (EMNLP-CoNLL)_, 858–867 (2007).


**2.** Devlin, J., Chang, M.-W., Lee, K. & Toutanova, K. Bert: Pre-training of deep bidirectional transformers for language
understanding. _arXiv preprint arXiv:1810.04805_ (2018).


**3.** Radford, A., Narasimhan, K., Salimans, T., Sutskever, I. _et al._ Improving language understanding by generative pre-training.
_OpenAI_ (2018).


**4.** Brown, T. _et al._ Language models are few-shot learners. _Adv. neural information processing systems_ **33**, 1877–1901
(2020).


**5.** Wei, J. _et al._ Emergent abilities of large language models. _arXiv preprint arXiv:2206.07682_ (2022).


**6.** Webb, T., Holyoak, K. J. & Lu, H. Emergent analogical reasoning in large language models. _Nat. Hum. Behav._ **7**,
1526–1541 (2023).


**7.** Chen, M. _et al._ Evaluating large language models trained on code. _arXiv preprint arXiv:2107.03374_ (2021).


**8.** Bubeck, S. _et al._ Sparks of artificial general intelligence: Early experiments with gpt-4. _arXiv preprint arXiv:2303.12712_
(2023).


**9.** Coda-Forno, J. _et al._ Meta-in-context learning in large language models. _Adv. Neural Inf. Process. Syst._ **36**, 65189–65201
(2023).


**10.** Bommasani, R. _et al._ On the opportunities and risks of foundation models. _arXiv preprint arXiv:2108.07258_ (2021).


**11.** Fudenberg, D., Rand, D. G. & Dreber, A. Slow to anger and fast to forgive: Cooperation in an uncertain world. _Am. Econ._
_Rev._ **102**, 720–749 (2012).


**12.** Mailath, G. J. & Morris, S. Coordination failure in repeated games with almost-public monitoring. _Available at SSRN_
_580681_ (2004).


**13.** Camerer, C. F., Behavioral game theory: Experiments in strategic interaction. _Princet. university press_ (2011).


**14.** Fudenberg, D. & Tirole, J. _Game theory_ (MIT press, 1991).


**15.** Von Neumann, J. & Morgenstern, O. Theory of games and economic behavior. In _Theory of games and economic behavior_
(Princeton university press, 1944).


**16.** Camerer, C. F. Progress in behavioral game theory. _J. economic perspectives_ **11**, 167–188 (1997).


**17.** Henrich, J. _et al._ In search of homo economicus: behavioral experiments in 15 small-scale societies. _Am. Econ. Rev._ **91**,
73–78 (2001).


**18.** Rousseau, D. M., Sitkin, S. B., Burt, R. S. & Camerer, C. Not so different after all: A cross-discipline view of trust. _Acad._
_management review_ **23**, 393–404 (1998).


**19.** Johnson, T. & Obradovich, N. Measuring an artificial intelligence agent’s trust in humans using machine incentives. _arXiv_
_preprint arXiv:2212.13371_ (2022).


**20.** Achiam, J. _et al._ Gpt-4 technical report. _arXiv preprint arXiv:2303.08774_ (2023).


**21.** Owen, G. _Game theory_ (Emerald Group Publishing, 2013).


**22.** Robinson, D. & Goforth, D. _The topology of the 2x2 games: a new periodic table_, vol. 3 (Psychology Press, 2005).


**23.** Jones, G. Are smarter groups more cooperative? evidence from prisoner’s dilemma experiments, 1959–2003. _J. Econ._
_Behav. & Organ._ **68**, 489–497 (2008).


**24.** Axelrod, R. & Hamilton, W. D. The evolution of cooperation. _science_ **211**, 1390–1396 (1981).


**25.** Hawkins, R. X. & Goldstone, R. L. The formation of social conventions in real-time environments. _PloS one_ **11**, e0151670
(2016).


**26.** Young, H. P. The economics of convention. _J. economic perspectives_ **10**, 105–122 (1996).


**27.** Andalman, A. & Kemp, C. Alternation in the repeated battle of the sexes. _Cambridge: MIT Press. Andreoni, J., & Miller,_
_J.(2002). Giv. according to GARP: an experimental test consistency preferences for altruism. Econom._ **70**, 737753 (2004).


**28.** Lau, S.-H. P. & Mui, V.-L. Using turn taking to mitigate coordination and conflict problems in the repeated battle of the
sexes game. _Theory Decis._ **65**, 153–183 (2008).


**13/15**


**29.** McKelvey, R. D. & Palfrey, T. R. Playing in the dark: Information, learning, and coordination in repeated games. _California_
_Inst. Technol._ (2001).


**30.** Arifovic, J. & Ledyard, J. Learning to alternate. _Exp. Econ._ **21**, 692–721 (2018).


**31.** Swettenham, J. What’s inside someone’s head? conceiving of the mind as a camera helps children with autism acquire an
alternative to a theory of mind. _Cogn. Neuropsychiatry_ **1**, 73–88 (1996).


**32.** Westby, C. & Robinson, L. A developmental perspective for promoting theory of mind. _Top. language disorders_ **34**,
362–382 (2014).


**33.** Begeer, S. _et al._ Theory of mind training in children with autism: A randomized controlled trial. _J. autism developmental_
_disorders_ **41**, 997–1006 (2011).


**34.** Moghaddam, S. R. & Honey, C. J. Boosting theory-of-mind performance in large language models via prompting. _arXiv_
_preprint arXiv:2304.11490_ (2023).


**35.** Ouyang, L. _et al._ Training language models to follow instructions with human feedback. _Adv. Neural Inf. Process. Syst._ **35**,
27730–27744 (2022).


**36.** Wolf, Y., Wies, N., Levine, Y. & Shashua, A. Fundamental limitations of alignment in large language models. _arXiv_
_preprint arXiv:2304.11082_ (2023).


**37.** Ullman, T. Large language models fail on trivial alterations to theory-of-mind tasks. _arXiv preprint arXiv:2302.08399_
(2023).


**38.** Le, M., Boureau, Y.-L. & Nickel, M. Revisiting the evaluation of theory of mind through question answering. In
_Proceedings of the 2019 Conference on Empirical Methods in Natural Language Processing and the 9th International_
_Joint Conference on Natural Language Processing (EMNLP-IJCNLP)_, 5872–5877 (2019).


**39.** Kosinski, M. Theory of mind may have spontaneously emerged in large language models. _arXiv preprint arXiv:2302.02083_
**4**, 169 (2023).


**40.** Horton, J. J. Large language models as simulated economic agents: What can we learn from homo silicus? Tech. Rep.,
National Bureau of Economic Research (2023).


**41.** Aher, G. V., Arriaga, R. I. & Kalai, A. T. Using large language models to simulate multiple humans and replicate human
subject studies. In _International Conference on Machine Learning_, 337–371 (PMLR, 2023).


**42.** Dal Bó, P. & Fréchette, G. R. The evolution of cooperation in infinitely repeated games: Experimental evidence. _Am. Econ._
_Rev._ **101**, 411–429 (2011).


**43.** Nowak, M. A. & Sigmund, K. Evolution of indirect reciprocity. _Nature_ **437**, 1291–1298 (2005).


**44.** Radford, A. _et al._ Language models are unsupervised multitask learners. _OpenAI blog_ **1**, 9 (2019).


**45.** Nowak, M. A. Five rules for the evolution of cooperation. _Science_ **314**, 1560–1563 (2006).


**46.** Wei, J. _et al._ Chain-of-thought prompting elicits reasoning in large language models. _Adv. neural information processing_
_systems_ **35**, 24824–24837 (2022).


**47.** Engle-Warnick, J. & Slonim, R. L. The evolution of strategies in a repeated trust game. _J. Econ. Behav. & Organ._ **55**,
553–573 (2004).


**48.** Rankin, D. J., Bargum, K. & Kokko, H. The tragedy of the commons in evolutionary biology. _Trends ecology & evolution_
**22**, 643–651 (2007).


**49.** Rahwan, I. _et al._ Machine behaviour. _Mach. Learn. City: Appl. Archit. Urban Des._ 143–166 (2022).


**50.** Schulz, E. & Dayan, P. Computational psychiatry for computers. _Iscience_ **23**, 101772 (2020).


**51.** Binz, M. & Schulz, E. Using cognitive psychology to understand gpt-3. _Proc. Natl. Acad. Sci._ **120**, e2218523120 (2023).


**52.** Coda-Forno, J. _et al._ Inducing anxiety in large language models increases exploration and bias. _arXiv preprint_
_arXiv:2304.11111_ (2023).


**53.** Kojima, T., Gu, S. S., Reid, M., Matsuo, Y. & Iwasawa, Y. Large language models are zero-shot reasoners. _Adv. neural_
_information processing systems_ **35**, 22199–22213 (2022).


**54.** Rabinowitz, N. _et al._ Machine theory of mind. In _International conference on machine learning_, 4218–4227 (PMLR,
2018).


**14/15**


**55.** Cuzzolin, F., Morelli, A., Cirstea, B. & Sahakian, B. J. Knowing me, knowing you: theory of mind in ai. _Psychol. medicine_
**50**, 1057–1061 (2020).


**56.** Alon, N., Schulz, L., Dayan, P. & Rosenschein, J. A (dis-) information theory of revealed and unrevealed preferences. In
_NeurIPS 2022 Workshop on Information-Theoretic Principles in Cognitive Systems_ (2022).


**57.** Frith, C. & Frith, U. Theory of mind. _Curr. biology_ **15**, R644–R645 (2005).


**58.** Vélez, N. & Gweon, H. Learning from other minds: An optimistic critique of reinforcement learning models of social
learning. _Curr. opinion behavioral sciences_ **38**, 110–115 (2021).


**59.** Lissek, S. _et al._ Cooperation and deception recruit different subsets of the theory-of-mind network. _PloS one_ **3**, e2023
(2008).


**60.** Hula, A., Montague, P. R. & Dayan, P. Monte carlo planning method estimates planning horizons during interactive social
exchange. _PLoS computational biology_ **11**, e1004254 (2015).


**61.** Ho, M. K., Saxe, R. & Cushman, F. Planning with theory of mind. _Trends Cogn. Sci._ (2022).


**62.** Han, T. A., Perret, C. & Powers, S. T. When to (or not to) trust intelligent machines: Insights from an evolutionary game
theory analysis of trust in repeated games. _Cogn. Syst. Res._ **68**, 111–124 (2021).


**63.** Chan, A., Riché, M. & Clifton, J. Towards the scalable evaluation of cooperativeness in language models. _arXiv preprint_
_arXiv:2303.13360_ (2023).


**64.** Dasgupta, I. _et al._ Language models show human-like content effects on reasoning. _arXiv preprint arXiv:2207.07051_
(2022).


**65.** Crandall, J. W. & Goodrich, M. A. Learning to compete, coordinate, and cooperate in repeated games using reinforcement
learning. _Mach. Learn._ **82**, 281–314 (2011).


**66.** Goodfellow, I. _et al._ Generative adversarial networks. _Commun. ACM_ **63**, 139–144 (2020).


**67.** Santos, F. P. Prosocial dynamics in multiagent systems. _AI Mag._ **45**, 131–138 (2024).


**68.** Guo, H. _et al._ Facilitating cooperation in human-agent hybrid populations through autonomous agents. _Iscience_ **26** (2023).


**69.** Powers, S. T. _et al._ The stuff we swim in: regulation alone will not lead to justifiable trust in ai. _IEEE Technol. Soc. Mag._
**42**, 95–106 (2023).


**70.** Palan, S. & Schitter, C. Prolific. ac—a subject pool for online experiments. _J. behavioral experimental finance_ **17**, 22–27
(2018).


**71.** Normann, H.-T. & Wallace, B. The impact of the termination rule on cooperation in a prisoner’s dilemma experiment. _Int._
_J. Game Theory_ **41**, 707–718 (2012).


**72.** Charness, G. & Rabin, M. Understanding social preferences with simple tests. _The quarterly journal economics_ **117**,
817–869 (2002).


**73.** Wong, R. Y.-m. & Hong, Y.-y. Dynamic influences of culture on cooperation in the prisoner’s dilemma. _Psychol. science_
**16**, 429–434 (2005).


**74.** Liu, P. _et al._ Pre-train, prompt, and predict: A systematic survey of prompting methods in natural language processing.
_ACM Comput. Surv._ **55**, 1–35 (2023).


**75.** Rouder, J. N., Speckman, P. L., Sun, D., Morey, R. D. & Iverson, G. Bayesian t tests for accepting and rejecting the null
hypothesis. _Psychon. bulletin & review_ **16**, 225–237 (2009).


**15/15**


