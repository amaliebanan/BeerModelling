from mesa.batchrunner import BatchRunner
from Model import Model, busy_employees,queuing,number_of_transactions_during_concert,number_of_stalls,number_of_transactions_total
import matplotlib.pyplot as plt
import numpy as np

fixed_params = {"width":50, "height": 50} #size of  grid
variable_params = {"N": range(500,501)}
iterationer = 50 #iterations to run
skridt = 631 #time steps in each iteration

stalls_ = number_of_stalls
x_,y_ = [],[]
'''
from https://realpython.com/python-rounding/#truncation '''
def truncate(n, decimals=0):
    multiplier = 10 ** decimals
    return int(n * multiplier) / multiplier

'''
def plot_busy(fix_par, var_par, model, iter, steps):
    """
    Function running simulations and using BatchRunner function to collect data.
    Returns a plot of number of busy employees divided by total number of employees as a function of timesteps.
    :param fix_par: dictionary, size of grid
    :param var_par: dictionary, number of agents at start
    :param model: Model
    :param iter: int
    :param steps: int
    :return: plot
    """
    batch_run = BatchRunner(model, #running batchrunner to collect data
    variable_parameters=var_par,
    fixed_parameters=fix_par,
    iterations=iter,
    max_steps=steps,
    model_reporters={"busy": lambda m: busy_employees(m)}, )
    batch_run.run_all() #run batchrunner

    data_list = list(batch_run.get_collector_model().values()) # saves batchrunner data in a list

    sum_of_busy = [0]*(steps+1) #makes list for y-values
    mean_busy=[]
    std_ = []
    for i in range(len(data_list)):
        temp=[]
        for j in range(len(data_list[i]["busy"])):
            sum_of_busy[j]+=data_list[i]["busy"][j] #at the right index add number of busy
            temp.append(data_list[i]["busy"][j])
            std_.append((data_list[i]["busy"][j])/(stalls_*4))
        mean_busy.append(np.mean(temp)/(stalls_*4))
    sum_of_b =[(number / iter)/(stalls_*4) for number in sum_of_busy] #divide list with number of iterations to get avg
    sum_of_b_correct = sum_of_b[123:631]

    time_correct = [i for i in range(123,631)]

    plt.plot(time_correct, sum_of_b_correct, label= 'Andel beskæftigede', color = 'Green')
    standard = str(truncate(np.std(std_),3)) #getting std
    x_.append(sum_of_b_correct)
    y_.append(time_correct)
    mean=str(truncate(np.mean(mean_busy),3)) #getting mean
    print("std",standard)
    print("mean",mean)
    plt.xlabel('Tidsskridt') #setting up plot
    plt.ylabel('Andel af beskæftigede medarbejdere')
    plt.title('%s simulationer med 2 ølboder' %iter)
    plt.legend()

    return

plot_busy(fixed_params, variable_params, Model, iterationer, skridt) #returning plot

'''


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



plt.show()

