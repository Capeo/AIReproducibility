function [distances, neighbors] = KNN(training_set, observation, k, original_index)
    best_distances = ones(1,k) .* 1000;
    neighbors = zeros(1,k);
    distances = pdist2(observation, training_set, 'cosine');
    for j=1:size(training_set,1)
        if j ~= original_index
            distance = distances(j);
            if distance < max(best_distances)
                index = find(best_distances==max(best_distances));
                neighbors(index(1)) = j;
                best_distances(index(1)) = distance;
            end
        end
    end
    distances = best_distances;
end

