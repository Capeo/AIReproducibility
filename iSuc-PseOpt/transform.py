# Used to clean data copied from pdf files

positive_file_in = open('Data/S1.txt','r')
negative_file_in = open('Data/S2.txt','r')

positive_file_out = open('Data/Positive.txt','w')
negative_file_out = open('Data/Negative.txt','w')

for line in positive_file_in:
	split = line.split(' ')
	if len(split) == 3:
		str = split[0] + " " + split[1] + " " + split[2]
	else:
		str = split[1] + " " + split[2] + " " + split[3]
	positive_file_out.write(str)
	
positive_file_in.close()
positive_file_out.close()

for line in negative_file_in:
	split = line.split(' ')
	if len(split) == 3:
		str = split[0] + " " + split[1] + " " + split[2]
	else:
		str = split[1] + " " + split[2] + " " + split[3]
	negative_file_out.write(str)

negative_file_in.close()
negative_file_out.close()