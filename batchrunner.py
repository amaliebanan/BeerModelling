from mesa.batchrunner import BatchRunner
from Model import Model, busy_employees,queuing
import matplotlib.pyplot as plt

fixed_params = {"width":50, "height": 50}
variable_params = {"N": range(40,41)}
iterationer = 3
skridt = 720


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

    sum_of_b =[number / iter for number in sum_of_busy] #divide list with number of iterations to get avg
    time = [i for i in range(0,steps+1)] #makes list of x-values for plotting
    plt.plot(time, sum_of_b, label= '# busy employees', color = 'Green')
  #  plt.plot(time, num_of_susceptible, label= 'Number of Susceptible', color = 'Green', linestyle='dashed')
    plt.xlabel('Tidsskridt')
    plt.ylabel('Mean busy employees')
    plt.title('ved %s simulationer' %iter)
    plt.legend()
    return
plot_busy(fixed_params, variable_params, Model, iterationer, skridt)
plt.show()

