function [converted, positive_probs, positive_intersect_probs, negatives_probs, negatives_intersect_probs] = Convert(positives, negatives)
    amino_acids = 'ACDEFGHIKLMNPQRSTVWY';

    % Calculate probabilities for positive dataset
    nr_acids = length(amino_acids);
    positive_counts = zeros(31, nr_acids);
    positive_intersect_counts = zeros(31, nr_acids, nr_acids);
    for i = 1:length(positives)
        str = positives{i};
        for j = 1:31
            if j ~= 16
                c = str(j);
                if c == 'X'
                    for k=1:nr_acids
                        positive_counts(j, k) = positive_counts(j, k) + (1/nr_acids);
                    end
                else
                    index = strfind(amino_acids,c);
                    positive_counts(j, index) = positive_counts(j, index) + 1;
                end
                
                if j < 16
                    m = j+1;
                else
                    m = j-1;
                end
                c2 = str(m);
                if c2 == 'X'
                    for k=1:nr_acids
                        positive_intersect_counts(j, index, k) = positive_intersect_counts(j, index, k) + (1/nr_acids);
                    end
                else
                    index2 = strfind(amino_acids, c2);
                    positive_intersect_counts(j, index, index2) = positive_intersect_counts(j, index, index2) + 1;
                end
                
            end
        end
    end
    positive_probs = positive_counts./length(positives);
    positive_intersect_probs = positive_intersect_counts./length(positives);
    
    % Calculate probabilities for negative dataset
    negatives_counts = zeros(31,nr_acids);
    negatives_intersect_counts = zeros(31,nr_acids,nr_acids);
    for i = 1:length(negatives)
        str = negatives{i};
        for j = 1:31
            if j ~= 16
                c = str(j);
                if c == 'X'
                    for k=1:nr_acids
                        negatives_counts(j, index) = negatives_counts(j, index) + (1/nr_acids);
                    end
                else
                    index = strfind(amino_acids,c);
                    negatives_counts(j, index) = negatives_counts(j, index) + 1;
                end
                
                if j < 16
                    m = j+1;
                else
                    m = j-1;
                end
                c2 = str(m);
                if c2 == 'X'
                    for k=1:nr_acids
                        negatives_intersect_counts(j, index, k) = negatives_intersect_counts(j, index, k) + (1/nr_acids);
                    end
                else
                    index2 = strfind(amino_acids, c2);
                    negatives_intersect_counts(j, index, index2) = negatives_intersect_counts(j, index, index2) + 1;
                end
            end
        end
    end
    negatives_probs = negatives_counts./length(negatives);
    negatives_intersect_probs = negatives_intersect_counts./length(negatives);
    
    % Convert each sample
    positive_converted = [];
    for i = 1:length(positives)
        str = positives{i};
        converted = ConvertSample(str, i, 1, positive_probs, positive_intersect_probs, negatives_probs, negatives_intersect_probs);
        positive_converted = [positive_converted converted];
    end
    
    negative_converted = [];
    for i = 1:length(negatives)
        str = negatives{i};
        id = length(positives) + i;
        converted = ConvertSample(str, id, 0, positive_probs, positive_intersect_probs, negatives_probs, negatives_intersect_probs);
        negative_converted = [negative_converted converted];
    end
    
    converted = [positive_converted negative_converted];
end