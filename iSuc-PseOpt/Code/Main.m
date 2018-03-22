% Input arguments
random_seed = 1;
input_positive_instances_file = '../Data/Positive.txt';
input_negative_instances_file = '../Data/Negative.txt';
output_folder = '../Results';
K = 6; % Tested with 6, 8, and 10
ihts_method = "ihts_smote"; % Alternatives: "ihts", "ihts_simple", and "ihts_smote"

% Set random seed
rng(random_seed);

% Read data
format = '%s %s %s';

positives_file = fopen(input_positive_instances_file, 'r');
negatives_file = fopen(input_negative_instances_file, 'r');

positives = textscan(positives_file, format);
negatives = textscan(negatives_file, format);

fclose(positives_file);
fclose(negatives_file);

% Convert peptide
[converted, positive_probs, positive_intersect_probs, negatives_probs, negatives_intersect_probs] = Convert(positives{3}, negatives{3});

% Partition data
partitions = PartitionEqual(converted, K);

sn_sum = 0;
sp_sum = 0;
acc_sum = 0;
mcc_sum = 0;

% For each set
for i = 1:length(partitions)
    output_path = strcat(output_folder, '/K', num2str(K), '/', num2str(i), '/');
    
    % Partition into training and test
    test_set = partitions{i};
    training_set = [];
    for j = 1:length(partitions)
        if j ~= i
            training_set = [training_set partitions{j}];
        end
    end

    % Save ids' of training instances
    ids = transpose(training_set(1,:));
    training_file = strcat(output_path, 'training.csv');
    dlmwrite(training_file, ids);
    
    % Optimize imbalance
    optimized_training_set = OptimizeImbalance(training_set, positive_probs, positive_intersect_probs, negatives_probs, negatives_intersect_probs, ihts_method);
    
    % Train Random Forest model
    classes = transpose(optimized_training_set(2,:));
    optimized_training_set(1,:) = [];
    optimized_training_set(1,:) = [];
    observations = transpose(optimized_training_set);
    model = classRF_train(observations, classes);

    % Calculate iSuc-Pseopt predictor
    test_ids = transpose(test_set(1,:));
    test_classes = transpose(test_set(2,:));
    test_set(1,:) = [];
    test_set(1,:) = [];
    test_observations = transpose(test_set);
    [Y_new, votes, prediction_per_tree] = classRF_predict(test_observations, model);

    % Save results
    results = [test_ids Y_new];
    results_file = strcat(output_path, 'results.csv');
    dlmwrite(results_file, results, 'delimiter', ';');
    
    % Calculate metrics
    nr_positives = 0;
    nr_negatives = 0;
    false_negatives = 0;
    false_positives = 0;
    for j=1:length(test_classes)
        if test_classes(j) == 1
            nr_positives = nr_positives + 1;
        elseif test_classes(j) == 0
            nr_negatives = nr_negatives + 1;
        end
        if test_classes(j) == 1 && Y_new(j) == 0
            false_negatives = false_negatives + 1;
        end
        if test_classes(j) == 0 && Y_new(j) == 1
            false_positives = false_positives + 1;
        end
    end
    sn = Sn(false_negatives, nr_positives);
    sp = Sp(false_positives, nr_negatives);
    acc = Acc(false_negatives, false_positives, nr_positives, nr_negatives);
    mcc = MCC(false_negatives, false_positives, nr_positives, nr_negatives);
    sn_sum = sn_sum + sn;
    sp_sum = sp_sum + sp;
    acc_sum = acc_sum + acc;
    mcc_sum = mcc_sum + mcc;
end

% Average metrics
sn_average = sn_sum / length(partitions);
sp_average = sp_sum / length(partitions);
acc_average = acc_sum / length(partitions);
mcc_average = mcc_sum / length(partitions);

results = [sn_average sp_average acc_average mcc_average]