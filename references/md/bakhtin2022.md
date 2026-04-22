## M ASTERING THE G AME OF N O -P RESS D IPLOMACY VIA H UMAN -R EGULARIZED R EINFORCEMENT L EARNING AND P LANNING

**Anton Bakhtin** _[∗]_ **David J Wu** _[∗]_ **Adam Lerer** _[∗]_ **Jonathan Gray** _[∗]_ **Athul Paul Jacob** _[∗]_
Meta AI Meta AI Meta AI Meta AI MIT


**Gabriele Farina** _[∗]_ **Alexander H Miller** **Noam Brown**

Meta AI Meta AI Meta AI


A BSTRACT


No-press Diplomacy is a complex strategy game involving both cooperation and
competition that has served as a benchmark for multi-agent AI research. While
self-play reinforcement learning has resulted in numerous successes in purely
adversarial games like chess, Go, and poker, self-play alone is insufficient for
achieving optimal performance in domains involving cooperation with humans.
We address this shortcoming by first introducing a planning algorithm we call
DiL-piKL that regularizes a reward-maximizing policy toward a human imitationlearned policy. We prove that this is a no-regret learning algorithm under a modified utility function. We then show that DiL-piKL can be extended into a self-play
reinforcement learning algorithm we call RL-DiL-piKL that provides a model of
human play while simultaneously training an agent that responds well to this human model. We used RL-DiL-piKL to train an agent we name Diplodocus. In a
200-game no-press Diplomacy tournament involving 62 human participants spanning skill levels from beginner to expert, two Diplodocus agents both achieved a
higher average score than all other participants who played more than two games,
and ranked first and third according to an Elo ratings model.


1 I NTRODUCTION


In two-player zero-sum (2p0s) settings, principled self-play algorithms converge to a minimax equilibrium, which in a balanced game ensures that a player will not lose in expectation regardless of
the opponent’s strategy (Neumann, 1928). This fact has allowed self-play, even without human
data, to achieve remarkable success in 2p0s games like chess (Silver et al., 2018), Go (Silver et al.,
2017), poker (Bowling et al., 2015; Brown & Sandholm, 2017), and Dota 2 (Berner et al., 2019). [1]
In principle, _any_ finite 2p0s game can be solved via self-play given sufficient compute and memory.
However, in games involving _cooperation_, self-play alone no longer guarantees good performance
when playing with humans, even with _infinite_ compute and memory. This is because in complex
domains there may be arbitrarily many conventions and expectations for how to cooperate, of which
humans may use only a small subset (Lerer & Peysakhovich, 2019). The clearest example of this
is language. A self-play agent trained from scratch without human data in a cooperative game involving free-form communication channels would almost certainly not converge to using English
as the medium of communication. Obviously, such an agent would perform poorly when paired
with a human English speaker. Indeed, prior work has shown that na¨ıve extensions of self-play from
scratch without human data perform poorly when playing with humans or human-like agents even in
dialogue-free domains that involve cooperation rather than just competition, such as the benchmark
games no-press Diplomacy (Bakhtin et al., 2021) and Hanabi (Siu et al., 2021; Cui et al., 2021).


_∗_ Equal first author contribution.
1 Dota 2 is a two-team zero-sum game, but the presence of full information sharing between teammates
makes it equivalent to 2p0s. Beyond 2p0s settings, self-play algorithms have also proven successful in highly
adversarial games like six-player poker Brown & Sandholm (2019).


1


Recently, (Jacob et al., 2022) introduced piKL, which models human behavior in many games better
than pure behavioral cloning (BC) on human data by regularizing inference-time planning toward a
BC policy. In this work, we introduce an extension of piKL, called DiL-piKL, that replaces piKL’s
single fixed regularization parameter _λ_ with a probability distribution over _λ_ parameters. We then
show how DiL-piKL can be combined with self-play reinforcement learning, allowing us to train a
strong agent that performs well with humans. We call this algorithm **RL-DiL-piKL** .


Using RL-DiL-piKL we trained an agent, Diplodocus, to play no-press Diplomacy, a difficult benchmark for multi-agent AI that has been actively studied in recent years (Paquette et al., 2019; Anthony
et al., 2020; Gray et al., 2020; Bakhtin et al., 2021; Jacob et al., 2022). We conducted a 200-game
no-press Diplomacy tournament with a diverse pool of human players, including expert humans, in
which we tested two versions of Diplodocus using different RL-DiL-piKL settings, and other baseline agents. All games consisted of one bot and six humans, with all players being anonymous for
the duration of the game. These two versions of Diplodocus achieved the top two average scores
in the tournament among all 48 participants who played more than two games, and ranked first and
third overall among all participants according to an Elo ratings model.


2 B ACKGROUND AND P RIOR WORK


Diplomacy is a benchmark 7-player mixed cooperative/competitive game featuring simultaneous
moves and a heavy emphasis on negotiation and coordination. In the no-press variant of the game,
there is no cheap talk communication. Instead, players only implicitly communicate through moves.


In the game, seven players compete for majority control of 34 “supply centers” (SCs) on a map.
On each turn, players simultaneously choose actions consisting of an order for each of their units to
hold, move, support or convoy another unit. If no player controls a majority of SCs and all remaining
players agree to a draw or a turn limit is reached then the game ends in a draw. In this case, we use
a common scoring system in which the score of player _i_ is _C_ _i_ [2] _[/]_ [ �] _i_ _[′]_ _[ C]_ _i_ [2] _[′]_ [, where] _[ C]_ _[i]_ [ is the number of]
SCs player _i_ owns. A more detailed description of the rules is provided in Appendix B.


Most recent successes in no-press Diplomacy use deep learning to imitate human behavior given a
corpus of human games. The first Diplomacy agent to leverage deep imitation learning was Paquette
et al. (2019). Subsequent work on no-press Diplomacy have mostly relied on a similar architecture
with some modeling improvements (Gray et al., 2020; Anthony et al., 2020; Bakhtin et al., 2021).


Gray et al. (2020) proposed an agent that plays an improved policy via one-ply search. It uses policy
and value functions trained on human data to to conduct search using regret minimization.


Several works explored applying self-play to compute improved policies. Paquette et al. (2019)
applied an actor-critic approach and found that while the agent plays stronger in populations of
other self-play agents, it plays worse against a population of human-imitation agents. Anthony
et al. (2020) used a self-play approach based on a modification of fictitious play in order to reduce
drift from human conventions. The resulting policy is stronger than pure imitation learning in both
1vs6 and 6vs1 settings but weaker than agents that use search. Most recently, Bakhtin et al. (2021)
combined one-ply search based on equilibrium computation with value iteration to produce an agent
called DORA. DORA achieved superhuman performance in a 2p0s version of Diplomacy without
human data, but in the full 7-player game plays poorly with agents other than itself.


Jacob et al. (2022) showed that regularizing inference-time search techniques can produce agents
that are not only strong but can also model human behaviour well. In the domain of no-press Diplomacy, they show that regularizing hedge (an equilibrium-finding algorithm) with a KL-divergence
penalty towards a human imitation learning policy can match or exceed the human action prediction
accuracy of imitation learning while being substantially stronger. KL-regularization toward human
behavioral policies has previously been proposed in various forms in single- and multi-agent RL
algorithms (Nair et al., 2018; Siegel et al., 2020; Nair et al., 2020), and was notably employed in
AlphaStar (Vinyals et al., 2019), but this has typically been used to improve sample efficiency and
aid exploration rather than to better model and coordinate with human play.


An alternative line of research has attempted to build human-compatible agents without relying
on human data (Hu et al., 2020; 2021; Strouse et al., 2021). These techniques have shown some
success in simplified settings but have not been shown to be competitive with humans in large-scale
collaborative environments.


2


2.1 M ARKOV G AMES


In this work, we focus on multiplayer Markov games (Shapley, 1953).


**Definition.** _An n-player Markov game_ ∆ _is a tuple ⟨S, A_ 1 _, . . ., A_ _n_ _, r_ 1 _, . . ., r_ _n_ _, p⟩_ _where S is the_
_state space, A_ _[i]_ _is the action space of player i (i_ = 1 _, . . ., n), r_ _i_ : _S × A_ 1 _× · · · × A_ _n_ _→_ R _is the_
_reward function for player i, f_ : _S × A_ 1 _× · · · × A_ _n_ _→_ _S is the transition function._


The goal of each player _i_, is to choose a policy _π_ _i_ ( _s_ ) : _S →_ ∆ _A_ _i_ that maximizes the expected
reward for that player, given the policies of all other players. In case of _n_ = 1, a Markov game
reduces to a Markov Decision Process (MDP) where an agent interacts with a fixed environment.


At each state _s_, each player _i_ simultaneously chooses an action _a_ _i_ from a set of actions _A_ _i_ . We
denote the actions of all players other than _i_ as _**a**_ _−i_ . Players may also choose a probability distribution over actions, where the probability of action _a_ _i_ is denoted _π_ _i_ ( _s, a_ _i_ ) or _σ_ _i_ ( _a_ _i_ ) and the vector of
probabilities is denoted _**π**_ _i_ ( _s_ ) or _**π**_ _i_ .


2.2 H EDGE


**Hedge** Littlestone & Warmuth (1994); Freund & Schapire (1997) is an iterative algorithm that converges to an equilibrium. We use variants of hedge for planning by using them to compute an
equilibrium policy on each turn of the game and then playing that policy.


Assume that after player _i_ chooses an action _a_ _i_ and all other players choose actions _a_ _−i_, player _i_
receives a reward of _u_ _i_ ( _a_ _i_ _,_ _**a**_ _−i_ ), where _u_ _i_ will come from our RL-trained value function. We denote
the average reward in hindsight for action _a_ _i_ up to iteration _t_ as _Q_ _[t]_ ( _a_ _i_ ) = [1] _t_ � _t_ _[′]_ _≤t_ _[u]_ _[i]_ [(] _[a]_ _[i]_ _[, a]_ _−_ _[t]_ _[′]_ _i_ [)][.]


On each iteration _t_ of hedge, the policy _**π**_ _i_ _[t]_ [(] _[a]_ _[i]_ [)][ is set according to] _**[ π]**_ _i_ _[t]_ [(] _[a]_ _[i]_ [)] _[ ∝]_ [exp] � _Q_ _[t][−]_ [1] ( _a_ _i_ ) _/κ_ _t−_ 1 �

where _κ_ _t_ is a temperature parameter. [2]



_t_ _[′]_ _≤t_ _[u]_ _[i]_ [(] _[a]_ _[i]_ _[, a]_ _−_ _[t]_ _[′]_ _i_ [)][.]



_t_ �



1
It is proven that if _κ_ _t_ is set to
~~_√_~~



It is proven that if _κ_ _t_ is set to ~~_√_~~ _t_ [then as] _[ t][ →∞]_ [the] _[ average]_ [ policy over all iterations converges to a]

coarse correlated equilibrium, though in practice it often comes close to a Nash equilibrium as well.
In all experiments we set _κ_ _t_ = 103 _S_ ~~_√_~~ _t_ _t_ [on iteration] _[ t]_ [, where] _[ S]_ _[t]_ [ is the observed standard deviation of]



In all experiments we set _κ_ _t_ = 10 ~~_√_~~ _t_ _t_ [on iteration] _[ t]_ [, where] _[ S]_ _[t]_ [ is the observed standard deviation of]

the player’s utility up to iteration _t_, based on a heuristic from Brown et al. (2017). A simpler choice
is to set _κ_ _t_ = 0, which makes the algorithm equivalent to fictitious play (Brown, 1951).


**Regret matching (RM)** (Blackwell et al., 1956; Hart & Mas-Colell, 2000) is an alternative
equilibrium-finding algorithm that has similar theoretical guarantees to hedge and was used in previously work on Diplomacy Gray et al. (2020); Bakhtin et al. (2021). We do not use this algorithm
but we do evaluate baseline agents that use RM.


2.3 DORA: S ELF - PLAY LEARNING IN M ARKOV GAMES


Our approach draws significantly from DORA (Bakhtin et al., 2021), which we describe in more
detail here. In this approach, the authors run an algorithm that is similar to past model-based
reinforcement-learning methods such as AlphaZero (Silver et al., 2018), except in place of Monte
Carlo tree search, which is unsound in simultaneous-action games such as Diplomacy or other imperfect information games, it instead uses an equilibrium-finding algorithm such as hedge or RM
to iteratively approximate a Nash equilibrium for the current state (i.e., one-step lookahead search).
A deep neural net trained to predict the policy is used to sample plausible actions for all players to
reduce the large action space in Diplomacy down to a tractable subset for the equilibrium-finding
procedure, and a deep neural net trained to predict state values is used to evaluate the results of
joint actions sampled by this procedure. Beginning with a policy and value network randomly initialized from scratch, a large number of self-play games are played and the resulting equilibrium
policies and the improved 1-step value estimates computed on every turn from equilibrium-finding
are added to a replay buffer used for subsequently improving the policy and value. Additionally, a
double-oracle (McMahan et al., 2003) method was used to allow the policy to explore and discover
additional actions, and the same equilibrium-finding procedure was also used at test time.


For the core update step, Bakhtin et al. (2021) propose Deep Nash Value Iteration (DNVI), a value
iteration procedure similar to Nash Q-Learning (Hu & Wellman, 2003), which is a generalization


2
We use _κ_ _t_ rather than _η_ used in Jacob et al. (2022) in order to clean up notation. _κ_ _t_ = 1 _/_ ( _η · t_ ).


3


of Q-learning (Watkins, 1989) from MDPs to Stochastic games. The idea of Nash-Q is to compute
equilibrium policies _σ_ in a subgame where the actions correspond to the possible actions in a current
state and the payoffs are defined using the current approximation of the value function. Bakhtin et al.
(2021) propose an equivalent update that uses a state value function _V_ ( _s_ ) instead of a state-action
value function _Q_ ( _s, a_ ):


_**V**_ ( _s_ ) _←_ (1 _−_ _α_ ) _**V**_ ( _s_ ) + _α_ ( _**r**_ + _γ_ � _σ_ ( _**a**_ _**[′]**_ ) _**V**_ ( _f_ ( _s,_ _**a**_ _**[′]**_ ))) (1)


_**a**_ _**[′]**_


where _α_ is the learning rate, _σ_ ( _·_ ) is the probability of joint action in equilibrium, _**a**_ _**[′]**_ is joint action,
and _f_ is the transition function. For 2p0s games and certain other game classes, this algorithm converges to a Nash equilibrium in the original stochastic game under the assumption that an exploration
policy is used such that each state is visited infinitely often .


The tabular approach of Nash-Q does not scale to large games such as Diplomacy. DNVI replaces
the explicit value function table and update rule in 1 with a value function parameterized by a neural
network, _**V**_ ( _s_ ; _θ_ _v_ ) and uses gradient descent to update it using the following loss:



_σ_ ( _**a**_ _**[′]**_ ) _**V**_ _f_ ( _s,_ _**a**_ _**[′]**_ ); _θ_ [ˆ] _v_ (2)
� � [�] [2]
_**a**_ _**[′]**_



ValueLoss( _θ_ _v_ ) = [1]

2



�



_**V**_ ( _s_ ; _θ_ _v_ ) _−_ _**r**_ ( _s_ ) _−_ _γ_ �



The summation used in 2 is not feasible in games with large action spaces as the number of joint
actions grow exponentially with the number of players. Bakhtin et al. (2021) address this issue by
considering only a subset of actions at each step. An auxiliary function, a policy proposal network
_π_ _i_ ( _s, a_ _i_ ; _θ_ _π_ ), models the probability that an action _a_ _i_ of player _i_ is in the support of the equilibrium _σ_ . Only the top- _k_ sampled actions from this distribution are considered when solving for the
equilibrium policy _σ_ and computing the above value loss. Once the equilibrium is computed, the
equilibrium policy is also used to further train the policy proposal network using cross entropy loss:



PolicyLoss( _θ_ _π_ ) = _−_ �


_i_



� _σ_ _i_ ( _a_ ) log _π_ _i_ ( _s, a_ _i_ ; _θ_ _π_ ) _._ (3)

_a_ _i_ _∈A_ _i_



Bakhtin et al. (2021) report that the resulting agent DORA does very well when playing with other
copies of itself. However, DORA performs poorly in games with 6 human human-like agents.


2.4 PI KL: M ODELING HUMANS WITH IMITATION - ANCHORED PLANNING


_Behavioral cloning (BC)_ is the standard approach for modeling human behaviors given data. Behavioral cloning learns a policy that maximizes the likelihood of the human data by gradient descent on
a cross-entropy loss. However, as observed and discussed in Jacob et al. (2022), BC often falls short
of accurately modeling or matching human-level performance, with BC models underperforming the
human players they are trained to imitate in games such as Chess, Go, and Diplomacy. Intuitively,
it might seem that initializing self-play with an imitation-learned policy would result in an agent
that is both strong and human-like. Indeed, Bakhtin et al. (2021) showed improved performance
against human-like agents when initializing the DORA training procedure from a human imitation
policy and value, rather than starting from scratch. However, we show in subsection 5.3 that such an
approach still results in policies that deviate from human-compatible equilibria.


Jacob et al. (2022) found that an effective solution was to perform search with a regularization
penalty proportional to the KL divergance from a human imitation policy. This algorithm is referred
to as **piKL** . The form of piKL we focus on in this paper is a variant of hedge called piKL-hedge, in
which each player _i_ seeks to maximize expected reward, while at the same time playing “close” to
a fixed **anchor policy** _**τ**_ _i_ . The two goals can be reconciled by defining a composite utility function
that adds a penalty based on the “distance” between the player policy and their anchor policy, with
coefficient _λ_ _i_ _∈_ [0 _, ∞_ ) scaling the penalty.


For each player _i_, we define _i_ ’s utility as a function of the agent policy _**π**_ _i_ _∈_ ∆( _A_ _i_ ) given policies
_**π**_ _−i_ of all other agents:


˜
_u_ _i,λ_ _i_ ( _**π**_ _i_ _,_ _**π**_ _−i_ ) := _u_ _i_ ( _**π**_ _i_ _,_ _**π**_ _−i_ ) _−_ _λ_ _i_ _D_ KL ( _**π**_ _i_ _∥_ _**τ**_ _i_ ) (4)


4


**Algorithm 1:** D I L- PI KL (for Player _i_ )

**Data:**  - _A_ _i_ set of actions for Player _i_ ;

      - _u_ _i_ reward function for Player _i_ ;

    - Λ _i_ a set of _λ_ values to consider for
Player _i_ ;

      - _β_ _i_ a belief distribution over _λ_ values for
Player _i_ .


1 **function** I NITIALIZE ()

2 _t ←_ 0

3 **for each** action _a_ _i_ _∈_ _A_ _i_ **do**

4 Q [0] _i_ [(] _[a]_ _[i]_ [)] _[ ←]_ [0]


5 **function** P LAY ()













Figure 1: DiL-piKL algorithm. Lines with highlights show
the main differences between this algorithm and piKL-Hedge
algorithm proposed in Jacob et al. (2022).



Figure 2: _λ_ _pop_ represents the commonknowledge belief about the _λ_ parameter or
distribution used by all players. _λ_ _agent_ represents the _λ_ value actually used by the agent to
determine its policy. By having _λ_ _agent_ differ
from _λ_ _pop_, DiL-piKL interpolates between an
equilibrium under the utility function _u_ _i_, behavioral cloning and best response to behavioral cloning policies. piKL assumed a common _λ_, which moved it along one axis of the
space. Our agent models and coordinates with
high- _λ_ players while playing a lower _λ_ itself.



This results in a modification of hedge such that on each iteration _t_, _**π**_ _i_ _[t]_ [(] _[a]_ _[i]_ [)][ is set according to]



_t−_ 1
_Q_ ( _a_ _i_ ) + _λ_ log _τ_ _i_ ( _a_ _i_ )
_**π**_ _i_ _[t]_ [(] _[a]_ _[i]_ [)] _[ ∝]_ [exp]
� _κ_ _t−_ 1 + _λ_



(5)
�



When _λ_ is large, the utility function is dominated by the KL-divergence term _λ_ _i_ _D_ KL ( _**π**_ _i_ _∥_ _**τ**_ _i_ ), and
so the agent will naturally tend to play a policy _**π**_ _i_ close to the anchor policy _**τ**_ _i_ . When _λ_ _i_ is small, the
dominating term is the rewards _u_ _i_ ( _**π**_ _i_ _,_ _**a**_ _[t]_ _−i_ [)][ and so the agent will tend to maximize reward without]
as closely matching the anchor policy _**τ**_ _i_ .


3 D ISTRIBUTIONAL L AMBDA PI KL (D I L- PI KL)


piKL trades off between the strength of the agent and the closeness to the anchor policy using a
single fixed _λ_ parameter. In practice, we find that sampling _λ_ from a probability distribution each
iteration produces better performance. In this section, we introduce **distributional lambda piKL**
**(DiL-piKL)**, which replaces the single _λ_ parameter in piKL with a probability distribution _β_ over _λ_
values. On each iteration, each player _i_ samples a _λ_ value from _β_ _i_ and then chooses a policy based
on Equation 5 using that sampled _λ_ . Figure 1 highlights the difference between piKL and DiL-piKL.


One interpretation of DiL-piKL is that each choice of _λ_ is an agent **type**, where agent types with high
_λ_ choose policies closer to _**τ**_ while agent types with low _λ_ choose policies that are more “optimal”
and less constrained to a common-knowledge anchor policy. A priori, each player is randomly sampled from this population of agent types, and the distribution _β_ _i_ represents the common-knowledge
uncertainty about which of the agent types player _i_ may be. Another interpretation is that piKL
assumed an exponential relation between action EV and likelihood, whereas DiL-piKL results in a
fatter-tailed distribution that may more robustly model different playing styles or game situations.


5


3.1 C OORDINATING WITH PI KL POLICIES


While piKL and DiL-piKL are intended to model human behavior, an optimal policy in cooperative
environments should be closer to a _best response_ to this distribution. Selecting different _λ_ values for
the common-knowledge population versus the policy the agent actually plays allows us to interpolate
between BC, best response to BC, and equilibrium policies (Figure 2). In practice, our agent samples
from _β_ _i_ during equilibrium computation but ultimately plays a low _λ_ policy, modeling the fact that
other players are unaware of our agent’s true type.


3.2 T HEORETICAL P ROPERTIES OF D I L- PI KL


DiL-piKL can be understood as a _sampled_ form of follow-the-regularized-leader (FTRL). Specifically, one can think of Algorithm 1 as an instantiation of FTRL over the Bayesian game induced by
the set Λ _i_ = supp _β_ _i_ of types _λ_ _i_ and the regularized utilities ˜ _u_ _i,λ_ _i_ of each player _i_ . In the appendix
we show that when a player _i_ learns using DiL-piKL, the distributions _**π**_ _i,λ_ _[t]_ [for any type] _[ λ]_ _[i]_ _[ ∈]_ [Λ] _[i]_ [ are]
no-regret with respect to the regularized utilities ˜ _u_ _i,λ_ _i_ defined in (4). Formally:


**Theorem 1** (abridged) **.** _Let W be a bound on the maximum absolute value of any payoff in the game,_
_and Q_ _i_ := _n_ 1 _i_ � _a∈A_ _i_ [log] _**[ τ]**_ _[i]_ [(] _[a]_ [)] _[. Then, for any player][ i][, type][ λ]_ _[i]_ _[ ∈]_ [Λ] _[i]_ _[, and number of iterations][ T]_ _[,]_

_the regret cumulated can be upper bounded as_



_T_
�
� _t_ =1



�



g _T_

_, Tη_ + [lo][g] _[ n]_ _[i]_
_λ_ _i_ � _η_



+ _ρ_ _i,λ_ _i_ _,_
_η_



_≤_ _[W]_ [ 2]




[ 2] 2 log _T_

min
4 � _λ_ _i_



max
_**π**_ _∈_ ∆( _A_ _i_ )



� _u_ ˜ _i,λ_ _i_ ( _**π**_ _,_ _**a**_ _[t]_ _−i_ [)] _[ −]_ _[u]_ [˜] _[i,λ]_ _i_ [(] _**[π]**_ _i,λ_ _[t]_ _i_ _[,]_ _**[ a]**_ _−_ _[t]_ _i_ [)]


_t_ =1



_where the game constant ρ_ _i,λ_ _i_ _is defined as ρ_ _i,λ_ _i_ := _λ_ _i_ (log _n_ _i_ + _Q_ _i_ ) _._



The traditional analysis of FTRL is not applicable to DiL-piKL because the utility functions, as
well as their gradients, can be unbounded due to the nonsmoothness of the regularization term
_−λ_ _i_ _D_ KL ( _**π**_ _∥_ _**τ**_ _i_ ) that appears in the regularized utility function ˜ _u_ _i,λ_ _i_, and therefore a more sophisticated analysis needs to be carried out. Furthermore, even in the special case of a single type ( _i.e._,
a singleton set Λ _i_ ), where DiL-piKL coincides with piKL, the above guarantee significantly refines
the analysis of piKL in two ways. First, it holds no matter the choice of stepsize _η >_ 0, thus implying a _O_ (log _T/_ ( _Tλ_ _i_ )) regret bound without assumptions on _η_ other than _η_ = Ω(1). Second, in
the cases in which _λ_ _i_ is tiny, by choosing _η_ = Θ(1 _/√T_ ) we recover a sublinear guarantee (of order

_√T_ ) on the regret.


In 2p0s games, the logarithmic regret of Theorem 1 immediately implies that the _average policy_
_**π**_ ¯ _i,λ_ _[T]_ _i_ [:=] _T_ [1] � _Tt_ =1 _**[π]**_ _i,λ_ _[t]_ _i_ [of each player] _[ i]_ [ is a] _[ C]_ [ lo] _T_ [g] _[ T]_ -approximate Bayes-Nash equilibrium strategy.



_T_ ) on the regret.



_T_ [1] � _Tt_ =1 _**[π]**_ _i,λ_ _[t]_ _i_ [of each player] _[ i]_ [ is a] _[ C]_ [ lo] _T_ [g] _[ T]_



¯ [g]
_**π**_ _i,λ_ _i_ [:=] _T_ � _t_ =1 _**[π]**_ _i,λ_ _i_ [of each player] _[ i]_ [ is a] _T_ -approximate Bayes-Nash equilibrium strategy.

In fact, a strong guarantee on the _last-iterate_ convergence of the algorithm can be obtained too:


**Theorem 2** (abridged; Last-iterate convergence of piKL in 2p0s games) **.** _When both players in a_
_2p0s game learn using DiL-piKL for T iterations, their policies converge almost surely to the unique_
_Bayes-Nash equilibrium_ ( _**π**_ _i,λ_ _[∗]_ _i_ [)] _[ of the regularized game defined by utilities]_ [ ˜] _[u]_ _[i,λ]_ _i_ [(4)] _[.]_


The last-iterate guarantee stated in Theorem 2 crucially relies on the strong convexity of the regularized utilities, and conceptually belongs with related efforts in showing last-iterate convergence
of online learning methods. However, a key difficulty that sets apart Theorem 2 is the fact that the
learning agents observe _sampled_ actions from the opponents, which makes the proof of the result
(as well as the obtained convergence rate) different from prior approaches.


4 D ESCRIPTION OF D IPLODOCUS


By replacing the equilibrium-finding algorithm used in DORA with DiL-piKL, we hypothesize that
we can learn a strong and human-compatible policy as well as a value function that can accurately
evaluate game states, assuming strong and human-like continuation policies. We call this self-play
algorithm RL-DiL-piKL. We use RL-DiL-piKL to train value and policy proposal networks and use
DiL-piKL during test-time search.


6


4.1 T RAINING


Our training algorithm closely follows that of DORA, described in Section 2.3. The loss functions
used are identical to DORA and the training procedure is largely the same, except in place of RM to
compute the equilibrium policy _σ_ on each turn of a game during self-play, we use DiL-piKL with a
_λ_ distribution and human imitation anchor policy _τ_ that is fixed for all of training. See Appendix H
for a detailed description of differences between DORA and RL-DiL-piKL.


4.2 T EST -T IME S EARCH


Following Bakhtin et al. (2021), at evaluation time we perform 1-ply lookahead where on each turn
we sample up to 30 of the most likely actions for each player from the RL policy proposal network.
However, rather than using RM to compute the equilibrium _σ_, we apply DiL-piKL.


As also mentioned previously in Section 3, while our agent samples _λ_ _i_ from the probability distribution _β_ _i_ when computing the DiL-piKL equilibrium, the agent chooses its own action to actually play using a fixed low _λ_ . For all experiments, including all ablations, the agent uses the
same BC anchor policy. For DiL-piKL experiments for each player _i_ we set _β_ _i_ to be uniform over
_{_ 10 _[−]_ [4] _,_ 10 _[−]_ [3] _,_ 10 _[−]_ [2] _,_ 10 _[−]_ [1] _}_ and play according to _λ_ = 10 _[−]_ [4], except for the first turn of the game. On
the first turn we instead sample from _{_ 10 _[−]_ [2] _,_ 10 _[−]_ [1] _[.]_ [5] _,_ 10 _[−]_ [1] _,_ 10 _[−]_ [0] _[.]_ [5] _}_ and play according to _λ_ = 10 _[−]_ [2],
so that the agent plays more diverse openings, which more closely resemble those that humans play.


5 E XPERIMENTS


We first compare the performance of two variants of Diplodocus in a population of prior agents and
other baseline agents. We then report results of Diplodocus playing in a tournament with humans.


5.1 E XPERIMENTAL SETUP


In order to measure the ability of agents to play well against a diverse set of opponents, we play
many games between AI agents where each of the seven players are sampled randomly from a
population of baselines (listed in Appendix D) or the agent to be tested. We report scores for each
of the following algorithms against the baseline population:


**Diplodocus-Low** and **Diplodocus-High** are the proposed agents that use RL-DiL-piKL during training with 2 player types _{_ 10 _[−]_ [4] _,_ 10 _[−]_ [1] _}_ and _{_ 10 _[−]_ [2] _,_ 10 _[−]_ [1] _}_, respectively.
**DORA** is an agent that is trained via self-play and uses RM as the search algorithm during training
and test-time. Both the policy and the value function are randomly initialized at the start of training.
**DNVI** is similar to DORA, but the policy proposal and value networks are initialized from human
BC pretraining.
**DNVI-NPU** is similar to DNVI, but during training only the RL value network is updated. The
policy proposal network is still trained but never fed back to self-play workers, to limit self-play
drift from human conventions. The final RL policy proposal network is only used at the end, at test
time (along with the RL value network).
**BRBot** is an approximate best response to the BC policy. It was trained the same as Diplodocus,
except that during training the agent plays one distinguished player each game with _λ_ = 0 while all
other players use _λ ≈∞_ .
**SearchBot**, a one-step lookahead equilibrium search agent from (Gray et al., 2020), evaluated using
their published model.
**HedgeBot** is an agent similar to SearchBot (Gray et al., 2020) but using our latest architecture and
using hedge rather than RM as the equilibrium-finding algorithm.
**FPPI-2** and **SL** are two agents from (Anthony et al., 2020), evaluated using their published model.


After computing these population scores, as a final evaluation we organized a tournament where
we evaluated four agents for 50 games each in a population of online human participants. We
evaluated two baseline agents, BRBot and DORA, and two of our new agents, Diplodocus-Low and
Diplodocus-High.


In order to limit the duration of games to only a few hours, these games used a time limit of 5
minutes per turn and a stochastic game-end rule where at the beginning of each game year between


7


**Agent** **Score against population**


Diplodocus-Low 29% _±_ 1%
Diplodocus-High 28% _±_ 1%
DNVI-NPU (retrained) (Bakhtin et al., 2021) 20% _±_ 1%
BRBot 18% _±_ 1%
DNVI (retrained) (Bakhtin et al., 2021) 15% _±_ 1%
HedgeBot (retrained) (Jacob et al., 2022) 14% _±_ 1%
DORA (retrained) (Bakhtin et al., 2021) 13% _±_ 1%


FPPI-2 (Anthony et al., 2020) 9% _±_ 1%
SearchBot (Gray et al., 2020) 7% _±_ 1%
SL (Anthony et al., 2020) 6% _±_ 1%


Table 1: Performance of different agents in a population of various agents. Agents above the line were trained
using identical neural network architectures. Agents below the line were evaluated using the models and the
parameters provided by the authors. The _±_ shows one standard error.


1909 and 1912 the game ends immediately with 20% chance per year, increasing in 1913 to a 40%
chance. Players were not told which turn the game would end on for a specific game, but were
told the distribution it was sampled from. Our agents were also trained based on this distribution. [3]
Players were recruited from Diplomacy mailing lists and from webdiplomacy.net. In order to
mitigate the risk of cheating by collusion, players were paid hourly rather than based on in-game
performance. Each game had exactly one agent and six humans. The players were informed that
there was an AI agent in each game, but did not know which player was the bot in each particular
game. In total 62 human participants played 200 games with 44 human participants playing more
than two games and 39 human participants playing at least 5 games.


5.2 E XPERIMENTAL R ESULTS


We first report results for our agents in the fixed population described in Appendix D. The results,
shown in Table 1, show Diplodocus-Low and Diplodocus-High perform the best by a wide margin.


We next report results for the human tournament in Table 2. For each listed player, we report their
average score, Elo rating, and rank within the tournament based on Elo among players who played
at least 5 games. Elo ratings were computed using a standard generalization of BayesElo (Coulom,
2005) to multiple players (Hunter, 2004) (see Appendix I for details). This gives similar rankings as
average score, but also attempts to correct for both the average strength of the opponents, since some
games may have stronger or weaker opposition, as well as for which of the seven European powers
a player was assigned in each game, since some starting positions in Diplomacy are advantaged over
others. To regularize the model, a weak Bayesian prior was applied such that each player’s rating
was normally distributed around 0 with a standard deviation of around 350 Elo.


The results show that Diplodocus-High performed best among all the humans by both Elo and average score. Diplodocus-Low followed closely behind, ranking second according to average score
and third by Elo. BRBot performed relatively well, but ended ranked below that of both DiL-piKL
agents and several humans. DORA performed relatively poorly.


Two participants achieved a higher average score than the Diplodocus agents, a player averaging
35% but who only played two games, and a player with a score of 29% who played only one game.


We note that given the large statistical error margins, the results in Table 2 do not conclusively
demonstrate that Diplodocus outperforms the best human players, nor do they alone demonstrate
an unambiguous separation between Diplodocus and BRBot. However, the results do indicate that
Diplodocus performs at least at the level of expert players in this population of players with diverse
skill levels. Additionally, the superior performance of both Diplodocus agents compared to BRBot
is consistent with the results from the agent population experiments in Table 1.


3 Games were run by a third-party contractor. In contradiction of the criteria we specified, the contractor
ended games artificially early for the first _∼_ 80 games played in the tournament, with end dates of 1909-1911
being more common than they should have been. We immediately corrected this problem once it was identified.


8


**Rank** **Elo** **Avg Score** **# Games**


**Diplodocus-High** 1 181 27% _±_ 4% 50
Human 2 162 25% _±_ 6% 13
**Diplodocus-Low** 3 152 26% _±_ 4% 50
Human 4 138 22% _±_ 9% 7

Human 5 136 22% _±_ 3% 57

**BRBot** 6 119 23% _±_ 4% 50

Human 7 102 18% _±_ 8% 8

Human 8 96 17% _±_ 3% 51

_· · ·_ _· · ·_ _· · ·_ _· · ·_ _· · ·_

**DORA** 32 -20 13% _±_ 3% 50

_· · ·_ _· · ·_ _· · ·_ _· · ·_ _· · ·_

Human 43 -187 1% _±_ 1% 7


Table 2: Performance of four different agents in a population of human players, ranked by Elo, among all 43
participants who played at least 5 games. The _±_ shows one standard error.



20


15


10


5



Score vs 6 HedgeBot agents


0 100000 200000 300000
Num updates



60


40


20



Prediction accuracy of human actions


0 100000 200000 300000
Num updates



Diplodocus-High

Diplodocus-Low

DNVI-NPU

DNVI

DORA



Figure 3: Performance of different agents as a function of the number of RL training steps. **Left:** Scores
against 6 human-like HedgeBot agents. The gray dotted line at score 1 _/_ 7 _≈_ 14 _._ 3% corresponds to tying
HedgeBot. The error bars show one standard error. **Right:** Order prediction accuracy of each agent’s raw
RL policy on a held-out set of human games. The gray dotted line corresponds to the behavioral cloning
policy. **Overall:** Diplodocus-High achieves a high score while also maintaining high prediction accuracy.
Unregularized agents DNVI and DORA do far worse on both metrics.


In addition to the tournament, we asked three expert human players to evaluate the strength of the
agents in the tournament games based on the quality of their actions. Games were presented to
these experts with anonymized labels so that the experts were _not_ aware of which agent was which
in each game when judging that agent’s strategy. All the experts picked a Diplodocus agent as
the strongest agent, though they disagreed about whether Diplodocus-High or Diplodocus-Low was
best. Additionally, all experts indicated one of the Diplodocus agents as the one they would most
like to cooperate with in a game. We provide detailed responses in Appendix C.


5.3 RL TRAINING COMPARISON


Figure 3 compares different RL agents across the course of training. To simplify the comparison,
we vary the training methods for the value and policy proposal networks, but use the same search
setting at evaluation time.


As a proxy for agent strength, we measure the average score of an agent vs 6 copies of HedgeBot.
As a proxy for modeling humans, we compute prediction accuracy of human moves on a validation
dataset of roughly 630 games held out from training of the human BC model, i.e., how often the most
probable action under the policy corresponds to the one chosen by a human. Similar to Bakhtin et al.
(2021), we found that agents without biasing techniques (DORA and DNVI) diverge from human
play as training progress. By contrast, Diplodocus-High achieves significant improvement in score
while keeping the human prediction accuracy high.


9


6 D ISCUSSION


In this work we describe RL-DiL-piKL and use it to train an agent for no-press Diplomacy that
placed first in a human tournament. We ascribe Diplodocus’s success in Diplomacy to two ideas.


First, DiL-piKL models a population of player types with different amounts of regularization to a
human policy while ultimately playing a strong (low- _λ_ ) policy itself. This improves upon simply
playing a best response to a BC policy by accounting for the fact that humans are less likely to play
highly suboptimal actions and by reducing overfitting of the best response to the BC policy. Second,
incorporating DiL-piKL in self-play allows us to learn an accurate value function in a diversity of
situations that arise from strong and human-like players. Furthermore, this value assumes a human
continuation policy that makes fewer blunders than the BC policy, allowing us to correctly estimate
the values of positions that require accurate play (such as stalemate lines).


In conclusion, combining human imitation, planning, and RL presents a promising avenue for building agents for complex cooperative and mixed-motive environments. Further work could explore
regularized search policies that condition on more complex human behavior, including dialogue.


R EFERENCES


Thomas Anthony, Tom Eccles, Andrea Tacchetti, J´anos Kram´ar, Ian Gemp, Thomas Hudson,
Nicolas Porcel, Marc Lanctot, Julien Perolat, Richard Everett, Satinder Singh, Thore Graepel, and Yoram Bachrach. Learning to play no-press diplomacy with best response policy
iteration. In H. Larochelle, M. Ranzato, R. Hadsell, M. F. Balcan, and H. Lin (eds.), _Ad-_
_vances in Neural Information Processing Systems_, volume 33, pp. 17987–18003. Curran As[sociates, Inc., 2020. URL https://proceedings.neurips.cc/paper/2020/file/](https://proceedings.neurips.cc/paper/2020/file/d1419302db9c022ab1d48681b13d5f8b-Paper.pdf)
[d1419302db9c022ab1d48681b13d5f8b-Paper.pdf.](https://proceedings.neurips.cc/paper/2020/file/d1419302db9c022ab1d48681b13d5f8b-Paper.pdf)


Anton Bakhtin, David Wu, Adam Lerer, and Noam Brown. No-press diplomacy from scratch. In
_Thirty-Fifth Conference on Neural Information Processing Systems_, 2021.


Christopher Berner, Greg Brockman, Brooke Chan, Vicki Cheung, Przemysław Debiak, Christy
Dennison, David Farhi, Quirin Fischer, Shariq Hashme, Chris Hesse, et al. Dota 2 with large
scale deep reinforcement learning. _arXiv preprint arXiv:1912.06680_, 2019.


David Blackwell et al. An analog of the minimax theorem for vector payoffs. _Pacific Journal of_
_Mathematics_, 6(1):1–8, 1956.


Michael Bowling, Neil Burch, Michael Johanson, and Oskari Tammelin. Heads-up limit hold’em
poker is solved. _Science_, 347(6218):145–149, 2015.


George W Brown. Iterative solution of games by fictitious play. _Activity analysis of production and_
_allocation_, 13(1):374–376, 1951.


Noam Brown and Tuomas Sandholm. Superhuman AI for heads-up no-limit poker: Libratus beats
top professionals. _Science_, pp. eaao1733, 2017.


Noam Brown and Tuomas Sandholm. Superhuman AI for multiplayer poker. _Science_, 365(6456):
885–890, 2019.


Noam Brown, Christian Kroer, and Tuomas Sandholm. Dynamic thresholding and pruning for regret
minimization. In _Proceedings of the AAAI Conference on Artificial Intelligence_, volume 31, 2017.


[R´emi Coulom. Bayeselo. https://www.remi-coulom.fr/Bayesian-Elo/#theory,](https://www.remi-coulom.fr/Bayesian-Elo/#theory)
2005.


Brandon Cui, Hengyuan Hu, Luis Pineda, and Jakob Foerster. K-level reasoning for zero-shot
coordination in hanabi. _Advances in Neural Information Processing Systems_, 34:8215–8228,
2021.


Brandon Fogel. To whom tribute is due: The next step in scoring systems, 2020.
URL [http://windycityweasels.org/wp-content/uploads/2020/04/](http://windycityweasels.org/wp-content/uploads/2020/04/2020-03-To-Whom-Tribute-Is-Due-The-Next-Step-in-Scoring-Systems.pdf)
[2020-03-To-Whom-Tribute-Is-Due-The-Next-Step-in-Scoring-Systems.](http://windycityweasels.org/wp-content/uploads/2020/04/2020-03-To-Whom-Tribute-Is-Due-The-Next-Step-in-Scoring-Systems.pdf)
[pdf.](http://windycityweasels.org/wp-content/uploads/2020/04/2020-03-To-Whom-Tribute-Is-Due-The-Next-Step-in-Scoring-Systems.pdf)


10


Yoav Freund and Robert E Schapire. A decision-theoretic generalization of on-line learning and an
application to boosting. _Journal of computer and system sciences_, 55(1):119–139, 1997.


Jonathan Gray, Adam Lerer, Anton Bakhtin, and Noam Brown. Human-level performance in nopress diplomacy via equilibrium search. In _International Conference on Learning Representa-_
_tions_, 2020.


Sergiu Hart and Andreu Mas-Colell. A simple adaptive procedure leading to correlated equilibrium.
_Econometrica_, 68(5):1127–1150, 2000.


Hengyuan Hu, Adam Lerer, Alex Peysakhovich, and Jakob Foerster. “other-play” for zero-shot
coordination. In _International Conference on Machine Learning_, pp. 4399–4410. PMLR, 2020.


Hengyuan Hu, Adam Lerer, Brandon Cui, Luis Pineda, David Wu, Noam Brown, and Jakob Foerster.
Off-belief learning. In _International Conference on Machine Learning_ . PMLR, 2021.


Junling Hu and Michael P Wellman. Nash q-learning for general-sum stochastic games. _Journal of_
_machine learning research_, 4(Nov):1039–1069, 2003.


David R. Hunter. Mm algorithms for generalized bradley-terry models. _The annals of statistics_,
32.1:384–406, 2004.


Athul Paul Jacob, David J Wu, Gabriele Farina, Adam Lerer, Hengyuan Hu, Anton Bakhtin, Jacob Andreas, and Noam Brown. Modeling strong and human-like gameplay with kl-regularized
search. In _International Conference on Machine Learning_, pp. 9695–9728. PMLR, 2022.


Adam Lerer and Alexander Peysakhovich. Learning existing social conventions via observationally augmented self-play. In _Proceedings of the 2019 AAAI/ACM Conference on AI, Ethics, and_
_Society_, pp. 107–114. ACM, 2019.


Nick Littlestone and Manfred K Warmuth. The weighted majority algorithm. _Information and_
_computation_, 108(2):212–261, 1994.


Brendan McMahan, Geoffrey Gordon, and Avrim Blum. Planning in the presence of cost functions
controlled by an adversary. In _International conference on machine learning_, pp. 536—-543,
2003.


Ashvin Nair, Bob McGrew, Marcin Andrychowicz, Wojciech Zaremba, and Pieter Abbeel. Overcoming exploration in reinforcement learning with demonstrations. In _2018 IEEE international_
_conference on robotics and automation (ICRA)_, pp. 6292–6299. IEEE, 2018.


Ashvin Nair, Murtaza Dalal, Abhishek Gupta, and Sergey Levine. Accelerating online reinforcement
learning with offline datasets. _arXiv preprint arXiv:2006.09359_, 2020.


J v Neumann. Zur theorie der gesellschaftsspiele. _Mathematische annalen_, 100(1):295–320, 1928.


Philip Paquette, Yuchen Lu, Seton Steven Bocco, Max Smith, O-G Satya, Jonathan K Kummerfeld,
Joelle Pineau, Satinder Singh, and Aaron C Courville. No-press diplomacy: Modeling multi-agent
gameplay. In _Advances in Neural Information Processing Systems_, pp. 4474–4485, 2019.


Lloyd S Shapley. Stochastic games. _Proceedings of the national academy of sciences_, 39(10):
1095–1100, 1953.


Noah Y Siegel, Jost Tobias Springenberg, Felix Berkenkamp, Abbas Abdolmaleki, Michael Neunert, Thomas Lampe, Roland Hafner, Nicolas Heess, and Martin Riedmiller. Keep doing
what worked: Behavioral modelling priors for offline reinforcement learning. _arXiv preprint_
_arXiv:2002.08396_, 2020.


David Silver, Julian Schrittwieser, Karen Simonyan, Ioannis Antonoglou, Aja Huang, Arthur Guez,
Thomas Hubert, Lucas Baker, Matthew Lai, Adrian Bolton, et al. Mastering the game of go
without human knowledge. _Nature_, 550(7676):354, 2017.


11


David Silver, Thomas Hubert, Julian Schrittwieser, Ioannis Antonoglou, Matthew Lai, Arthur Guez,
Marc Lanctot, Laurent Sifre, Dharshan Kumaran, Thore Graepel, et al. A general reinforcement
learning algorithm that masters chess, shogi, and go through self-play. _Science_, 362(6419):1140–
1144, 2018.


Ho Chit Siu, Jaime Pe˜na, Edenna Chen, Yutai Zhou, Victor Lopez, Kyle Palko, Kimberlee Chang,
and Ross Allen. Evaluation of human-ai teams for learned and rule-based agents in hanabi. _Ad-_
_vances in Neural Information Processing Systems_, 34:16183–16195, 2021.


DJ Strouse, Kevin McKee, Matt Botvinick, Edward Hughes, and Richard Everett. Collaborating
with humans without human data. _Advances in Neural Information Processing Systems_, 34:
14502–14515, 2021.


Oriol Vinyals, Igor Babuschkin, Wojciech M Czarnecki, Micha¨el Mathieu, Andrew Dudzik, Junyoung Chung, David H Choi, Richard Powell, Timo Ewalds, Petko Georgiev, et al. Grandmaster
level in starcraft ii using multi-agent reinforcement learning. _Nature_, 575(7782):350–354, 2019.


Christopher John Cornish Hellaby Watkins. Learning from delayed rewards. 1989.


A A UTHOR C ONTRIBUTIONS


A. Bakhtin primarily contributed to RL, infrastructure, experimentation, and direction. D. J. Wu
primarily contributed to RL and infrastructure. A. Lerer primarily contributed to DiL-piKL, infrastructure, and direction. J. Gray primarily contributed to infrastructure. A. P. Jacob primarily
contributed to DiL-piKL and experimentation. G. Farina primarily contributed to theory and DiLpiKL. A. H. Miller primarily contributed to experimentation. N. Brown primarily contributed to
DiL-piKL, experimentation, and direction.


B D ESCRIPTION OF D IPLOMACY


The rules of no-press Diplomacy are complex; a full description is provided by Paquette et al. (2019).
No-press Diplomacy is a seven-player zero-sum board game in which a map of Europe is divided
into 75 provinces. 34 of these provinces contain supply centers (SCs), and the goal of the game is
for a player to control a majority (18) of the SCs. Each players begins the game controlling three or
four SCs and an equal number of units.


The game consists of three types of phases: movement phases in which each player assigns an order
to each unit they control, retreat phases in which defeated units retreat to a neighboring province,
and adjustment phases in which new units are built or existing units are destroyed.


During a movement phase, a player assigns an order to each unit they control. A unit’s order may be
to hold (defend its province), move to a neighboring province, convoy a unit over water, or support
a neighboring unit’s hold or move order. Support may be provided to units of any player. We refer
to a tuple of orders, one order for each of a player’s units, as an **action** . That is, each player chooses
one action each turn. There are an average of 26 valid orders for each unit (Paquette et al., 2019), so
the game’s branching factor is massive and on some turns enumerating all actions is intractable.


Importantly, all actions occur simultaneously. In live games, players write down their orders and
then reveal them at the same time. This makes Diplomacy an imperfect-information game in which
an optimal policy may need to be stochastic in order to prevent predictability.


Diplomacy is designed in such a way that cooperation with other players is almost essential in order
to achieve victory, even though only one player can ultimately win.


A game may end in a draw on any turn if all remaining players agree. Draws are a common outcome
among experienced players because players will often coordinate to prevent any individual from
reaching 18 centers. The two most common scoring systems for draws are **draw-size scoring (DSS)**,
in which all surviving players equally split a win, and **sum-of-squares scoring (SoS)**, in which
player _i_ receives a score of _C_ _i_ [2]
~~�~~ _j∈N_ _[C]_ _j_ [2] [, where] _[ C]_ _[i]_ [ is the number of SCs that player] _[ i]_ [ controls (Fogel,]

2020). Throughout this paper we use SoS scoring except in anonymous games against humans
where the human host chooses a scoring system.


12


C E XPERT EVALUATION OF THE AGENTS


The anonymous format of the tournament aimed at reducing possible biases of players towards the
agent, e.g., trying to collectively eliminate the agents as targeting the agent is a simple way to break
the symmetry. At the same time a significant property of Diplomacy is knowing the play styles of
different players and using this knowledge to make decision of whom to trust and whom to chose
as an ally. To evaluates this aspect of the game play we asked for qualitative feedback from three
Diplomacy experts. Each player was given 7 games (one per power) from each of the 4 different
agents that played in the tournament. The games evaluated by each expert were disjoint from the
games evaluated by the other experts. The games were anonymized such that the experts were not
able to tell which agent played in the game based on the username or from the date. We asked a few
questions about the game play of each agent independently and then asked the experts to choose the
best agent for strength and human-like behavior. The experts referred to the agents as Agent1, ...,
Agent4, but we de-anonymized the agents in the answers below.


C.1 O VERALL


W HAT IS THE STRONGEST AGENT ?


**Expert 1** I think Diplodocus-Low was the strongest, then BRBot closely followed by DiplodocusHigh. DORA is a distant third.


**Expert 2** Diplodocus-High.


**Expert 3** Diplodocus-Low. This feels stronger than a human in certain ways while still being very
human-like.


W HAT IS THE MOST HUMAN - LIKE / BOT - LIKE AGENT ?


**Expert 1** Most human-like is Diplodocus-High. A boring human, but a human nonetheless.
Diplodocus-Low is not far behind, then BRBot and DORA both of which are very non-human albeit
in very different ways.


**Expert 2** Diplodocus-High.


**Expert 3** Diplodocus-Low.


W HAT IS THE AGENT YOU ’ D LIKE TO COOPERATE WITH ?


**Expert 1** This is the most interesting question. I think Diplodocus-Low, because I like how it
plays - we’d “vibe” - but also because I think it is quite predictable in what motivates it to change
alliances. That’s potentially exploitable, even with the strong tactics it has. I’d least like to work with
Diplodocus-High as it seems to be very much in it for itself. I suspect it would be quite unpleasant
to play against as it is tactically excellent and seems hard to work with.


I’d love to be on a board with DORA, as I’d expect my chances to solo to go up dramatically! It
would be a very fun game so long as you weren’t on the receiving end of some of its play.


**Expert 2** Diplodocus-High.


**Expert 3** Diplodocus-Low. Diplodocus-High is also strong, but seems much less interesting to
play with, because of the way it commits to alliances without taking into account who is actually
willing to work with it. This limits what a human can do to change their situation quite a lot and
would be fairly frustrating in the position of a neighbour being attacked by it.


BRBot and DORA feel too weak to be particularly interesting.


13


C.2 DORA


H OW WOULD YOU EVALUATE THE OVERALL STRENGTH OF THE AGENT ?


**Expert 1** Not great. There’s a lot to criticize here - from bad opening play (Russia = bonkers),
to poor defense (Turkey) and just generally bad tactics and strategy compared to the other agents
(France attacking Italy when Italy is their only ally was an egregious example of this).


**Expert 2** Very weak. Seemed to invite its own demise with the way it routinely picked fights in
theaters it had no business being in and failing to cooperate with neighbors


**Expert 3** Poor. It is bad at working with players, and it makes easily avoidable blunders even
when working alone.


H OW WOULD YOU EVALUATE THE ABILITY OF THE AGENT TO COOPERATE ?


**Expert 1** It seems to make efforts, but it also seems to misjudge what humans are likely to do.
There’s indicative support orders and they’re pretty good, but it also doesn’t seem to understand or
account for vindictiveness over always playing best. The Turkey game where it repeatedly seems to
expect Russia to not attack is an example of this.


**Expert 2** Poor. Seemed to pick fights without seeing or soliciting support necessary to win, failed
to support potential allies in useful ways to take advantage of their position.


**Expert 3** Middling to Poor. It very occasionally enters good supports but it often enters bad ones,
and has a habit of attacking too many people at once (and not considering that attacking those people
will turn them against it). It has a habit of annoying many players and doing badly as a result.


C.3 BRB OT


H OW WOULD YOU EVALUATE THE OVERALL STRENGTH OF THE AGENT ?


**Expert 1** The agent has solid, at least human level tactics and clearly sees opportunities to advance
and acts accordingly. Sometimes this is to the detriment of the strategic position, but the balance is
fair given the gunboat nature of the games. Overall, the bot feels naturally to be in the “better than
average human” range rather than super-human, but the results indicate that it performs at a higher
level than the “feeling” it gives. It has a major opportunity for improvement, discussed in the next
point.


**Expert 2** Overall, seemed fairly weak and seemed to be able to succeed most frequently when
benefiting from severe mistakes from neighboring agents. That being said it was able to exploit
those mistakes somewhat decently in some cases and at least grow to some degree off of it.


**Expert 3** Middling. It is tactically strong when not having to work with other players and when
it has a considerable number of units, but is quite weak when attempting to cooperate with other
players. Its defensive strength varies quite significantly too, possibly also based on unit count when it had relatively few units it missed very obvious defensive tactics.


H OW WOULD YOU EVALUATE THE ABILITY OF THE AGENT TO COOPERATE ?


**Expert 1** The bot is hyperactively trying to coordinate and signal to the other players that it wants
to work with them. Sometimes this is in the form of ridiculous orders that probably indicate desperation more than a mutually beneficial alliance, and this backfires as you may expect. At its best it
makes exceptional signaling moves (RUSSIA game [4] : War - Mos in Fall 1901 is exceptional) but at
worst it is embarrassingly bad and leads to it getting attacked (TURKEY game [5] : supporting convoys
from Gre - Smy or supporting other powers moving to Armenia). The other weakness is that it tends


4 DOUBLE BLIND
5 DOUBLE BLIND


14


to make moves like these facing all other powers - this is not optimal as indicating to all other powers
that you want to work with them is equivalent to not indicating anything at all - if anything it seems
a little duplicitous. This is especially true when the bot is still inclined to stab when the opportunity
presents itself, which means the signaling is superficial and unlikely to work repeatedly. Overall,
the orders show the ability to cooperate, signal, and work together, but the hyperactivity of the bot
is limiting the effectiveness of the tools to achieve the best results.


**Expert 2** Poor. Random support orders seemed to be thrown without an overarching strategy
behind them. Moves didn’t seem to suggest long term thoughts of collaboration.


**Expert 3** Poor. When attempting to work with another player, it almost always gives them the
upper hand, and even issues supports that suggest it is okay with that player taking its SCs when it
should not be. It sometimes matches supports to human moves, but does not seem to do this very
often. The nonsensical supports are much more common.


C.4 D IPLODOCUS -H IGH


H OW WOULD YOU EVALUATE THE OVERALL STRENGTH OF THE AGENT ?


**Expert 1** The tactics are unadventurous and sometimes seem below human standards (for example,
the train of army units in the Italy game; the whole Turkey game) but conversely they also have a
longer view of the game (see also: Italy game - the trained bounces don’t matter strategically).
There’s less nonsense too; if I were to sum the bot up in two words it would be “practical” and
“boring”.


**Expert 2** Seemed to be strong. Wrote generally good tactical orders, showed generally good
strategic sense. Showed discipline and a willingness to let allies survive in weak positions while
having units that could theoretically stab for dots with ease remaining right next to that weak ally.


There were some highly questionable moments as both Italy and France early on in 1901 strategy
which seemed to heavily harm their ability to get out of the box.


The Austrian game was particularly impressive in terms of its ability to handle odd scenarios and
achieve the solo despite receiving pressure on multiple occasions on multiple fronts.


**Expert 3** Generally strong. It is good at signalling and forming alliances, is tactically strong when
in its favoured alliance, and is especially strong when ahead. Its main weakness seems to be an
inability to adapt - if its favoured alliance is declined, it will often keep trying to ‘pitch’ that same
alliance instead of working towards alternatives.


H OW WOULD YOU EVALUATE THE ABILITY OF THE AGENT TO COOPERATE ?


**Expert 1** Low. It doesn’t put much effort into this. The French game, for example, the bot just
seems to accept it is being attacked and fight through it. It’s so boring and tactical and shows little
care for cooperation. Many great gunboat players do this but it will not hold up in press games.
What it does seem to do is capitalize on other player’s mistakes - see the Austrian game where it
sneaks into Scandinavia and optimizes to get to 18 (there can’t be a lot of training data for that!).


**Expert 2** Very strong ability to cooperate as seen in the Turkish game, but in other games seemed
to try and pick fights against the entire world in ways that were ultimately self-defeating.


**Expert 3** Good. It can work well with human players, matching supports and even using signalling
supports in ways humans would. It frequently attempts to side with a player who is attacking it,
though, so it seems to have a problem with identifying which player to work with.


15


C.5 D IPLODOCUS -L OW


H OW WOULD YOU EVALUATE THE OVERALL STRENGTH OF THE AGENT ?


**Expert 1** Exceptional. Very strong tactics and a clear directionality to what it does - it seems to
understand what the strategic value of a position is and it acts with efficiency to achieve the strategic
goals. It has great results (time drawn out of a few wins!) but also fights back from “losing”
positions extremely well which makes it quantifiably strong, but it also just plays a beautiful and
effective game. Very strong indeed. It does sometimes act too aggressively for tournament play
(Austria is the example where this came home to roost) - the high risk/reward plays are generally
but not always correct in single games, but for tournament play it goes for broke a bit too much (This
is outside the scope of the agent I suspect, as it is playing to scoring system not tournament scoring
system). Against human players who may not see the longer term impact of their play, it results in
games like this one... which is ugly both for Austria and for everyone else except Turkey.


**Expert 2** Very weak. Seemed to abandon its own position in many cases to pursue questionable
adventures. Sometimes they worked out but generally they failed, resulting in things like a Germany
under siege holding Edi while they as England are off in Portugal and are holding onto their home
centers only because FG were under siege by the south.


**Expert 3** Very strong. It can signal alliances very well and generally chooses the correct allies,
seems strong tactically even on defence, and makes some plays you would not expect from a human
player but which are outright stronger than a human player would make.


H OW WOULD YOU EVALUATE THE ABILITY OF THE AGENT TO COOPERATE ?


**Expert 1** Pretty good. It sends signaling moves and makes efforts to support other players quite
a lot (see in particular Russia). I particularly like the skills being shown to work together tactically
and try and support other units - this is both effective and quite human. This is my favorite bot by
some distance when it comes to cooperating with the other players. There is a weakness in that it
does seem to reassess alliances every turn, which means sometimes the excellent work indicating
and supporting is undone without getting the chance to realize the gains (Examples with Russia and
Italy).


**Expert 2** Poor. Didn’t seem to give meaningful support orders when they would have helped
and gave plenty of meaningless signaling supports and some questionable ones like supporting the
English into SKA in F1901 as Germany among other oddities


**Expert 3** Good. It signals alliances in very human ways, through clear signalling builds, accurate
support moves where it makes sense, and support holds otherwise. It also seems to match supports
with its allies well.


D P OPULATION BASED EVALUATION


In general-sum games like Diplomacy, winrate in head-to-head matches against a previous version
of an agent may not be as informative because of nontransitivity between agents. For example,
exploitative agents such as best-response-to-BC may do particularly well against BC or other pure
imitation-learning agents, and less well against all other agents. Additionally, Bakhtin et al. (2021)
found that a pair of independently and equally-well-trained RL agents may each appear very weak
in a population composed of the other due to converging to incompatible equilibria. Many agents
also varied significantly in how well they performed against other search-based agents.


Therefore, we resort to playing against a population of previously training agents as was done in Jacob et al. (2022), intended to measure more broadly how well an agent does on average against a
wider suite of various human-like agents.


More precisely, we define a fixed set of baseline agents as a population. To determine an agent’s
average population score, we add that agent into the population and then play games where in each
game, all 7 players are uniformly randomly sampled from the population with replacement, keeping


16


only games where the agent to be tested was sampled at least once. Note that unlike Jacob et al.
(2022), we run a separate population test for each new agent to be tested, rather than combining all
agents to be tested within a single population.


For the experiments in Table 1 and subsection 5.1 we used the following 8 baseline agents:


    - An single-turn BR agent that assumes everyone else plays the BC policy.

   - An agent doing RM search with BC policy and value functions. We use 2 copies of this
agent trained on different subsets of data.

    - DiL-piKL agent with BC policy and value functions. We use 4 different versions of this
data with different training data and model architecture.

   - DiL-piKL agent where the policy and value functions are trained with self-play with
Reinforced-PiKL with high lambda ( _λ_ = 3 _×_ 10 _[−]_ [2] ).


For the experiments in this paper we used 1000 games for each such population test.


E T HEORETICAL P ROPERTIES OF D I L- PI KL


In this section we study the last-iterate convergence of DiL-piKL, establishing that in two-player
zero-sum games DiL-piKL converges to the (unique) Bayes-Nash equilibrium of the regularized
Bayesian game. As a corollary (in the case in which each player has exactly one type), we conclude
that piKL converges to the Nash equilibrium of the regularized game in two-player zero-sum games.
We start from a technical result. In all that follows, we will always let _**u**_ _[t]_ _i_ [be a shorthand for the]
vector ( _u_ _i_ ( _a,_ _**a**_ _[t]_ _−i_ [))] _[a][∈][A]_ _i_ [.]

**Lemma 1.** _Fix any player i, λ_ _i_ _∈_ Λ _i_ _, and t ≥_ 1 _. For all_ _**π**_ _,_ _**π**_ _[′]_ _∈_ ∆( _A_ _i_ ) _, the iterates_ _**π**_ _i,λ_ _[t]_ _i_ _[and]_
_**π**_ _i,λ_ _[t]_ [+1] _i_ _[defined in Line 8 of Algorithm 1 satisfy]_
� _ηλ_ _i_ _tη_ + 1 � _−_ _**u**_ _[t]_ _i_ [+] _[ λ]_ _[i]_ _[∇][φ]_ [(] _**[π]**_ _i,λ_ _[t]_ _i_ [)] _[ −]_ _[λ]_ _[i]_ _[∇][φ]_ [(] _**[τ]**_ _[i]_ [)] � + _∇φ_ ( _**π**_ _i,λ_ _[t]_ [+1] _i_ [)] _[ −∇][φ]_ [(] _**[π]**_ _i,λ_ _[t]_ _i_ [)] _[,]_ _**[ π]**_ _[ −]_ _**[π]**_ _[′]_ � = 0 _._


_Proof._ If _t_ = 1, then the results follows from direct inspection: _**π**_ _i,λ_ [1] _i_ [is the uniform policy (and so]
_⟨∇φ_ ( _**π**_ _i,λ_ [1] _i_ [)] _[,]_ _**[ π]**_ _[−]_ _**[π]**_ _[′]_ _[⟩]_ [= 0][ for any] _**[ π]**_ _[,]_ _**[ π]**_ _[′]_ _[ ∈]_ [∆(] _[A]_ _[i]_ [)][, and so the statement reduces to the first-order opti-]
mality conditions for the problem _**π**_ _i,λ_ [2] _i_ [= arg max] _**π**_ _∈_ ∆( _A_ _i_ ) _[{−][φ]_ [(] _**[π]**_ [)] _[/η]_ [+] _[⟨]_ _**[u]**_ _i_ [1] _[, π][⟩−][λ]_ _[i]_ _[D]_ [KL] [(] _**[π]**_ _[ ∥]_ _**[τ]**_ _[i]_ [)] _[}]_ [.]
So, we now focus on the case _t ≥_ 2. The iterates _**π**_ _i,λ_ _[t]_ [+1] _i_ [and] _**[ π]**_ _i,λ_ _[t]_ _i_ [produced by DiL-piKL are respec-]
tively the solutions to the optimization problem



_−_ _[φ]_ [(] _**[π]**_ [)]
� _ηt_



_**π**_ _[t]_ [+1]
_i,λ_ _i_ [= arg max]
_**π**_ _∈_ ∆( _A_ _i_ )




[(] _**[π]**_ [)]

_ηt_ + _⟨_ _**U**_ [¯] _i_ _[t]_ _[,]_ _**[ π]**_ _[⟩−]_ _[λ]_ _[i]_ _[D]_ [KL] [(] _**[π]**_ _[ ∥]_ _**[τ]**_ _[i]_ [)] � _,_



_−_ _[φ]_ [(] _**[π]**_ [)]
� _η_ ( _t −_



_**π**_ _[t]_
_i,λ_ _i_ [= arg max]
_**π**_ _∈_ ∆( _A_ _i_ )




_[φ]_ [(] _**[π]**_ [)] _i_ _,_ _**π**_ _⟩−_ _λ_ _i_ _D_ KL ( _**π**_ _∥_ _**τ**_ _i_ ) _,_

_η_ ( _t −_ 1) [+] _[ ⟨]_ _**[U]**_ [¯] _[ t][−]_ [1] �



where we let the averages utility vectors be



_t_



¯ 1
_**U**_ _i_ _[t][−]_ [1] :=
_t −_ 1



_t−_ 1
�



� _**u**_ _[t]_ _i_ _[′]_ _[,]_ _**U**_ ¯ _i_ _[t]_ [:= 1] _t_

_t_ _[′]_ =1



_t_
� _**u**_ _[t]_ _i_ _[′]_ _[.]_


_t_ _[′]_ =1



Since the regularizing function negative entropy _φ_ is Legendre, the policies _**π**_ _i,λ_ _[t]_ [+1] _i_ [and] _**[ π]**_ _i,λ_ _[t]_ _i_ [are in]
the relative interior of the probability simplex, and therefore the first-order optimality conditions for
_**π**_ _i,λ_ _[t]_ [+1] _i_ [and] _**[ π]**_ _i,λ_ _[t]_ _i_ [are respectively]
� _−_ _**U**_ [¯] _i_ _[t]_ [+] _[ λ]_ _[i]_ _[∇][φ]_ [(] _**[π]**_ _i,λ_ _[t]_ [+1] _i_ [)] _[ −]_ _[λ]_ _[i]_ _[∇][φ]_ [(] _**[τ]**_ _[i]_ [) +] _ηt_ [1] _[∇][φ]_ [(] _**[π]**_ _i,λ_ _[t]_ [+1] _i_ [)] _[,]_ _**[ π]**_ _[ −]_ _**[π]**_ _[′]_ � = 0 _∀_ _**π**_ _,_ _**π**_ _[′]_ _∈_ ∆( _A_ _i_ ) _,_

(6)

1
_−_ _**U**_ [¯] _i_ _[t][−]_ [1] + _λ_ _i_ _∇φ_ ( _**π**_ _i,λ_ _[t]_ _i_ [)] _[ −]_ _[λ]_ _[i]_ _[∇][φ]_ [(] _**[τ]**_ _[i]_ [) +] _i,λ_ _i_ [)] _[,]_ _**[ π]**_ _[ −]_ _**[π]**_ _[′]_ = 0 _∀_ _**π**_ _,_ _**π**_ _[′]_ _∈_ ∆( _A_ _i_ ) _._
� _η_ ( _t −_ 1) _[∇][φ]_ [(] _**[π]**_ _[t]_ �


17


Taking the difference between the equalities, we find
� _−_ _**U**_ [¯] _i_ _[t]_ [+ ¯] _**[U]**_ _[ t]_ _i_ _[−]_ [1] + � _λ_ _i_ + _ηt_ [1] � _∇φ_ ( _**π**_ _i,λ_ _[t]_ [+1] _i_ [)] _[ −]_ �



1
� _∇φ_ ( _**π**_ _i,λ_ _[t]_ [+1] _i_ [)] _[ −]_ � _λ_ _i_ + _η_ ( _t −_ 1)



_∇φ_ ( _**π**_ _i,λ_ _[t]_ _i_ [)] _[,]_ _**[ π]**_ _[ −]_ _**[π]**_ _[′]_ = 0
� �



_ηt_



We now use the fact that



¯ 1 ¯ 1
_**U**_ _i_ _[t]_ _[−]_ _**[U]**_ [¯] _[ t]_ _i_ _[−]_ [1] = _−_ _**U**_ _i_ _[t]_ [+] _i_ _[.]_
_t −_ 1 _t −_ 1 _**[u]**_ _[t]_



to further write

1 1
� _t −_ 1 � _−_ _**u**_ _[t]_ _i_ [+ ¯] _**[U]**_ _[ t]_ _i_ � + � _λ_ _i_ + _ηt_ [1] � _∇φ_ ( _**π**_ _i,λ_ _[t]_ [+1] _i_ [)] _[ −]_ � _λ_ _i_ + _η_ ( _t −_ 1)


From Equation (6) we find



_∇φ_ ( _**π**_ _i,λ_ _[t]_ _i_ [)] _[,]_ _**[ π]**_ _[ −]_ _**[π]**_ _[′]_ = 0 (7)
� �



_⟨_ _**U**_ [¯] _i_ _[t]_ _[,]_ _**[ π]**_ _[ −]_ _**[π]**_ _[′]_ _[⟩]_ [=] � _λ_ _i_ _∇φ_ ( _**π**_ _i,λ_ _[t]_ [+1] _i_ [)] _[ −]_ _[λ]_ _[i]_ _[∇][φ]_ [(] _**[τ]**_ _[i]_ [) +] _ηt_ [1] _[∇][φ]_ [(] _**[π]**_ _i,λ_ _[t]_ [+1] _i_ [)] _[,]_ _**[ π]**_ _[ −]_ _**[π]**_ _[′]_ �



and so, plugging back the previous relationship in Equation (7) we can write, for all _**π**_ _,_ _**π**_ _[′]_ _∈_ ∆( _A_ _i_ ),



1
0 =
� _t −_ 1


1

=
� _t −_ 1



_−_ _**u**_ _[t]_ _i_ [+] _[ λ]_ _[i]_ _[∇][φ]_ [(] _**[π]**_ _i,λ_ _[t]_ [+1] _i_ [)] _[ −]_ _[λ]_ _[i]_ _[∇][φ]_ [(] _**[τ]**_ _[i]_ [) +] [1]
�



1
� _−_ _**u**_ _[t]_ _i_ [+] _[ λ]_ _[i]_ _[∇][φ]_ [(] _**[π]**_ _i,λ_ _[t]_ [+1] _i_ [)] _[ −]_ _[λ]_ _[i]_ _[∇][φ]_ [(] _**[τ]**_ _[i]_ [)] � + � _λ_ _i_ + _η_ ( _t −_ 1)



_ηt_ [1] _[∇][φ]_ [(] _**[π]**_ _i,λ_ _[t]_ [+1] _i_ [)] � + � _λ_ _i_ + _ηt_ [1]



_ηt_



_∇φ_ ( _**π**_ _i,λ_ _[t]_ [+1] _i_ [)]
�



1
_−_ _λ_ _i_ +
� _η_ ( _t −_ 1)



_∇φ_ ( _**π**_ _i,λ_ _[t]_ _i_ [)] _[,]_ _**[ π]**_ _[ −]_ _**[π]**_ _[′]_
� �



_∇φ_ ( _**π**_ _i,λ_ _[t]_ [+1] _i_ [)]
�



1
_−_ _λ_ _i_ +
� _η_ ( _t −_ 1)



_∇φ_ ( _**π**_ _i,λ_ _[t]_ _i_ [)] _[,]_ _**[ π]**_ _[ −]_ _**[π]**_ _[′]_
� �



1
= � _t −_ 1 � _−_ _**u**_ _[t]_ _i_ [+] _[ λ]_ _[i]_ _[∇][φ]_ [(] _**[π]**_ _i,λ_ _[t]_ _i_ [)] _[ −]_ _[λ]_ _[i]_ _[∇][φ]_ [(] _**[τ]**_ _[i]_ [)] � + _[η]_ _η_ _[λ]_ ( _t_ _[i]_ _−_ _[t]_ [ + 1] 1) _[∇][φ]_ [(] _**[π]**_ _i,λ_ _[t]_ [+1] _i_ [)]

_−_ _[η][λ]_ _[i]_ _[t]_ [ + 1] _i,λ_ _i_ [)] _[,]_ _**[ π]**_ _[ −]_ _**[π]**_ _[′]_ _._

_η_ ( _t −_ 1) _[∇][φ]_ [(] _**[π]**_ _[t]_ �

Dividing by ( _ηλ_ _i_ _t_ + 1) _/_ ( _η_ ( _t −_ 1)) yields the statement.


**Corollary 1.** _Fix any player i, λ_ _i_ _∈_ Λ _i_ _, and t ≥_ 1 _. For all_ _**π**_ _∈_ ∆( _A_ _i_ ) _, the iterates_ _**π**_ _i,λ_ _[t]_ _i_ _[and]_ _**[ π]**_ _i,λ_ _[t]_ [+1] _i_
_defined in Line 8 of Algorithm 1 satisfy_
� _−_ _**u**_ _[t]_ _i_ [+] _[ λ]_ _[i]_ _[∇][φ]_ [(] _**[π]**_ _i,λ_ _[t]_ _i_ [)] _[ −]_ _[λ]_ _[i]_ _[∇][φ]_ [(] _**[τ]**_ _[i]_ [)] _[,]_ _**[ π]**_ _[ −]_ _**[π]**_ _i,λ_ _[t]_ [+1] _i_ �



= � _λ_ _i_ _t_ + _η_ [1] �� _D_ KL ( _**π**_ _∥_ _**π**_ _i,λ_ _[t]_ [+1] _i_ [)] _[ −]_ _[D]_ [KL] [(] _**[π]**_ _[ ∥]_ _**[π]**_ _i,λ_ _[t]_ _i_ [) +] _[ D]_ [KL] [(] _**[π]**_ _i,λ_ _[t]_ [+1] _i_ _[∥]_ _**[π]**_ _i,λ_ _[t]_ _i_ [)] � _._



_Proof._ Since Lemma 1 holds for all _**π**_ _,_ _**π**_ _[′]_ _∈_ ∆( _A_ _i_ ), we can in particular set _**π**_ _[′]_ = _**π**_ _i,λ_ _[t]_ [+1] _i_ [, and obtain]
_ηλ_ _i_ _tη_ + 1 � _−_ _**u**_ _[t]_ _i_ [+] _[ λ]_ _[i]_ _[∇][φ]_ [(] _**[π]**_ _i,λ_ _[t]_ _i_ [)] _[ −]_ _[λ]_ _[i]_ _[∇][φ]_ [(] _**[τ]**_ _[i]_ [)] _[,]_ _**[ π]**_ _[ −]_ _**[π]**_ _i,λ_ _[t]_ [+1] _i_ �



� _−_ _**u**_ _[t]_ _i_ [+] _[ λ]_ _[i]_ _[∇][φ]_ [(] _**[π]**_ _i,λ_ _[t]_ _i_ [)] _[ −]_ _[λ]_ _[i]_ _[∇][φ]_ [(] _**[τ]**_ _[i]_ [)] _[,]_ _**[ π]**_ _[ −]_ _**[π]**_ _i,λ_ _[t]_ [+1] _i_



�



+ � _∇φ_ ( _**π**_ _i,λ_ _[t]_ [+1] _i_ [)] _[ −∇][φ]_ [(] _**[π]**_ _i,λ_ _[t]_ _i_ [)] _[,]_ _**[ π]**_ _[ −]_ _**[π]**_ _i,λ_ _[t]_ [+1] _i_



= 0 _._ (8)
�



Using the three-point identity
� _∇φ_ ( _**π**_ _i,λ_ _[t]_ [+1] _i_ [)] _[ −∇][φ]_ [(] _**[π]**_ _i,λ_ _[t]_ _i_ [)] _[,]_ _**[ π]**_ _[ −]_ _**[π]**_ _i,λ_ _[t]_ [+1] _i_



� = _D_ KL ( _**π**_ _∥_ _**π**_ _i,λ_ _[t]_ _i_ [)] _[ −]_ _[D]_ [KL] [(] _**[π]**_ _[ ∥]_ _**[π]**_ _i,λ_ _[t]_ [+1] _i_ [)] _[ −]_ _[D]_ [KL] [(] _**[π]**_ _i,λ_ _[t]_ [+1] _i_ _[∥]_ _**[π]**_ _i,λ_ _[t]_ _i_ [)]



in Equation (8) yields
_D_ KL ( _**π**_ _∥_ _**π**_ _i,λ_ _[t]_ [+1] _i_ [) =] _[ D]_ [KL] [(] _**[π]**_ _[ ∥]_ _**[π]**_ _i,λ_ _[t]_ _i_ [)] _[ −]_ _[D]_ [KL] [(] _**[π]**_ _i,λ_ _[t]_ [+1] _i_ _[∥]_ _**[π]**_ _i,λ_ _[t]_ _i_ [)]



+ _ηλ_ _i_ _tη_ + 1 � _−_ _**u**_ _[t]_ _i_ [+] _[ λ]_ _[i]_ _[∇][φ]_ [(] _**[π]**_ _i,λ_ _[t]_ _i_ [)] _[ −]_ _[λ]_ _[i]_ _[∇][φ]_ [(] _**[τ]**_ _[i]_ [)] _[,]_ _**[ π]**_ _[ −]_ _**[π]**_ _i,λ_ _[t]_ [+1] _i_



_._
�



Multiplying by _λ_ _i_ _t_ + 1 _/η_ yields the statement.



18


E.1 R EGRET A NALYSIS


Let ˜ _u_ _[t]_ _i,λ_ _i_ [be the regularized utility of agent type] _[ λ]_ _[i]_ _[ ∈]_ [Λ] _[i]_


_u_ ˜ _[t]_ _i,λ_ _i_ [: ∆(] _[A]_ _[i]_ [)] _[ ∋]_ _**[π]**_ _[ �→⟨]_ _**[u]**_ _i_ _[t]_ _[,]_ _**[ π]**_ _[⟩−]_ _[λ]_ _[i]_ _[D]_ [KL] [(] _**[π]**_ _[ ∥]_ _**[τ]**_ _[i]_ [)] _[.]_


**Observation 1.** _We note the following:_


    - _For any i ∈{_ 1 _,_ 2 _} and λ_ _i_ _∈_ Λ _i_ _, the function_ ˜ _u_ _[t]_ _i,λ_ _i_ _[satisfies]_


_u_ ˜ _[t]_ _i,λ_ _i_ [(] _**[π]**_ [) = ˜] _[u]_ _[t]_ _i,λ_ _i_ [(] _**[π]**_ _[′]_ [) +] _[ ⟨∇][u]_ [˜] _[t]_ _i,λ_ _i_ [(] _**[π]**_ _[′]_ [)] _[,]_ _**[ π]**_ _[ −]_ _**[π]**_ _[′]_ _[⟩−]_ _[λ]_ _[i]_ _[D]_ [KL] [(] _**[π]**_ _[ ∥]_ _**[π]**_ _[′]_ [)] _∀_ _**π**_ _,_ _**π**_ _[′]_ _∈_ ∆( _A_ _i_ ) _._


    - _Furthermore,_


_−∇u_ ˜ _[t]_ _i,λ_ _i_ [(] _**[π]**_ _i,λ_ _[t]_ _i_ [) =] _[ −]_ _**[u]**_ _i_ _[t]_ [+] _[ λ]_ _[i]_ _[∇][φ]_ [(] _**[π]**_ _[t]_ [)] _[ −]_ _[λ]_ _[i]_ _[∇][φ]_ [(] _**[τ]**_ _[i]_ [)] _[.]_


Using Corollary 1 we have the following


**Lemma 2.** _For any player i and type λ_ _i_ _∈_ Λ _i_ _,_


˜ _∥_ _**u**_ _[t]_ _i_ _[∥]_ _∞_ [2]
_u_ _[t]_ _i,λ_ _i_ [(] _**[π]**_ [)] _[ −]_ _[u]_ [˜] _[t]_ _i,λ_ _i_ [(] _**[π]**_ _i,λ_ _[t]_ _i_ [)] _[ ≤]_ 4 _λ_ _i_ _t_ + 4 _/η_ [+] _[ λ]_ _[i]_ � _D_ KL ( _**π**_ _i,λ_ _[t]_ _i_ _[∥]_ _**[τ]**_ _[i]_ [)] _[ −]_ _[D]_ [KL] [(] _**[π]**_ _i,λ_ _[t]_ [+1] _i_ _[∥]_ _**[τ]**_ _[i]_ [)] �



_−_ _λ_ _i_ _t_ + [1]
� _η_



_D_ KL ( _**π**_ _∥_ _**π**_ _i,λ_ _[t]_ [+1] _i_ [) +] _λ_ _i_ ( _t −_ 1) + [1]
� � _η_



_D_ KL ( _**π**_ _∥_ _**π**_ _i,λ_ _[t]_ _i_ [)] _[.]_
�



_Proof._ From Lemma 1,



0 = _λ_ _i_ _t_ + [1]
� _η_

= _λ_ _i_ _t_ + [1]
� _η_


= _λ_ _i_ _t_ + [1]
� _η_



˜
�� _−_ _D_ KL ( _**π**_ _∥_ _**π**_ _i,λ_ _[t]_ [+1] _i_ [) +] _[ D]_ [KL] [(] _**[π]**_ _[ ∥]_ _**[π]**_ _i,λ_ _[t]_ _i_ [)] _[ −]_ _[D]_ [KL] [(] _**[π]**_ _i,λ_ _[t]_ [+1] _i_ _[∥]_ _**[π]**_ _i,λ_ _[t]_ _i_ [)] � + _⟨−∇u_ _[t]_ _i,λ_ _i_ [(] _**[π]**_ _i,λ_ _[t]_ _i_ [)] _[,]_ _**[ π]**_ _[ −]_ _**[π]**_ _i,λ_ _[t]_ [+1] _i_ _[⟩]_

�� _−_ _D_ KL ( _**π**_ _∥_ _**π**_ _i,λ_ _[t]_ [+1] _i_ [) +] _[ D]_ [KL] [(] _**[π]**_ _[ ∥]_ _**[π]**_ _i,λ_ _[t]_ _i_ [)] _[ −]_ _[D]_ [KL] [(] _**[π]**_ _i,λ_ _[t]_ [+1] _i_ _[∥]_ _**[π]**_ _i,λ_ _[t]_ _i_ [)] �

+ _⟨∇u_ ˜ _[t]_ _i,λ_ _i_ [(] _**[π]**_ _i,λ_ _[t]_ _i_ [)] _[,]_ _**[ π]**_ _i,λ_ _[t]_ _i_ [+] _**[ π]**_ _i,λ_ _[t]_ [+1] _i_ _[⟩]_ [+] _[ ⟨−∇][u]_ [˜] _i,λ_ _[t]_ _i_ [(] _**[π]**_ _i,λ_ _[t]_ _i_ [)] _[,]_ _**[ π]**_ _[ −]_ _**[π]**_ _i,λ_ _[t]_ _i_ _[⟩]_

�� _−_ _D_ KL ( _**π**_ _∥_ _**π**_ _i,λ_ _[t]_ [+1] _i_ [) +] _[ D]_ [KL] [(] _**[π]**_ _[ ∥]_ _**[π]**_ _i,λ_ _[t]_ _i_ [)] _[ −]_ _[D]_ [KL] [(] _**[π]**_ _i,λ_ _[t]_ [+1] _i_ _[∥]_ _**[π]**_ _i,λ_ _[t]_ _i_ [)] �

+ _⟨−∇u_ ˜ _[t]_ _i,λ_ _i_ [(] _**[π]**_ _i,λ_ _[t]_ _i_ [)] _[,]_ _**[ π]**_ _i,λ_ _[t]_ _i_ _[−]_ _**[π]**_ _i,λ_ _[t]_ [+1] _i_ _[⟩−]_ _[u]_ [˜] _i,λ_ _[t]_ _i_ [(] _**[π]**_ [) + ˜] _[u]_ _[t]_ _i,λ_ _i_ [(] _**[π]**_ _i,λ_ _[t]_ _i_ [)] _[ −]_ _[λ]_ _[i]_ _[D]_ [KL] [(] _**[π]**_ _[ ∥]_ _**[π]**_ _i,λ_ _[t]_ _i_ [)] _[.]_



Rearranging, we find


˜
_u_ _[t]_ _i,λ_ _i_ [(] _**[π]**_ [)] _[ −]_ _[u]_ [˜] _[t]_ _i,λ_ _i_ [(] _**[π]**_ _i,λ_ _[t]_ _i_ [) =] _[ −]_ _λ_ _i_ _t_ + [1]
� _η_



_D_ KL ( _**π**_ _∥_ _**π**_ _i,λ_ _[t]_ [+1] _i_ [) +] _λ_ _i_ ( _t −_ 1) + [1]
� � _η_



_D_ KL ( _**π**_ _∥_ _**π**_ _i,λ_ _[t]_ _i_ [)]
�



_−_ _λ_ _i_ _t_ + [1]
� _η_



_D_ KL ( _**π**_ _i,λ_ _[t]_ [+1] _i_ _[∥]_ _**[π]**_ _i,λ_ _[t]_ _i_ [) +] _[ ⟨−∇][u]_ [˜] _[t]_ _i,λ_ _i_ [(] _**[π]**_ _i,λ_ _[t]_ _i_ [)] _[,]_ _**[ π]**_ _i,λ_ _[t]_ _i_ _[−]_ _**[π]**_ _i,λ_ _[t]_ [+1] _i_ _[⟩]_
� ~~�~~ ~~��~~ ~~�~~
(9)

(10)



_._



We now upper bound the term in (9) using convexity of the function _**π**_ _�→_ _D_ KL ( _**π**_ _∥_ _**τ**_ _i_ ), as follows:


_⟨−∇u_ ˜ _[t]_ _i,λ_ _i_ [(] _**[π]**_ _i,λ_ _[t]_ _i_ [)] _[,]_ _**[ π]**_ _i,λ_ _[t]_ _i_ _[−]_ _**[π]**_ _i,λ_ _[t]_ [+1] _i_ _[⟩]_ [=] _[ ⟨−]_ _**[u]**_ _i_ _[t]_ _[,]_ _**[ π]**_ _i,λ_ _[t]_ _i_ _[−]_ _**[π]**_ _i,λ_ _[t]_ [+1] _i_ _[⟩]_ [+] _[ λ]_ _[i]_ _[⟨∇][φ]_ [(] _**[π]**_ _i,λ_ _[t]_ _i_ [)] _[ −∇][φ]_ [(] _**[τ]**_ _[i]_ [)] _[,]_ _**[ π]**_ _i,λ_ _[t]_ [+1] _i_ _[−]_ _**[π]**_ _i,λ_ _[t]_ _i_ _[⟩]_

_≤⟨−_ _**u**_ _[t]_ _i_ _[,]_ _**[ π]**_ _i,λ_ _[t]_ _i_ _[−]_ _**[π]**_ _i,λ_ _[t]_ [+1] _i_ _[⟩]_ [+] _[ λ]_ _[i]_ � _D_ KL ( _**π**_ _i,λ_ _[t]_ [+1] _i_ _[∥]_ _**[τ]**_ _[i]_ [)] _[ −]_ _[D]_ [KL] [(] _**[π]**_ _i,λ_ _[t]_ _i_ _[∥]_ _**[τ]**_ _[i]_ [)] � _._


19


Substituting the above bound into (10) yields


˜
_u_ _[t]_ _i,λ_ _i_ [(] _**[π]**_ [)] _[ −]_ _[u]_ [˜] _[t]_ _i,λ_ _i_ [(] _**[π]**_ _i,λ_ _[t]_ _i_ [)] _[ ≤⟨−]_ _**[u]**_ _i_ _[t]_ _[,]_ _**[ π]**_ _i,λ_ _[t]_ _i_ _[−]_ _**[π]**_ _i,λ_ _[t]_ [+1] _i_ _[⟩−]_ _λ_ _i_ _t_ + [1]
� _η_



_D_ KL ( _**π**_ _i,λ_ _[t]_ [+1] _i_ _[∥]_ _**[π]**_ _i,λ_ _[t]_ _i_ [)]
�



+ _λ_ _i_ � _D_ KL ( _**π**_ _i,λ_ _[t]_ _i_ _[∥]_ _**[τ]**_ _[i]_ [)] _[ −]_ _[D]_ [KL] [(] _**[π]**_ _i,λ_ _[t]_ [+1] _i_ _[∥]_ _**[τ]**_ _[i]_ [)] �



_−_ _λ_ _i_ _t_ + [1]
� _η_



_D_ KL ( _**π**_ _∥_ _**π**_ _i,λ_ _[t]_ [+1] _i_ [) +] _λ_ _i_ ( _t −_ 1) + [1]
� � _η_



_D_ KL ( _**π**_ _∥_ _**π**_ _i,λ_ _[t]_ _i_ [)]
�



_≤_ 4 _λ∥_ _i_ _**u**_ _t_ + 4 _[t]_ _i_ _[∥]_ _∞_ [2] _/η_ [+] � _λ_ _i_ _t_ + _η_ [1] � _∥_ _**π**_ _i,λ_ _[t]_ _i_ _[−]_ _**[π]**_ _i,λ_ _[t]_ [+1] _i_ _[∥]_ 1 [2] _[−]_ � _λ_ _i_ _t_ + _η_ [1]

+ _λ_ _i_ � _D_ KL ( _**π**_ _i,λ_ _[t]_ _i_ _[∥]_ _**[τ]**_ _[i]_ [)] _[ −]_ _[D]_ [KL] [(] _**[π]**_ _i,λ_ _[t]_ [+1] _i_ _[∥]_ _**[τ]**_ _[i]_ [)] �



_D_ KL ( _**π**_ _i,λ_ _[t]_ [+1] _i_ _[∥]_ _**[π]**_ _i,λ_ _[t]_ _i_ [)]
�



_−_ _λ_ _i_ _t_ + [1]
� _η_



_D_ KL ( _**π**_ _∥_ _**π**_ _i,λ_ _[t]_ [+1] _i_ [) +] _λ_ _i_ ( _t −_ 1) + [1]
� � _η_



_D_ KL ( _**π**_ _∥_ _**π**_ _i,λ_ _[t]_ _i_ [)] _[,]_
�



where the second inequality follows from Young’s inequality. Finally, by using the strong convexity
of the KL divergence between points _**π**_ _i,λ_ _[t]_ _i_ [and] _**[ π]**_ _i,λ_ _[t]_ [+1] _i_ [, that is,]

_D_ KL ( _**π**_ _i,λ_ _[t]_ [+1] _i_ _[∥]_ _**[π]**_ _i,λ_ _[t]_ _i_ [)] _[ ≥∥]_ _**[π]**_ _i,λ_ _[t]_ [+1] _i_ _[−]_ _**[π]**_ _i,λ_ _[t]_ _i_ _[∥]_ 1 [2] _[,]_

yields the statement.



Noting that the right-hand side of Lemma 2 is telescopic, we immediately have the following.
**Theorem 3.** _For any player i and type λ_ _i_ _∈_ Λ _i_ _, and policy_ _**π**_ _∈_ ∆( _A_ _i_ ) _, the following regret bound_
_holds at all times T_ _:_

_T_

˜ 2 log _T_

� _u_ _[t]_ _i,λ_ _i_ [(] _**[π]**_ [)] _[ −]_ _[u]_ [˜] _[t]_ _i,λ_ _i_ [(] _**[π]**_ _i,λ_ _[t]_ _i_ [)] _[ ≤]_ _[W]_ [ 2] min _, Tη_ + [lo][g] _[ n]_ _[i]_ + _λ_ _i_ (log _n_ _i_ + _Q_ _i_ ) _._



_u_ ˜ _[t]_

� _i,λ_ _i_ [(] _**[π]**_ [)] _[ −]_ _[u]_ [˜] _[t]_ _i,λ_ _i_ [(] _**[π]**_ _i,λ_ _[t]_ _i_ [)] _[ ≤]_ _[W]_ 4 [ 2]

_t_ =1




[ 2] 2 log _T_

min
4 � _λ_ _i_



g _T_

_, Tη_ + [lo][g] _[ n]_ _[i]_
_λ_ _i_ � _η_



+ _λ_ _i_ (log _n_ _i_ + _Q_ _i_ ) _._
_η_



_Proof._ From Lemma 2 we have that



_T_

_u_ ˜ _[t]_

� _i,λ_ _i_ [(] _**[π]**_ [)] _[ −]_ _[u]_ [˜] _[t]_ _i,λ_ _i_ [(] _**[π]**_ _i,λ_ _[t]_ _i_ [)] _[ ≤]_


_t_ =1



_W_ [2]


4

�



_T_
�


_t_ =1



1

_λ_ _i_ _t_ + 1 _/η_



�



+ _λ_ _i_ _D_ KL ( _**π**_ _i,λ_ [1] _i_ _[∥]_ _**[τ]**_ _[i]_ [) +] _D_ KL ( _**π**_ _∥_ _**π**_ _i_ [1] _,λ_ _i_ [)]
_η_



1

_λ_ _i_ _t_ _[, η]_ � [�]



_≤_ _[W]_ [ 2]

4



_T_
�
� _t_ =1



1

� _t_ =1 min� _λ_ _i_



+ _λ_ _i_ (log _n_ _i_ + _Q_ _i_ ) + [lo][g] _[ n]_ _[i]_

_η_



_≤_ _[W]_ [ 2]



g _T_ _, ηT_ + _λ_ _i_ (log _n_ _i_ + _Q_ _i_ ) + [lo][g] _[ n]_ _[i]_

_λ_ _i_ � _η_



_,_
_η_




[ 2] 2 log _T_

min
4 � _λ_ _i_



where the second inequality follows from the fact that _λ_ _i_ _t_ + 1 _/η ≥_ max _{λ_ _i_ _t,_ 1 _/η}_ and the fact that
_**π**_ _i,λ_ [1] _i_ [is the uniform strategy.]


E.2 L AST -I TERATE C ONVERGENCE IN T WO -P LAYER Z ERO -S UM G AMES


In two-player game with payoff matrix _**A**_ for Player 1, a Bayes-Nash equilibrium to the regularized
game is a collection of policies ( _**π**_ _i,λ_ _[∗]_ _i_ [)][ such that for any supported type] _[ λ]_ _[i]_ [ of Player] _[ i][ ∈{]_ [1] _[,]_ [ 2] _[}]_ [, the]
policy _**π**_ _i,λ_ _[∗]_ _i_ [is a best response to the average policy of the opponent. In symbols,]



� _**π**_ 2 _[∗]_ _,λ_ 2 � _,_ _**π**_ _⟩_ + _λ_ 1 _D_ KL ( _**π**_ _∥_ _**τ**_ 1 )� _∀_ _λ_ 1 _∈_ Λ 1 _,_



_**π**_ 1 _[∗]_ _,λ_ 1 _[∈]_ [arg max]
_**π**_ _∈_ ∆( _A_ 1 )


_**π**_ 2 _[∗]_ _,λ_ 2 _[∈]_ [arg max]
_**π**_ _∈_ ∆( _A_ 2 )



_⟨_ _**A**_ E
� _λ_ 2 _∼β_ 2



_⟨−_ _**A**_ _[⊤]_ E
� _λ_ 1 _∼β_ 1



� _**π**_ 1 _[∗]_ _,λ_ 1 � _,_ _**π**_ _⟩_ + _λ_ 2 _D_ KL ( _**π**_ _∥_ _**τ**_ 2 )� _∀_ _λ_ 2 _∈_ Λ 2 _._



Denoting ¯ _**π**_ 1 _[∗]_ [:=][ E] _[λ]_ 1 _[∼][β]_ 1 � _**π**_ 1 _[∗]_ _,λ_ 1 � _,_ ¯ _**π**_ 2 _[∗]_ [:=][ E] _[λ]_ 2 _[∼][β]_ 2 � _**π**_ 2 _[∗]_ _,λ_ 2 �, the first-order optimality conditions for
the best response problems above are
_⟨_ _**A**_ ¯ _**π**_ 2 _[∗]_ [+] _[ λ]_ [1] _[∇][φ]_ [(] _**[π]**_ 1 _[∗]_ _,λ_ 1 [)] _[ −]_ _[λ]_ [1] _[∇][φ]_ [(] _**[τ]**_ [1] [)] _[,]_ _**[ π]**_ 1 _[∗]_ _,λ_ 1 _[−]_ _**[π]**_ 1 _[′]_ _,λ_ 1 _[⟩≥]_ [0] _∀_ _**π**_ 1 _[′]_ _,λ_ 1 _[∈]_ [∆(] _[A]_ [1] [)] _[,]_

_⟨−_ _**A**_ _[⊤]_ _**π**_ ¯ 1 _[∗]_ [+] _[ λ]_ [2] _[∇][φ]_ [(] _**[π]**_ 2 _[∗]_ _,λ_ 2 [)] _[ −]_ _[λ]_ [2] _[∇][φ]_ [(] _**[τ]**_ [2] [)] _[,]_ _**[ π]**_ 2 _[∗]_ _,λ_ 2 _[−]_ _**[π]**_ 2 _[′]_ _,λ_ 2 _[⟩≥]_ [0] _∀_ _**π**_ 2 _[′]_ _,λ_ 2 _[∈]_ [∆(] _[A]_ [2] [)] _[.]_


20


We also mention the following standard lemma.
**Lemma 3.** _Let_ ( _**π**_ _i,λ_ _[∗]_ _i_ [)] _[i][∈{]_ [1] _[,]_ [2] _[}][,λ]_ 1 _[∈]_ [Λ] _i_ _[be the unique Bayes-Nash equilibrium of the regularized game.]_
_Let policies_ _**π**_ _i,λ_ _[′]_ _i_ _[be arbitrary, and let:]_


   - ¯ _**π**_ 1 _[′]_ [:=][ E] _[λ]_ 1 _[∼][β]_ 1 � _**π**_ 1 _[′]_ _,λ_ 1 � _,_ _**π**_ ¯ 2 _[′]_ [:=][ E] _[λ]_ 2 _[∼][β]_ 2 � _**π**_ 2 _[′]_ _,λ_ 2 � _;_




 - _α_ := E
_λ_ 1 _∼β_ 1


 - _β_ := E
_λ_ 2 _∼β_ 2



� _⟨−_ _**Aπ**_ ¯ 2 _[′]_ [+] _[ λ]_ [1] _[∇][φ]_ [(] _**[π]**_ 1 _[′]_ _,λ_ 1 [)] _[ −]_ _[λ]_ [1] _[∇][φ]_ [(] _**[τ]**_ [1] [)] _[,]_ _**[ π]**_ 1 _[∗]_ _,λ_ 1 _[−]_ _**[π]**_ 1 _[′]_ _,λ_ 1 _[⟩]_ � _;_


� _⟨_ _**A**_ _[⊤]_ _**π**_ ¯ 1 _[′]_ [+] _[ λ]_ [2] _[∇][φ]_ [(] _**[π]**_ 2 _[′]_ _,λ_ 2 [)] _[ −]_ _[λ]_ [2] _[∇][φ]_ [(] _**[τ]**_ [2] [)] _[,]_ _**[ π]**_ 2 _[∗]_ _,λ_ 2 _[−]_ _**[π]**_ 2 _[′]_ _,λ_ 2 _[⟩]_ � _._



_Then,_



_α_ + _β ≤−_ � _λ_ _i_ E _∼β_ _i_

_i∈{_ 1 _,_ 2 _}_



� _λ_ _i_ _D_ KL ( _**π**_ _i,λ_ _[′]_ _i_ _[∥]_ _**[π]**_ _i,λ_ _[∗]_ _i_ [) +] _[ λ]_ _[i]_ _[D]_ [KL] [(] _**[π]**_ _i,λ_ _[∗]_ _i_ _[∥]_ _**[π]**_ _i,λ_ _[′]_ _i_ [)] � _._



The following potential function will be key in the analysis:



_D_ KL ( _**π**_ _i,λ_ _[∗]_ _i_ _[∥]_ _**[π]**_ _i,λ_ _[t]_ _i_ [) +] _[ λ]_ _[i]_ _[D]_ [KL] [(] _**[π]**_ _i,λ_ _[t]_ _i_ _[∥]_ _**[τ]**_ _[i]_ [)] _,_ _t ∈{_ 1 _,_ 2 _, . . . }._
� �



Ψ _[t]_ := � _λ_ _i_ E _∼β_ _i_

_i∈{_ 1 _,_ 2 _}_



_λ_ _i_ ( _t −_ 1) + [1]
�� _η_



**Proposition 1.** _At all times t ∈{_ 1 _,_ 2 _, . . . }, let_


_**π**_ ¯ _−_ _[t]_ _i_ [:=] E
_λ_ _−i_ _∼β_ _−i_


_The potential_ Ψ _[t]_ _satisfies the inequality_



� _**π**_ _−_ _[t]_ _i,λ_ _−i_ � _._



Ψ _[t]_ [+1] _≤_ Ψ _[t]_ + E
� _λ_ _i_ _∼β_ _i_

_i∈{_ 1 _,_ 2 _}_



Ψ _[t]_ [+1] _≤_ Ψ _[t]_ +
�



_∥_ _**u**_ _[t]_ _i_ _[∥]_ [2] _∞_
4 _λ_ _i_ _t_ + 4 _/η_ [+] � _**A**_ _i_ ¯ _**π**_ _−_ _[t]_ _i_ _[−]_ _**[u]**_ _[t]_ _i_ _[,]_ _**[ π]**_ _i,λ_ _[∗]_ _i_ _[−]_ _**[π]**_ _i,λ_ _[t]_ _i_ � _._
� �



_._



_Proof._ By multiplying both sides of Corollary 1 for the choice _**π**_ = _**π**_ _i,λ_ _[∗]_ _i_ [, taking expectations over]
_λ_ _i_ _∼_ _β_ _i_, and summing over the player _i ∈{_ 1 _,_ 2 _}_, we find



_λ_ _i_ _t_ + [1]
�� _η_



_D_ KL ( _**π**_ _i,λ_ _[∗]_ _i_ _[∥]_ _**[π]**_ _i,λ_ _[t]_ _i_ [)]
� �



� _λ_ _i_ E _∼β_ _i_

_i∈{_ 1 _,_ 2 _}_



_λ_ _i_ _t_ + [1]
�� _η_



� _D_ KL ( _**π**_ _i,λ_ _[∗]_ _i_ _[∥]_ _**[π]**_ _i,λ_ _[t]_ [+1] _i_ [)] � = _i∈{_ � 1 _,_ 2 _}_ _λ_ _i_ E _∼β_ _i_



_D_ KL ( _**π**_ _i,λ_ _[∗]_ _i_ _[∥]_ _**[π]**_ _i,λ_ _[t]_ [+1] _i_ [)] = �
� �



_D_ KL ( _**π**_ _i,λ_ _[t]_ [+1] _i_ _[∥]_ _**[π]**_ _i,λ_ _[t]_ _i_ [)]
� �



_−_ � _λ_ _i_ E _∼β_ _i_

_i∈{_ 1 _,_ 2 _}_



_−_
�



_λ_ _i_ _t_ + [1]
�� _η_



+ E
� _λ_ _i_ _∼β_ _i_

_i∈{_ 1 _,_ 2 _}_



+
�



�� _−_ _**u**_ _[t]_ _i_ [+] _[ λ]_ _[i]_ _[∇][φ]_ [(] _**[π]**_ _i,λ_ _[t]_ _i_ [)] _[ −]_ _[λ]_ _[i]_ _[∇][φ]_ [(] _**[τ]**_ _[i]_ [)] _[,]_ _**[ π]**_ _i,λ_ _[∗]_ _i_ _[−]_ _**[π]**_ _i,λ_ _[t]_ [+1] _i_



_._

��



_._ (11)



~~�~~ ~~�~~ � ~~�~~
( _♣_ )


We now proceed to analyze the last summation on the right-hand side. First,



( _♣_ ) = � _λ_ _i_ E _∼β_ _i_ �� _−_ _**A**_ _i_ ¯ _**π**_ _−_ _[t]_ _i_ [+] _[ λ]_ _[i]_ _[∇][φ]_ [(] _**[π]**_ _i,λ_ _[t]_ _i_ [)] _[ −]_ _[λ]_ _[i]_ _[∇][φ]_ [(] _**[τ]**_ _[i]_ [)] _[,]_ _**[ π]**_ _i,λ_ _[∗]_ _i_ _[−]_ _**[π]**_ _i,λ_ _[t]_ _i_ ��

_i∈{_ 1 _,_ 2 _}_

~~�~~ � ~~�~~ ~~�~~
( _♠_ )



+ E
� _λ_ _i_ _∼β_ _i_

_i∈{_ 1 _,_ 2 _}_



+
�



�� _−_ _**u**_ _[t]_ _i_ [+] _[ λ]_ _[i]_ _[∇][φ]_ [(] _**[π]**_ _i,λ_ _[t]_ _i_ [)] _[ −]_ _[λ]_ _[i]_ _[∇][φ]_ [(] _**[τ]**_ _[i]_ [)] _[,]_ _**[ π]**_ _i,λ_ _[t]_ _i_ _[−]_ _**[π]**_ _i,λ_ _[t]_ [+1] _i_



��



~~�~~ ~~�~~ � ~~�~~
( _♥_ )

+ � _λ_ _i_ E _∼β_ _i_ �� _**A**_ _i_ ¯ _**π**_ _−_ _[t]_ _i_ _[−]_ _**[u]**_ _[t]_ _i_ _[,]_ _**[ π]**_ _i,λ_ _[∗]_ _i_ _[−]_ _**[π]**_ _i,λ_ _[t]_ _i_ �� _._ (12)

_i∈{_ 1 _,_ 2 _}_


21


Using Lemma 3 we can immediately write


( _♠_ ) _≤_ � _λ_ _i_ E _∼β_ _i_

_i∈{_ 1 _,_ 2 _}_



� _−λ_ _i_ _D_ KL ( _**π**_ _i,λ_ _[∗]_ _i_ _[∥]_ _**[π]**_ _i,λ_ _[t]_ _i_ [)] � _._



By manipulating the inner product in ( _♥_ ), we have



( _♥_ ) = � _λ_ _i_ E _∼β_ _i_

_i∈{_ 1 _,_ 2 _}_



_≤_ E
� _λ_ _i_ _∼β_ _i_

_i∈{_ 1 _,_ 2 _}_



� _⟨−_ _**u**_ _[t]_ _i_ _[,]_ _**[ π]**_ _i,λ_ _[t]_ _i_ _[−]_ _**[π]**_ _i,λ_ _[t]_ [+1] _i_ _[⟩−]_ _[λ]_ _[i]_ � _∇φ_ ( _**π**_ _i,λ_ _[t]_ _i_ [)] _[ −]_ _[φ]_ [(] _**[π]**_ _i,λ_ _[t]_ [+1] _i_ [)] _[,]_ _**[ π]**_ _i,λ_ _[t]_ [+1] _i_ _[−]_ _**[π]**_ _i,λ_ _[t]_ _i_ ��


� _⟨−_ _**u**_ _[t]_ _i_ _[,]_ _**[ π]**_ _i,λ_ _[t]_ _i_ _[−]_ _**[π]**_ _i,λ_ _[t]_ [+1] _i_ _[⟩]_ [+] _[ λ]_ _[i]_ � _D_ KL ( _**π**_ _i,λ_ _[t]_ [+1] _i_ _[∥]_ _**[τ]**_ _[i]_ [)] _[ −]_ _[D]_ [KL] [(] _**[π]**_ _i,λ_ _[t]_ _i_ _[∥]_ _**[τ]**_ _[i]_ [)] ��



�



_≤_ E
� _λ_ _i_ _∼β_ _i_

_i∈{_ 1 _,_ 2 _}_



_∥_ _**u**_ _[t]_ _i_ _[∥]_ [2] _∞_
_λ_ _i_ _t_ + [1]
� 4 _λ_ _i_ _t_ + 4 _/η_ [+] � _η_



_t_
_**π**_ _i,λ_ _i_ _[−]_ _**[π]**_ _i,λ_ _[t]_ [+1] _i_
����



��� 21



��� 21



+ E
� _λ_ _i_ _∼β_ _i_

_i∈{_ 1 _,_ 2 _}_



� _λ_ _i_ � _D_ KL ( _**π**_ _i,λ_ _[t]_ [+1] _i_ _[∥]_ _**[τ]**_ _[i]_ [)] _[ −]_ _[D]_ [KL] [(] _**[π]**_ _i,λ_ _[t]_ _i_ _[∥]_ _**[τ]**_ _[i]_ [)] �� _,_



where the last inequality follow from the fact that _ab ≤_ _a_ [2] _/_ (4 _ρ_ ) + _ρb_ [2] for all choices of _a, b ≥_ 0
and _ρ >_ 0. Substituting the individual bounds into (12) yields



( _♣_ ) _≤_ � _λ_ _i_ E _∼β_ _i_

_i∈{_ 1 _,_ 2 _}_



� _λ_ _i_ � _D_ KL ( _**π**_ _i,λ_ _[t]_ [+1] _i_ _[∥]_ _**[τ]**_ _[i]_ [)] _[ −]_ _[D]_ [KL] [(] _**[π]**_ _i,λ_ _[t]_ _i_ _[∥]_ _**[τ]**_ _[i]_ [)] ��



�



+ E
� _λ_ _i_ _∼β_ _i_

_i∈{_ 1 _,_ 2 _}_



_∥_ _**u**_ _[t]_ _i_ _[∥]_ [2] _∞_
_λ_ _i_ _t_ + [1]
� 4 _λ_ _i_ _t_ + 4 _/η_ [+] � _η_



_t_
_**π**_ _i,λ_ _i_ _[−]_ _**[π]**_ _i,λ_ _[t]_ [+1] _i_
����



��� 21



+ E
� _λ_ _i_ _∼β_ _i_

_i∈{_ 1 _,_ 2 _}_



�� _**A**_ _i_ ¯ _**π**_ _−_ _[t]_ _i_ _[−]_ _**[u]**_ _[t]_ _i_ _[,]_ _**[ π]**_ _i,λ_ _[∗]_ _i_ _[−]_ _**[π]**_ _i,λ_ _[t]_ _i_ �� _._



Finally, plugging the above bound into (11) and rearranging terms yields



_D_ KL ( _**π**_ _i,λ_ _[t]_ [+1] _i_ _[∥]_ _**[π]**_ _i,λ_ _[t]_ _i_ [)]
� �



Ψ _[t]_ [+1] _≤_ Ψ _[t]_ + E
� _λ_ _i_ _∼β_ _i_

_i∈{_ 1 _,_ 2 _}_



_−_ _λ_ _i_ _t_ + [1]
� � _η_



+ E
� _λ_ _i_ _∼β_ _i_

_i∈{_ 1 _,_ 2 _}_



_∥_ _**u**_ _[t]_ _i_ _[∥]_ [2] _∞_
_λ_ _i_ _t_ + [1]
� 4 _λ_ _i_ _t_ + 4 _/η_ [+] � _η_



_t_
_**π**_ _i,λ_ _i_ _[−]_ _**[π]**_ _i,λ_ _[t]_ [+1] _i_
����



��� 21



��� 21



+ E
� _λ_ _i_ _∼β_ _i_

_i∈{_ 1 _,_ 2 _}_



�� _**A**_ _i_ ¯ _**π**_ _−_ _[t]_ _i_ _[−]_ _**[u]**_ _[t]_ _i_ _[,]_ _**[ π]**_ _i,λ_ _[∗]_ _i_ _[−]_ _**[π]**_ _i,λ_ _[t]_ _i_ �� _._



2
_t_ +1
_**π**_
���� _i,λ_ _i_ _[−]_ _**[π]**_ _i,λ_ _[t]_ _i_ ��� 1



�



_≤_ Ψ _[t]_ + E
� _λ_ _i_ _∼β_ _i_

_i∈{_ 1 _,_ 2 _}_



_−_ _λ_ _i_ _t_ + [1]
� � _η_



�


�



+ E
� _λ_ _i_ _∼β_ _i_

_i∈{_ 1 _,_ 2 _}_



_∥_ _**u**_ _[t]_ _i_ _[∥]_ [2] _∞_
_λ_ _i_ _t_ + [1]
� 4 _λ_ _i_ _t_ + 4 _/η_ [+] � _η_



_t_
_**π**_ _i,λ_ _i_ _[−]_ _**[π]**_ _i,λ_ _[t]_ [+1] _i_
����



��� 21



��� 21



+ E
� _λ_ _i_ _∼β_ _i_

_i∈{_ 1 _,_ 2 _}_



�� _**A**_ _i_ ¯ _**π**_ _−_ _[t]_ _i_ _[−]_ _**[u]**_ _[t]_ _i_ _[,]_ _**[ π]**_ _i,λ_ _[∗]_ _i_ _[−]_ _**[π]**_ _i,λ_ _[t]_ _i_ �� _._



_≤_ Ψ _[t]_ + E
� _λ_ _i_ _∼β_ _i_

_i∈{_ 1 _,_ 2 _}_



4 _λ∥_ _i_ _**u**_ _t_ + 4 _[t]_ _i_ _[∥]_ [2] _∞_ _/η_ [+] � _**A**_ _i_ ¯ _**π**_ _−_ _[t]_ _i_ _[−]_ _**[u]**_ _[t]_ _i_ _[,]_ _**[ π]**_ _i,λ_ _[∗]_ _i_ _[−]_ _**[π]**_ _i,λ_ _[t]_ _i_ � _,_
� �



as we wanted to show.


**Theorem 4.** _As in Proposition 1, let_

_**π**_ ¯ _−_ _[t]_ _i_ [:=] _λ_ _−i_ E _∼β_ _−i_ � _**π**_ _−_ _[t]_ _i,λ_ _−i_ � _._


22


_Let_ _D_ [˜] KL _[T]_ _[be the notion of distance defined as]_



_D_ ˜ KL _[T]_ [:=] � _λ_ _i_ E _∼β_ _i_ �( _λ_ _i_ + _κ_ _T −_ 1 ) _D_ KL ( _**π**_ _i,λ_ _[∗]_ _i_ _[∥]_ _**[π]**_ _i,λ_ _[T]_ _i_ [)] � _._

_i∈{_ 1 _,_ 2 _}_


_At all times T_ = 2 _,_ 3 _, . . .,_




_[ n]_ _[i]_

+ _[W]_ [ 2]
_η_ 2



� _λ_ _i_ E _∼β_ _i_

_i∈{_ 1 _,_ 2 _}_







_D_ ˜ KL _[T]_ _[≤]_ [1]

_T_







_ρ_ + [lo][g] _[ n]_ _[i]_

_η_





2



2 log _T_
min
� � _λ_ _i_



g _T_

_, ηT_
_λ_ _i_ �� []



�



� _λ_ _i_ E _∼β_ _i_

_i∈{_ 1 _,_ 2 _}_



+ [2]

_T_



_T_
�


_t_ =1



�� _**A**_ _i_ ¯ _**π**_ _−_ _[t]_ _i_ _[−]_ _**[u]**_ _[t]_ _i_ _[,]_ _**[ π]**_ _i,λ_ _[∗]_ _i_ _[−]_ _**[π]**_ _i,λ_ _[t]_ _i_ �� _,_



_where_



_ρ_ := 2 � _λ_ _i_ E _∼β_ _i_ [[] _[λ]_ _[i]_ [] (log] _[ n]_ _[i]_ [ +] _[ Q]_ _[i]_ [)] _[.]_

_i∈{_ 1 _,_ 2 _}_



_Proof._ Using the bound on Ψ _[t]_ [+1] _−_ Ψ _[t]_ given by Proposition 1 we obtain



Ψ _[T]_ _−_ Ψ [1] =


_≤_



_T −_ 1
�(Ψ _[t]_ [+1] _−_ Ψ _[t]_ )


_t_ =1



_T −_ 1
�


_t_ =1



� _λ_ _i_ E _∼β_ _i_

_i∈{_ 1 _,_ 2 _}_



�



4 _λ∥_ _i_ _**u**_ _t_ + 4 _[t]_ _i_ _[∥]_ [2] _∞_ _/η_ [+] � _**A**_ _i_ ¯ _**π**_ _−_ _[t]_ _i_ _[−]_ _**[u]**_ _[t]_ _i_ _[,]_ _**[ π]**_ _i,λ_ _[∗]_ _i_ _[−]_ _**[π]**_ _i,λ_ _[t]_ _i_ �
� �



�

�



= [1]

4


_≤_ [1]

4



� _λ_ _i_ E _∼β_ _i_

_i∈{_ 1 _,_ 2 _}_



� _λ_ _i_ E _∼β_ _i_

_i∈{_ 1 _,_ 2 _}_



_T_
�


_t_ =1


_T_
�


_t_ =1



� _λ_ _i_ E _∼β_ _i_

_i∈{_ 1 _,_ 2 _}_



� _λ_ _i_ E _∼β_ _i_

_i∈{_ 1 _,_ 2 _}_



�



�



�� _**A**_ _i_ ¯ _**π**_ _−_ _[t]_ _i_ _[−]_ _**[u]**_ _[t]_ _i_ _[,]_ _**[ π]**_ _i,λ_ _[∗]_ _i_ _[−]_ _**[π]**_ _i,λ_ _[t]_ _i_ ��



�� _**A**_ _i_ ¯ _**π**_ _−_ _[t]_ _i_ _[−]_ _**[u]**_ _[t]_ _i_ _[,]_ _**[ π]**_ _i,λ_ _[∗]_ _i_ _[−]_ _**[π]**_ _i,λ_ _[t]_ _i_ �� _._



_T_
�
� _t_ =1


_T −_ 1
�
� _t_ =1



_∥_ _**u**_ _[t]_ _i_ _[∥]_ [2] _∞_
_λ_ _i_ _t_ + 1 _/η_


_W_ [2]


_λ_ _i_ _t_ + 1 _/η_



+


+



We can now bound


_T_
�


_t_ =1


On the other hand, note that



_W_ [2] _T_

_λ_ _i_ _t_ + 1 _/η_ _[≤]_ _[W]_ [ 2] �



1

_λ_ _i_ _t_ _[, η]_ �



_W_ [2]



1

� _t_ =1 min� _λ_ _i_



_T_
�
� _t_ =1



�



_T_
� _η_


_t_ =1



_T_
�



_≤_ _W_ [2] min



_t_ =1



1

_λ_ _i_ _t_ _[,]_



_≤_ _W_ [2] min 2 log _T_ _, Tη_ _._
� _λ_ _i_ �



_λ_ _i_ ( _T −_ 1) + [1]

_i_ �� _η_



Ψ _[T]_ _−_ Ψ [1] = _−_ Ψ [1] + E
� _λ_ _i_ _∼β_ _i_

_i∈{_ 1 _,_ 2 _}_



_D_ KL ( _**π**_ _i,λ_ _[∗]_ _i_ _[∥]_ _**[π]**_ _i,λ_ _[T]_ _i_ [) +] _[ λ]_ _[i]_ _[D]_ [KL] [(] _**[π]**_ _i,λ_ _[T]_ _i_ _[∥]_ _**[τ]**_ _[i]_ [)]
� �



_≥−_ Ψ [1] + � ( _T −_ 1) _λ_ _i_ E _∼β_ _i_ �( _λ_ _i_ + _κ_ _T −_ 1 ) _D_ KL ( _**π**_ _i,λ_ _[∗]_ _i_ _[∥]_ _**[π]**_ _i,λ_ _[T]_ _i_ [)] �

_i∈{_ 1 _,_ 2 _}_



_D_ KL ( _**π**_ _i_ _[∗]_ _,λ_ _i_ _[∥]_ _**[π]**_ _i_ [1] _,λ_ _i_ [)] _−_ _λ_ _i_ _D_ KL ( _**π**_ _i,λ_ [1] _i_ _[∥]_ _**[τ]**_ _[i]_ [)]
_η_
� �



= ( _T −_ 1) _D_ [˜] KL _[T]_ _[−]_ � _λ_ _i_ E _∼β_ _i_

_i∈{_ 1 _,_ 2 _}_


_≥_ ( _T −_ 1) _D_ [˜] KL _[T]_ _[−]_ � _λ_ _i_ E _∼β_ _i_

_i∈{_ 1 _,_ 2 _}_

= ( _T −_ 1) _D_ [˜] KL _[T]_ _[−]_ _[ρ,]_



log _n_ _i_

+ _λ_ _i_ (log _n_ _i_ + _Q_ _i_ )

� _η_ �


23


where the last inequality follows from expanding the definition of the KL divergence and using the
fact that _**π**_ _i,λ_ [1] _i_ [is the uniform strategy. Combining the inequalities and dividing by] _[ T][ −]_ [1][ yields]



_D_ ˜ KL _[T]_ _[≤]_ _[W]_ [ 2]

4



� _λ_ _i_ E _∼β_ _i_

_i∈{_ 1 _,_ 2 _}_



�



2 log _T_ _T_ _ρ_
�min� ( _T −_ 1) _λ_ _i_ _,_ _T −_ 1 _[η]_ �� + _T −_ 1



2 log _T_ _T_ _ρ_

( _T −_ 1) _λ_ _i_ _,_ _T −_ 1 _[η]_ �� + _T −_ 1



� _λ_ _i_ E _∼β_ _i_

_i∈{_ 1 _,_ 2 _}_



1
+
_T −_ 1



_T_
�


_t_ =1



�� _**A**_ _i_ ¯ _**π**_ _−_ _[t]_ _i_ _[−]_ _**[u]**_ _[t]_ _i_ _[,]_ _**[ π]**_ _i,λ_ _[∗]_ _i_ _[−]_ _**[π]**_ _i,λ_ _[t]_ _i_ �� _._



Finally, using the fact that 2( _T −_ 1) _≥_ _T_ yields the statement.


**Theorem 5** (Last-iterate convergence of DiL-piKL in two-player zero-sum games) **.** _Let ρ be as in_
_the statement of Theorem 4. When both players in a zero-sum game learn using DiL-piKL for T_
_iterations, their policies converge to the unique Bayes-Nash equilibrium_ ( _**π**_ 1 _[∗]_ _[,]_ _**[ π]**_ 2 _[∗]_ [)] _[ of the regularized]_
_game defined by utilities_ (4) _, in the following senses:_


_(a) In expectation: for all i ∈{_ 1 _,_ 2 _} and λ_ _i_ _∈_ Λ _i_ _, at a rate of roughly_ log _T/_ ( _λ_ _i_ _T_ )




_[ n]_ _[i]_

+ _[W]_ [ 2]
_η_ 2



� _λ_ _j_ E _∼β_ _j_

_j∈{_ 1 _,_ 2 _}_



 _._



1
E � _D_ KL ( _**π**_ _i,λ_ _[∗]_ _i_ _[∥]_ _**[π]**_ _i,λ_ _[T]_ _i_ [)] � _≤_ _λ_ _i_ _T_







_ρ_ + [lo][g] _[ n]_ _[i]_

_η_





2 log _T_
min
� � _λ_ _j_



g _T_

_, ηT_ _._
_λ_ _j_ �� []



2



�



_(We remark that for η_ = 1 _/√_



_T the convergence is never slower than_ 1 _/√_



_T_ _)._



_(b) With high probability, at a rate of roughly_ 1 _/√_



_T_ _: for any δ ∈_ (0 _,_ 1) _and Player i ∈{_ 1 _,_ 2 _},_



_T_



�



~~�~~



log _[|]_ [Λ] _[i]_ _[|]_



P



�



_√_
_∀_ _λ_ _i_ _∈_ Λ _i_ : _D_ KL ( _**π**_ _i,λ_ _[∗]_ _i_ _[∥]_ _**[π]**_ _i,λ_ _[T]_ _i_ [)] _[ ≤]_ [E] � _D_ KL ( _**π**_ _i,λ_ _[∗]_ _i_ _[∥]_ _**[π]**_ _i,λ_ _[T]_ _i_ [)] � + [8]



_√_ 2 _W_

_λ_ _i_ ~~_√_~~ _T_



_≥_ 1 _−_ _δ._



_δ_



_A n upper bound on_ E � _D_ KL ( _**π**_ _i,λ_ _[∗]_ _i_ _[∥]_ _**[π]**_ _i,λ_ _[T]_ _i_ [)] � _was given in the previous point._


_(c) Almost surely in the limit:_


_T →_ + _∞_
P � _∀_ _λ_ _i_ _∈_ Λ _i_ : _D_ KL ( _**π**_ _i,λ_ _[∗]_ _i_ _[∥]_ _**[π]**_ _i,λ_ _[T]_ _i_ [)] _−−−−−→_ 0� = 1 _∀i ∈{_ 1 _,_ 2 _}._


_Proof._ We prove the three statements incrementally.


(a) Let _F_ _t_ be the _σ_ -algebra generated by _{_ _**u**_ _[t]_ _i_ _[′]_ _[|][ t]_ _[′]_ [ = 1] _[, . . ., t][ −]_ [1] _[, i][ ∈{]_ [1] _[,]_ [ 2] _[}}]_ [. We let][ E] _[t]_ [[] _[ ·]_ [ ] :=]
E[ _· | F_ _t_ ]. Since piKL is a deterministic algorithm, _**π**_ _i,λ_ _[t]_ _i_ [is] _[ F]_ _[t]_ [-measurable. Hence, given]
that _**u**_ _[t]_ _i_ [is an unbiased estimator of] _**[ A]**_ _[i]_ [ ¯] _**[π]**_ _−_ _[t]_ _i_ [we have that at all times] _[ t]_


E _t_ �� _**A**_ _i_ ¯ _**π**_ _−_ _[t]_ _i_ _[−]_ _**[u]**_ _[t]_ _i_ _[,]_ _**[ π]**_ _i,λ_ _[∗]_ _i_ _[−]_ _**[π]**_ _i,λ_ _[t]_ _i_ �� = �E _t_ � _**A**_ _i_ ¯ _**π**_ _−_ _[t]_ _i_ _[−]_ _**[u]**_ _[t]_ _i_ � _,_ _**π**_ _i,λ_ _[∗]_ _i_ _[−]_ _**[π]**_ _i,λ_ _[t]_ _i_ � = 0 _._ (13)


Note that from the definition of _D_ [˜] KL _[T]_ [given in Theorem 4]

_D_ KL ( _**π**_ _i,λ_ _[∗]_ _i_ _[∥]_ _**[π]**_ _i,λ_ _[T]_ _i_ [)] _[ ≤]_ _λ_ [1] _i_ _D_ ˜ KL _[T]_ _[.]_ (14)


Hence, taking expectations and using (13) yields the statement.



(b) To prove high-probability convergence, we use the Azuma-Hoeffding concentration inequality. In particular, (13) shows that the stochastic process
 _[t]_ _[t]_ _[∗]_ _[t]_ 



 _j∈{_ [�] 1 _,_



E
_λ_ _j_ _∼β_ _j_
_j∈{_ [�] 1 _,_ 2 _}_



� _⟨_ _**A**_ _j_ ¯ _**π**_ _−_ _[t]_ _j_ _[−]_ _**[u]**_ _[t]_ _j_ _[,]_ _**[ π]**_ _j_ _[∗]_ _[−]_ _**[π]**_ _j_ _[t]_ _[⟩]_ �







_,_ _t_ =1 _,_ 2 _,..._


is a martingale difference sequence adapted to the filtration _F_ _t_ . Furthermore, note that


� _λ_ _j_ E _∼β_ _j_ � _⟨_ _**A**_ _j_ ¯ _**π**_ _−_ _[t]_ _j_ _[−]_ _**[u]**_ _[t]_ _j_ _[,]_ _**[ π]**_ _j,λ_ _[∗]_ _j_ _[−]_ _**[π]**_ _j,λ_ _[t]_ _j_ _[⟩]_ � _≤_ 4 _W_

������ _j∈{_ 1 _,_ 2 _}_ ������



�



� _λ_ _j_ E _∼β_ _j_

_j∈{_ 1 _,_ 2 _}_



� _⟨_ _**A**_ _j_ ¯ _**π**_ _−_ _[t]_ _j_ _[−]_ _**[u]**_ _[t]_ _j_ _[,]_ _**[ π]**_ _j,λ_ _[∗]_ _j_ _[−]_ _**[π]**_ _j,λ_ _[t]_ _j_ _[⟩]_ � _≤_ 4 _W_
������



24


for all _t_ . Hence, using the Azuma-Hoeffding inequality for martingale difference sequences
we obtain that for all _δ ∈_ (0 _,_ 1),



� _⟨_ _**A**_ _j_ ¯ _**π**_ _−_ _[t]_ _j_ _[−]_ _**[u]**_ _[t]_ _j_ _[,]_ _**[ π]**_ _j_ _[∗]_ _[−]_ _**[π]**_ _j_ _[t]_ � _⟩≤_ 4 _W_



 _≥_ 1 _−_ _δ._





�



2 _T_ log [1]

_δ_



P







_T_



�


_t_ =1





_t_ =1



� _λ_ _j_ E _∼β_ _j_

_j∈{_ 1 _,_ 2 _}_



Plugging the above probability bound in the statement of Theorem 4 and using the union
bound over _λ_ _i_ _∈_ Λ _i_ yields the statement.


(c) follows from (b) via a standard application of the Borel-Cantelli lemma.


F M ODEL ARCHITECTURE


Our model architecture closely resembles the architecture used in past work on no-press Diplomacy
(Bakhtin et al., 2021; Jacob et al., 2022; Anthony et al., 2020; Paquette et al., 2019; Gray et al.,
2020).


**Feature** **Type** **Number of Channels**


Presence of army/fleet? Binary 2
Army/fleet owner One-hot (7 players), or all zero 7
Build turn build/disband Binary 2
Dislodged army/fleet? Binary 2
Dislodged unit owner One-hot (7 players), or all zero 7
Land/coast/water One-hot 3
Supply center owner One-hot (7 players), or all zero 8
Home center One-hot (7 players), or all zero 7


Table 3: Per-location board state input features


**Feature** **Type** **Number of Channels**


Number of builds allowed during winter Float 1


Table 4: Per-player board state input features


**Feature** **Type** **Channels**


Season (spring/fall/winter) One-hot 3
Year (encoded as ( _y −_ 1901) _/_ 10) Float 1
Game has dialogue? Binary 1
Scoring system used One-hot 2


Table 5: Global board state input features


Given a gamestate, to construct the input to the model, for each of the 81 possible locations and/or
special coastal areas on the board that a unit can occupy, we encode the 38 feature channels described
in Table 3 for that location. We also encode the previous board state in this way, as well using an
encoding of the order history as described in Gray et al. (2020) provides an additional 202 channels
per board location indicating the prior orders at that location.


Separately, we also encode per-player and global features of the gamestate into additional tensors
(Table 4,Table 5). Each of these tensors (per-location, per-player, global) is passed through a linear
layer with 224 output channels, and then all three are concatenated to a single (81+7+1) x 224
tensor. Thereafter, following Bakhtin et al. (2021), we apply a learnable positional bias and pass


25


Figure 4: Model architecture used for policy/value learning in no-press Diplomacy.


the result to a to a standard transformer encoder architecture with 10 layers, channel width 224, 8
dot-product-self-attention heads per layer, and GeLU activation.


Finally we decode the policy via the same LSTM decoder head as Gray et al. (2020), and predict the
game values of all 7 players using a value head that applies softmax attention to the encoder output,
followed by a linear layer with 224 channels, GeLU activation, a linear layer with 7 channels, and a
softmax. See Figure 4 for a graphical diagram of the model.


26


G H UMAN I MITATION A NCHOR P OLICY T RAINING


Similar to prior work (Bakhtin et al., 2021; Jacob et al., 2022; Gray et al., 2020), to obtain a human
imitation anchor policy with which to use for piKL regularization and to initialize the RL policy,
we train the architecture described in Appendix F on a dataset of roughly 46000 online Diplomacy
games provided by webdiplomacy.net. We train jointly on both games with full-press Diplomacy
(i.e. where players were able to communicate via messages) and no-press Diplomacy and at inference time and/or during RL, condition the relevant global feature in Table 5 to indicate the model
should predict for no-press Diplomacy. Also in common with the same prior work, we apply data
filtering to skip training on actions where players missed the time limit and a default null action was
inputted by the website, and to only train on actions played by the top half of rated players. We
also adopt the method of Jacob et al. (2022) to augment the data by permuting the labels of the 7
players randomly during training, since the game’s rules are fully equivariant to such permutations.
See Table 6 for a list of other hyperparameters.


Learning rate 2 _×_ 10 _[−]_ [3]
Learning rate decay per epoch 0.99
Linear LR warmup epochs 10
Total epochs 390
Gradient clip max norm 0.5
Batch size 16000
Batches per epoch 270
Value loss weight 0.7
Policy loss weight 0.3
Optimizer ADAM
Transformer encoder dropout 0.3
Policy head LSTM dropout 0.3


Table 6: Hyper-parameter values used to train the IL anchor policy on human data.


H S ELF - PLAY T RAINING


Our self-play training algorithm closely matches that of DORA from Bakhtin et al. (2021), described
in detail in Section 2.3. The overall self-play procedure (see Figure 5), the training data recorded,
loss function used on that data, and sampling methods we use are all the same. The differences are:


    - Although our model architecture is largely identical to that of past work, some minor details, including the precise encoding of input features, and the construction of the value
head are different, see Appendix F for description of our architecture.


   - During RL training, we initialize the RL policy proposal and value functions from the
human IL anchor policy and value function (Appendix G) instead of randomly from scratch,
and during training, rather than using regret matching to compute the 1-step equilibrium _σ_
on each turn of the game, we use DiL-piKL. The distribution of _λ_ and the human IL anchor
policy remain fixed through all of training.


    - During training, the action chosen to explore in the self-play game uses a randomly chosen
_λ_ from the DiL-piKL distribution. Similarly, the RL policy is trained to predict the policy
of a random _λ_ . This ensures that the RL policy, when used at test time to propose actions,
samples both human IL-like actions from high _λ_, as well as more optimized actions from
lower _λ_, and that gamestates resulting from the entire range of possible _λ_ are in-distribution
for the RL policy and value models.


   - Unlike DORA, double-oracle action exploration is _not_ used during training. We found
that with the additional diversity and regularization of the human anchor policy, it was

unnecessary.


    - All models were also trained with the same stochastic game-end rules we used in evaluation
games against human players described in Section 5.1.


27


**Algorithm 2:** RL Loop


1 **function** D ATA G ENERATION L OOP ()

2 **while** _true_ **do**

3 Game _←_ N EW G AME ()

4 _θ_ _v_ _←_ G ET N EW V ALUE F UNCTION ()

5 _θ_ _π_ _←_ G ET N EW P OLICY F UNCTION () // Not used for NPU algorithm

6 **while** _not_ I S D ONE _(Game)_ **do**

7 _s ←_ E NCODE S TATE (Game)

8 _**A**_ _←_ G ET P LAUSIBLE A CTION ( _θ_ _π_ )

9 _**A**_ _←_ D OUBLE O RACLE A CTION E XPLORATION ( _**A**_ _, θ_ _π_ _, θ_ _v_ ) // Only used for DORA

10 _**σ**_ _,_ _**u**_ _←_ R UN S EARCH ( _s,_ _**A**_ _, θ_ _v_ _, τ_ ) // Regret Matching or DiL-piKL

11 S END T O B UFFER ( _s,_ _**σ**_ _,_ _**u**_ )
// Sample from the policy with possible _ϵ_ -exploration

12 _**a**_ _←_ S ELECT A CTION ( _**σ**_ )

13 Game _←_ N EXT S TATE (Game _,_ _**a**_ )


14 **function** T RAINING L OOP ()

15 _θ_ _v_ _←_ _BCV alue_ () // Not used for DORA

16 _θ_ _π_ _←_ _BCPolicy_ () // Not used for DORA

17 **while** _true_ **do**

18 _s,_ _**σ**_ _,_ _**u**_ _←_ R EAD F ROM B UFFER ()

19 _Loss ←_ P OLICY L OSS ( _s,_ _**σ**_ _, θ_ _π_ ) + V ALUE L OSS ( _s,_ _**u**_ _, θ_ _v_ )

20 G RADIENT S TEP ( _Loss_ )

21 S AVE N EW V ALUE F UNCTION ( _θ_ _v_ )

22 S AVE N EW P OLICY F UNCTION ( _θ_ _π_ )


Figure 5: High-level description of DNVI-style algorithms. The DORA agent is initialized from
scratch and requires a Double Oracle action exploration procedure to perform well. The NPU
(no policy update) modification uses the behavioral cloning policy for the policy proposal network
throughout the whole training. DORA, DNVI, and DNVI-NPU use RM as the search algorithm,
while the other training methods use DiL-piKL. .


   - Some hyperparameters we use may be different than that of past work. See Appendix H.1
for a list of hyperparameters.


H.1 H YPER - PARAMETERS FOR RL TRAINING


For the evaluation in this paper we trained Diplodocus and BRBot agents and re-trained DNVI,
DNVI-NPU, and DORA agents. We provide the hyper-parameters used in table 7. We show parameters out of 3 agents from Bakhtin et al. (2021) as they are the same.


H.2 I NFERENCE TIME EFFECT OF D I L- PI KL


In Figure 6 we show that running DiL-piKL at evaluation time alone is not enough to get the demonstrated performance improvement in population scores. Using DiL-piKL on top of human imitationlearned policy/value functions does not improve the population score compared to Hedge. However,
applying this search method on top of policies/values that were trained via RL with DiL-piKL results
in significant improvement in the scores.


I B AYES -ELO


BayesElo (Coulom, 2005) models each player’s expected share of the total score in a 2-player game
as proportional to:
exp(( _r_ _i_ + _b_ _s_ ( _i_ ) ) _/c_ )


where _r_ _i_ is the Elo rating of player _i_, _b_ 1 and _b_ 2 are the advantage/disadvantage of playing first/second
in Elo, _s_ ( _i_ ) _∈_ 1 _,_ 2 indicates whether _i_ played first or second, and _c_ = 400 log 10 ( _e_ ) is a fixed scaling
constant that adjusts for the particular arbitrary numerical scale of ratings expected by users, in


28


Diplodocus Diplodocus BRBot DORA
High Low


Learning rate 10 _[−]_ [4]
Gradient clip max norm 0.5
Warmup updates 10k
Batch size 1024
Buffer size 1,280,000
Max train/generation ratio 6
Optimizer ADAM
Transformer encoder dropout 0
Policy head LSTM dropout 0


Search algorithm DiL-piKL DiL-piKL DiL-piKL RM
Type distribution (self) _{_ 10 _[−]_ [2] _,_ 10 _[−]_ [1] _}_ _{_ 10 _[−]_ [4] _,_ 10 _[−]_ [1] _}_ _{_ + _∞}_ _{_ 0 _}_
Type distribution (other) _{_ 10 _[−]_ [2] _,_ 10 _[−]_ [1] _}_ _{_ 10 _[−]_ [4] _,_ 10 _[−]_ [1] _}_ _{_ 0 _}_ _{_ 0 _}_
Search iterations 256 256 256 256
Number of candidate actions ( _N_ _c_ ) 50 50 50 50
Max candidate actions per unit 6 6 6 6
Nash explore ( _ε_ ) 0.1 0.1 0.1 0.1
Nash explore, S1901M 0.1 0.1 0.1 0.3
Nash explore, F1901M 0.1 0.1 0.1 0.2


Table 7: Hyper-parameter values used to train RL agents.








|5|Col2|Col3|Col4|Col5|Col6|Col7|Col8|Col9|Col10|Col11|Col12|
|---|---|---|---|---|---|---|---|---|---|---|---|
|5||||||||||||
|5<br>0<br>||||||||||||
|5<br>0<br>||||||||||||
|5<br>0<br>||||||||||||
|5<br>0<br>||||||||||||
|0||||||||||||
|~~Hedge~~<br>~~DiL-piKL~~<br>Inference search method<br>0<br>5||||||||||||



Figure 6: Performance of different search algorithms at inference time for models trained with RL
and IL. Applying DiL-piKL at inference time rather than Hedge only slightly improves an IL-based
search agent, but greatly improves RL agents trained with DiL-piKL.


particular that 400 points in Elo systems generally corresponds to a 10-fold increase in expected
winning odds or expected average score..


It then finds joint maximum-a-posteriori values _r_ _i_, _b_ _i_ given all observed data and an optional prior to
regularize the model. In some cases, the biases _b_ _i_ may also be hardcoded or provided as parameters
rather than inferred from the data, in our work we infer them. In our application, we use a weak
Bayesian prior such that each player’s rating was a-priori normally distributed around 0 with a
standard deviation of around 350 Elo.


BayesElo generalizes naturally to more than 2 players simply by allowing _i_ and _s_ ( _i_ ) to range over
_{_ 1 _, ..., n}_ rather than _{_ 1 _,_ 2 _}_, and we straightforwardly apply this to Diplomacy. Since there are 7
players, we similarly jointly fit _b_ 1,... _b_ 7 on the data to model the asymmetric advantage/disadvantage
of the 7 different starting positions. Computed Elo ratings closely reflect empirical winning percentages of players in a given population, but also take into account variability in the strength of
opposition in a game, and the starting advantage/disadvantage _b_ _i_ . For example, if a player achieved
a high average score but was abnormally lucky in drawing advantageous starting countries across
all their games, then the model would likely estimate a lower rating than if they achieved the same
results with more difficult starting countries.


29


In Diplomacy, on the 200 games of the human tournament in which we evaluated Diplodocus and
other agents, the empirical fitted _b_ _i_ values for the 7 different starting countries in the game are
displayed in Table 8.


Starting Country _b_ _i_ (Elo)


Austria -24
England -43
France 59
Germany 18
Italy -21
Russia -16
Turkey 27


Table 8: For each starting country, the empirical advantage/disadvantage of starting as that country measured
in Elo rating equivalent units, fitted jointly with all players’ Elo ratings on the 200 Diplomacy games of the
tournament. The values roughly agree with common opinions among Diplomacy players, particularly that
France is one of the best starting countries in no-press, while Austria and England are among the weaker starts.


30


