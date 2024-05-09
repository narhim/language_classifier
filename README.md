# language_classifier
## Directories
### Review
Contains the latex template as well as the compiled pdf that reviews Socher et al. (2013).

### Data
Contains the data for training and testing the language classifier, which was obtained from the [Discriminating between Similar Languages 2015 Task](http://ttg.uni-saarland.de/lt4vardial2015/dsl.html). All READMEs in this directory are as in the source. The subsets are the following:
1. **train.txt**: training set
2. **dev.txt**: development set
3. **test.txt**: test set- No gold labels.
4. **test-none.txt**: test set with no name entities. As the previous one, no gold labels.

### Src
Contains the language classifier, an implementation in Python of a Markov Model which combines information from Padró & Padró (2004), Xafopoulos et al. (2004), and Boodidhi (2011). Briefly put, the model considers the probabilities of unigrams and bigrams. Unigrams are single characters after some filtering and represent the initial probability. Bigrams are two consecutive characters after some have been filtered, and represent the transitional probabilities. 

### Results
Contains the tsv with the different results from running the language classifier. Specifically:
1. **dev_precision_accuracy.tsv**: precision and accuracy scores for the development set.
2. **dev_recall.tsv**: recall scores for the development set.
3. **dev.tsv**: each sentence from the development set with its gold and predicted labels.
4. **test.tsv**: each sentences from the test set with its predicted label.
5. **test_none.tsv**: each sentence from the test set with no name entities with its predicted label.


## References
Socher, R., Perelygin, A., Wu, J., Chuang, J., Manning, C. D., Ng, A. Y., & Potts, C. (2013, October). Recursive deep models for semantic compositionality over a sentiment treebank. In Proceedings of the 2013 conference on empirical methods in natural language processing (pp. 1631-1642).
Padró, M., & Padró, L. (2004). Comparing methods for language identification. Procesamiento del lenguaje natural, 33.
Xafopoulos, A., Kotropoulos, C., Almpanidis, G., & Pitas, I. (2004). Language identification in web documents using discrete HMMs. Pattern recognition, 37(3), 583-594.
Boodidhi, Sweatha, "Using smoothing techniques to improve the performance of Hidden Markov’s Model"
(2011). UNLV Theses, Dissertations, Professional Papers, and Capstones. 1007