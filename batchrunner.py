from mesa.batchrunner import BatchRunner
from Model import Model, busy_employees,queuing,queuing2,number_of_transactions
import matplotlib.pyplot as plt

fixed_params = {"width":50, "height": 50}
variable_params = {"N": range(500,501)}
iterationer = 10
skridt = 720

stalls_ = 4

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
    for i in range(len(data_list)):
        for j in range(len(data_list[i]["busy"])):
            sum_of_busy[j]+=data_list[i]["busy"][j] #at the right index add number of infected

    sum_of_b =[(number / iter)/(stalls_*4) for number in sum_of_busy] #divide list with number of iterations to get avg
    time = [i for i in range(0,steps+1)] #makes list of x-values for plotting
    plt.plot(time, sum_of_b, label= '# busy employees', color = 'Green')
  #  plt.plot(time, num_of_susceptible, label= 'Number of Susceptible', color = 'Green', linestyle='dashed')
    plt.xlabel('Tidsskridt')
    plt.ylabel('Mean busy employees')
    plt.title('ved %s simulationer' %iter)
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
    model_reporters={"queuing2": lambda m: queuing2(m)}, )
    batch_run.run_all() #run batchrunner

    data_list = list(batch_run.get_collector_model().values()) # saves batchrunner data in a list

    sum_of_queuing_guests = [0]*(steps+1) #makes list for y-values
    for i in range(len(data_list)):
        for j in range(len(data_list[i]["queuing"])):
            sum_of_queuing_guests[j]+=data_list[i]["queuing"][j] #at the right index add number of infected

    sum_of_b =[(number / iter)/128 for number in sum_of_queuing_guests] #divide list with number of iterations to get avg
    time = [i for i in range(0,steps+1)] #makes list of x-values for plotting
    plt.plot(time, sum_of_b, label= '# queuing guests', color = 'Green')
  #  plt.plot(time, num_of_susceptible, label= 'Number of Susceptible', color = 'Green', linestyle='dashed')
    plt.xlabel('Tidsskridt')
    plt.ylabel('Mean queuing guests')
    plt.title('ved %s simulationer' %iter)
    plt.legend()
    return
plot_queuing(fixed_params, variable_params, Model, iterationer, skridt)



def plot_transactions(fix_par, var_par, model, iter, steps):
    batch_run = BatchRunner(model,
    variable_parameters=var_par,
    fixed_parameters=fix_par,
    iterations=iter,
    max_steps=steps,
    model_reporters={"transaction": lambda m: number_of_transactions(m)}, )
    batch_run.run_all() #run batchrunner

    data_list = list(batch_run.get_collector_model().values()) # saves batchrunner data in a list

    sum_of_transactions = [0]*(steps+1) #makes list for y-values
    for i in range(len(data_list)):
        for j in range(len(data_list[i]["transaction"])):
            sum_of_transactions[j]+=data_list[i]["transaction"][j] #at the right index add number of infected

    sum_of_b =[(number / iter) for number in sum_of_transactions] #divide list with number of iterations to get avg
    time = [i for i in range(0,steps+1)] #makes list of x-values for plotting
    plt.plot(time, sum_of_b, label= '# transaction', color = 'Green')
  #  plt.plot(time, num_of_susceptible, label= 'Number of Susceptible', color = 'Green', linestyle='dashed')
    plt.xlabel('Tidsskridt')
    plt.ylabel('Mean transactions')
    plt.title('ved %s simulationer' %iter)
    plt.legend()
    return
plot_transactions(fixed_params, variable_params, Model, iterationer, skridt)
'''


plt.show()

