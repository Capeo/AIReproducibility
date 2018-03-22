function optimized = OptimizeImbalance(training_set, positive_probs, positive_intersect_probs, negatives_probs, negatives_intersect_probs, ihts_method)
    positive_samples = [];
    negative_samples = [];
    
    % Use KNNC to clean negative samples
    for i=1:size(training_set,2)
        if training_set(2,i) == 0
            current_col = training_set(:,i);
            current_col_exclude_class = transpose(current_col([1:0 3:end]));
            training_exclude_class = transpose(training_set([1:0 3:end],:));
            
            [distances, neighbors] = KNN(training_exclude_class, current_col_exclude_class, 3, i);
            
            nearest_neighbors = training_set(:,neighbors);
            positive_neighbors = 0;
            for j=1:size(nearest_neighbors, 2)
                if nearest_neighbors(2,j) == 1
                    positive_neighbors = positive_neighbors + 1;
                end
            end
            if positive_neighbors == 0
                negative_samples = [negative_samples training_set(:,i)];
            end
        else
            positive_samples = [positive_samples training_set(:,i)];
        end
    end
    
    % Insert hypothetical positive samples
    if strcmp(ihts_method, "ihts")
        for i=1:(size(negative_samples,2) - size(positive_samples,2))
            new_sample = IHTS(positive_probs, positive_intersect_probs, negatives_probs, negatives_intersect_probs);
            positive_samples = [positive_samples new_sample];
        end
    elseif strcmp(ihts_method, "ihts_simple")
        for i=1:(size(negative_samples,2) - size(positive_samples,2))
            new_sample = IHTSSimple(positive_probs, positive_intersect_probs, negatives_probs, negatives_intersect_probs);
            positive_samples = [positive_samples new_sample];
        end
    elseif strcmp(ihts_method, "ihts_smote")
        N = round((size(negative_samples,2) / size(positive_samples,2)) + 1) * 100;
        new_samples = IHTSSmote(positive_samples, negative_samples, N, 5);
        n = size(new_samples, 2);
        shuffle = randsample(n,n);
        new_samples = new_samples(:,shuffle);
        dif = size(negative_samples,2) - size(positive_samples,2);
        new_samples = new_samples(:,1:dif);
        positive_samples = [positive_samples new_samples];
    end
    
    disp(size(positive_samples, 2))
    disp(size(negative_samples, 2))
    
    optimized = [positive_samples negative_samples];
end

