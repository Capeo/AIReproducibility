function mcc = MCC(false_negatives, false_positives, nr_positives, nr_negatives)
    mcc = (1 - ((false_negatives / nr_positives) + (false_positives / nr_negatives))) / sqrt((1 + ((false_positives - false_negatives) / nr_positives)) * (1 + ((false_negatives - false_positives) / nr_negatives)));
end

