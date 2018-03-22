function acc = Acc(false_negatives, false_positives, nr_positives, nr_negatives)
    acc = 1 - ((false_negatives + false_positives) / (nr_positives + nr_negatives));
end

