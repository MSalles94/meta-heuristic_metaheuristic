#main project
class s_instance():
    def __init__(self,n_instance) -> None:
        self.input='./main_instances.csv'
        #selecting the instance
        self.read_data()
        self.distances,self.dots=self.select(n_instance=n_instance) #define the main parameters of the instance
        #self.distances = distances between dots
        #self.dots = dots of the instance
               
    def read_data(self):
        #reading the data set
        import pandas as pd
        self.data=pd.read_csv(self.input,sep=';')
      
    def select(self,n_instance):
        #select one instance from the data set
        instances=self.data['instance'].unique() 
        try:
            i=n_instance-1
            self.instance_name=instances[i]
            print('select instance :'+instances[i])
            selected_instance=self.data[self.data['instance']==instances[i]]
            selected_instance.reset_index(inplace=True,drop=True)
            distances=self.calc_dist_dots(dots=selected_instance)
            return distances,selected_instance
        except:
            print('dont exist the instance '+str(n_instance))
        
    def calc_dist_dots(self,dots):
        #calculate distance between every dot

        def dot_AxB(A=1,B=2,dots=dots):
            #distance between two dots
            A=list(dots.loc[A-1,['X','Y']])
            B=list(dots.loc[B-1,['X','Y']])
            Dx=A[0]-B[0]
            Dy=A[1]-B[1]
            D=(Dx*Dx+Dy*Dy)**(1/2)
            return D
        
        import pandas as pd
        distances=pd.DataFrame()
    
        for i in dots['n_dot']:
            for j in dots['n_dot']:
                distances.loc[i,j]=dot_AxB(A=i,B=j,dots=dots)

        return distances

    def calc_sol_value(self,solution):
    #calculating the value of the function
        value=0
        for i in range(1,len(solution)):
            A=solution[i-1]
            B=solution[i]
            dist_AB=distances.loc[A,B]
            value=value+dist_AB

        return value
    
class construction():
    def __init__(self,distances,methods) -> None:
        self.distances=distances
        self.methods=methods
    def random(self,first=1):
        #generate a random solution
        import random
        a_solution=list(self.distances.index)
        a_solution.remove(first)
        random.shuffle(a_solution)
        solution = [first]+list(a_solution)+[first]
        value=self.methods.solution_value(solution=solution)
        return solution,value
    def gulosa(self,first=1):
        #create a solution where we look for nearest dot
        dist=self.distances.copy()
        solution=[first]
        while len(solution)<len(self.distances.index):
            i=solution[-1]
            check=dist[[i]]
            check=check[check.index.isin(solution)==False]#remove used points
            min_dist=check[i].min()
            min_dist=list(check.index[check[i]==min_dist])[0]
            solution.append(min_dist)
        solution=solution+[first]
        value=self.methods.solution_value(solution=solution)
        return solution,value

class tool_box(): #useful funcions to the model
    def __init__(self,distances) -> None:
        self.distances=distances

    def solution_value(self,solution):
        value=0
        for i in range(1,len(solution)):
            value=self.distances.loc[solution[i],solution[i-1]]+value
        return value
    
    def remove_duplicates(self,list_sample):
        x=[]
        for i in list_sample:
            if i not in x and list(reversed(i)) not in x:
                x.append(i)
        return x

    def next_neighboor(self,solution,moves):
        #generate a solution moving through neighborhood
        import random
        x=solution[:]
        for i in range(moves):
            #do "i" changes in the solution
            sequence=range(len(x))[1:-1]
            A,B=random.sample(sequence,k=2)
            x[A],x[B]=x[B],x[A]
        return x

class refinement():
    def __init__(self,distances,n_neighbor,p_stop,methods) -> None:
        #mains parameters
        self.distances=distances
        self.n_neighbor=n_neighbor
        self.p_stop=p_stop
        self.methods=methods

    def first_improvment(self,solution):
        solution,value=solution[0],solution[1]

        def next_neighbor(solution):
            #generate a solution moving through neighborhood
            import random
            x=solution[:]
            for i in range(self.n_neighbor):
                #do "i" changes in the solution
                sequence=range(len(x))[1:-1]
                A,B=random.sample(sequence,k=2)
                x[A],x[B]=x[B],x[A]
                return x
        
        for i in range(self.p_stop):
            #testing "_stop" times looking for improvments
            new_solution=next_neighbor(solution=solution)
            new_value=self.methods.solution_value(new_solution)

            if new_value<value:
                value=new_value
                solution=new_solution         
        return [solution,value]

class log_method(): ###
    def __init__(self,name) -> None:
        self.test_name=name
        self.prepare_log()
    def prepare_log(self):
        #start the text of output log
        import time
        self.time=time
        self.execution_time=time.time()
        self.log_name='./'+self.test_name+'.txt'
        self.log=''+self.test_name
        self.insert_log()
    def insert_log(self,text='\n'):
        #insert information to the output log
        self.log=self.log+str(text)+'\n'
    def save_log(self):
        #save information
        self.execution_time=self.time.time()-self.execution_time
        self.insert_log('Execution time :'+str(self.execution_time)+' seconds')
        with open(self.log_name,'w') as file:
            file.write(self.log)
        return self.execution_time

class save_result():
    def __init__(self,df,dir='./csv_data',file='register.csv') -> None:
        self.dir=dir
        self.file=dir+'/'+file

        self.new_df=df
        self.read_data()
        self.print_data()
    def read_data(self):
        import os 
        import pandas
        self.pandas=pandas

        if os.path.isdir(self.dir):
            pass
        else:
            os.mkdir(self.dir)

        if os.path.isfile(path=self.file):
            self.exist_file=True
            self.register_file=pandas.read_csv(self.file,sep=';')
        else:
            self.exist_file=False
    
    def print_data(self):

        #self.new_df['ID']=self.new_df['instance']+'_'+self.new_df['test_name']
        #self.new_df.set_index('ID',inplace=True)
        if self.exist_file:
            self.register_file=self.pandas.concat([self.register_file,self.new_df])
            self.register_file.sort_values(by=['instance','n_test'],inplace=True)
        else:
            self.register_file=self.new_df

        for i in self.register_file.columns:
            self.register_file[i]=self.register_file[i].map(lambda x:str(x).replace('.',','))

        self.register_file.to_csv(self.file,sep=';',index=False)

def read_input():
    import pandas 
    x=pandas.read_csv('input.csv',sep=';')
    parameter={}
    for i in x.index:
        value=x.loc[i,'value']
        key=x.loc[i,'parameter']
        if key in ['n_instance','pop_size','elite_size','gen_no_improve']:
            value=int(value)
        if key in ['mutating_move','mutating_factor']:
            value=float(value)
        parameter[key]=value
    
    return parameter

class genetic_solution():
    def __init__(self,
                 test_name='test',
                 instance=1,
                 pop_size=50,
                 gen_no_improve=100,
                 mutating_move=10,
                 mutating_factor=10,
                 elite_size=20,
                 file=''):
        self.parameters={
            'test_name':test_name,   #name the output file
            'n_instance':instance,         #select instance
            'pop_size':pop_size,          #population size
            'gen_no_improve':gen_no_improve,   #n_generation with no improve
            'mutating_move':mutating_move,    #% of gene will modify
            'mutating_factor':mutating_factor,   #% of the gene to transform
            'elite_size':elite_size         #elite group size
        }
        self.parameters=read_input()
        import time
        self.start_time=time.time()
        self.solution_time=0
        self.prepare_method()
        self.first_generation()
        
        
        #self.next_generation() # testing
        def prepare_log():
            self.log.insert_log('-----------------------------------')
            self.log.insert_log('-----------------------------------')
            self.log.insert_log('----EVOLUTION----------------------')
            self.log.insert_log('')
            self.log.insert_log('gen / top_value / elite mean')
        prepare_log()

        def play_loop():
            stop=0
            while stop<self.parameters['gen_no_improve']:
                #print(stop)
                self.next_generation()
                self.top_value[self.timer]=self.elite_group.loc[0,'value']
                self.x=[self.timer,
                     round(self.top_value[self.timer],4),
                     round(self.elite_group['value'].mean(),2)]
                stop=stop+1
                if self.top_value[self.timer]<self.top_value[self.timer-1]:
                    stop=0
                    #print(self.top_value[self.timer])
                    self.log.insert_log(str(self.x))
                    self.solution_time=time.time()-self.start_time
                else:
                    #self.log.insert_log(str(log))
                    pass
                if stop==self.parameters['gen_no_improve']:
                    self.log.insert_log(str(self.x))
        play_loop()

        self.log.insert_log()
        self.log.insert_log('final elite group')
        for i in self.elite_group.index:
            register=str(round(self.elite_group.iloc[i,1],2))+'///'+str(self.elite_group.iloc[i,0])
            self.log.insert_log(register)
        
        time=self.log.save_log()

        #register values in csv
        import datetime
        columns={
            'instance':self.instance_name,
            'n_test':self.parameters['test_name'],
            'pop_size':self.parameters['pop_size'],
            'gen_no_improve':self.parameters['gen_no_improve'],
            'mutating_move':self.parameters['mutating_move'],
            'mutating_factor':self.parameters['mutating_factor'],
            'elite_size':self.parameters['elite_size'],
            'max_generation':self.x[0],
            'top_solution':self.x[1],
            'elite_mean':self.x[2],
            'total_time_sec':time,
            'solution_time':self.solution_time,
            'timestamp':str(datetime.datetime.now())
        }
        self.x=self.pd.DataFrame([list(columns.values())],columns=columns.keys())
        if file!='':
            save_result(df=self.x,file=file)
        save_result(df=self.x,file='geral_register.csv')
        
    def prepare_method(self):
        #basic preparation to the model
        #defining the instance
        instance=s_instance(n_instance=self.parameters['n_instance'])
        self.instance_name=instance.instance_name
        #useful functions
        self.methods=tool_box(distances=instance.distances)
        import pandas 
        self.pd=pandas
        import random
        self.random=random
        #import construction methods
        self.constructions=construction(distances=instance.distances,methods=self.methods)
        #cursor to count generations
        self.timer=0
        #define the parents number
        n_parents=0
        for i in range(1,self.parameters['pop_size']):
            n_parents=i*(i-1)
            if n_parents>self.parameters['pop_size']:
                n_parents=i
                break
        self.n_parents=n_parents
        #define number of moves , mutating_move
        self.parameters['mutating_move']=int(self.parameters['mutating_move']*self.parameters['pop_size']/200)
        #register the output
        self.name=self.instance_name+'_'+self.parameters['test_name']
        self.log=log_method(name=self.name)
        #register data
        self.generation={}
        self.top_value={}

        self.log.insert_log('Parameters:'+str(self.parameters))
        self.log.insert_log('------------------------------------------')
        self.log.insert_log('------------------------------------------')

    def first_generation(self):
        #generate the first generation
        first_gen=[]
        first_gen.append(self.constructions.gulosa())
        size=self.parameters['pop_size']
        for i in range(size-1):
            first_gen.append(self.constructions.random())
        first_gen=self.pd.DataFrame(first_gen,columns=['order','value'])
        first_gen.sort_values(by='value',inplace=True)
        first_gen.reset_index(inplace=True,drop=True)
        self.generation[self.timer]=first_gen
        self.elite_group=self.pd.DataFrame()
        self.update_elite(first_gen)
        self.top_value[self.timer]=self.elite_group.loc[0,'value']
        #REGISTER THE ELITE GROUP
        self.log.insert_log('-----------------------')
        self.log.insert_log('--FIRST ELITE GROUP--')
        for i in self.elite_group.index:
            register=str(float(round(self.elite_group.iloc[i,1],2)))+'///'+str(list(self.elite_group.iloc[i,0]))
            self.log.insert_log(register)
        self.log.insert_log('-----------------------')
 
    def update_elite(self,df_candidates):  #tool
        #atualize the elite group
        self.elite_group=self.pd.concat([self.elite_group,df_candidates])
        self.elite_group=self.remove_equals(self.elite_group)
        self.elite_group.sort_values(by='value',inplace=True)
        self.elite_group.reset_index(inplace=True,drop=True)
        self.elite_group=self.elite_group[self.elite_group.index<self.parameters['elite_size']]

    def select_next_gen(self,df_candidates):
        next_gen=list(self.elite_group.head(1)['order']) #get the best solution

        x_top_candidates=int(self.parameters['pop_size']*0.5) #get half from the best

        next_gen=next_gen+list(df_candidates.head(x_top_candidates)['order'])
        df_candidates=df_candidates[df_candidates['order'].isin(next_gen)==False] #remove the choosen
        n=self.parameters['pop_size']-len(next_gen)+1 # the number to complete population
        next_gen=next_gen+self.random.sample(list(df_candidates['order']),n) #complete selecting random solutions

        #transform in dataframe
        next_gen=[[i] for i in next_gen]
        next_gen=self.pd.DataFrame(next_gen,columns=['order'])
        next_gen['value']=next_gen['order'].map(lambda x:self.methods.solution_value(x))
        next_gen=self.remove_equals(next_gen)
        next_gen=next_gen.head(self.parameters['pop_size'])
        return next_gen
         
    def remove_equals(self,df_candidates): #tool
        #remove equal solutions froma a dataframe

        df_candidates=list(df_candidates['order'])
        new_list=[]
        for i in df_candidates:
            if (i not in new_list) and (list(reversed(i)) not in new_list):
                new_list.append(i)
        new_list=[[i,self.methods.solution_value(i)] for i in new_list]
        new_list=self.pd.DataFrame(new_list,columns=['order','value'])
        new_list.sort_values(by='value',inplace=True)
        new_list.reset_index(inplace=True,drop=True)
        return new_list

    def next_generation(self):
        #generating sons from the actual population
        next_gen=self.generating_sons(opitions=self.generation[self.timer].copy())

        #remove duplicates
        #next_gen=self.remove_equals(df_candidates=next_gen)

        #update elit group
        self.update_elite(df_candidates=next_gen)
    
        #select next generation
        next_gen=self.select_next_gen(df_candidates=next_gen)

        #save next generation
        self.timer=self.timer+1
        self.generation[self.timer]=next_gen

    def generating_sons(self,opitions):
        #generating sons by cross over
        #chose parents for combination
        opitions=[i[1:-1] for i in opitions['order']]
        parents=self.elite_group.loc[0,'order'][1:-1] #chose the best solution
        parents=[parents]+self.random.sample(opitions,self.n_parents-1)

        def have_family(p1,p2,p_split):
            #generating sons by pairs
            cross_over=[]
            [cross_over.append(i) if i not in p1[:p_split] else '' for i in p2[:p_split]]
            cross_over=self.random.sample(cross_over,len(cross_over))
            co_parent=[i if i not in p1[:p_split] else cross_over.pop(0)for i in p2[p_split:]]
            son=p1[:p_split]+co_parent
            return son

        def mutating_factor(son,chance=1):
            moves=self.parameters['mutating_move']
            if chance<self.random.randint(1,100):
                x=son[:]
                for i in range(moves):
                    #do "i" changes in the solution
                    sequence=range(len(x))
                    A,B=self.random.sample(sequence,k=2)
                    x[A],x[B]=x[B],x[A]
                return x
            else:
                return son
            
        sons=[]
        while len(sons)<self.parameters['pop_size']*2:
            split_point=self.random.randint(2,len(parents[0]))
            for father in parents:
                for mother in parents:
                    if father==mother:
                        #ignore equals
                        pass
                    else:
                        #generate children
                        son1=have_family(father,mother,p_split=split_point)
                        son2=have_family(mother,father,p_split=split_point)
                        for i in [son1,son2]:
                            if i in sons or reversed(i) in sons:
                                #mutate equal sons
                                mutated_son=mutating_factor(i,chance=self.parameters['mutating_factor'])
                                if mutated_son in sons or reversed(mutated_son) in sons:
                                    pass #ignore existing sons
                                else:
                                    sons.append(mutated_son)
                            else:
                                #apend new solutions "sons"
                                sons.append(i)
        sons=[[[1]+i+[1]] for i in sons]

        sons=self.pd.DataFrame(sons,columns=['order'])
        sons['value']=sons['order'].map(lambda x:self.methods.solution_value(x))
        sons.sort_values(by='value',inplace=True)
        sons.reset_index(inplace=True,drop=True)
        return sons


genetic_solution()