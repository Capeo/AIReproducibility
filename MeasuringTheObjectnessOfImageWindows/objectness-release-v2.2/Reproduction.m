% Input arguments
test_file = '../Data/Testset/test.txt';
output_dir = '../Results/VOC2007Test/';
image_dir = '../Data/VOC2007/Test/JPEGImages/';
annotations_dir = '../Data/VOC2007/Test/Annotations/';
max_windows = 1000;
random_seed = 1;

rng(random_seed);

% Read list of test files
test_file = fopen(test_file, 'r');
format_spec = '%f';
test_data = fscanf(test_file, format_spec);
fclose(test_file);

% Set parameters
nr_files = length(test_data);
params = defaultParams();
stepVector = [10 100];

auc = staticNrWindows(max_windows, nr_files, test_data, params, image_dir, annotations_dir, output_dir)

% Run objectness with fixed number of windows
function auc = staticNrWindows(nr_windows, nr_files, test_data, params, image_dir, annotations_dir, output_dir)
    total_nr_objects = 0;

    % Initialize DR - Percentage of objects covered by set of windows
    DR = containers.Map('KeyType','double','ValueType','double');
    for i=1:nr_windows
        DR(i) = 0;
    end

    output_file_path = strcat(output_dir, 'VOC2007Test.csv');
    output_file = fopen(output_file_path, 'w');
    
    % For each image
    for i=1:nr_files
        disp(i);
        id = num2str(test_data(i));
        % Pad file name
        len = length(id);
        if len == 1
            name = strcat('00000', id);
        elseif len == 2
            name = strcat('0000', id);
        elseif len == 3
            name = strcat('000', id);
        elseif len == 4
            name = strcat('00', id);
        elseif len == 5
            name = strcat('0', id);
        else
            name = id;
        end

        % Read image
        image = imread(strcat(image_dir, name, '.jpg'));

        % Initialize DR for the current file
        file_DR = containers.Map('KeyType','double','ValueType','double');
        for j = 1:nr_windows
            file_DR(j) = 0;
        end

        % Run objectness, returning a set of boxes/windows
        boxes = runObjectness(image, nr_windows, params);

        % Write results to file
        format_spec = "(%f,%f,%f,%f,%f)";
        formatted = compose(format_spec, boxes);
        list_string = "[";
        for j=1:size(formatted, 1)
            list_string = strcat(list_string, formatted(j));
            if j < size(formatted, 1)
                list_string = strcat(list_string, ",");
            end
        end
        list_string = strcat(list_string, "]");
        fprintf(output_file, '%s;%s\n', [name list_string]);
        
        % Open XML file for image containing ground truths
        xml_file_name = strcat(name, '.xml');
        xml_file_path = fullfile(annotations_dir, xml_file_name);
        xml = xmlread(xml_file_path);
        objects = xml.getElementsByTagName('object');
        nr_objects = objects.getLength;
        
        % For each ground truth object
        for j = 0:nr_objects-1
            % Check if object is difficult
            object = objects.item(j);
            difficult = str2double(object.getElementsByTagName('difficult').item(0).getFirstChild.getData);
            if (difficult == 0)
                total_nr_objects = total_nr_objects + 1;
                
                % Find object boundaries
                box = object.getElementsByTagName('bndbox').item(0);
                xmin = str2double(box.getElementsByTagName('xmin').item(0).getFirstChild.getData);
                ymin = str2double(box.getElementsByTagName('ymin').item(0).getFirstChild.getData);
                xmax = str2double(box.getElementsByTagName('xmax').item(0).getFirstChild.getData);
                ymax = str2double(box.getElementsByTagName('ymax').item(0).getFirstChild.getData);
                bounds = [xmin ymin xmax ymax];

                % For each box found by runObjectness
                for k = 1:size(boxes,1)
                    % Compute pascal score of object and box to determine if
                    % object covered by box. Set boundary of 0.5
                    score = computePascalScore(boxes(k,:),bounds);
                    if score >= 0.5
                        % Record that object can be found with k number of
                        % boxes, and any number of boxes above k
                        for l=k:nr_windows
                            file_DR(l) = file_DR(l) + 1;
                        end
                        break;
                    end
                end 
            end
        end

        % Add the DR of the file to total DR score
        for j = 1:nr_windows
            DR(j) = DR(j) + file_DR(j);
        end
    end

    fclose(output_file);
    
    % Log normalize the x-axis
    normalizedx = [];
    for i=1:nr_windows
        normalizedx = [normalizedx; log10(i)/log10(nr_windows)];
    end

    key_set = keys(DR);
    value_set = values(DR);
    x = cell2mat(key_set);
    y = cell2mat(value_set)./total_nr_objects;

    disp("Objects:")
    disp(total_nr_objects);
    
    disp('DR, 10 windows:');
    disp(DR(10)/total_nr_objects);
    disp('DR, 100 windows:');
    disp(DR(100)/total_nr_objects);
    disp('DR, 1000 windows:');
    disp(DR(1000)/total_nr_objects);
    
    axis_limits = [0 1000 0 1];
    % Calculate and return area under curve
    auc = trapz(normalizedx, y);
    
    % Plot curve
    semilogx(x,y);
    axis(axis_limits);
    legend(num2str(auc))
end
