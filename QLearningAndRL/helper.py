import matplotlib.pyplot as plt
from IPython import display

plt.ion()

def plot(scores, mean_scores):
    #This clears the previous ouput in the notebook to prep for updated plot
    display.clear_output(wait=True)
    #This then displays the current figure
    display.display(plt.gcf())
    #Clears the current figure so the new data does not overlap with the old date
    plt.clf()
    plt.title('SnakeAI Data')
    plt.xlabel('# of Games')
    plt.ylabel('Score')
    #This plots the scores list as well as the mean scores list
    plt.plot(scores)
    plt.plot(mean_scores)
    plt.ylim(ymin=0)
    #Places a text annotation at last point of the scores plot
    plt.text(len(scores)-1, scores[-1], str(scores[-1]))
    plt.text(len(mean_scores)-1, mean_scores[-1], str(mean_scores[-1]))
    plt.show(block=False)
    #Pauses to allow for the plot to render correctly
    plt.pause(.1)