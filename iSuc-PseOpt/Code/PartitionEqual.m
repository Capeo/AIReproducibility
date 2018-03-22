function partitions = PartitionEqual(samples, k)
    nr_positives = 0;
    nr_negatives = 0;
    
    for i=1:size(samples,2)
        if samples(2,i) == 1
            nr_positives = nr_positives + 1;
        else
            nr_negatives = nr_negatives + 1;
        end
    end
    
    positive_partitions = [];
    negative_partitions = [];
    for i=1:size(samples,2)
        if samples(2,i) == 1
            partition_found = false;
            while (~partition_found)
                r = randi(k);
                if length(positive_partitions) < r
                    new_partition = [samples(:,i)];
                    positive_partitions = [positive_partitions; {new_partition}];
                    partition_found = true;
                else
                    if size(positive_partitions{r}, 2) < nr_positives / k
                        positive_partitions{r} = [positive_partitions{r} samples(:,i)];
                        partition_found = true;
                    end
                end
            end
        else
            partition_found = false;
            while (~partition_found)
                r = randi(k);
                if length(negative_partitions) < r
                    new_partition = [samples(:,i)];
                    negative_partitions = [negative_partitions; {new_partition}];
                    partition_found = true;
                else
                    if size(negative_partitions{r}, 2) < nr_negatives / k
                        negative_partitions{r} = [negative_partitions{r} samples(:,i)];
                        partition_found = true;
                    end
                end
            end
        end
    end
    
    partitions = [];
    for i=1:k
       combined = [positive_partitions{i} negative_partitions{i}];
       partitions = [partitions; {combined}];
    end
end

