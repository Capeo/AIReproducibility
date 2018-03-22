function new_sample = IHTSSimple(positive_probs, positive_intersect_probs, negatives_probs, negatives_intersect_probs)
    amino_acids = 'ACDEFGHIKLMNPQRSTVWY';
    
    sample = '';
    for j=1:31
        if j ~= 16
            probs = positive_probs(j,:);
            r = rand;
            total = 0.0;
            for k=1:length(amino_acids)
                if probs(k) ~= 0 && r >= total && r <= total + probs(k)
                    sample = strcat(sample, amino_acids(k));
                    break;
                else
                    total = total + probs(k);
                end
            end
        else
            sample = strcat(sample, 'K');
        end
    end
    new_sample = ConvertSample(sample, 0, 1, positive_probs, positive_intersect_probs, negatives_probs, negatives_intersect_probs);
end

