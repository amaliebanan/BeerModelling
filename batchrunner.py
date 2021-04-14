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

def truncate(n, decimals=0):
    """
    Function to truncate floats to specified number of decimals, is taking from https://realpython.com/python-rounding/#truncation
    :param n: float
    :param decimals: how many decimals
    :return: float with only specified decimals
    """
    multiplier = 10 ** decimals
    return int(n * multiplier) / multiplier


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



'''

def plot_queuing(fix_par, var_par, model, iter, steps):
    """
    Function running simulations and using BatchRunner function to collect data.
    Returns a plot of the number of guest that are queuing divided by total number of guests as a function of timesteps.
    :param fix_par: dictionary, size of grid
    :param var_par: dictionary, number of agents at start
    :param model: Model
    :param iter: int
    :param steps: int
    :return: plot
    """
    batch_run = BatchRunner(model, #running batchrunner
    variable_parameters=var_par,
    fixed_parameters=fix_par,
    iterations=iter,
    max_steps=steps,
    model_reporters={"queuing": lambda m: queuing(m)}, )
    batch_run.run_all() #run batchrunner

    data_list = list(batch_run.get_collector_model().values()) # saves batchrunner data in a list
    mean_queue = []
    std_ = []
    sum_of_queuing_guests = [0]*(steps+1) #makes list for y-values
    for i in range(len(data_list)):
        temp = []
        for j in range(len(data_list[i]["queuing"])):
            sum_of_queuing_guests[j]+=data_list[i]["queuing"][j] #at the right index add number of queuing
            temp.append(data_list[i]["queuing"][j])
            std_.append(data_list[i]["queuing"][j]/(stalls_*4*5))
        mean_queue.append(np.mean(temp)/(stalls_*4*5))
    sum_of_b =[(number / iter)/(stalls_*4*5) for number in sum_of_queuing_guests] #divide list with number of iterations to get avg
    sum_of_b_correct = sum_of_b[123:631]
    time = [i for i in range(0,steps+1)] #makes list of x-values for plotting
    time_correct = [i for i in range(123,631)]
    standard = str(truncate(np.std(std_),3))
    mean=str(truncate(np.mean(mean_queue),3))
    print("std",standard) #getting mean and standard deviation
    print("mean",mean)
    x_.append(sum_of_b_correct)
    y_.append(time_correct)
    plt.plot(time_correct, sum_of_b_correct, label= 'Andel optagede køpladser', color = 'Green') #setting up plot
    mean = str(truncate(np.mean(mean_queue),3))
    plt.xlabel('Tidsskridt')
    plt.ylabel('Andel af optagede køpladser')
    plt.title('%s simulationer med 1 ølbod under koncert' %iter,fontsize=15, y=0.99)
    plt.legend()
    return
plot_queuing(fixed_params, variable_params, Model, iterationer, skridt)
'''

'''
def plot_transactions_during_concert(fix_par, var_par, model, iter, steps):
    """
    Function running simulations and using BatchRunner function to collect data.
    Returns a plot of accumulating transactions only during concert time as a function of timesteps.
    :param fix_par: dictionary, size of grid
    :param var_par: dictionary, number of agents at start
    :param model: Model
    :param iter: int
    :param steps: int
    :return: plot
    """
    batch_run = BatchRunner(model, #running batchrunner
                            variable_parameters=var_par,
                            fixed_parameters=fix_par,
                            iterations=iter,
                            max_steps=steps,
                            model_reporters={"transaction": lambda m: number_of_transactions_during_concert(m)}, )
    batch_run.run_all() #run batchrunner

    data_list = list(batch_run.get_collector_model().values()) # saves batchrunner data in a list

    max_transactions = []
    sum_of_transactions = [0]*(steps+1) #makes list for y-values
    std_ = []
    for i in range(len(data_list)):
        temp_list = []
        for j in range(len(data_list[i]["transaction"])):
            sum_of_transactions[j]+=data_list[i]["transaction"][j] #at the right index add number of infected
            temp_list.append(data_list[i]["transaction"][j])
            std_.append(data_list[i]["transaction"][j])
        max_transactions.append(max(temp_list))

    sum_of_b =[(number / iter) for number in sum_of_transactions] #divide list with number of iterations to get avg
    sum_of_b_correct = sum_of_b[123:631]
    time = [i for i in range(0,steps+1)] #makes list of x-values for plotting
    time_correct = [i for i in range(123,631)]

    standard = str(truncate(np.std(max_transactions),3)) #getting standard deviation 
    mean=str(truncate(np.mean(max_transactions),3)) #getting mean
    x_.append(sum_of_b_correct)
    y_.append(time_correct)
    print("yoyoyo",max_transactions)
    print("std",standard)
    print("mean",mean)
    plt.plot(time_correct, sum_of_b_correct, label= '# solgte øl', color = 'Green')
    mean = str(np.mean(max_transactions))


    plt.xlabel('Tidsskridt') #making plot
    plt.ylabel('Antal solgte øl')
    plt.title('%s simulationer med 1 ølbod under koncert' %iter,)
    plt.legend()
    return
plot_transactions_during_concert(fixed_params, variable_params, Model, iterationer, skridt)
print(x_,y_)

'''

'''
def plot_transactions_total(fix_par, var_par, model, iter, steps):
    """
    Function running simulations and using BatchRunner function to collect data.
    Returns a plot of accumulating transactions only during the whole simulation as a function of timesteps.
    :param fix_par: dictionary, size of grid
    :param var_par: dictionary, number of agents at start
    :param model: Model
    :param iter: int
    :param steps: int
    :return: plot
    """
    batch_run = BatchRunner(model, #running batchrunner
                            variable_parameters=var_par,
                            fixed_parameters=fix_par,
                            iterations=iter,
                            max_steps=steps,
                            model_reporters={"transaction_total": lambda m: number_of_transactions_total(m)}, )
    batch_run.run_all() #run batchrunner

    data_list = list(batch_run.get_collector_model().values()) # saves batchrunner data in a list

    max_transactions = []
    sum_of_transactions = [0]*(steps+1) #makes list for y-values
    std_ = []
    for i in range(len(data_list)):
        temp_list = []
        for j in range(len(data_list[i]["transaction_total"])):
            sum_of_transactions[j]+=data_list[i]["transaction_total"][j] #at the right index add number of infected
            temp_list.append(data_list[i]["transaction_total"][j])
            std_.append(data_list[i]["transaction_total"][j])
        max_transactions.append(max(temp_list))

    print(max_transactions)
    sum_of_b =[(number / iter) for number in sum_of_transactions[:-2]] #divide list with number of iterations to get avg
    time = [i for i in range(0,steps-1)] #makes list of x-values for plotting
    print(sum_of_b)
    print(time)
    standard = str(truncate(np.std(max_transactions),3))
    mean=str(truncate(np.mean(max_transactions),3))
    print("std",standard) #getting standard deviation
    print("mean",mean) #printing mean
    plt.plot(time, sum_of_b, label= '# solgte øl', color = 'Green')
    mean = str(np.mean(max_transactions))


    plt.xlabel('Tidsskridt') #making plot
    plt.ylabel('Antal solgte øl')
    plt.title('%s simulationer med 4 ølboder under koncert' %iter,)
    plt.legend()
    return
plot_transactions_total(fixed_params, variable_params, Model, iterationer, skridt)
'''



