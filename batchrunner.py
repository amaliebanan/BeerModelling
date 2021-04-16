from mesa.batchrunner import BatchRunner
from Model import Model, busy_employees,queuing,number_of_transactions_during_concert,number_of_stalls,number_of_transactions_total
import matplotlib.pyplot as plt
import numpy as np

fixed_params = {"width":50, "height": 50} #size of  grid
variable_params = {"N": range(500,501)} #Initialize with 500 guests
no_of_simulations = 1 #how many simulations to run
steps = 720 #time steps in each iteration

#Number of stalls, taking from Model
stalls_ = number_of_stalls
what_type_of_analysis = "busy" #Either "busy", "queuing" or "transactions"

def plot_(fix_par, var_par, model, no_of_simulations, steps,whatType = None):

    """
    Function running simulations and using BatchRunner module to save data from our DataCollector-object
    Returns a plot as a function of timesteps.
    What to plot is specified in the whatType-parameter (busy, queuing or transactions)
    :param fix_par: dictionary, size of grid
    :param var_par: dictionary, number of agents at start
    :param model: Model
    :param iter: int
    :param steps: int
    :param whatType: None or string, what to plot (busy, queuing, transactions)
    :return: plot
    """
    if whatType is None:  #Set default
        whatType = "busy"

    batch_run = BatchRunner(model,
    variable_parameters=var_par,
    fixed_parameters=fix_par,
    iterations=no_of_simulations,
    max_steps=steps)
    batch_run.run_all()

    data_ = list(batch_run.get_collector_model().values()) #Retrieve the data saved in the batchrunner and save it as a matrix
    y_values = np.zeros(steps+1)  #makes list for y-values

    for j in range(len(data_[0][whatType])):
        y_values[j] += data_[0][whatType][j] #at the right index add number of busy

    #Adjust y-values accordingly to what type of analysis we are running
    correct_y_values = []

    display_string,label,title = "", "",""
    if whatType == "busy":
        correct_y_values = [(n / no_of_simulations)/(stalls_*4) for n in y_values][123:631]
        display_string = "Andel af beskræftigede frivillige"
        label = str(number_of_stalls) + " ølboder"
        title = display_string + " ved " + str(no_of_simulations)+ " simulation(er) med " + str(number_of_stalls) + " ølbod(er) åbne"
    elif whatType == "queuing":
        correct_y_values =[(n / no_of_simulations)/(stalls_*4*5) for n in y_values][123:631]
        display_string = "Andel af optagede køpladser"
        label = str(number_of_stalls) + " ølboder"
        title = display_string + " ved " + str(no_of_simulations)+ " simulation(er) med " + str(number_of_stalls) + " ølbod(er) åbne"
    elif whatType == "transactions":
        correct_y_values = [(n / no_of_simulations) for n in y_values][123:631]
        display_string = "Antal solgte øl"
        label = str(number_of_stalls) + " ølboder"
        title = display_string + " ved " + str(no_of_simulations)+ " simulation(er) med " + str(number_of_stalls) + " ølbod(er) åbne"

    x_during_concert = [i for i in range(123,631)]
    plt.plot(x_during_concert,correct_y_values, label= label, color = 'Green')
    plt.xlabel('Tidsskridt')
    plt.ylabel(display_string)
    plt.ylim(0,1)
    plt.xlim(123,630)
    plt.title(title)
    plt.legend()
    return

plot_(fixed_params, variable_params, Model, no_of_simulations, steps,what_type_of_analysis) #Laver plot
plt.show()

