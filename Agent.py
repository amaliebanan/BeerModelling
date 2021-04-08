from mesa import Agent, Model
import math
from itertools import chain
from scipy.stats import truncnorm,bernoulli
import random

def dispatch_time():
    '''
    Generates a random integer from a trunctuated normal distribution.
    :return: random integer from a trunctuated normal distribution with min 1, max 12, mean 4 and standard deviation 2.
    '''

    lower, upper = 1, 12         #min value 1,  max value 12
    mu, sigma = 4, 2               #mean 4, std deviation 2
    return math.floor(truncnorm.rvs((lower - mu) /sigma, (upper - mu) /sigma, loc = mu, scale=sigma)) #returns trunctuated normal distribution random variable as int

def distance(pos1,pos2):
    '''
    Calculates euclidean distance between two positions in the grid.  returns a float with the distance.

    :param pos1: a tuple
    :param pos2: a tuple
    :return: the distance in float
    '''
    return math.sqrt((pos2[0]-pos1[0])**2+(pos2[1]-pos1[1])**2) #euclidean distance.

class guest(Agent):
    '''
    A class to represent a guest.

    Attributes
    ----------
    id : int
        States with agent we are looking at
    model : Model
        Model the agent belongs to.
    number_of_transaction : int
        Number of transactions, or times the agent bought beer
    at_concert : bool
        States if the agent is at the concert
    employer : ()
        States which employee is serving the customer. Is empty when initialized.
    queuing : bool
        States if the guest is queuing
    going_to_queue : bool
        States if the guest is going to queue
    drinking_ : bool
        States if the guest is drinking beer
    buying_beer_counter : int
        Counts the timesteps remaining until the guest is finished with buying beer (transaction time)
    drinking_beer : int
        time that remains of the guest to drink beer
    buying : bool
        States if the guest is buying beer
    leave : bool
        States if the guest is going to leave through exit positions
    has_left : bool
        States if the guest has left the area
    entre_position : ()
        Is set when guest is leaving the area after concert is finish. Is empty position when guest has not chosen exit position yet.
    '''

    def __init__(self, id, model):
        """
        Construct the neccessary attributes for the guest object.

        :param id: int
        :param model: Model object
        """
        super().__init__(id, model)
        self.id = id
        self.model = model
        self.number_of_transaction = 0
        self.at_concert = False
        self.employer = () # Is updated when the buy_beer function is called.

        self.queuing = False
        self.going_to_queue = False

        self.drinking_ = False
        self.buying_beer_counter = 0
        self.drinking_beer = 0
        self.buying = False

        self.leave = False
        self.has_left = False
        self.entre_position = ()

    def wander(self):
        '''
        Makes the agent wander randomly around available positions in the concert area.
        If there are no available neighbouring positions, the agent may walk through other guests.
        :param self:
        :return: None
        '''
        all_steps = self.model.grid.get_neighborhood(self.pos,moore=True,include_center=False) #Getting the 8 neighbouring positions.
        possible_steps,back_up_list = [],[] #Creating lists for avaliable positions, and a back up list if avaliable positions are empty.

        for position in all_steps: #Check if positions in possible_steps list are not in any of the queues in the model, are empty and not exit positions.
            if (self.model.grid.is_cell_empty(position) and position not in self.model.queues) or position in self.model.entre_pos:
                possible_steps.append(position) #append to possible_empty steps if the above statement is true.

        #If there are no avaliable neighbouring cells, the guests may walk though other guests, but not the queues.
        if len(possible_steps) == 0:
            return
             #all_neighbors = self.model.grid.get_neighbors(self.pos,moore=True,include_center=False)
             #for n in all_neighbors:
              #   if isinstance(n,guest): #if the neighbouring position isn't in the queues, the agent may move there.
               #      if n.pos not in self.model.queues:
                #        back_up_list.append(n.pos)
             #pos = random.choice(back_up_list)
             #self.model.grid.move_agent(self,pos) #moving to a random position in the back up list.

        #If the first list "possible_steps" is not empty, move to a random position in the list.
        else:
            next_move = self.random.choice(possible_steps)
            self.model.grid.move_agent(self, next_move) #moving to a random position in possible steps.

    def go_to_specific_pos(self,pos,pos_type=None):
         """
         Makes the agent go to a specific position.
         :param pos: tuple
         :param pos_type: type of position, e.g. scene position, exit position.
         :return:
         """
         goal_pos = pos #The position the agent is going for
         distances = []
         all_steps = self.model.grid.get_neighborhood(self.pos,moore=True,include_center=False) #getting neighbours
         possible_steps = []

         for position in all_steps:    #Checking if cell is empty, and adding to list of possible empty steps.
            if self.model.grid.is_cell_empty(position) or (pos_type == "exit" and position in self.model.entre_pos):
                possible_steps.append(position)

         if len(possible_steps) == 0: #If possible empty steps is empty,
             if pos_type == "scene": #If going to scene
                  back_up_list = []
                  all_neighbors = self.model.grid.get_neighbors(self.pos,moore=True,include_center=False)
                  for n in all_neighbors:
                      if isinstance(n,guest):
                         back_up_list.append(n.pos)
                  try:
                      pos = random.choice(back_up_list)
                      self.model.grid.move_agent(self,pos)
                      return
                  except:
                      return
             return

         else:
             for pos in possible_steps:
                 distances.append((distance(goal_pos,pos),pos)) #find distance from the possible empty steps to goal position

             x_,y_ = min(distances,key=lambda x:x[0])[1] #choose position with shortest distance to goal
             if (x_,y_) == goal_pos: #if the chosen position is goal
                 if pos_type == "exit": #and the type is exit
                    self.has_left = True #Set agent to "has left"

             self.model.grid.move_agent(self,(x_,y_)) #move agent.

    def go_to_closest_stall(self):
         """
         Finds the closest beer stall and choose the closest employee at work in that stall.
         :return:
         """
         if self.model.concert_is_on == False: #if the concert is not on
             d = 7 #set "attraction distance" to 7
         else:
             d = 100 #is concert is on, "attraction distance" is 100 (basically, get closest)
         stalls = [s for s in self.model.schedule.agents if isinstance(s,beerstall) and distance(s.pos,self.pos) < d] #find stalls that attracts agent.
         if stalls == []: # If no stalls attract the agent
             self.wander() # Wander around
         else: #If agent is attracted by stall
             get_distance_to_stalls = [(distance(s.pos,self.pos),s) for s in stalls] #find the closest stall
             closest_stall = min(get_distance_to_stalls,key=lambda x:x[0])[1]
             employees = [e for e in self.model.schedule.agents if isinstance(e, employee) and e.stall == closest_stall and e.at_work == True] #Make list of employees by closest stall
             get_distance_to_employees = [(distance(e.pos,self.pos),e) for e in employees] #Find closest employee
             closest_employee = min(get_distance_to_employees,key=lambda x:x[0])[1]
             self.employer = closest_employee #set employer to closest employee
             self.going_to_queue = True #set going to queue as true
             self.go_to_queue() #calling go_to_queue.

    def go_to_random_stall(self):
         """
         Pick a random beerstall and find a random employee at work in that stall.
         """
         random_stall = [s for s in self.model.schedule.agents if isinstance(s,beerstall)][random.randint(0,len(self.model.stall_positions)-1)] #Find random stall
         employees_closest = [e for e in self.model.schedule.agents if isinstance(e, employee) and e.stall == random_stall and e.at_work == True] #List of employees at the closest stall.
         chosen_employee = employees_closest[random.randint(0,3)] #choosing random employee in that stall.
         self.employer = chosen_employee #setting employer
         self.go_to_queue() #calling go_to_queue
         self.going_to_queue = True #going to queue as true.

    def go_to_queue(self):
        '''
        Makes the agent move towards the last position of the queue to the chosen employee.
        If there are no avaliable steps, the agent stays in the same position.
        If the agent is arriving at the last position of the queue, they check if the queue is crowded (during concert),
        or full, and then change to another queue if this is the case.

        :param: self
        :return: None
        '''

        employee = self.employer
        goal_pos = employee.queue_list[-1] #the goal position is set as the last position in the queue for the chosen employee.
        all_steps = self.model.grid.get_neighborhood(self.pos, moore=True, include_center=False) #Getting the neighbouring positions of the agent.
        possible_steps = [] #Creating an empty list to save the possible empty steps in.

        for position in all_steps: #If the position is empty save to possible steps.
            if self.model.grid.is_cell_empty(position) and position not in employee.queue_list[:-1]:
                possible_steps.append(position)

        if len(possible_steps) == 0: #If no avaliable steps, stay put.
            return

        if goal_pos in all_steps: #If the goal position is in one of the 8 neighboring steps,
            if self.model.concert_is_on: # and the concert is on,
                if not employee.queue_is_crowded():  # and the queue is not crowded (5 or more people),
                     self.model.grid.move_agent(self, goal_pos) # Go to goal position.
                     self.queuing = True # Set agent to queuing.
                     self.going_to_queue = False
                else:                   #Queue is crowded
                    self.change_queue(employee) #Change queue
            else: #If concert is not on
                if not employee.queue_is_full(): # and queue is NOT full
                    self.model.grid.move_agent(self, goal_pos) #go to goal position
                    self.queuing = True #Set to queuing.
                    self.going_to_queue = False
                else: #If queue is full, change position.
                    self.change_queue(employee)

        else: #If goal_pos is not in possible steps, move to cell that is closest to goal_cell
            distances = [] #making a list of distances from possible positions to the goal position.
            for pos in possible_steps:
                distances.append((distance(goal_pos, pos), pos))
            x_,y_ = min(distances,key=lambda x:x[0])[1] #Finding the position with the shortest distance to the goal position.
            self.model.grid.move_agent(self, (x_,y_)) # moving agent to this position.

    def change_queue(self,employer):
        '''
        Randomly find another employee at beerstall between the other employees that are at work.
        :param: self
        :param:  Employee object (self's current employee)
        :return: None
        '''
        the_other_employees = [e for e in self.model.schedule.agents if isinstance(e,employee) and 0.1 < distance(e.pos,employer.pos) < 3 and e.at_work == True] #making list of other employees.
        new_employee = the_other_employees[random.randint(0,len(the_other_employees)-1)] #Choosing a random employee from the list.
        self.employer = new_employee
        self.go_to_queue() # Going to the new queue

    def move_in_queue(self, employer):
        '''
        Makes the guest move forward in the queue if it is possible, until they are first in the queue.
        If they are frist, they will buy beer.
        If it is not possible, they will stay in the same position.
        :param: self
        :param: Employee object (self's employee)
        :return: None
        '''
        for i in range(1,len(employer.queue_list)): #Going though all queue positions.
            if employer.queue_list[i] == self.pos: # If the agent is in the current position in the queue.
                if self.model.grid.is_cell_empty(employer.queue_list[i-1]): # If the position in front of the guest in the queue is avaliable
                    self.model.grid.move_agent(self, employer.queue_list[i-1]) #move forward
                    if self.pos == employer.queue_list[0]: #When the agent has moved, check if they are in front.
                        self.buy_beer() #Buy beer
                        self.buying = True #set guest to buying beer.
                else:#cant move in queue
                    return #stay put.

    def buy_beer(self):
        '''
        Makes an agent buy beer by setting the related employee as busy,
        generating the time it takes to serve the customer from dispatch_time() function,
        and counting another transaction.

        :param self:
        :return: None
        '''
        employee = self.employer #setting the correct employee serving the customer.
        time_at_counter = dispatch_time() #Generating time it takes to serve customer.
        employee.dispatch_time = time_at_counter #Setting this time to the employee, to know when they again are avaliable.
        employee.busy = True #Setting the employee as busy when they are serving the customer.
        self.number_of_transaction = self.number_of_transaction+1 #Counting another transaction.
        self.buying_beer_counter = time_at_counter #Setting the time the guest is at the counter, to know when they are finished being served.

    def step(self):
            """
            Checks all conditions for a guest, makes the guest act according to our assumptions about festival guests behaviour.
            :return: None
            """
            if self.pos not in self.model.queues: #if not in queue, queuing is false
                self.queuing = False

            self.drinking_beer = max(0, self.drinking_beer - 1) #counting down on beer drinking time
            if self.drinking_beer == 0:
                self.drinking_ = False # setting drinking to false if drinking time is 0.
            else:
                # When a guest bought beer and the concert is on, go to scene
                if self.model.concert_has_ended == False:
                  self.go_to_specific_pos(self.model.scene_pos,"scene")
                else: # If the concert had ended, walk towards exit after buying beer is finished.
                    if self.entre_position == ():
                        pos = random.choice(self.model.entre_pos) #choose random exit.
                        self.entre_position = pos
                        self.go_to_specific_pos(self.entre_position, "exit") #go to exit
                    else:
                        self.go_to_specific_pos(self.entre_position, "exit")

            if self.buying_beer_counter > 0: #if still buying beer, count down the beer counter.
                self.buying_beer_counter = max(0,self.buying_beer_counter-1)

                if self.buying_beer_counter == 0: #If guest finishing transaction this timestep, update parameters accordingly
                    self.buying = False
                    self.queuing = False
                    self.drinking_beer = 100 #Drinking parameter D is set to 100 and set drinking to true.
                    self.drinking_ = True
                    if self.model.concert_has_ended == False: #If the concert has not ended
                        self.model.grid.move_agent(self,self.employer.stall.stall_exit_pos[random.randint(0,1)]) #Leave stall through exit.
                        self.go_to_specific_pos(self.model.scene_pos,"scene") #go to scene.
                    else: #if the concert has ended
                         if self.entre_position == ():
                            self.entre_position = random.choice(self.model.entre_pos)
                            self.go_to_specific_pos(self.entre_position, "exit") # Walk towards exit.
                else:
                    return #Dont move

            #If the guest is leaving the concert area after the concert
            if self.leave == True:
                if self.entre_position == ():
                    pos = random.choice(self.model.entre_pos) #select an exit to walk towards if the agent doesn't have one already.
                    self.entre_position = pos
                self.go_to_specific_pos(self.entre_position, "exit") #go to exit.


            if self.queuing == False:  #If not queuing
                 if self.at_concert == False:   #If not at concert
                     if self.going_to_queue == True:   # If going towards queue, keep walking there.
                         self.go_to_queue()
                     elif self.going_to_queue == False and self.drinking_beer == 0 and self.leave == False:   # If not walking to queue, drinking beer nor leaving the area
                          #Before concert has ended, go to closest beer stall
                         if not self.model.concert_has_ended:
                             self.go_to_closest_stall()
                         else: # After concert
                             buy_beer_before_leaving = bernoulli.rvs(0.6) #buying beer before leaving with 60% probability
                             if buy_beer_before_leaving == 1:
                                 self.go_to_random_stall()
                             else:
                                 self.wander()
                                 self.leave = True
                 else: #at_concert = True, go to concert
                     self.go_to_specific_pos(self.model.scene_pos,"scene")
            else: #queuing = True, walk in the queue
                self.move_in_queue(self.employer)



class employee(Agent):
     '''
     A class to represent a guest.

     Attributes
     ----------
     id : int
        Indicates id of specific agent
     model : Model
        Model which the agent belongs to
     dispatch_time : int
        Time remaining until employee is finished serving current customer
     busy : bool
        Indicates if employee is serving a customer
     stall : position, tuple
        Indicates what stall the employee works at
     at_work : bool
        Indicates if the employee is currently working
     self.queue_list : list
        List containing positions where costumers can queue for this specific employee
    '''
     def __init__(self, id, model):
        """
        Construct the neccessary attributes for the employee object.

        :param id: int
        :param model: Model object
        """
        super().__init__(id, model)
        self.id = id
        self.model = model

        self.dispatch = False
        self.dispatch_time = 5

        self.busy = False
        self.stall = ()

        self.at_work = True
        self.queue_list = []

     def queue_is_full(self):
         """
         Checks if the queue is full
         :return: bool. Returns True is queue is full, False is there is room in queue
         """
         a = list(chain.from_iterable([self.model.grid.get_cell_list_contents(a) for a in self.queue_list])) #makes list of taken cells in queue
         if len(a) >= 8: #checks if queue is full
             return True
         else:
             return False

     def queue_is_crowded(self):
        """
        Checks if the queue contains more than 4 guests
        :return: bool. Returns True is queue has 5 or more guests, else false.
        """
        a = [self.model.grid.is_cell_empty(a) for a in self.queue_list] #check if cells are empty in queue list
        if sum(a)>4: #if less than 4 cells are non-empty return false
            return False
        else:
            return True


     def step(self):
         """
         Checks requirements and makes the employee act according to our model assumptions about employee agents.
         :return:  None
         """
         if self.at_work == False: #if not working, don't do anything
             return

         self.dispatch_time = max(0,self.dispatch_time-1) # Count down on remaining time to serve current costumer

         #only busy=False, if dispatch_time = 0 AND no one in the front of the queue.
         if self.dispatch_time==0 and self.model.grid.is_cell_empty(self.queue_list[0]):
             self.busy = False

class beerstall(Agent):
    """
    A class to represent the beerstall.

    Attributes
    ----------
    id : int
        Indicates what beerstall we are talking about
    model : Model
        The model the agent belongs to
    employees : list
        list of employees belonging to the current beerstall
    queue_starting_pos: list
        where the queues start
    stall_exit_pos : list
        list of positions guests can exit from when finished buying beer from stall
    """
    def __init__(self, id, model):
        """
        Construct the neccessary attributes for the beerstall object.

        :param id: int
        :param model: Model object
        """
        super().__init__(id, model)
        self.id = id
        self.model = model

        self.employees = []
        self.queue_starting_pos = []
        self.stall_exit_pos = []

class orangeScene(Agent):
     """
     A class to represent the orange scene. Visual.
     """
     def __init__(self, id, model):
        super().__init__(id, model)
        self.id = id
        self.model = model

class fence(Agent):
     """
     A class to represent the fence. Visual.
     """
     def __init__(self, id, model):
        super().__init__(id, model)
        self.id = id
        self.model = model
        self.orientation = ()

class desk(Agent):
      """
       A class to represent the desk. Visual.
      """
      def __init__(self, id, model):
        super().__init__(id, model)
        self.id = id
        self.model = model
        self.orientation = ()

class exit(Agent):
     """
     A class to represent the exit. Visual.
     """
     def __init__(self, id, model):
        super().__init__(id, model)
        self.id = id
        self.model = model

