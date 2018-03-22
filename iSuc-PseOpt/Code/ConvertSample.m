function converted = ConvertSample(sample, id, class, positive_probs, positive_intersect_probs, negatives_probs, negatives_intersect_probs)
    amino_acids = 'ACDEFGHIKLMNPQRSTVWY';
    
    converted = zeros(32,1);
    converted(1) = id;
    converted(2) = class;
    
    % Convert left handside
    for j=15:-1:1
        prob = 0.0;
        c = sample(j);
        
        if c == 'X'
            sample = ReplaceX(sample, j, class, positive_probs, positive_intersect_probs, negatives_probs, negatives_intersect_probs);
            index = strfind(amino_acids, sample(j));
        else
            index = strfind(amino_acids, c);
        end
        
        if j == 15
            prob = positive_probs(j, index) - negatives_probs(j, index);
        else
            m = j + 1;
            c2 = sample(m);
            
            index2 = strfind(amino_acids,c2);
            prob_pos = positive_intersect_probs(j, index, index2) / positive_probs(m, index2);
            prob_neg = negatives_intersect_probs(j, index, index2) / negatives_probs(m, index2);
            if isnan(prob_pos)
                prob_pos = 0.0;
            end
            if isnan(prob_neg)
                prob_neg = 0.0;
            end
            prob = prob_pos - prob_neg;
        end
        converted(j+2) = prob;
    end
    
    % Convert right handside
    for j=17:31
        prob = 0.0;
        c = sample(j);
        
        if c == 'X'
            sample = ReplaceX(sample, j, class, positive_probs, positive_intersect_probs, negatives_probs, negatives_intersect_probs);
            index = strfind(amino_acids, sample(j));
        else
            index = strfind(amino_acids, c);
        end
        
        if j == 17
            prob = positive_probs(j, index) - negatives_probs(j, index);
        else
            m = j - 1;
            c2 = sample(m);
            
            index2 = strfind(amino_acids,c2);
            prob_pos = positive_intersect_probs(j, index, index2) / positive_probs(m, index2);
            prob_neg = negatives_intersect_probs(j, index, index2) / negatives_probs(m, index2);
            if isnan(prob_pos)
                prob_pos = 0.0;
            end
            if isnan(prob_neg)
                prob_neg = 0.0;
            end
            prob = prob_pos - prob_neg;
        end
        converted(j+1) = prob;
    end
end

function sample = ReplaceX(sample, position, class, positive_probs, positive_intersect_probs, negatives_probs, negatives_intersect_probs)
    amino_acids = 'ACDEFGHIKLMNPQRSTVWY';
    most_likely_char = '';
    prob = 0;
    if position == 15 || position == 17
        if class == 1
            probs = positive_probs(position,:);
        else
            probs = negatives_probs(position,:);
        end
    else
        if position < 15
            index = position + 1;
        else
            index = position - 1;
        end
        c = sample(index);
        index2 = strfind(amino_acids, c);
        if class == 1
            probs = positive_intersect_probs(position,:,index2);
        else
            probs = negatives_intersect_probs(position,:,index2);
        end
    end

    for i=1:length(probs)
        if probs(i) > prob
            most_likely_char = amino_acids(i);
            prob = probs(i);
        end
    end
    sample(position) = most_likely_char;
end

