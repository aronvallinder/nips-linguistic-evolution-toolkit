## **Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks**

**Nils Reimers and Iryna Gurevych**
Ubiquitous Knowledge Processing Lab (UKP-TUDA)
Department of Computer Science, Technische Universit¨at Darmstadt

www.ukp.tu-darmstadt.de



**Abstract**


BERT (Devlin et al., 2018) and RoBERTa (Liu
et al., 2019) has set a new state-of-the-art
performance on sentence-pair regression tasks
like semantic textual similarity (STS). However, it requires that both sentences are fed
into the network, which causes a massive computational overhead: Finding the most similar pair in a collection of 10,000 sentences
requires about 50 million inference computations (~65 hours) with BERT. The construction
of BERT makes it unsuitable for semantic sim
ilarity search as well as for unsupervised tasks
like clustering.


In this publication, we present Sentence-BERT
(SBERT), a modification of the pretrained
BERT network that use siamese and triplet network structures to derive semantically meaningful sentence embeddings that can be compared using cosine-similarity. This reduces the
effort for finding the most similar pair from 65
hours with BERT / RoBERTa to about 5 sec
onds with SBERT, while maintaining the accuracy from BERT.


We evaluate SBERT and SRoBERTa on com
mon STS tasks and transfer learning tasks,
where it outperforms other state-of-the-art
sentence embeddings methods. [1]


**1** **Introduction**


In this publication, we present Sentence-BERT
(SBERT), a modification of the BERT network using siamese and triplet networks that is able to
derive semantically meaningful sentence embeddings [2] . This enables BERT to be used for certain
new tasks, which up-to-now were not applicable
for BERT. These tasks include large-scale seman

1 [Code available: https://github.com/UKPLab/](https://github.com/UKPLab/sentence-transformers)

[sentence-transformers](https://github.com/UKPLab/sentence-transformers)

2 With _semantically meaningful_ we mean that semantically
similar sentences are close in vector space.



tic similarity comparison, clustering, and information retrieval via semantic search.

BERT set new state-of-the-art performance on
various sentence classification and sentence-pair
regression tasks. BERT uses a cross-encoder: Two
sentences are passed to the transformer network
and the target value is predicted. However, this
setup is unsuitable for various pair regression tasks
due to too many possible combinations. Finding
in a collection of _n_ = 10 000 sentences the pair
with the highest similarity requires with BERT
_n·_ ( _n−_ 1) _/_ 2 = 49 995 000 inference computations.
On a modern V100 GPU, this requires about 65
hours. Similar, finding which of the over 40 million existent questions of Quora is the most similar
for a new question could be modeled as a pair-wise
comparison with BERT, however, answering a single query would require over 50 hours.
A common method to address clustering and semantic search is to map each sentence to a vector space such that semantically similar sentences
are close. Researchers have started to input individual sentences into BERT and to derive fixedsize sentence embeddings. The most commonly
used approach is to average the BERT output layer
(known as BERT embeddings) or by using the output of the first token (the [CLS] token). As we
will show, this common practice yields rather bad
sentence embeddings, often worse than averaging
GloVe embeddings (Pennington et al., 2014).
To alleviate this issue, we developed SBERT.
The siamese network architecture enables that

fixed-sized vectors for input sentences can be derived. Using a similarity measure like cosinesimilarity or Manhatten / Euclidean distance, semantically similar sentences can be found. These
similarity measures can be performed extremely
efficient on modern hardware, allowing SBERT
to be used for semantic similarity search as well
as for clustering. The complexity for finding the


most similar sentence pair in a collection of 10,000
sentences is reduced from 65 hours with BERT to

the computation of 10,000 sentence embeddings
(~5 seconds with SBERT) and computing cosinesimilarity (~0.01 seconds). By using optimized
index structures, finding the most similar Quora
question can be reduced from 50 hours to a few
milliseconds (Johnson et al., 2017).

We fine-tune SBERT on NLI data, which creates sentence embeddings that significantly outperform other state-of-the-art sentence embedding
methods like InferSent (Conneau et al., 2017) and
Universal Sentence Encoder (Cer et al., 2018). On
seven Semantic Textual Similarity (STS) tasks,
SBERT achieves an improvement of 11.7 points
compared to InferSent and 5.5 points compared to
Universal Sentence Encoder. On SentEval (Conneau and Kiela, 2018), an evaluation toolkit for
sentence embeddings, we achieve an improvement
of 2.1 and 2.6 points, respectively.
SBERT can be adapted to a specific task. It
sets new state-of-the-art performance on a challenging argument similarity dataset (Misra et al.,
2016) and on a triplet dataset to distinguish sentences from different sections of a Wikipedia article (Dor et al., 2018).

The paper is structured in the following way:
Section 3 presents SBERT, section 4 evaluates
SBERT on common STS tasks and on the chal
lenging Argument Facet Similarity (AFS) corpus
(Misra et al., 2016). Section 5 evaluates SBERT
on SentEval. In section 6, we perform an ablation
study to test some design aspect of SBERT. In section 7, we compare the computational efficiency of
SBERT sentence embeddings in contrast to other
state-of-the-art sentence embedding methods.


**2** **Related Work**


We first introduce BERT, then, we discuss stateof-the-art sentence embedding methods.
BERT (Devlin et al., 2018) is a pre-trained
transformer network (Vaswani et al., 2017), which

set for various NLP tasks new state-of-the-art re
sults, including question answering, sentence classification, and sentence-pair regression. The input
for BERT for sentence-pair regression consists of
the two sentences, separated by a special [SEP]
token. Multi-head attention over 12 (base-model)
or 24 layers (large-model) is applied and the output is passed to a simple regression function to derive the final label. Using this setup, BERT set a



new state-of-the-art performance on the Semantic
Textual Semilarity (STS) benchmark (Cer et al.,
2017). RoBERTa (Liu et al., 2019) showed, that
the performance of BERT can further improved by
small adaptations to the pre-training process. We
also tested XLNet (Yang et al., 2019), but it led in
general to worse results than BERT.

A large disadvantage of the BERT network
structure is that no independent sentence embeddings are computed, which makes it difficult to derive sentence embeddings from BERT. To bypass
this limitations, researchers passed single sentences through BERT and then derive a fixed sized
vector by either averaging the outputs (similar to
average word embeddings) or by using the output
of the special CLS token (for example: May et al.
(2019); Zhang et al. (2019); Qiao et al. (2019)).
These two options are also provided by the popular bert-as-a-service-repository [3] . Up to our knowledge, there is so far no evaluation if these methods
lead to useful sentence embeddings.

Sentence embeddings are a well studied area
with dozens of proposed methods. Skip-Thought
(Kiros et al., 2015) trains an encoder-decoder architecture to predict the surrounding sentences.
InferSent (Conneau et al., 2017) uses labeled
data of the Stanford Natural Language Inference
dataset (Bowman et al., 2015) and the MultiGenre NLI dataset (Williams et al., 2018) to train
a siamese BiLSTM network with max-pooling
over the output. Conneau et al. showed, that
InferSent consistently outperforms unsupervised
methods like SkipThought. Universal Sentence
Encoder (Cer et al., 2018) trains a transformer
network and augments unsupervised learning with
training on SNLI. Hill et al. (2016) showed, that
the task on which sentence embeddings are trained
significantly impacts their quality. Previous work
(Conneau et al., 2017; Cer et al., 2018) found that
the SNLI datasets are suitable for training sentence embeddings. Yang et al. (2018) presented
a method to train on conversations from Reddit

using siamese DAN and siamese transformer networks, which yielded good results on the STS
benchmark dataset.


Humeau et al. (2019) addresses the run-time

overhead of the cross-encoder from BERT and

present a method (poly-encoders) to compute
a score between _m_ context vectors and pre

3 [https://github.com/hanxiao/](https://github.com/hanxiao/bert-as-service/)
[bert-as-service/](https://github.com/hanxiao/bert-as-service/)


-1 … 1







Sentence A Sentence B


Figure 1: SBERT architecture with classification objective function, e.g., for fine-tuning on SNLI dataset.
The two BERT networks have tied weights (siamese
network structure).


computed candidate embeddings using attention.
This idea works for finding the highest scoring
sentence in a larger collection. However, polyencoders have the drawback that the score function

is not symmetric and the computational overhead
is too large for use-cases like clustering, which
would require _O_ ( _n_ [2] ) score computations.
Previous neural sentence embedding methods
started the training from a random initialization.
In this publication, we use the pre-trained BERT
and RoBERTa network and only fine-tune it to
yield useful sentence embeddings. This reduces
significantly the needed training time: SBERT can
be tuned in less than 20 minutes, while yielding
better results than comparable sentence embedding methods.


**3** **Model**


SBERT adds a pooling operation to the output
of BERT / RoBERTa to derive a fixed sized sentence embedding. We experiment with three pooling strategies: Using the output of the CLS-token,
computing the mean of all output vectors (MEANstrategy), and computing a max-over-time of the
output vectors (MAX-strategy). The default configuration is MEAN.

In order to fine-tune BERT / RoBERTa, we create siamese and triplet networks (Schroff et al.,
2015) to update the weights such that the produced
sentence embeddings are semantically meaningful
and can be compared with cosine-similarity.
The network structure depends on the available



Sentence A Sentence B


Figure 2: SBERT architecture at inference, for example, to compute similarity scores. This architecture is
also used with the regression objective function.


training data. We experiment with the following
structures and objective functions.
**Classification Objective Function.** We concatenate the sentence embeddings _u_ and _v_ with
the element-wise difference _|u_ _−_ _v|_ and multiply it
with the trainable weight _W_ _t_ _∈_ R [3] _[n][×][k]_ :


_o_ = softmax( _W_ _t_ ( _u, v, |u −_ _v|_ ))


where _n_ is the dimension of the sentence em
beddings and _k_ the number of labels. We optimize
cross-entropy loss. This structure is depicted in
Figure 1.
**Regression Objective Function.** The cosinesimilarity between the two sentence embeddings
_u_ and _v_ is computed (Figure 2). We use meansquared-error loss as the objective function.
**Triplet Objective Function.** Given an anchor
sentence _a_, a positive sentence _p_, and a negative
sentence _n_, triplet loss tunes the network such that
the distance between _a_ and _p_ is smaller than the
distance between _a_ and _n_ . Mathematically, we
minimize the following loss function:


_max_ ( _||s_ _a_ _−_ _s_ _p_ _|| −||s_ _a_ _−_ _s_ _n_ _||_ + _ϵ,_ 0)


with _s_ _x_ the sentence embedding for _a_ / _n_ / _p_, _|| · ||_
a distance metric and margin _ϵ_ . Margin _ϵ_ ensures
that _s_ _p_ is at least _ϵ_ closer to _s_ _a_ than _s_ _n_ . As metric
we use Euclidean distance and we set _ϵ_ = 1 in our

experiments.


**3.1** **Training Details**


We train SBERT on the combination of the SNLI

(Bowman et al., 2015) and the Multi-Genre NLI


|Model|STS12|STS13|STS14|STS15|STS16|STSb|SICK-R|Avg.|
|---|---|---|---|---|---|---|---|---|
|Avg. GloVe embeddings<br>Avg. BERT embeddings<br>BERT CLS-vector<br>InferSent - Glove<br>Universal Sentence Encoder|55.14<br>38.78<br>20.16<br>52.86<br>64.49|70.66<br>57.98<br>30.01<br>66.75<br>67.80|59.73<br>57.98<br>20.09<br>62.15<br>64.61|68.25<br>63.15<br>36.88<br>72.77<br>76.83|63.66<br>61.06<br>38.08<br>66.87<br>73.18|58.02<br>46.35<br>16.50<br>68.03<br>74.92|53.76<br>58.40<br>42.63<br>65.65<br>**76.69**|61.32<br>54.81<br>29.19<br>65.01<br>71.22|
|SBERT-NLI-base<br>SBERT-NLI-large|70.97<br>72.27|76.53<br>**78.46**|73.19<br>**74.90**|79.09<br>80.99|74.30<br>76.25|77.03<br>**79.23**|72.91<br>73.75|74.89<br>76.55|
|SRoBERTa-NLI-base<br>SRoBERTa-NLI-large|71.54<br>**74.53**|72.49<br>77.00|70.80<br>73.18|78.74<br>**81.85**|73.69<br>**76.82**|77.77<br>79.10|74.46<br>74.29|74.21<br>**76.68**|


Table 1: Spearman rank correlation _ρ_ between the cosine similarity of sentence representations and the gold labels
for various Textual Similarity (STS) tasks. Performance is reported by convention as _ρ ×_ 100. STS12-STS16:
SemEval 2012-2016, STSb: STSbenchmark, SICK-R: SICK relatedness dataset.



(Williams et al., 2018) dataset. The SNLI is a collection of 570,000 sentence pairs annotated with
the labels _contradiction_, _eintailment_, and _neu-_
_tral_ . MultiNLI contains 430,000 sentence pairs
and covers a range of genres of spoken and written
text. We fine-tune SBERT with a 3-way softmaxclassifier objective function for one epoch. We
used a batch-size of 16, Adam optimizer with
learning rate 2e _−_ 5, and a linear learning rate
warm-up over 10% of the training data. Our default pooling strategy is MEAN.


**4** **Evaluation - Semantic Textual**

**Similarity**


We evaluate the performance of SBERT for common Semantic Textual Similarity (STS) tasks.
State-of-the-art methods often learn a (complex)
regression function that maps sentence embeddings to a similarity score. However, these regression functions work pair-wise and due to the combinatorial explosion those are often not scalable if
the collection of sentences reaches a certain size.

Instead, we always use cosine-similarity to compare the similarity between two sentence embeddings. We ran our experiments also with negative Manhatten and negative Euclidean distances
as similarity measures, but the results for all approaches remained roughly the same.


**4.1** **Unsupervised STS**


We evaluate the performance of SBERT for STS
without using any STS specific training data. We
use the STS tasks 2012 - 2016 (Agirre et al., 2012,
2013, 2014, 2015, 2016), the STS benchmark (Cer
et al., 2017), and the SICK-Relatedness dataset
(Marelli et al., 2014). These datasets provide labels between 0 and 5 on the semantic relatedness

of sentence pairs. We showed in (Reimers et al.,
2016) that Pearson correlation is badly suited for



STS. Instead, we compute the Spearman’s rank
correlation between the cosine-similarity of the
sentence embeddings and the gold labels. The
setup for the other sentence embedding methods
is equivalent, the similarity is computed by cosinesimilarity. The results are depicted in Table 1.
The results shows that directly using the output
of BERT leads to rather poor performances. Averaging the BERT embeddings achieves an average correlation of only 54.81, and using the CLStoken output only achieves an average correlation
of 29.19. Both are worse than computing average
GloVe embeddings.
Using the described siamese network structure
and fine-tuning mechanism substantially improves
the correlation, outperforming both InferSent and
Universal Sentence Encoder substantially. The
only dataset where SBERT performs worse than
Universal Sentence Encoder is SICK-R. Universal

Sentence Encoder was trained on various datasets,
including news, question-answer pages and discussion forums, which appears to be more suitable
to the data of SICK-R. In contrast, SBERT was
pre-trained only on Wikipedia (via BERT) and on
NLI data.

While RoBERTa was able to improve the performance for several supervised tasks, we only
observe minor difference between SBERT and

SRoBERTa for generating sentence embeddings.


**4.2** **Supervised STS**


The STS benchmark (STSb) (Cer et al., 2017) provides is a popular dataset to evaluate supervised
STS systems. The data includes 8,628 sentence
pairs from the three categories _captions_, _news_, and
_forums_ . It is divided into train (5,749), dev (1,500)
and test (1,379). BERT set a new state-of-the-art
performance on this dataset by passing both sentences to the network and using a simple regres

sion method for the output.

|Model|Spearman|
|---|---|
|_Not trained for STS_|_Not trained for STS_|
|Avg. GloVe embeddings<br>Avg. BERT embeddings<br>InferSent - GloVe<br>Universal Sentence Encoder<br>SBERT-NLI-base<br>SBERT-NLI-large|58.02<br>46.35<br>68.03<br>74.92<br>77.03<br>79.23|
|_Trained on STS benchmark dataset_|_Trained on STS benchmark dataset_|
|BERT-STSb-base<br>SBERT-STSb-base<br>SRoBERTa-STSb-base|84.30_ ±_ 0.76<br>84.67_ ±_ 0.19<br>**84.92**_ ±_ 0.34|
|BERT-STSb-large<br>SBERT-STSb-large<br>SRoBERTa-STSb-large|**85.64**_ ±_ 0.81<br>84.45_ ±_ 0.43<br>85.02_ ±_ 0.76|
|_Trained on NLI data + STS benchmark data_|_Trained on NLI data + STS benchmark data_|
|BERT-NLI-STSb-base<br>SBERT-NLI-STSb-base<br>SRoBERTa-NLI-STSb-base|**88.33**_ ±_ 0.19<br>85.35_ ±_ 0.17<br>84.79_ ±_ 0.38|
|BERT-NLI-STSb-large<br>SBERT-NLI-STSb-large<br>SRoBERTa-NLI-STSb-large|**88.77**_ ±_ 0.46<br>86.10_ ±_ 0.13<br>86.15_ ±_ 0.35|



Table 2: Evaluation on the STS benchmark test set.

BERT systems were trained with 10 random seeds and
4 epochs. SBERT was fine-tuned on the STSb dataset,
SBERT-NLI was pretrained on the NLI datasets, then
fine-tuned on the STSb dataset.


We use the training set to fine-tune SBERT using the regression objective function. At prediction time, we compute the cosine-similarity between the sentence embeddings. All systems are
trained with 10 random seeds to counter variances

(Reimers and Gurevych, 2018).
The results are depicted in Table 2. We experimented with two setups: Only training on
STSb, and first training on NLI, then training on
STSb. We observe that the later strategy leads to a
slight improvement of 1-2 points. This two-step
approach had an especially large impact for the
BERT cross-encoder, which improved the performance by 3-4 points. We do not observe a significant difference between BERT and RoBERTa.


**4.3** **Argument Facet Similarity**


We evaluate SBERT on the Argument Facet Similarity (AFS) corpus by Misra et al. (2016). The
AFS corpus annotated 6,000 sentential argument
pairs from social media dialogs on three controversial topics: _gun control_, _gay marriage_, and
_death penalty_ . The data was annotated on a scale
from 0 (“different topic”) to 5 (“completely equivalent”). The similarity notion in the AFS corpus
is fairly different to the similarity notion in the
STS datasets from SemEval. STS data is usually



descriptive, while AFS data are argumentative excerpts from dialogs. To be considered similar, arguments must not only make similar claims, but
also provide a similar reasoning. Further, the lexical gap between the sentences in AFS is much
larger. Hence, simple unsupervised methods as
well as state-of-the-art STS systems perform badly
on this dataset (Reimers et al., 2019).

We evaluate SBERT on this dataset in two sce
narios: 1) As proposed by Misra et al., we evaluate
SBERT using 10-fold cross-validation. A drawback of this evaluation setup is that it is not clear
how well approaches generalize to different topics. Hence, 2) we evaluate SBERT in a cross-topic
setup. Two topics serve for training and the approach is evaluated on the left-out topic. We repeat
this for all three topics and average the results.

SBERT is fine-tuned using the Regression Objective Function. The similarity score is computed
using cosine-similarity based on the sentence embeddings. We also provide the Pearson correlation _r_ to make the results comparable to Misra et
al. However, we showed (Reimers et al., 2016)

that Pearson correlation has some serious draw
backs and should be avoided for comparing STS
systems. The results are depicted in Table 3.

Unsupervised methods like tf-idf, average
GloVe embeddings or InferSent perform rather
badly on this dataset with low scores. Training
SBERT in the 10-fold cross-validation setup gives
a performance that is nearly on-par with BERT.

However, in the cross-topic evaluation, we observe a performance drop of SBERT by about 7
points Spearman correlation. To be considered
similar, arguments should address the same claims
and provide the same reasoning. BERT is able to
use attention to compare directly both sentences
(e.g. word-by-word comparison), while SBERT
must map individual sentences from an unseen
topic to a vector space such that arguments with
similar claims and reasons are close. This is a

much more challenging task, which appears to require more than just two topics for training to work
on-par with BERT.


**4.4** **Wikipedia Sections Distinction**


Dor et al. (2018) use Wikipedia to create a thematically fine-grained train, dev and test set for
sentence embeddings methods. Wikipedia articles are separated into distinct sections focusing
on certain aspects. Dor et al. assume that sen

|Model|r|ρ|
|---|---|---|
|_Unsupervised methods_|_Unsupervised methods_|_Unsupervised methods_|
|tf-idf<br>Avg. GloVe embeddings<br>InferSent - GloVe|46.77<br>32.40<br>27.08|42.95<br>34.00<br>26.63|
|_10-fold Cross-Validation_|_10-fold Cross-Validation_|_10-fold Cross-Validation_|
|SVR (Misra et al., 2016)<br>BERT-AFS-base<br>SBERT-AFS-base<br>BERT-AFS-large<br>SBERT-AFS-large|63.33<br>77.20<br>76.57<br>78.68<br>77.85|-<br>74.84<br>74.13<br>76.38<br>75.93|
|_Cross-Topic Evaluation_|_Cross-Topic Evaluation_|_Cross-Topic Evaluation_|
|BERT-AFS-base<br>SBERT-AFS-base<br>BERT-AFS-large<br>SBERT-AFS-large|58.49<br>52.34<br>62.02<br>53.82|57.23<br>50.65<br>60.34<br>53.10|


Table 3: Average Pearson correlation _r_ and average
Spearman’s rank correlation _ρ_ on the Argument Facet
Similarity (AFS) corpus (Misra et al., 2016). Misra et
al. proposes 10-fold cross-validation. We additionally
evaluate in a cross-topic scenario: Methods are trained
on two topics, and are evaluated on the third topic.


tences in the same section are thematically closer
than sentences in different sections. They use this
to create a large dataset of weakly labeled sentence triplets: The anchor and the positive example come from the same section, while the negative example comes from a different section of
the same article. For example, from the Alice
Arnold article: Anchor: _Arnold joined the BBC_
_Radio Drama Company in 1988._, positive: _Arnold_
_gained media attention in May 2012._, negative:
_Balding and Arnold are keen amateur golfers._

We use the dataset from Dor et al. We use the

Triplet Objective, train SBERT for one epoch on
the about 1.8 Million training triplets and evaluate
it on the 222,957 test triplets. Test triplets are from
a distinct set of Wikipedia articles. As evaluation
metric, we use accuracy: Is the positive example
closer to the anchor than the negative example?
Results are presented in Table 4. Dor et al. finetuned a BiLSTM architecture with triplet loss to
derive sentence embeddings for this dataset. As
the table shows, SBERT clearly outperforms the
BiLSTM approach by Dor et al.


**5** **Evaluation - SentEval**


SentEval (Conneau and Kiela, 2018) is a popular
toolkit to evaluate the quality of sentence embeddings. Sentence embeddings are used as features
for a logistic regression classifier. The logistic regression classifier is trained on various tasks in a
10-fold cross-validation setup and the prediction
accuracy is computed for the test-fold.



|Model|Accuracy|
|---|---|
|mean-vectors<br>skip-thoughts-CS<br>Dor et al.|0.65<br>0.62<br>0.74|
|SBERT-WikiSec-base<br>SBERT-WikiSec-large<br>SRoBERTa-WikiSec-base<br>SRoBERTa-WikiSec-large|0.8042<br>**0.8078**<br>0.7945<br>0.7973|


Table 4: Evaluation on the Wikipedia section triplets
dataset (Dor et al., 2018). SBERT trained with triplet
loss for one epoch.


The purpose of SBERT sentence embeddings
are not to be used for transfer learning for other
tasks. Here, we think fine-tuning BERT as described by Devlin et al. (2018) for new tasks is
the more suitable method, as it updates all layers
of the BERT network. However, SentEval can still
give an impression on the quality of our sentence
embeddings for various tasks.
We compare the SBERT sentence embeddings
to other sentence embeddings methods on the following seven SentEval transfer tasks:


  - **MR** : Sentiment prediction for movie reviews
snippets on a five start scale (Pang and Lee,
2005).


  - **CR** : Sentiment prediction of customer product reviews (Hu and Liu, 2004).


  - **SUBJ** : Subjectivity prediction of sentences
from movie reviews and plot summaries
(Pang and Lee, 2004).


  - **MPQA** : Phrase level opinion polarity classification from newswire (Wiebe et al., 2005).


  - **SST** : Stanford Sentiment Treebank with bi
nary labels (Socher et al., 2013).


  - **TREC** : Fine grained question-type classification from TREC (Li and Roth, 2002).


  - **MRPC** : Microsoft Research Paraphrase Corpus from parallel news sources (Dolan et al.,
2004).


The results can be found in Table 5. SBERT

is able to achieve the best performance in 5 out
of 7 tasks. The average performance increases
by about 2 percentage points compared to InferSent as well as the Universal Sentence Encoder.

Even though transfer learning is not the purpose of
SBERT, it outperforms other state-of-the-art sentence embeddings methods on this task.


|Model|MR|CR|SUBJ|MPQA|SST|TREC|MRPC|Avg.|
|---|---|---|---|---|---|---|---|---|
|Avg. GloVe embeddings<br>Avg. fast-text embeddings<br>Avg. BERT embeddings<br>BERT CLS-vector<br>InferSent - GloVe<br>Universal Sentence Encoder|77.25<br>77.96<br>78.66<br>78.68<br>81.57<br>80.09|78.30<br>79.23<br>86.25<br>84.85<br>86.54<br>85.19|91.17<br>91.68<br>94.37<br>94.21<br>92.50<br>93.98|87.85<br>87.81<br>88.66<br>88.23<br>**90.38**<br>86.70|80.18<br>82.15<br>84.40<br>84.13<br>84.18<br>86.38|83.0<br>83.6<br>92.8<br>91.4<br>88.2<br>**93.2**|72.87<br>74.49<br>69.45<br>71.13<br>75.77<br>70.14|81.52<br>82.42<br>84.94<br>84.66<br>85.59<br>85.10|
|SBERT-NLI-base<br>SBERT-NLI-large|83.64<br>**84.88**|89.43<br>**90.07**|94.39<br>**94.52**|89.86<br>90.33|88.96<br>**90.66**|89.6<br>87.4|**76.00**<br>75.94|87.41<br>**87.69**|


Table 5: Evaluation of SBERT sentence embeddings using the SentEval toolkit. SentEval evaluates sentence
embeddings on different sentence classification tasks by training a logistic regression classifier using the sentence
embeddings as features. Scores are based on a 10-fold cross-validation.



It appears that the sentence embeddings from
SBERT capture well sentiment information: We
observe large improvements for all sentiment tasks
(MR, CR, and SST) from SentEval in comparison
to InferSent and Universal Sentence Encoder.

The only dataset where SBERT is significantly
worse than Universal Sentence Encoder is the

TREC dataset. Universal Sentence Encoder was

pre-trained on question-answering data, which appears to be beneficial for the question-type classification task of the TREC dataset.
Average BERT embeddings or using the CLStoken output from a BERT network achieved bad
results for various STS tasks (Table 1), worse than
average GloVe embeddings. However, for SentEval, average BERT embeddings and the BERT
CLS-token output achieves decent results (Table 5), outperforming average GloVe embeddings.
The reason for this are the different setups. For
the STS tasks, we used cosine-similarity to estimate the similarities between sentence embed
dings. Cosine-similarity treats all dimensions
equally. In contrast, SentEval fits a logistic regression classifier to the sentence embeddings. This
allows that certain dimensions can have higher or
lower impact on the classification result.
We conclude that average BERT embeddings /
CLS-token output from BERT return sentence embeddings that are infeasible to be used with cosinesimilarity or with Manhatten / Euclidean distance.
For transfer learning, they yield slightly worse
results than InferSent or Universal Sentence En
coder. However, using the described fine-tuning
setup with a siamese network structure on NLI
datasets yields sentence embeddings that achieve
a new state-of-the-art for the SentEval toolkit.


**6** **Ablation Study**


We have demonstrated strong empirical results for
the quality of SBERT sentence embeddings. In



this section, we perform an ablation study of different aspects of SBERT in order to get a better
understanding of their relative importance.
We evaluated different pooling strategies
(MEAN, MAX, and CLS). For the classification
objective function, we evaluate different concatenation methods. For each possible configuration,
we train SBERT with 10 different random seeds

and average the performances.
The objective function (classification vs. regression) depends on the annotated dataset. For the
classification objective function, we train SBERTbase on the SNLI and the Multi-NLI dataset. For

the regression objective function, we train on the
training set of the STS benchmark dataset. Performances are measured on the development split of
the STS benchmark dataset. Results are shown in

Table 6.

|Col1|NLI|STSb|
|---|---|---|
|_Pooling Strategy_|_Pooling Strategy_|_Pooling Strategy_|
|MEAN<br>MAX<br>CLS|**80.78**<br>79.07<br>79.80|**87.44**<br>69.92<br>86.62|
|_Concatenation_|_Concatenation_|_Concatenation_|
|(_u, v_)<br>(_|u −v|_)<br>(_u ∗v_)<br>(_|u −v|, u ∗v_)<br>(_u, v, u ∗v_)<br>(_u, v, |u −v|_)<br>(_u, v, |u −v|, u ∗v_)|66.04<br>69.78<br>70.54<br>78.37<br>77.44<br>**80.78**<br>80.44|-<br>-<br>-<br>-<br>-<br>-<br>-|



Table 6: SBERT trained on NLI data with the clas
sification objective function, on the STS benchmark
(STSb) with the regression objective function. Configurations are evaluated on the development set of the
STSb using cosine-similarity and Spearman’s rank correlation. For the concatenation methods, we only report
scores with MEAN pooling strategy.


When trained with the classification objective
function on NLI data, the pooling strategy has a
rather minor impact. The impact of the concatenation mode is much larger. InferSent (Conneau


et al., 2017) and Universal Sentence Encoder (Cer
et al., 2018) both use ( _u, v, |u −_ _v|, u ∗_ _v_ ) as input
for a softmax classifier. However, in our architecture, adding the element-wise _u ∗_ _v_ decreased the
performance.
The most important component is the elementwise difference _|u −_ _v|_ . Note, that the concatenation mode is only relevant for training the softmax classifier. At inference, when predicting similarities for the STS benchmark dataset, only the
sentence embeddings _u_ and _v_ are used in combination with cosine-similarity. The element-wise
difference measures the distance between the di
mensions of the two sentence embeddings, ensuring that similar pairs are closer and dissimilar pairs
are further apart.
When trained with the regression objective
function, we observe that the pooling strategy has
a large impact. There, the MAX strategy perform
significantly worse than MEAN or CLS-token strategy. This is in contrast to (Conneau et al., 2017),
who found it beneficial for the BiLSTM-layer of
InferSent to use MAX instead of MEAN pooling.


**7** **Computational Efficiency**


Sentence embeddings need potentially be computed for Millions of sentences, hence, a high
computation speed is desired. In this section, we
compare SBERT to average GloVe embeddings,
InferSent (Conneau et al., 2017), and Universal
Sentence Encoder (Cer et al., 2018).

For our comparison we use the sentences from
the STS benchmark (Cer et al., 2017). We compute average GloVe embeddings using a simple for-loop with python dictionary lookups and
NumPy. InferSent [4] is based on PyTorch. For
Universal Sentence Encoder, we use the TensorFlow Hub version [5], which is based on TensorFlow. SBERT is based on PyTorch. For improved
computation of sentence embeddings, we implemented a smart batching strategy: Sentences with
similar lengths are grouped together and are only
padded to the longest element in a mini-batch.
This drastically reduces computational overhead
from padding tokens.

Performances were measured on a server with

Intel i7-5820K CPU @ 3.30GHz, Nvidia Tesla


4 [https://github.com/facebookresearch/](https://github.com/facebookresearch/InferSent)

[InferSent](https://github.com/facebookresearch/InferSent)

5 [https://tfhub.dev/google/](https://tfhub.dev/google/universal-sentence-encoder-large/3)
[universal-sentence-encoder-large/3](https://tfhub.dev/google/universal-sentence-encoder-large/3)



V100 GPU, CUDA 9.2 and cuDNN. The results
are depicted in Table 7.

|Model|CPU|GPU|
|---|---|---|
|Avg. GloVe embeddings<br>InferSent<br>Universal Sentence Encoder<br>SBERT-base<br>SBERT-base - smart batching|6469<br>137<br>67<br>44<br>83|-<br>1876<br>1318<br>1378<br>2042|



Table 7: Computation speed (sentences per second) of
sentence embedding methods. Higher is better.


On CPU, InferSent is about 65% faster than
SBERT. This is due to the much simpler network architecture. InferSent uses a single BiLSTM layer, while BERT uses 12 stacked transformer layers. However, an advantage of transformer networks is the computational efficiency
on GPUs. There, SBERT with smart batching
is about 9% faster than InferSent and about 55%

faster than Universal Sentence Encoder. Smart

batching achieves a speed-up of 89% on CPU and
48% on GPU. Average GloVe embeddings is obviously by a large margin the fastest method to compute sentence embeddings.


**8** **Conclusion**


We showed that BERT out-of-the-box maps sentences to a vector space that is rather unsuitable to be used with common similarity measures
like cosine-similarity. The performance for seven
STS tasks was below the performance of average
GloVe embeddings.
To overcome this shortcoming, we presented
Sentence-BERT (SBERT). SBERT fine-tunes
BERT in a siamese / triplet network architecture. We evaluated the quality on various common benchmarks, where it could achieve a significant improvement over state-of-the-art sentence embeddings methods. Replacing BERT with
RoBERTa did not yield a significant improvement
in our experiments.
SBERT is computationally efficient. On a GPU,
it is about 9% faster than InferSent and about 55%

faster than Universal Sentence Encoder. SBERT

can be used for tasks which are computationally
not feasible to be modeled with BERT. For exam
ple, clustering of 10,000 sentences with hierarchical clustering requires with BERT about 65 hours,
as around 50 Million sentence combinations must

be computed. With SBERT, we were able to reduce the effort to about 5 seconds.


**Acknowledgments**


This work has been supported by the German
Research Foundation through the German-Israeli
Project Cooperation (DIP, grant DA 1600/1-1 and
grant GU 798/17-1). It has been co-funded by the
German Federal Ministry of Education and Research (BMBF) under the promotional references
03VP02540 (ArgumenText).


**References**


Eneko Agirre, Carmen Banea, Claire Cardie, Daniel
Cer, Mona Diab, Aitor Gonzalez-Agirre, Weiwei
Guo, Inigo Lopez-Gazpio, Montse Maritxalar, Rada
Mihalcea, German Rigau, Larraitz Uria, and Janyce
[Wiebe. 2015. SemEval-2015 Task 2: Semantic Tex-](http://www.aclweb.org/anthology/S15-2045)
[tual Similarity, English, Spanish and Pilot on Inter-](http://www.aclweb.org/anthology/S15-2045)
[pretability. In](http://www.aclweb.org/anthology/S15-2045) _Proceedings of the 9th International_
_Workshop on Semantic Evaluation (SemEval 2015)_,
pages 252–263, Denver, Colorado. Association for
Computational Linguistics.


Eneko Agirre, Carmen Banea, Claire Cardie, Daniel
Cer, Mona Diab, Aitor Gonzalez-Agirre, Weiwei
Guo, Rada Mihalcea, German Rigau, and Janyce
[Wiebe. 2014. SemEval-2014 Task 10: Multilingual](https://doi.org/10.3115/v1/S14-2010)
[Semantic Textual Similarity. In](https://doi.org/10.3115/v1/S14-2010) _Proceedings of the_
_8th International Workshop on Semantic Evaluation_
_(SemEval 2014)_, pages 81–91, Dublin, Ireland. Association for Computational Linguistics.


Eneko Agirre, Carmen Banea, Daniel M. Cer, Mona T.
Diab, Aitor Gonzalez-Agirre, Rada Mihalcea, German Rigau, and Janyce Wiebe. 2016. [SemEval-](http://aclweb.org/anthology/S/S16/S16-1081.pdf)
[2016 Task 1: Semantic Textual Similarity, Mono-](http://aclweb.org/anthology/S/S16/S16-1081.pdf)
[lingual and Cross-Lingual Evaluation. In](http://aclweb.org/anthology/S/S16/S16-1081.pdf) _Proceed-_
_ings of the 10th International Workshop on Seman-_
_tic Evaluation, SemEval@NAACL-HLT 2016, San_
_Diego, CA, USA, June 16-17, 2016_, pages 497–511.


Eneko Agirre, Daniel Cer, Mona Diab, Aitor Gonzalez[Agirre, and Weiwei Guo. 2013. *SEM 2013 shared](https://www.aclweb.org/anthology/S13-1004)
[task: Semantic Textual Similarity. In](https://www.aclweb.org/anthology/S13-1004) _Second Joint_
_Conference on Lexical and Computational Seman-_
_tics (*SEM), Volume 1: Proceedings of the Main_
_Conference and the Shared Task: Semantic Textual_
_Similarity_, pages 32–43, Atlanta, Georgia, USA. Association for Computational Linguistics.


Eneko Agirre, Mona Diab, Daniel Cer, and Aitor
[Gonzalez-Agirre. 2012. SemEval-2012 Task 6: A](http://dl.acm.org/citation.cfm?id=2387636.2387697)
[Pilot on Semantic Textual Similarity. In](http://dl.acm.org/citation.cfm?id=2387636.2387697) _Proceed-_
_ings of the First Joint Conference on Lexical and_
_Computational Semantics - Volume 1: Proceedings_
_of the Main Conference and the Shared Task, and_
_Volume 2: Proceedings of the Sixth International_
_Workshop on Semantic Evaluation_, SemEval ’12,
pages 385–393, Stroudsburg, PA, USA. Association
for Computational Linguistics.



Samuel R. Bowman, Gabor Angeli, Christopher Potts,
[and Christopher D. Manning. 2015. A large anno-](https://doi.org/10.18653/v1/D15-1075)
[tated corpus for learning natural language inference.](https://doi.org/10.18653/v1/D15-1075)
In _Proceedings of the 2015 Conference on Empiri-_
_cal Methods in Natural Language Processing_, pages
632–642, Lisbon, Portugal. Association for Computational Linguistics.


Daniel Cer, Mona Diab, Eneko Agirre, Iigo LopezGazpio, and Lucia Specia. 2017. [SemEval-2017](http://arxiv.org/abs/1708.00055)
[Task 1: Semantic Textual Similarity Multilingual](http://arxiv.org/abs/1708.00055)
[and Crosslingual Focused Evaluation. In](http://arxiv.org/abs/1708.00055) _Proceed-_
_ings of the 11th International Workshop on Semantic_
_Evaluation (SemEval-2017)_, pages 1–14, Vancouver, Canada.


Daniel Cer, Yinfei Yang, Sheng-yi Kong, Nan Hua,
Nicole Limtiaco, Rhomni St. John, Noah Constant,
Mario Guajardo-Cespedes, Steve Yuan, Chris Tar,
Yun-Hsuan Sung, Brian Strope, and Ray Kurzweil.
[2018. Universal Sentence Encoder.](http://arxiv.org/abs/1803.11175) _arXiv preprint_
_arXiv:1803.11175_ .


[Alexis Conneau and Douwe Kiela. 2018. SentEval: An](https://arxiv.org/abs/1803.05449)
[Evaluation Toolkit for Universal Sentence Represen-](https://arxiv.org/abs/1803.05449)
[tations.](https://arxiv.org/abs/1803.05449) _arXiv preprint arXiv:1803.05449_ .


Alexis Conneau, Douwe Kiela, Holger Schwenk, Lo¨ıc
Barrault, and Antoine Bordes. 2017. [Supervised](https://www.aclweb.org/anthology/D17-1070)
[Learning of Universal Sentence Representations](https://www.aclweb.org/anthology/D17-1070)
[from Natural Language Inference Data. In](https://www.aclweb.org/anthology/D17-1070) _Proceed-_
_ings of the 2017 Conference on Empirical Methods_
_in Natural Language Processing_, pages 670–680,
Copenhagen, Denmark. Association for Computational Linguistics.


Jacob Devlin, Ming-Wei Chang, Kenton Lee, and
Kristina Toutanova. 2018. [BERT: Pre-training of](https://arxiv.org/abs/1810.04805)
[Deep Bidirectional Transformers for Language Un-](https://arxiv.org/abs/1810.04805)
[derstanding.](https://arxiv.org/abs/1810.04805) _arXiv preprint arXiv:1810.04805_ .


[Bill Dolan, Chris Quirk, and Chris Brockett. 2004. Un-](https://doi.org/10.3115/1220355.1220406)
[supervised Construction of Large Paraphrase Cor-](https://doi.org/10.3115/1220355.1220406)
[pora: Exploiting Massively Parallel News Sources.](https://doi.org/10.3115/1220355.1220406)
In _Proceedings of the 20th International Confer-_
_ence on Computational Linguistics_, COLING ’04,
Stroudsburg, PA, USA. Association for Computational Linguistics.


Liat Ein Dor, Yosi Mass, Alon Halfon, Elad Venezian,
Ilya Shnayderman, Ranit Aharonov, and Noam
[Slonim. 2018. Learning Thematic Similarity Metric](https://doi.org/10.18653/v1/P18-2009)
[from Article Sections Using Triplet Networks. In](https://doi.org/10.18653/v1/P18-2009)
_Proceedings of the 56th Annual Meeting of the As-_
_sociation for Computational Linguistics (Volume 2:_
_Short Papers)_, pages 49–54, Melbourne, Australia.
Association for Computational Linguistics.


Felix Hill, Kyunghyun Cho, and Anna Korhonen.
[2016. Learning Distributed Representations of Sen-](https://doi.org/10.18653/v1/N16-1162)
[tences from Unlabelled Data.](https://doi.org/10.18653/v1/N16-1162) In _Proceedings of_
_the 2016 Conference of the North American Chap-_
_ter of the Association for Computational Linguis-_
_tics: Human Language Technologies_, pages 1367–
1377, San Diego, California. Association for Computational Linguistics.


[Minqing Hu and Bing Liu. 2004. Mining and Sum-](https://doi.org/10.1145/1014052.1014073)
[marizing Customer Reviews. In](https://doi.org/10.1145/1014052.1014073) _Proceedings of the_
_Tenth ACM SIGKDD International Conference on_
_Knowledge Discovery and Data Mining_, KDD ’04,
pages 168–177, New York, NY, USA. ACM.


Samuel Humeau, Kurt Shuster, Marie-Anne Lachaux,
and Jason Weston. 2019. [Real-time Inference](http://arxiv.org/abs/1905.01969)
[in Multi-sentence Tasks with Deep Pretrained](http://arxiv.org/abs/1905.01969)
[Transformers.](http://arxiv.org/abs/1905.01969) _arXiv preprint arXiv:1905.01969_,
abs/1905.01969.


Jeff Johnson, Matthijs Douze, and Herv´e J´egou. 2017.

[Billion-scale similarity search with GPUs.](https://arxiv.org/abs/1702.08734) _arXiv_
_preprint arXiv:1702.08734_ .


Ryan Kiros, Yukun Zhu, Ruslan R Salakhutdinov,
Richard Zemel, Raquel Urtasun, Antonio Torralba,
[and Sanja Fidler. 2015. Skip-Thought Vectors. In](http://papers.nips.cc/paper/5950-skip-thought-vectors.pdf)
C. Cortes, N. D. Lawrence, D. D. Lee, M. Sugiyama,
and R. Garnett, editors, _Advances in Neural Infor-_
_mation Processing Systems 28_, pages 3294–3302.
Curran Associates, Inc.


[Xin Li and Dan Roth. 2002. Learning Question Classi-](https://doi.org/10.3115/1072228.1072378)
[fiers. In](https://doi.org/10.3115/1072228.1072378) _Proceedings of the 19th International Con-_
_ference on Computational Linguistics - Volume 1_,
COLING ’02, pages 1–7, Stroudsburg, PA, USA.
Association for Computational Linguistics.


Yinhan Liu, Myle Ott, Naman Goyal, Jingfei Du, Mandar Joshi, Danqi Chen, Omer Levy, Mike Lewis,
Luke Zettlemoyer, and Veselin Stoyanov. 2019.
[RoBERTa: A Robustly Optimized BERT Pretrain-](http://arxiv.org/abs/1907.11692)
[ing Approach.](http://arxiv.org/abs/1907.11692) _arXiv preprint arXiv:1907.11692_ .


Marco Marelli, Stefano Menini, Marco Baroni, Luisa
Bentivogli, Raffaella Bernardi, and Roberto Zamparelli. 2014. [A SICK cure for the evaluation of](http://www.lrec-conf.org/proceedings/lrec2014/pdf/363_Paper.pdf)
[compositional distributional semantic models.](http://www.lrec-conf.org/proceedings/lrec2014/pdf/363_Paper.pdf) In
_Proceedings of the Ninth International Conference_
_on Language Resources and Evaluation (LREC’14)_,
pages 216–223, Reykjavik, Iceland. European Language Resources Association (ELRA).


Chandler May, Alex Wang, Shikha Bordia, Samuel R.
Bowman, and Rachel Rudinger. 2019. [On Mea-](http://arxiv.org/abs/1903.10561)
[suring Social Biases in Sentence Encoders.](http://arxiv.org/abs/1903.10561) _arXiv_
_preprint arXiv:1903.10561_ .


Amita Misra, Brian Ecker, and Marilyn A. Walker.
2016. [Measuring the Similarity of Sentential Ar-](http://aclweb.org/anthology/W/W16/W16-3636.pdf)
[guments in Dialogue. In](http://aclweb.org/anthology/W/W16/W16-3636.pdf) _Proceedings of the SIG-_
_DIAL 2016 Conference, The 17th Annual Meeting_
_of the Special Interest Group on Discourse and Di-_
_alogue, 13-15 September 2016, Los Angeles, CA,_
_USA_, pages 276–287.


[Bo Pang and Lillian Lee. 2004. A Sentimental Educa-](https://doi.org/10.3115/1218955.1218990)
[tion: Sentiment Analysis Using Subjectivity Sum-](https://doi.org/10.3115/1218955.1218990)
[marization Based on Minimum Cuts. In](https://doi.org/10.3115/1218955.1218990) _Proceed-_
_ings of the 42nd Meeting of the Association for_
_Computational Linguistics (ACL’04), Main Volume_,
pages 271–278, Barcelona, Spain.



[Bo Pang and Lillian Lee. 2005. Seeing Stars: Exploit-](https://doi.org/10.3115/1219840.1219855)
[ing Class Relationships for Sentiment Categoriza-](https://doi.org/10.3115/1219840.1219855)
[tion with Respect to Rating Scales. In](https://doi.org/10.3115/1219840.1219855) _Proceedings_
_of the 43rd Annual Meeting of the Association for_
_Computational Linguistics (ACL’05)_, pages 115–
124, Ann Arbor, Michigan. Association for Computational Linguistics.


Jeffrey Pennington, Richard Socher, and Christo[pher D. Manning. 2014. GloVe: Global Vectors for](https://www.aclweb.org/anthology/D14-1162)
[Word Representation. In](https://www.aclweb.org/anthology/D14-1162) _Empirical Methods in Nat-_
_ural Language Processing (EMNLP)_, pages 1532–
1543.


Yifan Qiao, Chenyan Xiong, Zheng-Hao Liu, and
Zhiyuan Liu. 2019. [Understanding the Be-](http://arxiv.org/abs/1904.07531)
[haviors of BERT in Ranking.](http://arxiv.org/abs/1904.07531) _arXiv preprint_
_arXiv:1904.07531_ .


Nils Reimers, Philip Beyer, and Iryna Gurevych. 2016.

[Task-Oriented Intrinsic Evaluation of Semantic Tex-](https://www.aclweb.org/anthology/C16-1009)
[tual Similarity.](https://www.aclweb.org/anthology/C16-1009) In _Proceedings of the 26th Inter-_
_national Conference on Computational Linguistics_
_(COLING)_, pages 87–96.


[Nils Reimers and Iryna Gurevych. 2018. Why Com-](http://arxiv.org/abs/1803.09578)
[paring Single Performance Scores Does Not Al-](http://arxiv.org/abs/1803.09578)
[low to Draw Conclusions About Machine Learn-](http://arxiv.org/abs/1803.09578)
[ing Approaches.](http://arxiv.org/abs/1803.09578) _arXiv preprint arXiv:1803.09578_,
abs/1803.09578.


Nils Reimers, Benjamin Schiller, Tilman Beck, Johannes Daxenberger, Christian Stab, and Iryna
Gurevych. 2019. [Classification and Clustering of](https://www.aclweb.org/anthology/P19-1054)
[Arguments with Contextualized Word Embeddings.](https://www.aclweb.org/anthology/P19-1054)
In _Proceedings of the 57th Annual Meeting of the As-_
_sociation for Computational Linguistics_, pages 567–
578, Florence, Italy. Association for Computational
Linguistics.


Florian Schroff, Dmitry Kalenichenko, and James
[Philbin. 2015. FaceNet: A Unified Embedding for](http://arxiv.org/abs/1503.03832)
[Face Recognition and Clustering.](http://arxiv.org/abs/1503.03832) _arXiv preprint_
_arXiv:1503.03832_, abs/1503.03832.


Richard Socher, Alex Perelygin, Jean Wu, Jason
Chuang, Christopher D. Manning, Andrew Ng, and
[Christopher Potts. 2013. Recursive Deep Models for](https://www.aclweb.org/anthology/D13-1170)
[Semantic Compositionality Over a Sentiment Tree-](https://www.aclweb.org/anthology/D13-1170)
[bank.](https://www.aclweb.org/anthology/D13-1170) In _Proceedings of the 2013 Conference on_
_Empirical Methods in Natural Language Process-_
_ing_, pages 1631–1642, Seattle, Washington, USA.
Association for Computational Linguistics.


Ashish Vaswani, Noam Shazeer, Niki Parmar, Jakob
Uszkoreit, Llion Jones, Aidan N Gomez, Łukasz
[Kaiser, and Illia Polosukhin. 2017. Attention is All](http://papers.nips.cc/paper/7181-attention-is-all-you-need.pdf)
[you Need. In I. Guyon, U. V. Luxburg, S. Bengio,](http://papers.nips.cc/paper/7181-attention-is-all-you-need.pdf)
H. Wallach, R. Fergus, S. Vishwanathan, and R. Garnett, editors, _Advances in Neural Information Pro-_
_cessing Systems 30_, pages 5998–6008.


Janyce Wiebe, Theresa Wilson, and Claire Cardie.
2005. [Annotating Expressions of Opinions and](https://doi.org/10.1007/s10579-005-7880-9)
[Emotions in Language.](https://doi.org/10.1007/s10579-005-7880-9) _Language Resources and_
_Evaluation_, 39(2):165–210.


Adina Williams, Nikita Nangia, and Samuel Bowman.
2018. [A Broad-Coverage Challenge Corpus for](http://aclweb.org/anthology/N18-1101)
[Sentence Understanding through Inference. In](http://aclweb.org/anthology/N18-1101) _Pro-_
_ceedings of the 2018 Conference of the North Amer-_
_ican Chapter of the Association for Computational_
_Linguistics: Human Language Technologies, Vol-_
_ume 1 (Long Papers)_, pages 1112–1122. Association
for Computational Linguistics.


Yinfei Yang, Steve Yuan, Daniel Cer, Sheng-Yi Kong,
Noah Constant, Petr Pilar, Heming Ge, Yun-hsuan
Sung, Brian Strope, and Ray Kurzweil. 2018.
[Learning Semantic Textual Similarity from Conver-](https://www.aclweb.org/anthology/W18-3022)
[sations.](https://www.aclweb.org/anthology/W18-3022) In _Proceedings of The Third Workshop_
_on Representation Learning for NLP_, pages 164–
174, Melbourne, Australia. Association for Computational Linguistics.


Zhilin Yang, Zihang Dai, Yiming Yang, Jaime G.
Carbonell, Ruslan Salakhutdinov, and Quoc V. Le.
[2019. XLNet: Generalized Autoregressive Pretrain-](http://arxiv.org/abs/1906.08237)
[ing for Language Understanding.](http://arxiv.org/abs/1906.08237) _arXiv preprint_
_arXiv:1906.08237_, abs/1906.08237.


Tianyi Zhang, Varsha Kishore, Felix Wu, Kilian Q.
Weinberger, and Yoav Artzi. 2019. [BERTScore:](http://arxiv.org/abs/1904.09675)
[Evaluating Text Generation with BERT.](http://arxiv.org/abs/1904.09675) _arXiv_
_preprint arXiv:1904.09675_ .


