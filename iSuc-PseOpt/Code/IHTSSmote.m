function new_samples = IHTSSmote(positive_samples, negative_samples, N, k)
    N = N / 100;
    original_samples = [positive_samples negative_samples];
    new_samples = [];
    for i=1:size(positive_samples, 2)
        current_col = positive_samples(:,i);
        current_exclude_class = transpose(current_col([1:0 3:end]));
        original_exclude_class = transpose(original_samples([1:0 3:end],:));
        [distances, neighbors] = KNN(original_exclude_class, current_exclude_class, k, i);
        
        % Populate
        count = N;
        while (count ~= 0)
            nn = randi(k);
            new_sample = [0 1];
            for j=3:32
                dif = original_samples(j, neighbors(nn)) - original_samples(j,i);
                gap = rand;
                value = original_samples(j,i) + gap * dif;
                new_sample = [new_sample value];
            end
            new_sample = transpose(new_sample);
            new_samples = [new_samples new_sample];
            count = count - 1;
        end
    end
end