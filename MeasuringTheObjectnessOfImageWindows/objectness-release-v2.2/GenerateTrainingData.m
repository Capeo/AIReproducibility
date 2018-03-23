%annotations = dir('../VOC2007/Train/Annotations/*.xml');

testFile = fopen('../VOC2007/Train/ImageSets/Main/trainval.txt','r');
formatSpec = '%f';
trainingFiles = fscanf(testFile,formatSpec);
fclose(testFile);
nrImages = length(trainingFiles);
structGT = struct;
structNew = 1;

totalNrObjects = 0;

for i = 1:nrImages
    id = num2str(trainingFiles(i));
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
    
    include = 0;
    boxes = [];
    
    % Open XML file
    xmlFilePath = fullfile('../VOC2007/Train/Annotations/', strcat(name, '.xml'));
    xml = xmlread(xmlFilePath);
    objects = xml.getElementsByTagName('object');
    nrObjects = objects.getLength;
    for j = 0:nrObjects-1
        object = objects.item(j);
        objectName = object.getElementsByTagName('name').item(0).getFirstChild.getData;
        if strcmp(objectName, 'bird') || strcmp(objectName, 'car') || strcmp(objectName, 'cat') || strcmp(objectName, 'cow') || strcmp(objectName, 'dog') || strcmp(objectName, 'sheep')
            difficulty = object.getElementsByTagName('difficult').item(0).getFirstChild.getData;
            truncated = object.getElementsByTagName('truncated').item(0).getFirstChild.getData;
            if strcmp(difficulty, '0')
                if include == 0
                    include = 1;
                end
                box = object.getElementsByTagName('bndbox').item(0);
                xmin = str2double(box.getElementsByTagName('xmin').item(0).getFirstChild.getData);
                ymin = str2double(box.getElementsByTagName('ymin').item(0).getFirstChild.getData);
                xmax = str2double(box.getElementsByTagName('xmax').item(0).getFirstChild.getData);
                ymax = str2double(box.getElementsByTagName('ymax').item(0).getFirstChild.getData);
                boxes = [boxes; xmin ymin xmax ymax];
            else
                include = 2;
            end
        else
            include = 2;
        end
    end
    if include == 1
        totalNrObjects = totalNrObjects + size(boxes,1);
        if structNew == 1
            structGT(1).boxes = boxes;
            structGT(1).img = strcat(name, '.jpg');
            structNew = 0;
        else
            structGT(length(structGT)+1).boxes = boxes;
            structGT(length(structGT)).img = strcat(name, '.jpg');
        end
        source = strcat('../VOC2007/Train/JPEGImages/', name, '.jpg');
        destination = strcat('../Training/', name, '.jpg');
        %copyfile(source, destination);
    end
end

disp(totalNrObjects)

%save('../Training/structGT.mat', 'structGT');
