# TODO: Add comment
# 
# Author: ai
###############################################################################

cars_data = mtcars
cars_data_excerpt = cars_data[1:10,1:4]
cars_data_excerpt_2 = cars_data[1:5, 1:6]

sum(cars_data_excerpt[,2])

##


plot(c(1,2,3,4,5,6),c(4,3,6,2,1,1), #x and y data for our example plot
		xlab = "Sample number", #X axis title
		ylab = "Sample value", #Y axis title
		main = "Test", #Main title of plot
		las = 1, #Rotate all tick labels horizontal
		type = "b", #Plot points with lines between them.
		lty = 3, #Define line type. 0 = blank, 3 = dotted
		font.axis = 4, #Display axis tick labels in bold italics
		font.main = 3, #Display the main title in italics
		cex.axis = 1.2, #Make axis tick labels 1.2x larger than regular font
		cex.main = 1.5, #Make main title 1.5x larger than regular font size
		cex.lab = 1.5, #Make axis title 1.5x larger than regular font size
		bty = "l", #Specify which axes to draw (l = left + bottom)
		mgp = c(2.1,1,0), #Specify axis label + tick locations relative to plot
		col = "red", #Plot the points + lines in red
		col.axis = "blue", #Set the axis tick label color
		col.lab = "dark red", #Set the axis title color
		col.main = "#CC00CC", #Set the figure title color using hex values.
#Hex values are simply an alternate way to specify a
#color.
) #Closing parenthesis for plot command