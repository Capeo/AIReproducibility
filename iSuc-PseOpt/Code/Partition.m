function partitions = Partition(samples, n)
    partition_size = size(samples, 2) / n;
    columns = [1:1:size(samples,2)];
    partitioning = randperm(numel(columns));
    indexes = [0:partition_size:size(samples,2)+1];
    partitions = [];
    for i = 1:n
        subset = samples(:,partitioning(indexes(i)+1:indexes(i+1)));
        partitions = [partitions; {subset}];
    end
end

