from mesa.batchrunner import BatchRunner
from Model import Model, busy_employees,queuing,number_of_transactions,number_of_stalls
import matplotlib.pyplot as plt
import numpy as np

fixed_params = {"width":50, "height": 50}
variable_params = {"N": range(500,501)}
iterationer = 1
skridt = 635

stalls_ = number_of_stalls
'''
from https://realpython.com/python-rounding/#truncation '''
def truncate(n, decimals=0):
    multiplier = 10 ** decimals
    return int(n * multiplier) / multiplier


def plot_busy(fix_par, var_par, model, iter, steps):
    batch_run = BatchRunner(model,
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
            sum_of_busy[j]+=data_list[i]["busy"][j] #at the right index add number of infected
            temp.append(data_list[i]["busy"][j])
            std_.append((data_list[i]["busy"][j])/(stalls_*4))
        mean_busy.append(np.mean(temp)/(stalls_*4))
    sum_of_b =[(number / iter)/(stalls_*4) for number in sum_of_busy] #divide list with number of iterations to get avg
    sum_of_b_correct = sum_of_b[90:631]
    print(np.std(std_))

    time = [i for i in range(0,steps+1)] #makes list of x-values for plotting
    time_correct = [i for i in range(90,631)]
    plt.plot(time_correct, sum_of_b_correct, label= 'Andel beskæftigede', color = 'Green')
    standard = str(truncate(np.std(std_),3))

    mean=str(truncate(np.mean(mean_busy),3))
    print("std",standard)
    print("mean",mean)
    plt.xlabel('Tidsskridt')
    plt.ylabel('Andel af beskæftigede medarbejdere')
    plt.title('%s simulationer med 3 ølboder under koncert' %iter,)
    plt.legend()

    return

plot_busy(fixed_params, variable_params, Model, iterationer, skridt)



'''

def plot_queuing(fix_par, var_par, model, iter, steps):
    batch_run = BatchRunner(model,
    variable_parameters=var_par,
    fixed_parameters=fix_par,
    iterations=iter,
    max_steps=steps,
    model_reporters={"queuing": lambda m: queuing(m)}, )
    batch_run.run_all() #run batchrunner

    data_list = list(batch_run.get_collector_model().values()) # saves batchrunner data in a list
    mean_queue = []
    sum_of_queuing_guests = [0]*(steps+1) #makes list for y-values
    for i in range(len(data_list)):
        temp = []
        for j in range(len(data_list[i]["queuing"])):
            sum_of_queuing_guests[j]+=data_list[i]["queuing"][j] #at the right index add number of infected
            temp.append(data_list[i]["queuing"][j])
        mean_queue.append(np.mean(temp)/(stalls_*4*8))
    sum_of_b =[(number / iter)/(stalls_*4*8) for number in sum_of_queuing_guests] #divide list with number of iterations to get avg
    sum_of_b_correct = sum_of_b[90:631]
    time = [i for i in range(0,steps+1)] #makes list of x-values for plotting
    time_correct = [i for i in range(90,631)]

    plt.plot(time_correct, sum_of_b_correct, label= 'Andel optagede køpladser', color = 'Green')
    mean = str(truncate(np.mean(mean_queue),3))
    plt.xlabel('Tidsskridt')
    plt.ylabel('% af optagede køpladser')
    plt.title('Gennenmsnitlig andel af optagede køpladser %s'%mean,fontsize=10)
    plt.suptitle('%s simulationer med 3 ølboder under koncert' %iter,fontsize=15, y=0.99)
    plt.legend()
    print(sum_of_b_correct)
    print(time_correct)
    return
plot_queuing(fixed_params, variable_params, Model, iterationer, skridt)
'''
'''

def plot_transactions(fix_par, var_par, model, iter, steps):
    batch_run = BatchRunner(model,
    variable_parameters=var_par,
    fixed_parameters=fix_par,
    iterations=iter,
    max_steps=steps,
    model_reporters={"transaction": lambda m: number_of_transactions(m)}, )
    batch_run.run_all() #run batchrunner

    data_list = list(batch_run.get_collector_model().values()) # saves batchrunner data in a list

    max_transactions = []
    sum_of_transactions = [0]*(steps+1) #makes list for y-values
    for i in range(len(data_list)):
        temp_list = []
        for j in range(len(data_list[i]["transaction"])):
            sum_of_transactions[j]+=data_list[i]["transaction"][j] #at the right index add number of infected
            temp_list.append(data_list[i]["transaction"][j])
        max_transactions.append(max(temp_list))

    sum_of_b =[(number / iter) for number in sum_of_transactions] #divide list with number of iterations to get avg
    sum_of_b_correct = sum_of_b[90:631]
    time = [i for i in range(0,steps+1)] #makes list of x-values for plotting
    time_correct = [i for i in range(90,631)]
    np.mean(max_transactions)
    plt.plot(time_correct, sum_of_b_correct, label= '# solgte øl', color = 'Green')
    mean = str(np.mean(max_transactions))
    print(mean)

    plt.xlabel('Tidsskridt')
    plt.ylabel('Antal solgte øl')
    plt.title('Gennenmsnit antal solgte øl: %s'%mean,fontsize=10)
    plt.suptitle('%s simulationer med 2 ølboder under koncert' %iter,fontsize=15, y=0.99)
    plt.legend()
    return
plot_transactions(fixed_params, variable_params, Model, iterationer, skridt)
'''

plt.show()

