function new_sample = IHTS(positive_probs, positive_intersect_probs, negatives_probs, negatives_intersect_probs)
    amino_acids = 'ACDEFGHIKLMNPQRSTVWY';
    
    sample = 'K';
    for j=15:-1:1
        index1 = j;
        if index1 == 15
            probs = positive_probs(index1,:);
        else
            c = sample(1);
            index = strfind(amino_acids, c);
            intersect = positive_intersect_probs(index1,:,index);
            probs = intersect ./ positive_probs(index1+1, index);
            probs(isnan(probs))=0;
        end
        
        c1 = '';
        r = rand;
        total = 0.0;
        for k=1:length(amino_acids)
            if probs(k) ~= 0 && r >= total && r <= total + probs(k)
                c1 = amino_acids(k);
                break;
            else
                total = total + probs(k);
            end
        end
        
        index2 = 32 - j;
        if index2 == 17
            probs = positive_probs(index2,:);
        else
            c = sample(end);
            index = strfind(amino_acids, c);
            intersect = positive_intersect_probs(index2,:,index);
            probs = intersect ./ positive_probs(index2-1, index);
            probs(isnan(probs))=0;
        end
        
        c2 = '';
        r = rand;
        total = 0.0;
        for k=1:length(amino_acids)
            if probs(k) ~= 0 && r >= total && r <= total + probs(k)
                c2 = amino_acids(k);
                break;
            else
                total = total + probs(k);
            end
        end
        
        sample = strcat(c1, sample, c2);
        
    end
    new_sample = ConvertSample(sample, 0, 1, positive_probs, positive_intersect_probs, negatives_probs, negatives_intersect_probs);
end

