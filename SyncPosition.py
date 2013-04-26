def WritePosAndTime(position, time, out_file):
	x, y = position[0], position[1]
	outfile.write(time + "\t" + x + "\t" + y)
