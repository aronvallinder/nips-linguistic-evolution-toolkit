Published as a conference paper at ICLR 2022

# E MERGENT C OMMUNICATION AT S CALE


**Rahma Chaabouni** _[∗]_, **Florian Strub** _[∗]_, **Florent Altch´e**, **Corentin Tallec**, **Eugene Trassov**, **Elnaz**
**Davoodi**, **Kory Mathewson**, **Olivier Tieleman**, **Angeliki Lazaridou**, **Bilal Piot**


DeepMind


A BSTRACT


Emergent communication aims for a better understanding of human language evolution and building more efficient representations. We posit that reaching these
goals will require scaling up, in contrast to a significant amount of literature that
focuses on setting up small-scale problems to tease out desired properties of the
emergent languages. We focus on three independent aspects to scale up, namely
the dataset, task complexity, and population size. We provide a first set of results for large populations solving complex tasks on realistic large-scale datasets,
as well as an easy-to-use codebase to enable further experimentation [1] . In more
complex tasks and datasets, we find that RL training can become unstable, but responds well to established stabilization techniques. We also identify the need for
a different metric than topographic similarity, which does not correlate with the
generalization performances when working with natural images. In this context,
we probe ease-of-learnability and transfer methods to assess emergent languages.
Finally, we observe that larger populations do not induce robust emergent protocols with high generalization performance, leading us to explore different ways to
leverage population, through voting and imitation learning.


1 I NTRODUCTION


Language emergence is at the intersection of cognitive science and machine learning. From a cognitive science view, researchers have been looking at artificial agents as another expressive species to
shed light on the source of linguistic regularities (Wagner et al., 2003; Guo et al., 2019; Chaabouni
et al., 2021). From a machine learning view, language evolution is deemed as a promising direction
to shape agents’ representation and design interactive AI (Steels, 1997; Lazaridou et al., 2020).


Most of the literature in this field relies on different variants of the Lewis game (Lewis, 1969).
There, a speaker network must describe an object to a listener network, which must then retrieve it
among a set of other objects. To solve the game, the two agents need to settle on a communication
protocol. While deep agents manage to solve the Lewis game, their communication protocols are
usually degenerate, lacking core properties of human languages (Bouchacourt & Baroni, 2018;
Chaabouni et al., 2019). In response to these findings, several works proposed ad-hoc solutions
by constraining the game and agents’ capacity (Kottur et al., 2017; Resnick et al., 2020). While
reducing problem complexity is tempting, it can lead to unexpected outcomes and may miss general
language emergence behaviors (Hayes, 1985). We take a different route and advocate that scaling
up communication games is a prerequisite to building interactive AI (Baroni et al., 2017; Sutton,
2019) or modeling language evolution (Barsalou, 2008). Indeed, contrary to other machine learning
communities, the emergent communication field mostly relies on small-scale games where only one
speaker and one listener communicate about disentangled stimuli, which can hinder the generality of
its conclusions. In this paper, we focus on three scaling dimensions: the dataset, the task complexity,
and the population size. That is, we argue that making populations of deep agents communicate
about larger and more realistic datasets and solve more complex tasks, is necessary if in the end we
want these agents to interact with us or if we want to model human communication.


We study three properties of emergent languages: generalization, robustness to input noise, and ease
of learning over transfer tasks, analyzing different facets of communication protocols. The proposed


_∗_ Contributed equally. Corresponding authors: _{_ rahmac,fstrub,piot _}_ @deepmind.com
1 Source code: github.com/deepmind/emergent_communication_at_scale


1


Published as a conference paper at ICLR 2022


scaling up remains computationally tractable, as most of the experiments can be done within a day
on a single GPU. The source code is based on the Jaxline pipeline (Babuschkin et al., 2020).


Overall, our experiments provide a large spectrum of observations, both positive and negative. First,
we found that scaling up the Lewis game quickly entails unstable RL optimization. We propose KL
regularization (Geist et al., 2019) as an effective way to overcome this issue. Second, we observe
that complexifying the task has two positive aspects: it better discriminates between methods and
improves the generalization of the learned communication protocol. Third, we note no correlation
between generalization and the widely used topographic similarity metric, which suggests that the
latter is not adequate to assess the compositionality of the languages in our more complex setup. Instead, we take inspiration from the self-supervised learning literature and explore transfer learning as
a new evaluation metric. Fourth, unlike what was observed in human communication (Gary Lupyan,
2010; Raviv et al., 2019a;b), we find little to no systematic benefit on emergent languages’ properties
when increasing the population size. Instead, we propose alternative methods to leverage populations, namely voting and imitation among speakers (Hester et al., 2018; Vecerik et al., 2017). In
particular, we show that such population dynamics lead to more robust, productive, and in some
cases easy-to-learn languages even when compared to our best seed without population, opening
up new research opportunities. In the end, we expect that these observations, baselines, and good
practices would allow the language emergence community to benefit further from deep RL advances
and move the field closer to its goals of improving representations and interactive systems.


2 S ETUP


2.1 D ISCRIMINATION GAME


The discrimination game involves two players, _Speaker_ and _Listener_, and is decomposed into three
sequential stages. First, Speaker receives a target image _x_ and outputs a message _m_ that is sent to
Listener. Second, Listener receives _m_ and selects an image ˆ _x_ among a set _C_ of different images
containing the target image _x_ . The set _C_ is called _candidates_ . Finally, the target image _x_ is revealed
to Listener. If Listener selects the target image, then both players receive a positive reward of 1, and
0 otherwise. Speaker and Listener are parameterized by a set of parameters _θ_ and _φ_ respectively. The
message _m_ ( _x, θ_ ) = ( _w_ _t_ ( _x, θ_ )) _[T]_ _t_ =0 _[ −]_ [1] [is a sequence of length] _[ T]_ [ of words] _[ w]_ _[t]_ [(] _[x, θ]_ [)][. When no confusion]
is possible, we omit the dependence on _x_ and _θ_ to simplify notations. A word _w_ _t_ is an element of a
finite vocabulary set _W_ . For the image selected by Listener ˆ _x_ ( _φ, m, C_ ), we also omit the dependence
on _φ_, _m_ and _C_ . Finally, the reward for Listener and Speaker is denoted by _R_ ( _x,_ ˆ _x_ ) = 1 _x_ =ˆ _x_ .


**Communication in a population of agents.** A straightforward extension of the standard discrimination game is to train a population of agents. In this case, given a population of _N_ Speakers and _N_
Listeners, we sample _S_ Speakers and _S_ Listeners with replacement at each training step to construct
_S_ random pairs; where each Speaker is paired with only one Listener. [2] All pairs observe the same
examples and are trained independently to play the discrimination game as described in the 1-pair
setting above. In our case, _S_ = _N_ so that each agent is trained on average once per step, which
allows a fair comparison with the baseline of 1-pair. At inference time, we take the first _P_ Speakers and Listeners and construct all the possible _P_ [2] pairs to compute the accuracy, by averaging the
rewards of all pairs as in (Mordatch & Abbeel, 2018).


**Exploiting the population.** The training dynamic of the population of agents described above does
not take advantage of the diversity of the population. Indeed, we treat all agents in the same way.
Yet, one motivation for the effectiveness of the population is the variety between Speakers to invent
new structures and between Listeners to avoid over-specialization (Bromham et al., 2015). Prior
works have looked at the impact of training agents with different dynamics (e.g., Ren et al., 2019;
Guo et al., 2019; Cogswell et al., 2019; Li & Bowling, 2019). In this work, we introduce two
different ways to exploit the population; on Speakers’ side, we add imitation, and on Listeners’ side,
we allow Listeners to vote to get the final prediction. Mathematical details are found in Sec. 2.3.

_Imitation_ training consists of two different steps. First, as described above, Speakers and Listeners
are paired randomly for _M_ interaction steps to learn to communicate. Second, Speakers are trained
for 1 imitation step as follows: we select the best Speaker (called “teacher”) among _K_ randomly
sampled Speakers without replacement, and use the remaining _K_ -1 samples as “students”. We then
train all students in a supervised way to imitate the teacher. We alternate between the interaction


2 In this work, we only consider populations with the same number of Speakers and Listeners.


2


Published as a conference paper at ICLR 2022


and imitation steps. Both _M_ and _K_ are hyper-parameters (see Appendix A.5). Finally, _Voting_ is
only used at inference time, irrespective of the training mode. Here, instead of averaging _P_ [2] pairs’
rewards to compute accuracy, we now allow _P_ Listeners to vote to get a unique prediction. This is
inspired by ensemble methods to reduce prediction errors (Polikar, 2012). More details on imitation
and voting are reported in Sec. 2.3. For completeness, we also reproduce ease-of-teaching protocol
as another effective way to exploit population in Appendix B.4 (Li & Bowling, 2019).


2.2 D ATASETS AND N EURAL A RCHITECTURES


**Datasets.** We use the ImageNet (Deng et al., 2009; Russakovsky et al., 2015), and CelebA
datasets (Liu et al., 2015), which respectively contain 1400k and 200k labelled images. CelebA
contains 40 binary attributes per image, such as the presence of glasses, blond ~~h~~ air. As the official
CelebA splits have non-overlapping identities, it is impossible to perform regular identity classification on the test/valid sets. We thus construct a new split, where we shuffle images to have overlapping
identities across splits. In both datasets, each image is center-cropped before being processed by a
ResNet-50 encoder _f_ pretrained on ImageNet with the self-supervised method BYOL (Grill et al.,
2020) to extract a representation of size 2048. Full implementation details are in Appendix A.6.


**Speaker architecture.** Speaker is a neural network that receives an image _x_ and outputs a message _m_ = ( _w_ _t_ ) _[T]_ _t_ =0 _[ −]_ [1] [. It is composed of a fixed (non-trainable) image encoder] _[ f]_ [ that transforms]
_x_ into an embedding _f_ ( _x_ ), before being projected by a state adapter _c_ _θ_ to an initial state of an
LSTM (Hochreiter & Schmidhuber, 1997), _z_ _−_ 1 _,θ_ = _c_ _θ_ ( _f_ ( _x_ )). The LSTM receives as input a word
embedding _e_ _t,θ_ = _g_ _θ_ ( _w_ _t−_ 1 ) and outputs the next state _z_ _t,θ_ = _h_ _θ_ ( _z_ _t−_ 1 _,θ_ _, e_ _t,θ_ ). The first word embedding _e_ 0 _,θ_ = _g_ _θ_ (sos) is initialized with a start of sequence. The state _z_ _t,θ_ is then fed to two
different heads; the value head _v_ _θ_ estimates the value of the expected reward knowing _z_ _t,θ_ and the
policy head _π_ _θ_ computes the probability of the chosen word given _z_ _t,θ_ . Then, a sampling function
_s_ picks the word _w_ _t_ = _s_ ( _π_ _θ_ ( _.|z_ _t,θ_ )). Finally _w_ _t_ is fed back to _g_ _θ_ to produce the next word and
so on until the maximum length _T_ is reached. At training, the word _w_ _t_ is sampled according to
the policy whereas it is greedily selected at evaluation. Contrary to prior works (e.g., Kottur et al.,
2017; Resnick et al., 2020), we do not restrict the channel capacity of agents to spur the emergence
of systematic languages. Instead, we endow Speaker with a message space of size _|W_ _|_ _[T]_ = 20 [10]
( _|W_ _|_ = 20, _T_ = 10), significantly larger than the number of available training examples.


**Listener architecture.** Listener is a neural network that receives Speaker’s message _m_ and a set
of image candidates _C_, containing the target image _x_ . It outputs the probability over each image
_x_ ˜ _∈C_ of being the target image. Listener is composed of an LSTM cell _h_ _φ_, which is initialized to
the null vector _z_ _−_ 1 _,φ_ . The message _m_ is decoded by processing the sequence of word embeddings
_e_ _t,φ_ = _g_ _φ_ ( _w_ _t_ ) through the LSTM such as _z_ _t,φ_ = _h_ _φ_ ( _z_ _t−_ 1 _,φ_ _, e_ _t,φ_ ). The state _z_ _T −_ 1 _,φ_ is then fed to the
network _p_ _φ_ to output _p_ _m,φ_ = _p_ _φ_ ( _z_ _T −_ 1 _,φ_ ). In parallel, each image ˜ _x_ is projected through the encoder
_f_ and the network _t_ _φ_ to obtain the image embedding _t_ _x_ ˜ = _t_ _φ_ ( _f_ (˜ _x_ )). Both message and image
embeddings are then compared through a score function score( _m,_ ˜ _x, φ_ ) = cos( _∥pp_ _m,φm,φ_ _∥_ 2 _[,]_ _∥tt_ _x_ ˜ _x_ ˜ _∥_ 2 [)][.]
The scores over all images are normalized via a softmax to get a probability _π_ _φ_ ( _.|m, C_ ). Finally,
Listener selects an image by taking the best guess according to _π_ _φ_, i.e. ˆ _x ∈_ arg max _x_ ˜ _∈C_ _π_ _φ_ (˜ _x|m, C_ ).


Architecture details, hyper-parameters and graphical descriptions are provided in Appendices A.2
and A.4. All experiments are run over 10 seeds.


2.3 O PTIMIZATION


**Speaker training and loss.** The goal of Speaker is to optimize the message _m_ sent to Listener such
that the expected reward of the game is the highest possible. This can be framed as a sequential
decision making problem where the decision is the choice of each word _w_ _t_ . Therefore, following
the policy gradient approach with a baseline (Sutton et al., 2000), we train Speaker’s network by (i)
minimizing a value loss _L_ _V_ ( _θ_ ) to make the value head _v_ _θ_ ( _z_ _t,θ_ ) fit the expected reward over a batch
_X_ : _L_ _V_ ( _θ_ ) = _|X|_ 1 � _x∈X_ � _Tt_ =0 _−_ 1 [(] _[R]_ [(] _[x,]_ [ ˆ] _[x]_ [)] _[ −]_ _[v]_ _[θ]_ [(] _[z]_ _[t,θ]_ [))] [2] _[,]_ [ (ii) maximizing the expected reward through]

minimizing the policy loss _L_ _π_ ( _θ_ ) = _|X|_ 1 � _x∈X_ � _tT_ =0 _−_ 1 [sg][ (] _[R]_ [(] _[x,]_ [ ˆ] _[x]_ [)] _[ −]_ _[v]_ _[θ]_ [(] _[z]_ _[t,θ]_ [)) log(] _[π]_ _[θ]_ [(] _[w]_ _[t]_ _[|][z]_ _[t,θ]_ [))][,]

where sg( _._ ) is the stop gradient function.


In addition, it is common practice in RL and emergent language literature to minimize an entropy
loss _L_ _H_ ( _θ_ ) encouraging to explore other choices of words by Speaker (Mnih et al., 2016; Williams
& Peng, 1991; Espeholt et al., 2018). Finally, several deep RL (Schulman et al., 2015; 2017) and


3


Published as a conference paper at ICLR 2022


theoretical RL papers (Geist et al., 2019; Vieillard et al., 2020a;b) argued that minimizing a KL
loss _L_ KL ( _θ_ ) between the online policy _π_ _θ_ and a target policy _π_ _θ_ instead of or in addition to entropy
regularization could be beneficial for better final performance as well as stabilizing the learning.
The policy _π_ _θ_ is obtained by doing an exponential moving average of the weights _θ_ over training:
_θ ←_ (1 _−_ _η_ ) _θ_ + _ηθ_ where _η_ is the exponential moving average parameter. The KL minimization
encourages the online policy to change slowly and smoothly.
To sum up, the speaker training loss _L_ ( _θ_ ) on a batch of images _X_ is: _L_ ( _θ_ ) = _L_ _V_ ( _θ_ ) + _L_ _π_ ( _θ_ ) +
_αL_ _H_ ( _θ_ ) + _βL_ KL ( _θ_ ), where _α_ and _β_ are hyper-parameters.


**Listener training and loss.** Listener is also trained to maximize the reward but acts by predicting
the best guess for the game ˆ _x ∈_ arg max _x_ ˜ _∈C_ _π_ _φ_ (˜ _x|m, C_ ). For each image _x_ in a batch _X_, a set of
image candidates _C_ is sampled randomly (uniform without replacement over _X \ {x}_ ) chosen in _X_ .
When _|C|_ = _|X|_, we take _C_ = _X_ . Finally, Listener’s goal is to retrieve _x_ among _C_, i.e. outputting
a probability _π_ _φ_ (˜ _x|m, C_ ) = 1 if _x_ = ˜ _x_ and _π_ _φ_ (˜ _x|m, C_ ) = 0 otherwise. Therefore, we use a multiclass classification loss where the correct class is the index of _x_ in the set of candidates _C_ also called
InfoNCE loss (van den Oord et al., 2018): _L_ ( _φ_ ) = _−_ _|X|_ [1] � _x∈X_ [log (] _[π]_ _[φ]_ [(] _[x][|][m,][ C]_ [))][.]


**Imitation training among a group of Speakers.** In a training imitation step, a group of _K_ speakers
among the total population of _N_ speakers is sampled without replacement. Among those _K_ speakers, one speaker plays the role of the teacher and _K −_ 1 play the role of the students. To choose
the teacher, we compute, for each sampled speaker _i_, the exponential moving average of the accuracies over each batch on which the speaker _i_ has been trained on, _σ_ _i_ . Then the teacher is simply
the speaker with the highest _σ_ _i_ . For convenience,we respectively note _θ_ _T_ and _θ_ _S_ the parameters of
the teacher and student. A student _θ_ _S_ is trained on a batch of data _X_ by imitating the messages of
the teacher _θ_ _T_ with the following loss: _L_ _I_ ( _θ_ _S_ ) = _−_ [1] � _x∈X_ � _tT_ =0 _−_ 1 [log] _[ π]_ _[θ]_ _S_ [(] _[w]_ _[t]_ [(] _[x, θ]_ _[T]_ [ )] _[|][x, z]_ _[θ]_ _S_ _[,t]_ [)][,]



_|X|_ �



_x∈X_ [log (] _[π]_ _[φ]_ [(] _[x][|][m,][ C]_ [))][.]



the teacher _θ_ _T_ with the following loss: _L_ _I_ ( _θ_ _S_ ) = _−_ _|X|_ [1] � _x∈X_ � _tT_ =0 _−_ 1 [log] _[ π]_ _[θ]_ _S_ [(] _[w]_ _[t]_ [(] _[x, θ]_ _[T]_ [ )] _[|][x, z]_ _[θ]_ _S_ _[,t]_ [)][,]

where _L_ _I_ ( _θ_ _S_ ) is a cross-entropy loss to encourage a student to output the same words as the teacher.


**Listener’s voting at inference time.** At inference time, we can use all listeners ( _φ_ _i_ ) _[N]_ _i_ =0 _[−]_ [1] [of the pop-]
ulation as an ensemble of networks. Together, they vote for a joint guess ˆ _x_ over a set of candidates
_C_ of images for a message _m_ coming from a speaker. One simple way consists in averaging the
score probabilities of the listeners and taking the best guess of this average. Formally, for each listener _φ_ _i_, each message _m_ and batch _X_, we have the score probability _π_ _φ_ _i_ ( _.|m, C_ ). Then the choice
_x_ ˆ( _m, C,_ ( _φ_ _i_ ) _[N]_ _i_ =0 _[−]_ [1] [)][ of the population of listeners for the message] _[ m]_ [ and the set] _[ C]_ [ is the best guess of]
the average distribution which is ˆ _x_ ( _m, C,_ ( _φ_ _i_ ) _[N]_ _i_ =0 _[−]_ [1] [) = arg max] _x_ ˜ _∈C_ _N_ 1 � _Ni_ =0 _−_ 1 _[π]_ _[φ]_ _i_ [(˜] _[x][|][m,][ C]_ [)][.]


More details about how we derive the different losses are found in Appendix A.3.

2.4 L ANGUAGE P ROPERTIES


**Generalization.** It measures the ability of agents to communicate about never-seen inputs. To compute generalization, we simply report test accuracy. In the simple case where inputs are constructed
by disentangled attributes, test inputs are new combinations of previously seen attributes at training.


**Robustness.** We report agents’ drop of accuracy when faced with noisy inputs relatively to clean
inputs at test time. To construct noisy stimuli, we add a Gaussian noise for each batch, with mean
0 and a standard deviation that is half of the standard deviation of the batch. Note that we sample
different noises for Speakers’ and Listeners’ inputs. That is, while Listeners are trained to find the
exact input of Speakers at train time, they are now required to uncover a different input at eval time.


**Topographic Similarity (TopSim).** _TopSim_ (Brighton & Kirby, 2006) is used as a proxy for compositionality (e.g., Li & Bowling, 2019; Lazaridou et al., 2018), and it is widely considered crucial
for generalization (Fodor & Lepore, 2002; Marcus, 2003). _TopSim_ tests whether close objects in the
input space are described by close messages by computing the Spearman correlation between the
pairwise distances in the input and message spaces. Following prior works, we use the edit-distance
and the cosine-distance in the message and input spaces respectively.


**Ease and transfer learning (ETL).** It captures how fast and well the emergent language is transmitted to new Listeners performing a distinct task. It is similar to the ease-of-teaching (Li & Bowling,
2019) to the exception that Listeners are trained to solve a different task from the initial one that
the emergent language was optimized for. This task transfer is inspired by the self-supervised linear
evaluation protocol (Chen et al., 2020). To measure _ETL_, we take min( _N,_ 5) fixed Speakers from
the population after convergence, and feed their deterministic language to 3 newly initialized Lis

4



_|X|_ �


Published as a conference paper at ICLR 2022


teners. We argmax from Speakers’ distribution to construct the deterministic languages. Finally, we
show how fast and well new Listeners perform in a given task when trained on fixed languages by
reporting the training curve for 10k steps. We look at the ease of learning when Listeners are trained
to solve harder discrimination, classification, and image reconstruction tasks. Hence, _ETL_ not only
captures the generality of the language to new Listeners but also its ability to transfer to new tasks.


3 E XPERIMENTS


3.1 T ASK SCALING UP : I NCREASING THE NUMBER OF C ANDIDATES


In the emergent communication literature, agents are typically required to discriminate between less
than 20 objects (Mu & Goodman, 2021) or reconstruct hand-crafted attributes (Rita et al., 2020).
Yet, this simple training setting was shown to sometimes lead to degenerate communication protocols (Bouchacourt & Baroni, 2018). As highlighted by (Dess`ı et al., 2021; Guo et al., 2021), the
Lewis game is a discrete variant of Contrastive Predictive Coding in the self-supervised learning
field (van den Oord et al., 2018). There, it was observed that the intermediate representation quality improved when increasing the number of candidates (He et al., 2019). We hence look at the
impact of the number of candidates _|C|_ on languages generalization and the technical challenges it
introduces. In this subsection, we consider the 1-pair setting trained on ImageNet while varying _|C|_ .


**Scaling up task difficulty requires to carefully tune optimization.** We first train agents without
KL regularization ( _β_ = 0) as it is commonly done in the field (see e.g., Strub et al., 2017; Cao
et al., 2018; Lu et al., 2020, among many others). As displayed in Fig. 1(a), the training becomes
unstable when increasing the number of candidates from 20 to 1024 candidates. The mean train
accuracy drops from 98.9% to 76.0%, and we observe a large variance across seeds. This high
variance demonstrates how crucial it is to run multiple seeds to state robust conclusions. A remedy
against such instability in RL consists in adding a KL regularisation _L_ KL loss between the online
policy and a target policy as described in Sec. 2.3. Such a solution has yet not been explored in the
emergent communication field. We add a KL regularization with a coefficient _β_ = 0 _._ 5 and display
the results in Fig. 1(b). We note that, with this better regularization, 20 and 1024 candidates converge
to 99.8% and 98.3% mean accuracy respectively with small variance during training. Adding _L_ KL
thus stabilizes the training and leads to better performances. We illustrate further the effect of this
regularization across multiple sweeps in Appendix B.3.












|1.0<br>0.8<br>0.6 Accuracy<br>0.4<br>0.2<br>0.0<br>50K 100K 1<br>St|Col2|Col3|Col4|Col5|Col6|
|---|---|---|---|---|---|
|~~50K~~<br>~~100K~~<br>~~1~~<br>St<br>0.0<br>0.2<br>0.4<br>0.6<br>0.8<br>1.0<br>Accuracy||||||
|~~50K~~<br>~~100K~~<br>~~1~~<br>St<br>0.0<br>0.2<br>0.4<br>0.6<br>0.8<br>1.0<br>Accuracy||||||
|~~50K~~<br>~~100K~~<br>~~1~~<br>St<br>0.0<br>0.2<br>0.4<br>0.6<br>0.8<br>1.0<br>Accuracy||||||
|~~50K~~<br>~~100K~~<br>~~1~~<br>St<br>0.0<br>0.2<br>0.4<br>0.6<br>0.8<br>1.0<br>Accuracy||||||
|~~50K~~<br>~~100K~~<br>~~1~~<br>St<br>0.0<br>0.2<br>0.4<br>0.6<br>0.8<br>1.0<br>Accuracy|||||20<br>1024|
|~~50K~~<br>~~100K~~<br>~~1~~<br>St<br>0.0<br>0.2<br>0.4<br>0.6<br>0.8<br>1.0<br>Accuracy||||||



(a) KL coefficient _β_ = 0 _._ 0 (b) KL coefficient _β_ = 0 _._ 5


Figure 1: Training curves per task complexity (20 vs. 1024 candidates) w/ and w/o KL regularization
on ImageNet. Thin lines are the accuracy of 10 seeds while thick lines represent the mean.


**Scaling up task difficulty is necessary to differentiate representations and enhance protocol’s**
**generalization.** In Fig. 2(a), we train 1-pair of agents on different number of candidates ranging
from 64 to 1024 and evaluate them on 16 candidates. [3] Note that, in the literature, the number of distractors rarely exceeds a dozen both at train and eval times (Mu & Goodman, 2021; Li & Bowling,
2019). In such settings, our experiments do not provide any interesting conclusions: all methods
are above 99 _._ 7% test accuracy and within standard deviation. However, when evaluating the same
communication protocols now on harder tasks with 1024 candidates, as shown in Fig. 2(b), we note
that these protocols are actually different. In particular, agents achieve an accuracy of 87 _._ 36%,
93 _._ 25%, 96 _._ 09% when trained on 64, 256, and 1024 candidates respectively, differentiating the various representation’s generalization capacity. While expected in light of the recent self-supervised
results (Chen et al., 2020) - harder training tasks lead to better representation and harder evaluation
tasks better discriminate algorithms - these results clearly illustrate how current emergent language


3 We kept the training batch size to 1024, and only varied the number of candidates in the InfoNCE loss.


5


Published as a conference paper at ICLR 2022


experiments may be ill-scaled to have robust conclusions. We report further experiments in Appendix B.5. In the following, we use 1024 candidates at train and eval to fully leverage our findings.










|Col1|Col2|Col3|Col4|Col5|Col6|Col7|Col8|
|---|---|---|---|---|---|---|---|
|||||||||
|||||||||
|||||~~N~~|~~m candi~~|~~ates (tr~~<br>16<br>64<br>|~~ain)~~|
|||||||~~256~~<br>1024||


|Col1|Col2|Col3|Col4|Col5|Col6|Col7|
|---|---|---|---|---|---|---|
||||||||
||||||||
||||~~N~~|~~m candi~~|~~ates (tr~~<br>16<br>~~64~~<br>|~~ain)~~|
||||||256<br>1024||



(a) Num candidates (eval): 16 (b) Num candidates at (eval): 1024

Figure 2: Test accuracy for different _|C|_ at train (lines) and eval (subplot) times on ImageNet. (a)
Easy eval task: no differentiation between methods. (b) Hard eval task: more candidates at training
induces higher test accuracy. Shaded region represents the standard deviation across 10 seeds.


3.2 D ATASET SCALING UP : R ETHINKING E VALUATION


In most emergent communication works, deep agents are situated in a simple disentangled environment where objects are one-hot vectors (Kottur et al., 2017; Li & Bowling, 2019). As a result, the
state space rarely goes beyond a few thousands of discrete samples. Besides, such representations
are unambiguous as they are inherently compositional. We argue that such environments may be
too simplistic to reach complex or diverse communication behaviors. In contrast, the major success
stories in machine learning collectively prove the importance of training neural networks on a rich
and large amount of data to emulate complex distributions (Brown et al., 2020; Krizhevsky et al.,
2012; Sutton, 2019). Furthermore, if the goal is to reproduce human interaction, it is fundamental to incorporate complex stimuli to develop advanced concepts in language evolution (Miller &
Johnson-Laird, 1976; Barsalou, 2008). In this subsection, we scale up the input space by using large
natural image datasets, namely ImageNet and CelebA. In particular, we investigate further emergent
language properties in the same setting of 1-pair of agents while varying _|C|_ at train time.


_TopSim_ **ImageNet** **CelebA**
Training Image Image Attributes


_|C|_ = 16 15 _._ 50 _±_ 0 _._ 61 **31** _**.**_ **92** _**±**_ **1** _**.**_ **32** **14** _**.**_ **22** _**±**_ **1** _**.**_ **36**
_|C|_ = 64 **19** _**.**_ **01** _**±**_ **0** _**.**_ **35** 28 _._ 7 _±_ 0 _._ 56 12 _._ 23 _±_ 0 _._ 76
_|C|_ = 256 17 _._ 06 _±_ 1 _._ 09 30 _._ 69 _±_ 1 _._ 04 12 _._ 29 _±_ 1 _._ 27
_|C|_ = 1024 16 _._ 52 _±_ 1 _._ 16 30 _._ 21 _±_ 1 _._ 22 13 _._ 49 _±_ 0 _._ 89


Figure 3: (left) _TopSim_ (x100) with different representation of the input space (Image and Attributes)
for different training difficulties, _|C|_ . We do not observe a correlation between _TopSim_ and _|C|_, and
thus generalization. _±_ denotes 1 standard error of the mean. (right) Example of predicted images by
new Listener trained on reconstruction task given a message of 1-pair for _|C|_ =1024. Reconstructions
are expected to be blurry, as we are regressing the mean of all faces associated to one message.


_**TopSim**_ **may fall short with natural images.** We compute _TopSim_ using the pretrained image logits on ImageNet and CelebA as input representation while varying the task complexity at train, _|C|_ .
Results are provided in Fig. 3(left). We do not observe a consistent pattern between _TopSim_ and _|C|_ .
Furthermore, we note a non-significant (p-value _>_ 0.19) Spearman correlation of _−_ 0 _._ 09 and 0 _._ 08 between _TopSim_ and generalization for ImageNet and CelebA respectively. Although pretrained logits
are excellent linear features (Grill et al., 2020), they may not be compositional. We thus reiterate
the evaluation by using the attributes from CelebA as input representation to compute _TopSim_ . In

=
that case too we do not note any significant correlation (p-value 0.13). Similar findings have been
observed in (Andreas, 2019; Chaabouni et al., 2020). This could be due to different reasons. First,
agents could be communicating in a compositional way, to support good generalization, by encoding
unexpected compositional features that are not labeled, like forehead shape or smile angle. That is,
human-labeled features may differ from the agents’ ones. Second, _TopSim_ relies on strong assumptions, such as the chosen distance, and the use of a linear correlation. Such hypotheses may not
hold when moving from artificial to realistic data. Finally, due to the large channel capacity, agents
could be using synonyms to generalize with low _TopSim_ values. In sum, our results demonstrate that


6


Published as a conference paper at ICLR 2022


Table 1: Evaluation of Speakers on multiple settings on CelebA in %. _±_ denotes one standard error
of the mean. We report final accuracy for all _ETL_ tasks but Recons. where we report the final loss.


_Metrics_ **Generalization** **Ease and Transfer Learning**


Training Accuracy _↑_ Discr. _↑_ Identity _↑_ Attributes _↑_ Recons. _↓_


_|C|_ = 16 74 _._ 50 _±_ 0 _._ 96 56 _._ 31 _±_ 1 _._ 07 15 _._ 52 _±_ 0 _._ 90 86 _._ 99 _±_ 0 _._ 10 2448 _±_ 16
_|C|_ = 64 80 _._ 19 _±_ 0 _._ 63 66 _._ 53 _±_ 1 _._ 09 23 _._ 12 _±_ 1 _._ 06 87 _._ 91 _±_ 0 _._ 11 2419 _±_ 12
_|C|_ = 256 85 _._ 03 _±_ 0 _._ 72 76 _._ 61 _±_ 1 _._ 14 33 _._ 72 _±_ 1 _._ 52 88 _._ 81 _±_ 0 _._ 16 2355 _±_ 13
_|C|_ = 1024 **89** _**.**_ **00** _**±**_ **0** _**.**_ **48** **83** _**.**_ **57** _**±**_ **0** _**.**_ **78** **44** _**.**_ **00** _**±**_ **1** _**.**_ **26** **90** _**.**_ **08** _**±**_ **0** _**.**_ **13** **2351** _**±**_ **14**


_TopSim_ is not a good predictor of communication protocol generalization for large-scale settings.
Instead, we investigate the information content via _ETL_ .


_**ETL**_ **is a robust metric to evaluate languages with natural images.** _ETL_, contrary to _TopSim_,
evaluates how useful the emergent language is for a target task beyond overfitting. As such it is
an important metric, since the goal of emergent communication is to endow agents with communication skills, rather than solving a specific game. Results are reported in Table 1 over distinct
tasks on CelebA. We observe that, even though _ETL_ only looks at the information content and not at
compositionality, it is a better predictor for language generalization performances than _TopSim_, with
a strong and significant correlation _>_ 0.90 (p-value _∼_ 0) for all considered tasks. As a visual sanity
check, we generate predicted images of the reconstruction _ETL_ task in Fig. 3(right). There, a new
Listener is trained to minimize an _l_ [2] loss with the target images given the precomputed messages.
We observe that gender, makeup, and hair color are fairly encoded, while others such as the smile
are not. More samples and training details are available in Appendix B.1. Interestingly, some _ETL_
tasks, like discrimination or reconstruction, do not depend on (human-)predefined input representations, and are all more robust to channel capacity and linearity assumptions, as opposed to _TopSim_,
which makes _ETL_ a more general evaluation metric.


**Zero-shot dataset transfer highlights emergent protocols’ differences and limits.** Scaling up
to natural image opens a large diversity of visual distributions that we can leverage by using zeroshot dataset transfer (Yogatama et al., 2019; Lambert et al., 2020). We hence measure how generic
and high-level the emergent protocols are. We take agents trained on ImageNet with _|C|_ =1024, and
evaluate them on CelebA in a zero-shot fashion. There, the mean accuracy dropped from 95 _._ 96 to
36 _._ 73, and the standard deviation raised from 0 _._ 49 to 12 _._ 86. Noticeably, the most different agents
obtain a zero-shot accuracy of 27 _._ 88 and 68 _._ 49, while their initial ImageNet accuracy only differed
by 0 _._ 23. Firstly, such a standard deviation gap suggests that different emergent protocols have
emerged between agent pairs. Secondly, the accuracy drop indicates that the emergent protocols
remain specific to the initial data-distribution, and no systematic language has yet emerged.


3.3 P OPULATION SCALING UP : E XPLOITING THE POPULATION DYNAMIC


The emergent communication literature often considers a single pair of agents (Lazaridou et al.,
2017; Foerster et al., 2016). However, there is evidence in the multi-agent literature that such a setting may lead to extreme co-adaptation and overfitting (Lanctot et al., 2017). One counter-measure
consists of sampling agents within a population (Jaderberg et al., 2018). From a linguistic perspective, different large-scale corpora analyses and human simulations support the importance of
the population in shaping our languages (Gary Lupyan, 2010; Bromham et al., 2015; Raviv et al.,
2019a;b). In this context, Raviv et al. (2019a) show that larger populations develop more systematic languages through human experimentation. Nonetheless, a few artificial simulations tentatively
consider population sizes up to 32 agents, but with mixed results about their advantage (Mordatch
& Abbeel, 2018; Tieleman et al., 2018; Graesser et al., 2019; Cogswell et al., 2019). In this part, we
consider up to 100 agents. Specifically, we explore the impact of the population size on languages
properties when we deal with more complex tasks ( _|C|_ =1024 at train and eval) and realistic inputs
(CelebA & ImageNet) while varying the population size _N ∈{_ 1 _,_ 10 _,_ 50 _}_ pairs.


**The best single-pair seed should be the baseline against population.** A few works in the emergent
communication framework looked at the benefit of the population by comparing 2 _N_ -agent’s performances to the 2-agent baseline (Cogswell et al., 2019). However, the former introduces _×N_ more
parameters, which could be responsible for its slight observed benefit. Here, we consider instead the
“best 1 pair” setting to investigate whether it is computationally advantageous to train a population
of size _N_ rather than training _N_ independent pairs. That is, for a given computational budget, we
ask whether it is beneficial to train agents within a population as opposed to _N_ pairs in parallel, as


7


Published as a conference paper at ICLR 2022


Table 2: Different language properties on CelebA and ImageNet datasets, in %. For each setting we
report the mean over 10 seeds. _±_ denotes 1 standard error of the mean.


**CelebA** **ImageNet**


Setting Generalization _↑_ Robustness _↓_ Generalization _↑_ Robustness _↓_


best 1 pair 90 _._ 73 35 _._ 82 **97** _._ **55** 27 _._ 83
1 pair 89 _._ 00 _±_ 0 _._ 48 37 _._ 90 96 _._ 09 _±_ 0 _._ 21 18 _._ 90
10 pairs 91 _._ 06 _±_ 0 _._ 23 37 _._ 56 95 _._ 78 _±_ 0 _._ 29 14 _._ 58
50 pairs 90 _._ 69 _±_ 0 _._ 61 38 _._ 87 95 _._ 29 _±_ 0 _._ 34 15 _._ 21


10 pairs + imitation 91 _._ 84 _±_ 0 _._ 31 35 _._ 47 96 _._ 79 _±_ 0 _._ 12 13 _._ 46
10 pairs + imitation + vote 92 _._ 19 _±_ 0 _._ 30 35 _._ 21 96 _._ 95 _±_ 0 _._ 11 13 _._ 27
50 pairs + imitation 92 _._ 82 _±_ 0 _._ 51 32 _._ 69 96 _._ 70 _±_ 0 _._ 16 12 _._ 92
50 pairs + imitation + vote **93** _._ **13** _±_ **0** _._ **50** **32** _._ **40** 96 _._ 85 _±_ 0 _._ 15 **12** _._ **75**


also done in (Tieleman et al., 2018). “Best 1 pair” is constructed by selecting the best seed among
the 10 seeds of “1 pair”, based on validation accuracy, offering a fairer baseline _specifically_ for the
“10 pairs” setting. Results are shown in Table 2 and Fig. 4. We observe different behavior of “best 1
pair” across datasets. Particularly, if it always achieves better generalization and _ETL_ discrimination
compared to “1 pair”, it shows, for ImageNet only, the worst _Robustness_ and _ETL_ classification. We
hypothesize that in that specific case, the emergent protocol overspecializes to the task. Still, “best
1 pair” outperforms the standard baseline “1 pair” 6/8 times, which makes it a stronger baseline. In
the following, we thus always compare the population setting with “best 1 pair” for a fair evaluation.


**Population size does not lead to a systematic advantage.** We look at the language generalization
and robustness performances when increasing the population size. Results in Table 2 do not show
a clear trend between population size and these metrics. For example, for both datasets, “50 pairs”
achieves lower _Generalization_ and _Robustness_ than “10 pairs”. Furthermore, “best 1 seed” always
achieves better _Generalization_ compared to the largest population setting “50 pairs”. In Fig. 4, we
look at _ETL_ for a further investigation of the languages’ properties. CelebA results exhibit a benefit
of the population. However, this benefit does not always correlate with population size where “10
pairs” outperforms “50 pairs” on the discrimination task. This non-systematic benefit is also found
when experimenting with ImageNet. Again, our results suggest no benefit of the population size
in the current setting. We thus explore new approaches to leverage the population dynamics and
improve the representation of the emergent protocol in the following.


**A better use of the population is needed to see larger benefit.** As population size does not improve
the emergent language in itself, we took advantage of the richness of the population by considering imitation at training and vote at inference. In Table 2, we observe that both imitation and vote
introduce a systematic improvement compared to the standard training in a population and lead to
better performances compared to “1 pair” in all metrics. Moreover, when considering the stronger
baseline “best 1 pair”, the latter only outperforms the imitation and vote settings 1/4 times ( _Gen-_
_eralization_ for ImageNet). However, as noted previously, this case is an over-specialized protocol.
Furthermore, if both imitation and vote introduce a systematic improvement of the protocol, their
benefit is even more noticeable for distribution-shifted settings. For example, the imitation for 50
pairs adds a relative improvement of 12.8% in _Robusteness_ compared to 2.3% for _Generalization_ on
CelebA. The same observation holds for the vote but with a lower degree. Note that if vote induces
only a slight benefit, it does not incur any training cost. When considering _ETL_ on discrimination
in Figs. 4(a)&4(c), we observe that imitation leads to a systematic improvement. In CelebA, if the
standard population was already beneficial, adding the imitation strengthens the results. In ImageNet, “10/50 pairs + imitation” perform similarly at the end of training than the overspecialized
“best 1 pair” while having more stable optimization and it is considerably better than the standard
training w/ and w/o population. Yet, the results are more nuanced when considering _ETL_ over classification in Fig. 4(b)&4(d). Specifically, while CelebA experiments suggest an advantage when
training a population of agents w/o imitation as opposed w/ imitation or “1 pair”, this pattern is absent with ImageNet. There all settings with population are on par. In sum, both considered dynamics
outperform in most cases the strong “best 1 pair” baseline (7/8 times), highlighting their viability.
4 D ISCUSSION AND C ONCLUSION


The emergent communication framework has been extensively studied for decades before the successes of deep RL. In this context, many works have revisited this framework through deep RL
settings (e.g., Kirby 2002 _vs._ Ren et al. 2019, Myers-Scotton et al. 2002 _vs._ Graesser et al. 2019, or


8


Published as a conference paper at ICLR 2022


(a) CelebA _Discrimination_


(c) ImageNet _Discrimination_



(b) CelebA _Classification of Identities_


(d) ImageNet _Classification_





Figure 4: _ETL_ per datasets and tasks. The results are averaged across min( _N,_ 5) Speakers, 3 newborn Listeners’ over 10 different seeds. The shaded region represents the standard deviation.


Batali 1998 _vs._ Choi et al. 2018). However, the experimental settings have barely evolved for twenty
years. For instance, Kirby (2002) and Ren et al. (2019) both used a binary input vector of size eight,
and only a few papers try to go beyond such artificial input spaces or simple tasks (Lazaridou et al.,
2017; Havrylov & Titov, 2017; Dess`ı et al., 2021). While computational constraints may have been a
limiting factor, we show that our setting is possible with widely available hardware in Appendix B.2.
For example, Table 1 requires approximately 400 hours of compute, i.e. 16 GPUs for a single day.
Compared to other communities, this is equivalent to medium-scale studies in vision or NLP. We
argue that it is finally time for the emergent language community to scale up!


In this spirit, we start clearing the way by identifying some scaling up challenges: optimization
instabilities, ill-adapted metrics, or lack of population synergy. We show how to face these new
difficulties by proposing: alternative optimization (KL regularization), new evaluation protocols
(ETL, zero-shot dataset transfer, best seed baseline), and new dynamics to leverage populations
(imitation, voting). There are different theories about the necessity of complex tasks to model human
communication (e.g., (Barrett & Skyrms, 2017) vs. (Bickerton, 2015; Dupoux, 2018)). Hence, we
endorse here Bickerton’s view and adopt performance-inspired solutions to scale up such as KLregularization and imitation. An interesting future debate is whether our findings could influence
the status quo of similar research in human communication.


Although we only examine three scaling up dimensions, many other directions can be pursued in the
future: using larger or different architectures to improve agent abilities (Desai & Johnson, 2021),
experimenting with multimodal data like video or sounds for more realistic stimuli (Arandjelovic &
Zisserman, 2017), or building symmetric communication channels to have emergent dialogues (Gao
et al., 2019). Another frontier would be to incorporate interaction within environments to ground
language into actions (Bisk et al., 2020). As such embodiment is crucial for human language understanding (Harnad, 1990; Barsalou, 2008), we may start exploring small grid world (Kaji´c et al.,
2020) before scaling up to 3D-environments (Abramson et al., 2020).


9


Published as a conference paper at ICLR 2022


R EPRODUCIBILITY S TATEMENT


In this paper, we ensure the reproduciblity of the different findings through several (and voluntary
redundant) ways, namely:


_•_ The task is detailed in Section 2.1 and we provide a visual sketch in Appendix A.1.


_•_ We use open-source datasets (ImageNet and CelebA). Also, dataset processing is explained,
with pseudo-code to reproduce our splits, in Appendix A.6.


_•_ The speaker and listener architectures are first explained in Section 2.2, we then detail
model size values, and provide visual sketches in Appendix A.2. The specifics for image
reconstruction for _ETL_ are in Appendix B.1 with a pseudo-code for the reconstruction head.


_•_ The optimization is first described in Section 2.3. The equations are then fully detailed in
Appendix A.3.


_•_ All training and evaluation hyperparameters are listed in Appendix A.4.


_•_ Through the paper, we voluntary provide training curves, test curves, and final scores to
have a global view of the training trends.


_•_ We listed computation time and memory footprint for multiple experiments and multiple
hardware in Appendix B.2


_•_ The source code should be released upon paper acceptance.


A CKNOWLEDGEMENT


We would like to thank Will Dabney, Remi Munos, Karl Tuyls, Nathalie Beauguerlange as well
as the rest of the DeepMind Paris team for their continuous support. We would also like to thank
Marco Baroni, Eugene Kharitonov, Olivier Pietquin and Mathieu Rita for their discussions and
helpful feedback at the different stages of the project. Finally, we thank Alison Reid and Saran
Tunyasuvunakool for their help in open-sourcing the codebase.


R EFERENCES


Josh Abramson, Arun Ahuja, Iain Barr, Arthur Brussee, Federico Carnevale, Mary Cassin, Rachita Chhaparia,
Stephen Clark, Bogdan Damoc, Andrew Dudzik, et al. Imitating interactive intelligence. _arXiv preprint_
_arXiv:2012.05672_, 2020.


Jacob Andreas. Measuring compositionality in representation learning. In _Proc. of International Conference_
_on Learning Representations (ICLR)_, 2019.


Relja Arandjelovic and Andrew Zisserman. Look, listen and learn. In _Proc. of the IEEE International Confer-_
_ence on Computer Vision (ICCV)_, 2017.


Igor Babuschkin, Kate Baumli, Alison Bell, Surya Bhupatiraju, Jake Bruce, Peter Buchlovsky, David Budden,
Trevor Cai, Aidan Clark, Ivo Danihelka, Claudio Fantacci, Jonathan Godwin, Chris Jones, Tom Hennigan,
Matteo Hessel, Steven Kapturowski, Thomas Keck, Iurii Kemaev, Michael King, Lena Martens, Vladimir
Mikulik, Tamara Norman, John Quan, George Papamakarios, Roman Ring, Francisco Ruiz, Alvaro Sanchez,
Rosalia Schneider, Eren Sezener, Stephen Spencer, Srivatsan Srinivasan, Wojciech Stokowiec, and Fabio
[Viola. The DeepMind JAX Ecosystem, 2020. URL http://github.com/deepmind.](http://github.com/deepmind)


Marco Baroni, Armand Joulin, Allan Jabri, Germ`an Kruszewski, Angeliki Lazaridou, Klemen Simonic, and
Tomas Mikolov. CommAI: Evaluating the first steps towards a useful general AI. In _Proc. of International_
_Conference on Learning Representations (ICLR) - Workshop Track_, 2017.


Jeffrey A Barrett and Brian Skyrms. Self-assembling games. _The British Journal for the Philosophy of Science_,
68(2):329–353, 2017.


Lawrence Barsalou. Grounded cognition. _Annual Review of Psychology_, 59:617–645, 2008.


John Batali. Computational simulations of the emergence of grammar. In James Hurford, Michael StuddertKennedy, and Chris Knight (eds.), _Approaches to the Evolution of Language: Social and Cognitive Bases_,
pp. 405–426. Cambridge University Press, Cambridge, UK, 1998.


10


Published as a conference paper at ICLR 2022


Derek Bickerton. _Roots of language_ . Language Science Press, 2015.


Yonatan Bisk, Ari Holtzman, Jesse Thomason, Jacob Andreas, Yoshua Bengio, Joyce Chai, Mirella Lapata,
Angeliki Lazaridou, Jonathan May, Aleksandr Nisnevich, et al. Experience grounds language. In _Proc. of_
_Empirical Methods in Natural Language Processing (EMNLP)_, 2020.


Diane Bouchacourt and Marco Baroni. How agents see things: On visual representations in an emergent
language game. In _Proc. of Empirical Methods in Natural Language Processing (EMNLP)_, 2018.


Henry Brighton and Simon Kirby. Understanding linguistic evolution by visualizing the emergence of topographic mappings. _Artificial life_, 12(2):229–242, 2006.


Lindell Bromham, Xia Hua, Thomas G Fitzpatrick, and Simon J Greenhill. Rate of language evolution is
affected by population size. _Proc. of the National Academy of Sciences (PNAS)_, 112(7):2097–2102, 2015.


Tom B Brown, Benjamin Mann, Nick Ryder, Melanie Subbiah, Jared Kaplan, Prafulla Dhariwal, Arvind Neelakantan, Pranav Shyam, Girish Sastry, Amanda Askell, et al. Language models are few-shot learners. _arXiv_
_preprint arXiv:2005.14165_, 2020.


Kris Cao, Angeliki Lazaridou, Marc Lanctot, Joel Leibo, Karl Tuyls, and Stephen Clark. Emergent communication through negotiation. In _Proc. of International Conference on Learning Representations (ICLR)_,
2018.


Rahma Chaabouni, Eugene Kharitonov, Emmanuel Dupoux, and Marco Baroni. Anti-efficient encoding in
emergent communication. In _Proc. of Advances in Neural Information Processing Systems (NeurIPS)_, 2019.


Rahma Chaabouni, Eugene Kharitonov, Diane Bouchacourt, Emmanuel Dupoux, and Marco Baroni. Compositionality and generalization in emergent languages. In _Proc. of the Association for Computational Linguistics_
_(ACL)_, 2020.


Rahma Chaabouni, Eugene Kharitonov, Emmanuel Dupoux, and Marco Baroni. Communicating artificial
neural networks develop efficient color-naming systems. _Proc. of the National Academy of Sciences (PNAS)_,
118(12), 2021.


Ting Chen, Simon Kornblith, Mohammad Norouzi, and Geoffrey E. Hinton. A simple framework for contrastive learning of visual representations. In _Proc. of International Conference on Machine Learning_
_(ICML)_, 2020.


Edward Choi, Angeliki Lazaridou, and Nando de Freitas. Compositional obverter communication learning
from raw visual input. In _Proc. of International Conference on Learning Representations (ICLR)_, 2018.


Michael Cogswell, Jiasen Lu, Stefan Lee, Devi Parikh, and Dhruv Batra. Emergence of compositional language
with deep generational transmission. _arXiv preprint arXiv:1904.09067_, 2019.


J. Deng, W. Dong, R. Socher, L.-J. Li, K. Li, and L. Fei-Fei. ImageNet: A Large-Scale Hierarchical Image
Database. In _Proc. of Conference on Computer Vision and Pattern Recognition (CVPR)_, 2009.


Karan Desai and Justin Johnson. Virtex: Learning visual representations from textual annotations. In _Proc. of_
_Conference on Computer Vision and Pattern Recognition (CVPR)_, 2021.


Roberto Dess`ı, Eugene Kharitonov, and Marco Baroni. Interpretable agent communication from scratch (with
a generic visual processor emerging on the side). In _Proc. of Advances in Neural Information Processing_
_Systems (NeurIPS)_, 2021.


Emmanuel Dupoux. Cognitive science in the era of artificial intelligence: A roadmap for reverse-engineering
the infant language-learner. _Cognition_, 173:43–59, 2018.


Lasse Espeholt, Hubert Soyer, Remi Munos, Karen Simonyan, Vlad Mnih, Tom Ward, Yotam Doron, Vlad
Firoiu, Tim Harley, Iain Dunning, et al. Impala: Scalable distributed deep-rl with importance weighted
actor-learner architectures. In _Proc. of International Conference on Machine Learning (ICML)_, 2018.


Jerry Fodor and Ernest Lepore. _The Compositionality Papers_ . Oxford University Press, Oxford, UK, 2002.


Jakob Foerster, Ioannis Alexandros Assael, Nando de Freitas, and Shimon Whiteson. Learning to communicate with deep multi-agent reinforcement learning. In _Proc. of Advances in Neural Information Processing_
_Systems (NeurIPS)_, 2016.


Jianfeng Gao, Michel Galley, and Lihong Li. _Neural approaches to conversational AI: Question answering,_
_task-oriented dialogues and social chatbots_ . Now Foundations and Trends, 2019.


11


Published as a conference paper at ICLR 2022


Rick Dale Gary Lupyan. Language structure is partly determined by social structure. _PLoS ONE 5_, 1, 2010.


Matthieu Geist, Bruno Scherrer, and Olivier Pietquin. A theory of regularized markov decision processes. In
_Proc. of International Conference on Machine Learning (ICML)_, 2019.


Laura Graesser, Kyunghyun Cho, and Douwe Kiela. Emergent linguistic phenomena in multi-agent communication games. In _Proc. of Empirical Methods in Natural Language Processing (EMNLP)_, 2019.


Jean-Bastien Grill, Florian Strub, Florent Altch´e, Corentin Tallec, Pierre H Richemond, Elena Buchatskaya,
Carl Doersch, Bernardo Avila Pires, Zhaohan Daniel Guo, Mohammad Gheshlaghi Azar, et al. Bootstrap
your own latent: A new approach to self-supervised learning. In _Proc. of Advances in Neural Information_
_Processing Systems (NeurIPS)_, 2020.


Shangmin Guo, Yi Ren, Serhii Havrylov, Stella Frank, Ivan Titov, and Kenny Smith. The emergence of
compositional languages for numeric concepts through iterated learning in neural agents. _arXiv preprint_
_arXiv:1910.05291_, 2019.


Shangmin Guo, Yi Ren, Kory Mathewson, Simon Kirby, Stefano V Albrecht, and Kenny Smith. Expressivity
of emergent language is a trade-off between contextual complexity and unpredictability. _arXiv preprint_
_arXiv:2106.03982_, 2021.


Stevan Harnad. The symbol grounding problem. _Physica D: Nonlinear Phenomena_, 42(1-3):335–346, 1990.


Serhii Havrylov and Ivan Titov. Emergence of language with multi-agent games: Learning to communicate
with sequences of symbols. In _Proc. of Advances in Neural Information Processing Systems (NeurIPS)_,
2017.


Patrick J. Hayes. The second naive physics manifesto. In R. Shaw & J. Bransford (ed.), _Formal Theories of the_
_Commonsense World_, 1985.


Kaiming He, Haoqi Fan, Yuxin Wu, Saining Xie, and Ross B. Girshick. Momentum contrast for unsupervised
visual representation learning. In _Proc. of Conference on Computer Vision and Pattern Recognition (CVPR)_,
2019.


Todd Hester, Matej Vecerik, Olivier Pietquin, Marc Lanctot, Tom Schaul, Bilal Piot, Dan Horgan, John Quan,
Andrew Sendonaris, Ian Osband, et al. Deep q-learning from demonstrations. In _Proc. of Conference on_
_Artificial Intelligence (AAAI)_, 2018.


Sepp Hochreiter and J¨urgen Schmidhuber. Long short-term memory. _Neural Computation_, 9(8):1735–1780,
1997.


Max Jaderberg, WM Czarnecki, I Dunning, L Marris, G Lever, AG Castaneda, et al. Human-level performance in first-person multiplayer games with population-based deep reinforcement learning. _arXiv preprint_
_arXiv:1807.01281_, 2018.


Ivana Kaji´c, Eser Ayg¨un, and Doina Precup. Learning to cooperate: Emergent communication in multi-agent
navigation. _arXiv preprint arXiv:2004.01097_, 2020.


Diederik P. Kingma and Jimmy Ba. Adam: A method for stochastic optimization. In _Proc. of International_
_Conference on Learning Representations (ICLR)_, 2015.


Simon Kirby. Natural language from artificial life. _Artificial life_, 8(2):185–215, 2002.


Simon Kirby, Tom Griffiths, and Kenny Smith. Iterated learning and the evolution of language. _Current Opinion_
_in Neurobiology_, 28:108–114, 2014.


Satwik Kottur, Jos´e Moura, Stefan Lee, and Dhruv Batra. Natural language does not emerge ‘naturally’ in
multi-agent dialog. In _Proc. of Empirical Methods in Natural Language Processing (EMNLP)_, 2017.


Alex Krizhevsky, Ilya Sutskever, and Geoffrey E Hinton. Imagenet classification with deep convolutional neural
networks. In _Proc. of Advances in Neural Information Processing Systems (NeurIPS)_, 2012.


John Lambert, Zhuang Liu, Ozan Sener, James Hays, and Vladlen Koltun. Mseg: A composite dataset for
multi-domain semantic segmentation. In _Proc. of Conference on Computer Vision and Pattern Recognition_
_(CVPR)_, 2020.


Marc Lanctot, Vinicius Zambaldi, Audrunas Gruslys, Angeliki Lazaridou, Karl Tuyls, Julien P´erolat, David
Silver, and Thore Graepel. A unified game-theoretic approach to multiagent reinforcement learning. In
_Proc. of Advances in Neural Information Processing Systems (NeurIPS)_, 2017.


12


Published as a conference paper at ICLR 2022


Angeliki Lazaridou, Alexander Peysakhovich, and Marco Baroni. Multi-agent cooperation and the emergence
of (natural) language. In _Proc. of International Conference on Learning Representations (ICLR)_, 2017.


Angeliki Lazaridou, Karl Moritz Hermann, Karl Tuyls, and Stephen Clark. Emergence of linguistic communication from referential games with symbolic and pixel input. In _Proc. of International Conference on_
_Learning Representations (ICLR)_, 2018.


Angeliki Lazaridou, Anna Potapenko, and Olivier Tieleman. Multi-agent communication meets natural language: Synergies between functional and structural language learning. In _Proc. of the Association for Com-_
_putational Linguistics (ACL)_, 2020.


David Lewis. _Convention_ . Harvard University Press, Cambridge, MA, 1969.


Fushan Li and Michael Bowling. Ease-of-teaching and language structure from emergent communication. In
_Proc. of Advances in Neural Information Processing Systems (NeurIPS)_, 2019.


Ziwei Liu, Ping Luo, Xiaogang Wang, and Xiaoou Tang. Deep learning face attributes in the wild. In _Proc. of_
_the IEEE International Conference on Computer Vision (ICCV)_, 2015.


Yuchen Lu, Soumye Singhal, Florian Strub, Aaron Courville, and Olivier Pietquin. Countering language drift
with seeded iterated learning. In _Proc. of International Conference on Machine Learning (ICML)_, 2020.


Gary Marcus. _The Algebraic Mind_ . MIT Press, Cambridge, MA, 2003.


George A Miller and Philip N Johnson-Laird. _Language and perception._ Havard University Press, 1976.


Volodymyr Mnih, Adria Puigdomenech Badia, Mehdi Mirza, Alex Graves, Timothy Lillicrap, Tim Harley,
David Silver, and Koray Kavukcuoglu. Asynchronous methods for deep reinforcement learning. In _Proc. of_
_International Conference on Machine Learning (ICML)_, 2016.


Igor Mordatch and Pieter Abbeel. Emergence of grounded compositional language in multi-agent populations.
In _Proc. of Conference on Artificial Intelligence (AAAI)_, 2018.


Jesse Mu and Noah Goodman. Emergent communication of generalizations. In _Proc. of Advances in Neural_
_Information Processing Systems (NeurIPS)_, 2021.


Carol Myers-Scotton et al. _Contact linguistics: Bilingual encounters and grammatical outcomes_ . Oxford
University Press on Demand, 2002.


Robi Polikar. Ensemble learning. In _Ensemble machine learning_, pp. 1–34. Springer, 2012.


Alec Radford, Luke Metz, and Soumith Chintala. Unsupervised representation learning with deep convolutional
generative adversarial networks. In _Proc. of International Conference on Learning Representations (ICLR)_,
2016.


Limor Raviv, Antje Meyer, and Shiri Lev-Ari. Larger communities create more systematic languages. _Pro-_
_ceedings of the Royal Society B_, 286(1907):20191262, 2019a.


Limor Raviv, Antje Meyer, and Shiri Lev-Ari. Compositional structure can emerge without generational transmission. _Cognition_, 182:151–164, 2019b.


Yi Ren, Shangmin Guo, Serhii Havrylov, Shay Cohen, and Simon Kirby. Enhance the compositionality of emergent language by iterated learning. In _Proc. of the NeurIPS Emergent Communication Workshop (EmeCom)_,
2019.


Cinjon Resnick, Abhinav Gupta, Jakob Foerster, Andrew Dai, and Kyunghyun Cho. Capacity, bandwidth, and
compositionality in emergent language learning. In _Proc. of Autonomous Agents and Multiagent Systems_
_(AAMAS)_, 2020.


Mathieu Rita, Rahma Chaabouni, and Emmanuel Dupoux. ”LazImpa”: Lazy and Impatient neural agents learn
to communicate efficiently. In _Proc. of the Association for Computational Linguistics (ACL)_, 2020.


Olga Russakovsky, Jia Deng, Hao Su, Jonathan Krause, Sanjeev Satheesh, Sean Ma, Zhiheng Huang, Andrej
Karpathy, Aditya Khosla, Michael Bernstein, Alexander C. Berg, and Li Fei-Fei. ImageNet Large Scale
Visual Recognition Challenge. _International Journal of Computer Vision_, 115(3):211–252, 2015. doi:
10.1007/s11263-015-0816-y.


John Schulman, Sergey Levine, Pieter Abbeel, Michael Jordan, and Philipp Moritz. Trust region policy optimization. In _Proc. of International Conference on Machine Learning (ICML)_, 2015.


13


Published as a conference paper at ICLR 2022


John Schulman, Filip Wolski, Prafulla Dhariwal, Alec Radford, and Oleg Klimov. Proximal policy optimization
algorithms. _arXiv preprint arXiv:1707.06347_, 2017.


Luc Steels. The synthetic modeling of language origins. _Evolution of communication_, 1(1):1–34, 1997.


Florian Strub, Harm de Vries, J´er´emie Mary, Bilal Piot, Aaron C Courville, and Olivier Pietquin. End-toend optimization of goal-driven and visually grounded dialogue systems. In _Proc. of International Joint_
_Conference on Artificial Intelligence (IJCAI)_, 2017.


Rich Sutton. _The Bitter Lesson_, 2019. [http://www.incompleteideas.net/IncIdeas/](http://www.incompleteideas.net/IncIdeas/BitterLesson.html)
[BitterLesson.html.](http://www.incompleteideas.net/IncIdeas/BitterLesson.html)


Richard S Sutton, David A McAllester, Satinder P Singh, and Yishay Mansour. Policy gradient methods for
reinforcement learning with function approximation. In _Proc. of Advances in Neural Information Processing_
_Systems (NIPS)_, 2000.


Olivier Tieleman, Angeliki Lazaridou, Shibl Mourad, Charles Blundell, and Doina Precup. Shaping representations through communication. _arXiv preprint arXiv:1912.06208_, 2018.


A¨aron van den Oord, Yazhe Li, and Oriol Vinyals. Representation learning with contrastive predictive coding.
_arXiv preprint arXiv:1807.03748_, 2018.


Mel Vecerik, Todd Hester, Jonathan Scholz, Fumin Wang, Olivier Pietquin, Bilal Piot, Nicolas Heess, Thomas
Roth¨orl, Thomas Lampe, and Martin Riedmiller. Leveraging demonstrations for deep reinforcement learning
on robotics problems with sparse rewards. _arXiv preprint arXiv:1707.08817_, 2017.


Nino Vieillard, Tadashi Kozuno, Bruno Scherrer, Olivier Pietquin, R´emi Munos, and Matthieu Geist. Leverage
the average: an analysis of kl regularization in reinforcement learning. In _Proc. of Advances in Neural_
_Information Processing Systems (NeurIPS)_, 2020a.


Nino Vieillard, Olivier Pietquin, and Matthieu Geist. Munchausen reinforcement learning. In _Proc. of Advances_
_in Neural Information Processing Systems (NeurIPS)_, 2020b.


Kyle Wagner, James A Reggia, Juan Uriagereka, and Gerald S Wilkinson. Progress in the simulation of emergent communication and language. _Adaptive Behavior_, 11(1):37–69, 2003.


Ronald J Williams and Jing Peng. Function optimization using connectionist reinforcement learning algorithms.
_Connection Science_, 3(3):241–268, 1991.


Dani Yogatama, Cyprien de Masson d’Autume, Jerome Connor, Tomas Kocisky, Mike Chrzanowski, Lingpeng
Kong, Angeliki Lazaridou, Wang Ling, Lei Yu, Chris Dyer, et al. Learning and evaluating general linguistic
intelligence. _arXiv preprint arXiv:1901.11373_, 2019.


14


Published as a conference paper at ICLR 2022


A A DDITIONAL S ETTING D ETAILS


A.1 D ISCRIMINATION G AME







Figure 5: Example of a discrimination game on Imagenet with a set _C_ of 4 candidates. In this
specific instance, Listener does not select an image ˆ _x_ that is identical to the target image _x_ received
by Speaker. Therefore the reward received by both player _R_ ( _x,_ ˆ _x_ ) = 1 _x_ =ˆ _x_ will be 0.


A.2 A RCHITECTURE DETAILS


**Speaker** The speaker’s network architecture is composed of several components to transform the
target image _x_ into a message _m_ = ( _w_ _t_ ) _[T]_ _t_ =0 _[ −]_ [1] [:]


_•_ The encoder _f_ is a fixed Resnet-50 architecture that has been previously trained on Imagenet with the BYOL algorithm. The resulting embedding _f_ ( _x_ ) is of size 2048.


_•_ The RNN _h_ _θ_ used is an LSTM of hidden size 256. Therefore the core state _z_ _t,θ_ is of size
512.


_•_ The core-state adapter _c_ _θ_ is a linear layer with input size 2048 and an output size of 512 that
allows to transform the embedding _f_ ( _x_ ) into an appropriate core state _z_ _−_ 1 _,θ_ = _c_ _θ_ ( _f_ ( _x_ )).
We split _z_ _−_ 1 _,θ_ into two equal parts to obtain the initial hidden state _z_ _h,−_ 1 _,θ_ and the initial
cell state _z_ _c,−_ 1 _,θ_ .


_•_ The word embedder _g_ _θ_ associates to each discrete symbols in _W ∪{_ sos _}_ an embedding
of size 10.


_•_ The value head _v_ _θ_ first selects the hidden part _z_ _h,t,θ_ of the core state _z_ _t,θ_ and then applies
a linear layer of output size 1.


_•_ The policy head _π_ _θ_ first selects the hidden part _z_ _h,t,θ_ of the core state _z_ _t,θ_ and then applies
a linear layer of output size _|W|_ to obtain logits _l_ _t,θ_ . Then a softmax layer transforms the
logits into the output distribution _π_ _θ_ ( _.|z_ _t,θ_ ).


**Listener** The listener’s network architecture is composed of several components to transform the
message _m_ and the input image ˜ _x_ into a score score( _m,_ ˜ _x, φ_ ):


_•_ The encoder _f_ is a fixed Resnet-50 architecture that has been previously trained on Imagenet with the BYOL algorithm. The resulting embedding _f_ ( _x_ ) is of size 2048.


_•_ The RNN _h_ _φ_ used is an LSTM of hidden size 512. Therefore the core state _z_ _t,φ_ is of size
1024 and is composed of an hidden state _z_ _h,t,φ_ of size 512 and a cell state _z_ _c,t,φ_ of size
512.


_•_ The word embedder _g_ _φ_ associates to each discrete symbols in _W_ an embedding of size 10.


_•_ The target projection _t_ _φ_ is a linear layer with output size 256.


_•_ The core-state projection _p_ _φ_ is a linear layer with output size 256.


15


Published as a conference paper at ICLR 2022


As explained in Sec.2.2, the score function is defined as score( _m,_ ˜ _x, φ_ ) = cos( _∥pp_ _m,φm,φ_ _∥_ 2 _[,]_ _∥tt_ _x_ ˜ _x_ ˜ _∥_ 2 [)][.]
The scores over all images are normalized via a softmax to get a probability _π_ _φ_ ( _.|m, C_ ) such that:


˜ exp(score( _m,_ ˜ _x,_ _φ_ ))
_∀x ∈C, π_ _φ_ (˜ _x|m, C_ ) = ~~�~~ ~~_x∈_~~ _C_ [exp(][score][(] _[m, ]_ ~~_[x]_~~ _[, φ]_ [))] _[.]_


Finally, the listener selects an image by taking the best guess according to _π_ _φ_, i.e. _x_ ˆ _∈_
arg max _x_ ˜ _∈C_ _π_ _φ_ (˜ _x|m, C_ ).


Figure 6: Graphical representation of a speaker’s architecture that shows how the words ( _w_ _t_ ) _t_ _[T]_ =0 _[ −]_ [1]
are computed from the inputs _x_ .


Figure 7: Graphical representation of a listener’s architecture that shows how the score
score( _m,_ ˜ _x, φ_ ) is computed given a message ( _w_ _t_ ) _t_ _[T]_ =0 _[ −]_ [1] [and an input image][ ˜] _[x]_ [.]


A.3 O PTIMISATION DETAILS


**Speaker training and loss** The goal of a speaker, parameterized by _θ_, is to optimize the message
_m_ sent to a listener, parameterized by _φ_, such that the mean reward of the game is the highest possible. This can be framed as a sequential decision making problem where the decision is the choice of
each word _w_ _t_ . Thus, each word is sampled from a parameterized stochastic policy _π_ _θ_ ( _.|x,_ ( _w_ _k_ ) _[t]_ _k_ _[−]_ =0 [1] [)]
that depends on the image _x_ and past words ( _w_ _k_ ) _[t]_ _k_ _[−]_ =0 [1] [, where for] _[ t]_ [ = 0][ we have][ (] _[w]_ _[k]_ [)] _k_ _[−]_ =0 [1] [=] _[ ∅]_ [. Then,]
the goal is to maximize the expected reward _J_ ( _θ, φ_ ) by finding the best policy _π_ _θ_ :


_J_ ( _θ, φ_ ) = E _x∼ρ_ [E _π_ _θ_ _,x_ [ _R_ ( _x,_ ˆ _x_ )]] _,_


16


Published as a conference paper at ICLR 2022


where the expectation E _x∼ρ_ is over the dataset of training images and the expectation E _π_ _θ_ _,x_ is over
all possible sequences ( _x,_ ( _w_ _t_ ) _[T]_ _t_ =0 _[ −]_ [1] [)][ that can be generated by] _[ π]_ _[θ]_ [ starting from] _[ x]_ [. For a given image]
_x_, we define the value _V_ _[π]_ _[θ]_ ( _x_ ) = E _π_ _θ_ _,x_ [ _R_ ( _x,_ ˆ _x_ )] as the expected reward for a given image, here we
left the dependence over the choice of the listener ˆ _x_ for ease of notations as the speaker cannot act
on it. For a parameterized policy _π_ _θ_, we can use the policy gradient theorem to obtain the gradient:



_T −_ 1

_∂_ _θ_ _V_ _[π]_ _[θ]_ ( _x_ ) = E _π_ _θ_ _,x_ �

� _t_ =0



� _R_ ( _x,_ ˆ _x_ ) _−_ _V_ _t_ _[π]_ _−_ _[θ]_ 1 [(] _[x]_ [)] � _∂_ _θ_ log( _π_ _θ_ ( _w_ _t_ _|x,_ ( _w_ _k_ ) _[t]_ _k_ _[−]_ =0 [1] [))]

�



_,_



where _V_ _t_ _[π]_ _−_ _[θ]_ 1 [(] _[x]_ [) =][ E] _[π]_ _θ_ _[,x]_ � _R_ ( _x,_ ˆ _x_ ) _|_ ( _w_ _k_ ) _[t]_ _k_ _[−]_ =0 [1] � is the value conditioned on all the information revealed
at time _t −_ 1. For our particular choice of speaker network, we encode the policy _π_ _θ_ ( _.|x,_ ( _w_ _k_ ) _[t]_ _k_ _[−]_ =0 [1] [)]
and the value _V_ _t_ _[π]_ _−_ _[θ]_ 1 [(] _[x]_ [)][ with the policy head] _[ π]_ _[θ]_ [(] _[.][|][z]_ _[t,θ]_ [)][ and the value head] _[ v]_ _[θ]_ [(] _[z]_ _[t,θ]_ [)][ respectively. Doing]
so is legitimate because by construction of our recurrent speaker network the embedding _z_ _t,θ_ is
a function of the image _x_ and the past words ( _w_ _k_ ) _[t]_ _k_ _[−]_ =0 [1] [. We train then our speaker network by]
minimizing a value loss _L_ _V_ ( _θ_ ) to make _v_ _θ_ ( _z_ _t,θ_ ) fit _V_ _t_ _[π]_ _−_ _[θ]_ 1 [(] _[x]_ [)][ over a batch] _[ X]_ [ of images:]



1 1
_L_ _V_ ( _θ_ ) = � _L_ _V_ ( _θ, x_ ) =
_|X|_ _x∈X_ _|X|_



�


_x∈X_



_T −_ 1
� ( _R_ ( _x,_ ˆ _x_ ) _−_ _v_ _θ_ ( _z_ _t,θ_ )) [2] _,_


_t_ =0



and a policy loss function _L_ _π_ ( _θ_ ) to maximise the expected reward:



�


_x∈X_



1
_L_ _π_ ( _θ_ ) =
_|X|_



1

� _L_ _π_ ( _θ, x_ ) =

_x∈X_ _|X|_



_T −_ 1
� sg ( _R_ ( _x,_ ˆ _x_ ) _−_ _v_ _θ_ ( _z_ _t,θ_ )) log( _π_ _θ_ ( _w_ _t_ _|z_ _t,θ_ )) _,_


_t_ =0



where sg( _._ ) is the stop gradient function. If we assume that _v_ _θ_ ( _z_ _t,θ_ ) fits perfectly _V_ _t_ _[π]_ _−_ _[θ]_ 1 [(] _[x]_ [)][, one]
can easily verify that _∂_ _θ_ _L_ _π_ ( _θ, x_ ) is an unbiased estimate of _−∂_ _θ_ _V_ _[π]_ _[θ]_ ( _x_ ) therefore _∂_ _θ_ _L_ _π_ ( _θ_ ) is also
an unbiased estimate of _−∂_ _θ_ _J_ ( _θ, φ_ ). In addition to following the gradient _∂_ _θ_ _V_ _[π]_ _[θ]_ ( _x_ ), it is common
practice in RL and emergent language literature to maximize an entropy term encouraging to explore
other choices of words by Speaker:



��



_H_ ( _π_ _θ_ ) =E _x∼ρ_



�



E _π_ _θ_ _,x_



_T −_ 1
�
� _t_ =0



� _H_ ( _π_ _θ_ ( _.|x,_ ( _w_ _k_ ) _[t]_ _k_ _[−]_ =0 [1] [))]


_t_ =0



_,_



_T −_ 1
� E _w∼π_ _θ_ ( _.|x,_ ( _w_ _k_ ) _tk−_ =01 [)] � _π_ _θ_ ( _w|x,_ ( _w_ _k_ ) _[t]_ _k_ _[−]_ =0 [1] [) log(] _[π]_ _[θ]_ [(] _[w][|][x,]_ [ (] _[w]_ _[k]_ [)] _k_ _[t][−]_ =0 [1] [))] �
� _t_ =0 ��



= E _x∼ρ_



E _π_ _θ_ _,x_

�



_._



In practice, a sampled version of the negative entropy _L_ _H_ ( _θ_ ) is minimized with the speaker network:



_L_ _H_ ( _θ_ ) = _−_ [1]

_|X|_



�


_x∈X_



_T −_ 1
� E _w∼π_ _θ_ ( _.|z_ _t,θ_ ) [ _π_ _θ_ ( _w|z_ _t,θ_ ) log( _π_ _θ_ ( _w|z_ _t,θ_ ))] _._


_t_ =0



Recently, several deep RL (Schulman et al., 2015; 2017) and theoretical RL papers (Geist et al.,
2019; Vieillard et al., 2020a;b) argued that minimizing the KL between the online policy _π_ _θ_ and
a target policy _π_ _θ_ instead of or in addition to entropy regularization could be beneficial for better
final performance as well as stabilizing the learning. Generally, _π_ _θ_ is an older policy or an exponential moving average of past policies. Therefore, we also consider the following KL regularization
KL( _π_ _θ_ _,_ ~~_π_~~ _θ_ ~~)~~ :



��



KL( _π_ _θ_ _,_ ~~_π_~~ _θ_ ~~)~~ =E _x∼ρ_


=E _x∼ρ_



�

�



E _π_ _θ_ _,x_


E _π_ _θ_ _,x_



_T −_ 1
�
� _t_ =0



_T −_ 1
� E _w∼π_ _θ_ ( _.|x,_ ( _w_ _k_ ) _tk−_ =01 [)]
� _t_ =0



_T −_ 1
�
� _t_ =0



� KL( _π_ _θ_ ( _.|x,_ ( _w_ _k_ ) _[t]_ _k_ _[−]_ =0 [1] [)] _[, ]_ ~~_[π]_~~ _θ_ ~~[(]~~ _[.][|][x,]_ [ (] _[w]_ _[k]_ [)] _[t]_ _k_ _[−]_ =0 [1] [))]


_t_ =0



_,_




[(] _[w]_ _[k]_ [)] _[t]_ _k_ _[−]_ = [1] 0 [)]
_π_ _θ_ ( _w|x,_ ( _w_ _k_ ) _[t]_ _k_ _[−]_ =0 [1] [) log(] _[π]_ _[θ]_ [(] _[w][|][x][,]_
� _π_ _θ_ ~~(~~ _w|x,_ ( _w_ _k_ ) _[t]_ _k_ _[−]_ =0 [1] [))] � [��]



_._



In practice, the policy _π_ _θ_ is obtained by doing an exponential moving average of the weights _θ_ over
training. Then, a sampled version of the KL is minimized _L_ KL ( _θ_ ) with our specific speaker network:



�



�



1
_L_ KL ( _θ_ ) = �
_|X|_ _x∈X_



_T −_ 1
� E _w∼π_ _θ_ ( _.|z_ _t,θ_ )


_t_ =0


17



_π_ _θ_ ( _w|z_ _t,θ_ ) log( _[π]_ _[θ]_ [(] _[w][|][z]_ _[t][,][θ]_ [)]




_[,]_

_π_ _θ_ ( _w|z_ _t,θ_ ) [)]



_._


Published as a conference paper at ICLR 2022


To sum up, the speaker training loss _L_ ( _θ_ ) on a batch of images _X_ is:


_L_ ( _θ_ ) = _L_ _V_ ( _θ_ ) + _L_ _π_ ( _θ_ ) + _αL_ _H_ ( _θ_ ) + _βL_ KL ( _θ_ ) _,_


where _α_ and _β_ are hyper-parameters.


**Listener loss** One important detail in Sec. 2.3 is that for each image _x_ in a batch _X_, a set of image
candidates _C_ ( _x, X_ ) is sampled randomly (uniform without replacement over _X \ {x}_ ) chosen in _X_ .
We omitted the dependencies of _C_ ( _x, X_ ) on _x_ and _X_ in the main text for ease of reading. In addition,
as explained in Sec. 2.3, the listener loss is a multi-class classification loss where the correct class
is the index of _x_ in the set of candidates _C_ also called InfoNCE loss (van den Oord et al., 2018):
_L_ ( _φ_ ) = _−_ _|X|_ [1] � _x∈X_ [log (] _[π]_ _[φ]_ [(] _[x][|][m,][ C]_ [))][. This can be rewritten more explicitly:]



_L_ ( _φ_ ) = _−_ [1]

_|X|_


= _−_ [1]

_|X|_


= _−_ [1]

_|X|_



� log


_x∈X_



� log ( _π_ _φ_ ( _x|m, C_ )) _,_


_x∈X_



exp(score( _m, x,_ _φ_ ))

� log

_x∈X_ � ~~�~~ ~~_x∈_~~ _C_ [exp(][score][(] _[m, ]_ ~~_[x]_~~



�



~~_x∈_~~ _C_ [exp(][score][(] _[m, ]_ ~~_[x]_~~ _[, φ]_ [))]



_,_
�



exp(cos( _∥pp_ _m,φm,φ_ _∥_ 2 _[,]_ _∥tt_ _xx_ _∥_ 2 [))]
� ~~�~~ ~~_x∈_~~ _C_ [exp(cos(] _∥p_ ~~_p_~~ _m,φm,φ_ _∥_ 2 _[,]_ _∥_ ~~_tt_~~ ~~_xx_~~ ~~_∥_~~ 2 [))]



�



_._



**Imitation training among a group of speakers.** In a training imitation step, a group of _K_ speakers among the total population of _N_ speakers is selected. Among those _K_ speakers, one speaker
is going to play the role of the teacher and _K −_ 1 are going to play the role of the students. To
choose the teacher among the _K_ speakers, we use as metric the exponential moving average of the
accuracies over each batch on which a given speaker has been trained on. To be more precise, let _θ_ _i_
be the _i_ -th speaker and _X_ the present batch on which _θ_ _i_ has just been trained on, then _σ_ _i_ is updated
according to the following rule:



_σ_ _i_ _←_ _µσ_ _i_ + (1 _−_ _µ_ ) [1]

_|X|_



� 1 _x_ =ˆ _x_


_x∈X_



and is the exponential moving average of coefficient _µ_ of the accuracies over each batch on which
speaker _i_ has been trained. Then the teacher is simply the speaker with the highest _σ_ _i_ among the _K_
speakers. Now for convenience, let us note _θ_ _T_ the parameters of the teacher and _θ_ _S_ the parameters
of a student. A student _θ_ _S_ is going to be trained on a batch of data _X_ by imitating the messages of
the teacher _θ_ _T_ with the following loss:



_L_ _I_ ( _θ_ _S_ ) = _−_ [1]

_|X|_



�


_x∈X_



_T −_ 1
� log _π_ _θ_ _S_ ( _w_ _t_ ( _x, θ_ _T_ ) _|x, z_ _θ_ _S_ _,t_ ) _._


_t_ =0



The loss _L_ _I_ ( _θ_ _S_ ) is a cross-entropy loss that encourages the student to output the same words as the
teacher.


**Optimizer hyper-parameters** Each member of the population (listener or speaker) uses its own
optimiser. All optimisers are Adam optimisers (Kingma & Ba, 2015) with the same set of hyperparameters:


_•_ learning rate: 1 _e −_ 4,


_• β_ 1 : 0 _._ 9,


_• β_ 2 : 0 _._ 999,


_• ϵ_ : 1 _e_ _[−]_ [8] .


For the speakers’ loss, we use _α_ = 0 _._ 0001 for the entropy regularization and _β_ = 0 _._ 5 for the KL
regularization. See Sec. B.3 for more details about the impact of these parameters.


18


Published as a conference paper at ICLR 2022


A.4 H YPER - PARAMETERS


We use the same hyper-parameters across the different settings. When experimenting with ImageNet
vs. CelebA, we only vary the number of maximum steps. Specifically, we use 300k maximum steps
for CelebA (we already start observing some overfitting with this value) and 900k maximum steps
for ImageNet. In all cases, we select the best checkpoint for evaluation with respect to the listener
loss at validation time. For robust evaluation, we average the scores over 5 epochs to have different
candidates for a given target and get a score less dependent on the sampling of the candidates. Unless
mentioned otherwise, the remaining training hyper-parameters are reported in Table 3.


Table 3: Hyper-parameters values across datasets and settings.


Learning rate _lr_ 0.0001
Batch training size _|X|_ 1024
Number of Candidates _|C|_ 1024
Number of agent sampled _P_ min(N, 10)
KL coefficient _β_ 0.5
KL EMA _η_ 0.99
Entropy Coefficient _α_ 0.0001
Vocabulary size _|W|_ 20
Message Length _T_ 10
Imitation EMA _µ_ 0.99


_ETL_ learning rate _ETL_, _lr_ 0.001
_ETL_ training batch size _ETL_, _|X|_ 4096
_ETL_ training candidates _ETL_ discr., _|C|_ 4096


A.5 I MITATION HYPER - PARAMETERS


In all our experiments, we perform a grid search over the parameters of _M_ (number of interaction
steps) and _K_ (number of sampled speakers at the imitation step). For the case of a population of
_N_ = 10, _K_ is chosen from _{_ 1 _,_ 4 _,_ 9 _}_ and _M_ from _{_ 10 _,_ 50 _,_ 100 _}_ according to the validation accuracy.
For _N_ = 50, _K_ is selected from _{_ 4 _,_ 9 _,_ 24 _}_ and _M_ from _{_ 1 _,_ 10 _,_ 50 _}_ . Table 4 shows the selected
hyper-parameters ( _K, M_ ) for the different settings.


Table 4: Imitation hyper-parameters values chosen according to the best accuracy at validation.

|Dataset|10 pairs + imitation<br>(K, M)|50 pairs + imitation<br>(K, M)|
|---|---|---|
|CelebA|(1, 10)|(9, 10)|
|ImageNet|(1, 100)|(9, 10)|



19


Published as a conference paper at ICLR 2022


A.6 D ATASETS DETAILS


**ImageNet** ILSVRC2012, also known as ImageNet (Deng et al., 2009; Russakovsky et al., 2015)
is among the historical largest natural RGB image dataset. It mostly contains images of animals and
objects over 1000 labels, e.g., camel, ostrich, hourglass, or bow tie. In our experiments, we use 99%
of the official train set for training, i.e., 1300k images, the last 1% of the train set for validation, i.e.,
13k images, and the official validation set as our test set (i.e., 50k images).


**CelebA** CelebA is a large natural RGB dataset (Liu et al., 2015), which contains image of celebrity
faces over 10,177 identities. Noticeably, each face also contains 40 binary attributes, e.g., glasses
and hair. Such attributes are interesting to compute, for instance, language topography. Although
there is an official CelebA split, there are no overlapping identities between the train, validation,
and test set. We thus reshuffle the split as described in Listing 1. In the end, we respectively obtain
169,444 training, 16,669 valid, and 16,486 test images.


**Image Processing** In both datasets, we resize images to 256 pixels along the shorter side using bicubic resampling before applying a 224x224 center crop. We normalize the color channels
subtracting the mean color and dividing by ImageNet std. We then use the ResNet-50 encoder pretrained on ImageNet with the self-supervised method BYOL (Grill et al., 2020) to extract the final
representation of dimension 2048.


Listing 1: CelebA Splits


SPLIT RATIO = 5 _# the_ _r a t i o_ _t r a i n : v a l i d_ _i s_ _5:1_


**def** c e l e b a s p l i t s ( data ) :
_””” S p l i t_ _the_ _data_ _in_ _t h r e e_ _s e t s_ _with_ _overlapping_ _i d e n t i t i e s ”””_


_#_ _I n i t i a l i z e_ _v a r i a b l e s_
i m a g e t r a i n, image valid, i m a g e t e s t = [ ], [ ], [ ]
c o u n t e r l a b e l = c o l l e c t i o n s . Counter ( )


**for** data **in** d a t a s e t . values ( ) :


l a b e l = data [ ’ l a b e l ’ ] _#_ _l a b e l_ _encode_ _the_ _face_ _i d e n t i t y_
count = c o u n t e r l a b e l [ l a b e l ]


**i f** count _>_ 0 **and** count % SPLIT RATIO == 0:
_# We e q u a l l y_ _s p l i t_ _v a l i d_ _and_ _t e s t_ _by Even and Odd l a b e l s_
**i f** l a b e l % 2 == 0:
image valid . append ( data )
**e l s e** :
i m a g e t e s t . append ( data )
**e l s e** :
i m a g e t r a i n . append ( data )


c o u n t e r l a b e l [ l a b e l ] += 1


**return** i m a g e t r a i n, image valid, i m a g e t e s t


20


Published as a conference paper at ICLR 2022


Figure 8: Face reconstructions. Left: Randomly sampled input images from the CelebA dataset;
Middle: Reconstructions, using messages from a model trained with 16 candidates; Right: Reconstructions, using messages from a model trained with 1024 candidates.


B A DDITIONAL R ESULTS AND A NALYSIS


B.1 F ACE RECONSTRUCTION


To visualize some of the features encapsulated in the messages used by the agent, we propose a
face reconstruction procedure. For a single speaker, parameterized by _θ_, and given an initial image
_x ∈X_, we produce a message _m_ = ( _w_ _t_ ) _t_ _[T]_ =0 _[ −]_ [1] [. We feed the messages to a listener-like architecture,]
consisting of an embedding layer of size 10 followed by an LSTM with 512 units. We keep the
last output of the LSTM, _h_ _T −_ 1 as a message representation. We then pass the message through a
deconvolutional architecture, similar to the one in Radford et al. (2016), but without batch normalizations. Pseudocode for the architecture is provided in Listing 2. The full network is trained by
minimizing the _ℓ_ [2] loss between the input image and the reconstructed one. To optimize the loss, we
use AdamW (Kingma & Ba, 2015) with a batch size of 128, a learning rate of 3 _·_ 10 _[−]_ [4], _β_ 1 = _._ 9,
_β_ 2 = _._ 9, _ε_ = 10 _[−]_ [8] and a weight decay of 0 _._ 01. We clip gradients by norm with a clipping threshold
of 500, and skip gradient updates with norm superior to 2000. In Table 1, we report reconstruction
losses for different number of candidates _|C|_ . The reconstruction loss is computed as a squared error, summed over both spatial and channel axes. Figure 8 displays examples of input images, and
corresponding reconstructions for two discrimination games with different number of candidates.


Optimally, each reconstruction should converge to the average face, given the corresponding message. The more features a message contains, the better reconstructions should be. Note first that
reconstructions are far from perfect, and much worse than reconstructions that an auto-encoder
trained end to end on images would provide: first, solving the discrimination game does not require
fully reconstructing the input image, but only capturing enough features to identify uniquely the
image in a batch of candidates; second, the discrete nature of the message, its limited size, and the
fact that it is learnt using reinforcement learning act as strong bottlenecks, that prevents messages
from containing all the information about input images.


Nonetheless, as qualitatively shown in Figure 8, messages contain semantic information about inputs images. For instance, hair color, gender, or open mouth are mostly preserved throughout the
reconstruction process. Other features, such as face orientation, skin tone, or age are mostly ignored
in messages. Furthermore, both quantitative and qualitative difference are visible when going from
low number of discriminators to high number of candidates. Quantitatively, going from 16 to 1024
candidates improves the reconstruction error from 2448 _±_ 16 to 2351 _±_ 14 (Table 1). Qualitatively,
messages with 1024 candidates seem to contain information about presence of eye-glasses (top left
image), as well as presence of head cover (bottom right image), that are absent in messages from the
Speaker trained with 16 candidates.


21


Published as a conference paper at ICLR 2022


Listing 2: Face reconstruction Head


**def** upsample 2d ( x, f a c t o r : **i n t** = 2 ) :
bs, height, width, channels = x . shape
x = image . r e s i z e (
x, ( bs, h e i g h t _∗_ f a c t o r, width _∗_ f a c t o r, channels ), method= ’ n e a r e s t ’ )
**return** x


**def** i m g r e c o n s t r u c t i o n ( x ) :
_”””Take_ _the LSTM output,_ _and_ _turn_ _i t_ _i n t o_ _an image . ”””_


_#_ _P r o j e c t_ _the_ _f l a t_ _embedding_ _i n t o_ _a 2d_ _t e n s o r_ _of_ _dim 4 x4x128_
x = nn . Linear (4 _∗_ 4 _∗_ 128)( x )
x = x . reshape ( ( x . shape [ 0 ], 4, 4, 128))
x = nn . r e l u ( x )


x = upsample 2d ( x ) _# 8x8_
x = nn . Conv3x3 (64, w i t h b i a s =False, padding=”VALID” ) ( x )
x = nn . r e l u ( x )


x = upsample 2d ( x ) _# 16 x16_
x = nn . Conv3x3 (32, w i t h b i a s =False, padding=”VALID” ) ( x )
x = nn . r e l u ( x )


x = upsample 2d ( x ) _# 32 x32_
x = nn . Conv3x3 (16, w i t h b i a s =False, padding=”VALID” ) ( x )
x = nn . r e l u ( x )


x = upsample 2d ( x ) _# 64 x64_
x = nn . Conv3x3 (16, w i t h b i a s =False, padding=”VALID” ) ( x )
x = nn . r e l u ( x )
x = nn . Conv3x3 (3, w i t h b i a s =False, padding=”VALID” ) ( x )


**return** nn . tanh ( x )


B.2 C OMPUTATIONAL REQUIREMENTS


As mentioned in the article, our approach remains computationally tractable with widely available
hardware. Table 5 summarizes these requirements to reproduce our experimental setup.


B.3 I MPACT OF THE KL REGULARIZATION ON TRAINING STABILITY


We showed in the main paper how training a pair of agents to solve a complex task (a discrimination
game with 1024 candidates) becomes unstable when using common optimization algorithms. In this
section, we look at the training curves when agents are trained with and without KL regularization,
while varying the entropy coefficient _α ∈{_ 10 _[−]_ [4] _,_ 10 _[−]_ [3] _,_ 10 _[−]_ [2] _,_ 10 _[−]_ [1] _}_ . Results are shown with a
population of size 1 (Figure 9) and 10 (Figure 10). In both cases, agents are trained to solve the
complex discrimination task with 1024 candidates.


First, we observe that the lower _α_ is, the more crucial applying a KL regularization is. For example,
in Figure 9(a), we go from a chaotic setting that converges to an accuracy of _∼_ 40% when the
KL coefficient _β_ = 0 to a significantly more stable optimization with almost perfect accuracy when
_β ≥_ 0 _._ 5. Second, we observe that, if the KL regularization is useful for stable optimization, it comes
at the cost of the rapidity of convergence. This is clearly shown in Figures 9(c) and 10(c), where we
observe that the larger _β_ is, the slower the convergence is. In other words, one should select the best
_β_ optimizing the stability/rapidity trade-off. Third, in the presence of a KL regularization, training
stability depends less on the entropy coefficient _α_ . Indeed, we observe a stable and high training


22


Published as a conference paper at ICLR 2022


Table 5: Computational requirements for our base setup. “GPU memory” refers to the peak GPU

memory usage.


Dataset Device Pop. size, _N_ GPU memory (GiB) Step time (ms) Train. time (hours)


1 0.29 42 10.5
p100 10 0.71 381 95.2
50 2.63 1887 471.7


1 0.29 25 6.3

v100 10 0.71 223 55.7

50 2.63 1089 272.1


1 0.33 89 7.4
p100 10 0.75 457 38.1
50 2.60 2248 187.4


1 0.33 107 8.9

v100 10 0.75 293 24.4

50 2.60 1408 117.3





(a) _α_ = 0 _._ 0001


(c) _α_ = 0 _._ 01







(b) _α_ = 0 _._ 001



(d) _α_ = 0 _._ 1









Figure 9: Training accuracy for a 1 communicating pair when varying the KL coefficient _β_ . Each
sub-figure represents the results for a fixed entropy coefficient _α_ . Thin lines represent the training
accuracy curves of different seeds. Thick lines represent the average across 10 seeds.


curves for _α ∈{_ 10 _[−]_ [4] _,_ 10 _[−]_ [3] _,_ 10 _[−]_ [2] _}_ . [4] However, training without KL regularization (blue curves
with _β_ = 0) is very sensitive to the value of _α_ and the most stable case is observed for _α_ = 0 _._ 01.
Still even in this best case without KL regularization, having a _β >_ 0 is useful as shown in Figure 11.


4 It is also the case for _α_ = 0. Not shown here.


23


Published as a conference paper at ICLR 2022







(a) _α_ = 0 _._ 0001


(c) _α_ = 0 _._ 01







(b) _α_ = 0 _._ 001



(d) _α_ = 0 _._ 1







Figure 10: Training accuracy for a 10 communicating pairs when varying the KL coefficient _β_ . Each
sub-figure represents the results for a fixed entropy coefficient _α_ . Thin lines represent the training
accuracy curves of different seeds. Thick lines represent the average across 10 seeds.











(a) 1 pair



(b) 10 pairs



Figure 11: Training accuracy for 1 and 10 pairs. Each sub-figure compares the best setting with
no KL regularization (with entropy coefficient of 0 _._ 01) and the selected setting for our experiments,
with a KL coefficient of 0 _._ 5 and entropy coefficient of 0 _._ 0001. Thin lines represent the training
accuracy curves of different seeds. Thick lines represent the average across 10 seeds. In both cases,
the setting with the KL regularization, (0 _._ 5 _,_ 0 _._ 0001), exhibits a more stable convergence with a
larger difference for population of 10 pairs.


24


Published as a conference paper at ICLR 2022


Table 6: Different language properties on CelebA dataset, in %. For each setting we report the mean
over 10 seeds. _±_ denotes 1 standard error of the mean.


Setting Generalization Robustness


best 1 pair 90 _._ 73 35 _._ 82
1 pair 89 _._ 00 _±_ 0 _._ 48 37 _._ 90
10 pairs 91 _._ 06 _±_ 0 _._ 23 37 _._ 56
50 pairs 90 _._ 69 _±_ 0 _._ 61 38 _._ 87


10 pairs + imitation 91 _._ 84 _±_ 0 _._ 31 35 _._ 47
10 pairs + imitation + vote 92 _._ 19 _±_ 0 _._ 30 35 _._ 21
50 pairs + imitation 92 _._ 82 _±_ 0 _._ 51 32 _._ 69
50 pairs + imitation + vote **93** _._ **13** _±_ **0** _._ **50** 32 _._ 40


1 pair + reset 92 _._ 21 _±_ 0 _._ 44 **18** _._ **34**
10 pairs + reset 90 _._ 55 _±_ 0 _._ 56 35 _._ 32
50 pairs + reset 91 _._ 52 _±_ 0 _._ 42 34 _._ 46


B.4 S TUDY OF THE RESETTING ON THE C ELEB A DATASET


In this work, we argue that training deep agents to communicate in a population benefits from exploiting its richness, as opposed to a standard training (Mordatch & Abbeel, 2018). In this context,
we introduced imitation and voting mechanisms. However, other prior works have stipulated a similar argument by focusing instead on the idea of the expressivity/compressibility trade-off (Kirby
et al., 2014). The latter attests that our language is shaped by the two competing pressures of
expressivity and compressibility. In practice, there were different methods to implement this tradeoff in deep agents communication such as iterated learning (Ren et al., 2019), cultural transmission (Cogswell et al., 2019), or ease-of-teaching (Li & Bowling, 2019). In this section, we compare
imitation and voting to the ease-of-teaching. [5] To encourage languages’ ease-of-teaching, Li & Bowling (2019) trained deep agents to solve a discrimination task, while periodically resetting listeners.
In this section, we study the impact of this baseline on the different emergent languages’ properties
introduced in the main paper. Specifically, we consider 3 additional settings: (1) “1 pair + reset”
that consists of resetting the only listener, (2) “10 pairs + reset” where we reset a randomly selected
listener among the 10 available ones, and (3) “50 pairs + reset” where we reset a randomly selected
listener among the 50 available ones. In all cases, resetting takes place every 51k steps. Note that if
(1) is identical to Li & Bowling (2019) setting, (2) and (3) present 10 and 50 speakers respectively
unlike 1 speaker as it is the case in (Li & Bowling, 2019).


We observe in Table 6 that resetting has a noticeable benefit only in the case of “1 pair” on the
generalization and robustness of the languages. In particular, we note an average _Generalization_ of
89.00% for “1 pair” vs. 92.21% for “1 pair + reset” and an average _Robustness_ of 18.34% vs. 35.82%.
However, there is no systematic improvement when agents are trained in a population, (“10 pairs”
vs. “10 pairs + resetting”) and (“50 pairs” vs. “50 pairs + resetting”). This is in line with Li &
Bowling (2019)’s results which show that an abrupt change during training leads to better results.
Still, “1 pair + reset” does not systematically improve the emergent languages’ properties compared
to the population when imitation and voting are at play.


However, as mentioned in the original paper, the purpose of resetting is not to boost agents’ generalization or robustness, but instead to incentivize agents to develop easy-to-transmit languages. In the
following, we look at _ETL_ shown in Figure 12. Here, adding resetting does not lead to a significant
change showing curves almost identical to the ones with standard training in all cases.


Overall, our results suggest that resetting listeners is only beneficial in the one-pair agents in some
cases. Furthermore, resetting does not induce faster or better easy-to-learn communication protocols
over transfer tasks compared to the standard training of the Lewis game (with or without population).


5 We also considered the setup of Cogswell et al. (2019). However, preliminary results showed systematically worse results compared to the ease-of-teaching settings. Our codebase provides both options.


25


Published as a conference paper at ICLR 2022


(a) _Discrimination_



|0.6<br>0.5<br>0.4<br>0.3<br>0.2<br>0.1<br>0.0<br>1000 2000 3000 4000<br>Ste|6<br>5|Col3|Col4|
|---|---|---|---|
|~~1000 2000 3000 4000~~<br>Ste<br>0.0<br>0.1<br>0.2<br>0.3<br>0.4<br>0.5<br>0.6<br>|3<br>4<br>|||
|~~1000 2000 3000 4000~~<br>Ste<br>0.0<br>0.1<br>0.2<br>0.3<br>0.4<br>0.5<br>0.6<br>|3<br>4<br>|||
|~~1000 2000 3000 4000~~<br>Ste<br>0.0<br>0.1<br>0.2<br>0.3<br>0.4<br>0.5<br>0.6<br>|3<br>4<br>|||
|~~1000 2000 3000 4000~~<br>Ste<br>0.0<br>0.1<br>0.2<br>0.3<br>0.4<br>0.5<br>0.6<br>||||
|~~1000 2000 3000 4000~~<br>Ste<br>0.0<br>0.1<br>0.2<br>0.3<br>0.4<br>0.5<br>0.6<br>||||
|~~1000 2000 3000 4000~~<br>Ste<br>0.0<br>0.1<br>0.2<br>0.3<br>0.4<br>0.5<br>0.6<br>||||


(b) _Classification of Identities_











Figure 12: _ETL_ for the CelebA dataset of the emergent languages for different tasks. The results are
averaged across the emergent languages of _min_ (5 _, N_ ) different Speakers, newborn listeners’ seeds,
and across the 10 seeds of each setting. The shaded region represents the standard deviation.


B.5 I MPACT OF THE NUMBER OF CANDIDATES AT TRAINING AND EVALUATION TIME


In this part we look the impact of task complexity at train (Figure 14) and evaluation (Figure 13)
times, by varying the number of candidates _|C|_ . The results confirm our findings in the main paper.
That is, for a fixed train _|C|_, the harder the evaluation task is, the lower the test accuracy is. Still, if
the task is complex enough at train time (e.g., _|C|_ = 1024), agents reach overall higher accuracies
for all evaluation settings, confirming the importance of hard training tasks to see the emergence
of communication protocols with good generalization performances. Also, similarly to our results
in the main paper, we observe in Figure 14 that harder evaluation task is necessary to discriminate
between the communication protocols.


26


Published as a conference paper at ICLR 2022





|Col1|Col2|Col3|Col4|Col5|Col6|Col7|
|---|---|---|---|---|---|---|
||||||||
||||||||
||||N||||
||||N|um candi|dates (e<br>|al)|
||||||~~16~~<br>64<br>~~256~~||
||||||1024<br>4096||


(b) Num candidates at (train): 64

|Col1|Col2|Col3|Col4|Col5|Col6|Col7|
|---|---|---|---|---|---|---|
||||||||
||||||||
||||N||||
||||N|um candi|dates (e<br>|al)|
||||||~~16~~<br>64<br>~~256~~||
||||||1024<br>4096||



(d) Num candidates at (train): 1024





|Col1|Col2|Col3|Col4|Col5|Col6|Col7|
|---|---|---|---|---|---|---|
||||||||
||||||||
||||N||||
||||N|um candi|dates (e<br>|al)|
||||||~~16~~<br>64<br>~~256~~||
||||||1024<br>4096||


(a) Num candidates at (train): 16

|Col1|Col2|Col3|Col4|Col5|Col6|Col7|
|---|---|---|---|---|---|---|
||||||||
||||||||
||||N||||
||||N|um candi|dates (e<br>|al)|
||||||~~16~~<br>64<br>~~256~~||
||||||1024<br>4096||



(c) Num candidates at (train): 256



Figure 13: Test accuracy for different number of candidates at training time (subplot) and at evaluation time (lines) on ImageNet. As one would expect, given one model trained with _|C|_ candidates,
the more complex the evaluation task, the lower is the accuracy.


27


Published as a conference paper at ICLR 2022





|Col1|Col2|Col3|Col4|Col5|Col6|Col7|
|---|---|---|---|---|---|---|
||||||||
||||||||
||||||||
||||~~N~~|~~m candi~~|~~ates (tr~~<br>16<br>~~64~~<br>|~~in)~~|
||||||256<br>1024||
|~~100K 200K 300K 400~~<br>S|~~100K 200K 300K 400~~<br>S|~~100K 200K 300K 400~~<br>S|~~100K 200K 300K 400~~<br>S|~~100K 200K 300K 400~~<br>S|~~100K 200K 300K 400~~<br>S|~~100K 200K 300K 400~~<br>S|


(b) Num candidates at (eval): 64





|Col1|Col2|Col3|Col4|Col5|
|---|---|---|---|---|
||||||
||||||
||||||
||||~~Num ca~~|~~didates (tra~~<br>16<br>64<br>|
|||||~~256~~<br>1024|


(a) Num candidates at (eval): 16

|Col1|Col2|Col3|Col4|Col5|
|---|---|---|---|---|
||||||
||||||
||||~~Num ca~~|~~didates (tra~~<br>16<br>~~64~~<br>|
|||||256<br>1024|



(c) Num candidates at (eval): 256



|Col1|Col2|Col3|Col4|Col5|Col6|Col7|
|---|---|---|---|---|---|---|
||||||||
||||||||
||||~~N~~|~~um candi~~|~~dates (tr~~<br>16<br>~~64~~<br>|~~in)~~|
||||||256<br>1024||
|~~100K 200K 300K 400~~<br>S|~~100K 200K 300K 400~~<br>S|~~100K 200K 300K 400~~<br>S|~~100K 200K 300K 400~~<br>S|~~100K 200K 300K 400~~<br>S|~~100K 200K 300K 400~~<br>S|~~100K 200K 300K 400~~<br>S|


(d) Num candidates at (eval): 1024



|Col1|Col2|Col3|Col4|Col5|
|---|---|---|---|---|
||||||
||||||
|||Num ca|ndidates (tr<br>16<br>~~64~~|ain)|
||||256<br>1024||
|~~100K 200K 300K 400~~<br>S|~~100K 200K 300K 400~~<br>S|~~100K 200K 300K 400~~<br>S|~~100K 200K 300K 400~~<br>S|~~100K 200K 300K 400~~<br>S|


(e) Num candidates at (eval): 4096


Figure 14: Test accuracy for different number of candidates at training time (lines) and at evaluation
time on ImageNet. The more we complexify evaluation, the better we discriminate representations.


28


Published as a conference paper at ICLR 2022


B.6 C ELEB A ATTRIBUTES :


Table 7: CelebA _ETL_ attribute accuracies when varying the number of candidates at pretraining at
10k training steps.


Atribute _|C|_ = 16 _|C|_ = 64 _|C|_ = 256 _|C|_ = 1024


5 o Clock Shadow 89 _._ 93 _±_ 0 _._ 74 90 _._ 57 _±_ 0 _._ 75 91 _._ 46 _±_ 0 _._ 5 92 _._ 76 _±_ 0 _._ 54
Arched Eyebrows 77 _._ 73 _±_ 0 _._ 75 79 _._ 49 _±_ 0 _._ 88 81 _._ 35 _±_ 1 _._ 15 83 _._ 22 _±_ 0 _._ 8
Attractive 78 _._ 74 _±_ 1 _._ 01 80 _._ 08 _±_ 0 _._ 96 81 _._ 25 _±_ 0 _._ 75 83 _._ 27 _±_ 1 _._ 18
Bags Under Eyes 81 _._ 86 _±_ 0 _._ 85 83 _._ 53 _±_ 0 _._ 72 84 _._ 66 _±_ 0 _._ 68 86 _._ 51 _±_ 0 _._ 77
Bald 98 _._ 03 _±_ 0 _._ 15 98 _._ 03 _±_ 0 _._ 23 98 _._ 20 _±_ 0 _._ 25 98 _._ 43 _±_ 0 _._ 21
Bangs 85 _._ 60 _±_ 0 _._ 53 86 _._ 29 _±_ 0 _._ 71 87 _._ 05 _±_ 0 _._ 71 88 _._ 42 _±_ 0 _._ 62
Big Lips 77 _._ 57 _±_ 0 _._ 92 78 _._ 73 _±_ 0 _._ 81 80 _._ 31 _±_ 0 _._ 97 82 _._ 09 _±_ 0 _._ 87
Big Nose 80 _._ 58 _±_ 0 _._ 74 82 _._ 56 _±_ 0 _._ 77 83 _._ 77 _±_ 0 _._ 77 85 _._ 56 _±_ 0 _._ 75
Black Hair 78 _._ 22 _±_ 0 _._ 83 79 _._ 78 _±_ 1 _._ 32 81 _._ 32 _±_ 1 _._ 39 83 _._ 52 _±_ 0 _._ 93
Blond Hair 88 _._ 23 _±_ 2 _._ 31 89 _._ 42 _±_ 1 _._ 77 90 _._ 62 _±_ 2 _._ 07 91 _._ 94 _±_ 1 _._ 01
Blurry 95 _._ 11 _±_ 0 _._ 19 95 _._ 40 _±_ 0 _._ 26 95 _._ 65 _±_ 0 _._ 28 96 _._ 31 _±_ 0 _._ 41
Brown Hair 80 _._ 83 _±_ 0 _._ 81 81 _._ 82 _±_ 0 _._ 81 83 _._ 26 _±_ 1 _._ 0 84 _._ 80 _±_ 0 _._ 75
Bushy Eyebrows 86 _._ 53 _±_ 0 _._ 5 87 _._ 28 _±_ 0 _._ 51 87 _._ 87 _±_ 0 _._ 54 89 _._ 46 _±_ 0 _._ 5
Chubby 94 _._ 53 _±_ 0 _._ 34 94 _._ 89 _±_ 0 _._ 35 95 _._ 44 _±_ 0 _._ 34 96 _._ 06 _±_ 0 _._ 36
Double Chin 95 _._ 76 _±_ 0 _._ 34 95 _._ 97 _±_ 0 _._ 35 96 _._ 37 _±_ 0 _._ 25 96 _._ 86 _±_ 0 _._ 26
Eyeglasses 94 _._ 50 _±_ 0 _._ 53 95 _._ 98 _±_ 1 _._ 5 98 _._ 30 _±_ 0 _._ 95 98 _._ 48 _±_ 0 _._ 76
Goatee 94 _._ 28 _±_ 0 _._ 38 94 _._ 66 _±_ 0 _._ 36 95 _._ 00 _±_ 0 _._ 37 95 _._ 88 _±_ 0 _._ 44
Gray Hair 96 _._ 03 _±_ 0 _._ 2 96 _._ 45 _±_ 0 _._ 3 96 _._ 81 _±_ 0 _._ 25 97 _._ 41 _±_ 0 _._ 25
Heavy Makeup 88 _._ 08 _±_ 0 _._ 5 88 _._ 75 _±_ 0 _._ 64 89 _._ 36 _±_ 0 _._ 65 90 _._ 49 _±_ 0 _._ 95
High Cheekbones 77 _._ 94 _±_ 1 _._ 87 79 _._ 70 _±_ 1 _._ 07 79 _._ 98 _±_ 1 _._ 57 82 _._ 39 _±_ 1 _._ 33
Male 93 _._ 15 _±_ 0 _._ 44 93 _._ 82 _±_ 0 _._ 43 94 _._ 06 _±_ 0 _._ 51 94 _._ 73 _±_ 0 _._ 57
Mouth Slightly Open 71 _._ 25 _±_ 2 _._ 1 73 _._ 62 _±_ 1 _._ 2 74 _._ 77 _±_ 1 _._ 98 77 _._ 86 _±_ 1 _._ 53
Mustache 95 _._ 91 _±_ 0 _._ 32 96 _._ 15 _±_ 0 _._ 38 96 _._ 54 _±_ 0 _._ 33 97 _._ 06 _±_ 0 _._ 28
Narrow Eyes 89 _._ 12 _±_ 0 _._ 49 89 _._ 53 _±_ 0 _._ 55 89 _._ 98 _±_ 0 _._ 53 90 _._ 35 _±_ 0 _._ 45
No Beard 88 _._ 48 _±_ 0 _._ 68 89 _._ 05 _±_ 0 _._ 78 90 _._ 21 _±_ 0 _._ 84 91 _._ 82 _±_ 0 _._ 89
Oval Face 74 _._ 54 _±_ 0 _._ 76 76 _._ 21 _±_ 0 _._ 82 78 _._ 15 _±_ 0 _._ 9 80 _._ 82 _±_ 0 _._ 9
Pale Skin 95 _._ 69 _±_ 0 _._ 23 95 _._ 94 _±_ 0 _._ 24 96 _._ 13 _±_ 0 _._ 31 96 _._ 50 _±_ 0 _._ 31
Pointy Nose 75 _._ 61 _±_ 0 _._ 84 77 _._ 31 _±_ 1 _._ 03 78 _._ 78 _±_ 1 _._ 23 80 _._ 96 _±_ 0 _._ 79
Receding Hairline 92 _._ 49 _±_ 0 _._ 39 92 _._ 88 _±_ 0 _._ 3 93 _._ 23 _±_ 0 _._ 39 93 _._ 95 _±_ 0 _._ 42
Rosy Cheeks 93 _._ 79 _±_ 0 _._ 24 94 _._ 17 _±_ 0 _._ 3 94 _._ 70 _±_ 0 _._ 43 95 _._ 42 _±_ 0 _._ 45
Sideburns 94 _._ 80 _±_ 0 _._ 3 95 _._ 06 _±_ 0 _._ 32 95 _._ 62 _±_ 0 _._ 32 96 _._ 33 _±_ 0 _._ 47
Smiling 79 _._ 45 _±_ 2 _._ 54 81 _._ 39 _±_ 1 _._ 22 81 _._ 34 _±_ 2 _._ 28 83 _._ 56 _±_ 1 _._ 77
Straight Hair 80 _._ 55 _±_ 0 _._ 57 81 _._ 64 _±_ 0 _._ 6 82 _._ 95 _±_ 0 _._ 75 84 _._ 46 _±_ 0 _._ 77
Wavy Hair 76 _._ 42 _±_ 0 _._ 76 78 _._ 09 _±_ 0 _._ 98 80 _._ 24 _±_ 1 _._ 35 82 _._ 22 _±_ 0 _._ 92
Wearing Earrings 83 _._ 72 _±_ 0 _._ 59 84 _._ 65 _±_ 0 _._ 77 85 _._ 74 _±_ 0 _._ 8 87 _._ 08 _±_ 0 _._ 75
Wearing Hat 97 _._ 07 _±_ 1 _._ 46 97 _._ 03 _±_ 1 _._ 28 98 _._ 83 _±_ 0 _._ 4 98 _._ 95 _±_ 0 _._ 25
Wearing Lipstick 90 _._ 96 _±_ 0 _._ 38 91 _._ 52 _±_ 0 _._ 58 91 _._ 87 _±_ 0 _._ 58 92 _._ 57 _±_ 0 _._ 71
Wearing Necklace 87 _._ 93 _±_ 0 _._ 41 88 _._ 51 _±_ 0 _._ 47 89 _._ 23 _±_ 0 _._ 7 90 _._ 37 _±_ 0 _._ 59
Wearing Necktie 95 _._ 14 _±_ 0 _._ 24 95 _._ 56 _±_ 0 _._ 33 96 _._ 10 _±_ 0 _._ 3 96 _._ 44 _±_ 0 _._ 47
Young 83 _._ 45 _±_ 1 _._ 34 84 _._ 93 _±_ 1 _._ 12 85 _._ 79 _±_ 0 _._ 78 87 _._ 85 _±_ 0 _._ 65


B.7 O UT - OF - DISTRIBUTION GENERALIZATION : THE O FFICIAL C ELEB A SPLIT


In the main paper, we consider a new CelebA split where train and test sets have overlapping identities. This allows us to test in-distribution performances. In this Subsection, we look at out-ofdistribution generalization considering the official CelebA split, where train, validation, and test sets
include distinct identities. In other words, we now consider a harder form of generalization by testing agents on never-seen identities at training. Results are shown in Table 8. We observe a similar
pattern to the in-distribution results shown in Table 2. That is, we do not observe a benefit for the
population, where “best 1 pair” achieves better unseen-generalization than “10 pairs” and “50 pairs”.
However, when considering imitation and voting, agents develop languages that generalize better to


29


Published as a conference paper at ICLR 2022


never-seen identities. The setting “50 pairs + imitation + vote” attains the best performance, with a
93.75% success when communicating about previously unseen identities at training time.


Table 8: Generalization performance on the official CelebA split, in %. In this case, we look at
out-of-distribution generalization as train and test sets contain different identities. For each setting
we report the mean over 10 seeds. _±_ denotes 1 standard error of the mean.


Setting best 1 pair 1 pair 10 pairs 50 pairs


              -               -               - +imitation + imitation+vote               - +imitation + imitation+vote


Generalization 92 _._ 60 90 _._ 08 _±_ 0 _._ 54 90 _._ 42 _±_ 0 _._ 55 92 _._ 01 _±_ 0 _._ 40 92 _._ 37 _±_ 0 _._ 40 90 _._ 91 _±_ 0 _._ 37 93 _._ 41 _±_ 0 _._ 19 **93** _._ **75** _±_ 0 _._ 18


30


