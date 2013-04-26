
## DONE
## Think of a solution to the "moving" problem, I was the algorithm to be stable, not oscillate etc
## Implement said solution
## Implement a "going back and forth" functionality (so that when we get close to the edge it will turn back)
## I probably need to find a way of "shrinking" the image as mentioned by Anton. What was it very fast?
## Implement the position tracking currently written in LABVIEW
## Talk to the pump to reverse etc (and when to do that etc)
## Print time data to benchmar.txt to allow more easily what takes most time to work on the right thing. 
## Fix vertical corrections in velocity, our particle must be able to move up and down as well as left and right
## Save the speed between rounds and compare it to calculating it each time. This seems like a more stable way of doing things. 
## Implement static noise reduction
##		Implmement momentum
##			Easy mode: feed in rod vel and the difference between the vels is bad
##			!!!! Hopefully done? Let's reviewHard mode: As ez but also compensate for your correction vel 
## Improve particle detection
##		Go slower, this means the particle will move less fast and your low frame rate won't be as harmful.
##		Add a larger penalty to moving. 
## 		Remove the middle badness once a few iterations have passed.
##		Remove velocity punishment now that we have momentum maybe?
##		Add a size badnesS? Meassure the size the first 10 iterations, then form an average
##			The modified average will have the form ((old_average*iterations-1) + current_size)/(iterations)
## Improve speed corrections
## 		Find a better speed correction
##		Integral correction. That is really the main problem, we need to have integralverkan.
##		Turns out the main problem was the stupid step engine v_v
## Print the expected and actual location of the particle to see if there are any bugs with the momentum calculations. 


## LEFT TODO: 
## Improve particle detection
##		Implement Antons flood fill algorithm
## 		Tweak the parameters for badness, as well as the Canny Parameters
##		Add together adjacent contours if they are where the particle was last? 
##			I guess I could redefine my badness thing as a function and test if the combined particle would be less bad than the individual? 
## 		CRAZY: For a given level of zoom, map the entire channel, three frames high. 
##		0.4315000000000002 is my approximate step length of one screen
## Notice is the real particle has disappeared. If so we want to skip this turn and go to the next.
## 		How to "know" if a particle is gone. Maybe check if the best particle is further than X from the expected location? If so
## Fix the general particle detection.
##		How is it that two particles can have the same rank?
## Meassure tube expansion again. 
## Why does particle finding take so long sometimes?

## FOR REPORT 
## WRITE DOWN AN EQUATION DESCRIBING THE FORCE AS A FUNCTION OF THE AMOUNT OF AIR IN THE CHANNEL

## ALWAYS LEFT TODO :D
## Find good/better values for paramters ( :/ )
##         !!!IDEA!!
##		Use the better rod tracking Anton has implemented that can track the particles with very very high accuracy after the fact.
##		This algorithm can be used for supervised learning to find good parameter values, look at tons and tons of data.
## Refactor the code some more, I should probably create some fuctions for some of these "sections" like init

