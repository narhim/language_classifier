import extractfeatures as ef

features_class = ef.extract_features("data/train_dev/train.txt")
ngrams_list = features_class._build_ngrams()
