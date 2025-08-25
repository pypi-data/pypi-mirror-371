# Copyright (c) 2024 XX Xiao

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files(the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and / or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

r""" 
This module contains the Layout class, which is designed to select suitable layouts 
for quantum circuits on hardware backends.
"""

import os
#import warnings
import networkx as nx
import numpy as np
from typing import Literal
from itertools import combinations,zip_longest,product
from multiprocessing import Pool
from functools import partial
from .backend import Backend

class Layout:
    """
    Responsible for selecting suitable qubit layouts from a given chip for a quantum circuit.

    This class generates qubit layouts based on the required number of qubits, performance metrics, and the topology of the chip. It is designed to help map and execute quantum circuits on specific quantum hardware.
    """
    def __init__(self,nqubits: int, chip_backend: Backend):
        """Initialize the Layout class with the required number of qubits and chip backend.

        Args:
            nqubits (int): The number of qubits needed in the layout.
            chip_backend (Backend): An instance of the Backend class that contains the information 
            about the quantum chip to be used for layout selection
        """
        self.nqubits = nqubits
        self.size = chip_backend.size
        self.priority_qubits = chip_backend.priority_qubits
        self.graph = chip_backend.edge_filtered_graph(thres=0.6)
        self.ncore = os.cpu_count() // 2 
        self.fidelity_mean_threshold = 0.9
        self.edge_fidelitys = nx.get_edge_attributes(self.graph,'fidelity')
        self.algorithm_switch_threshold = 10

    def _get_node_neighbours(self,node:int):
        return list(self.graph.neighbors(node))
    
    def get_one_node_connect_dict(self,node:int):
        """ Generates a dictionary representing the multi-level neighbor connectivity of a given node.

        Args:
            node (int):The starting node for generating the connectivity dictionary.

        Returns:
            dict: A dictionary where keys are nodes and values are lists of neighboring nodes 
            up to `nqubits - 1` levels deep, each list representing the connectivity at that level.
        """
        current_neighbours = [i for i in self._get_node_neighbours(node) if i > node]
        dd = {node:current_neighbours}
        remove = list(range(node+1))
        for _ in range(self.nqubits-2):
            current = []
            for node0 in current_neighbours:
                node0_neighbours = self._get_node_neighbours(node0)
                node0_neighbours = [i for i in node0_neighbours if i not in remove]
                current.append(node0_neighbours)
                dd[node0] = node0_neighbours
            current_neighbours = list(set(item for sublist in current for item in sublist))
        return dd

    def get_one_node_subgraph(self,node:int):
        """Generates all possible subgraph combinations for a given node up to a specified number of nodes.

        Args:
            node (int): The starting node for generating subgraph combinations.

        Returns:
            list[tuple]:A list of tuples, each representing a unique combination of nodes that form
              a subgraph up to the specified `nqubits` in size.
        """

        def post_combinations(mid,dd,cut):
            rr = set([elem for node in mid if node in dd for elem in dd[node]])
            cc = []
            mm = min(cut,len(dd)) +1
            for idx in range(1,mm):
                cc +=  [list(comb) for comb in combinations(rr, idx)]
            return cc
        
        dd = self.get_one_node_connect_dict(node)
        collect = []
        init = [{'pre':[],'mid':[node],'post':post_combinations([node],dd,self.nqubits-1)}]
        for _ in range(self.nqubits):
            update = []
            for c0 in init:
                new_pre = c0['pre'] + c0['mid']
                new_pre.sort()
                new_pre = list(set(new_pre))
                if len(new_pre) == self.nqubits:
                    new_pre.sort()
                    collect.append(tuple(new_pre))
                elif len(new_pre) < self.nqubits:
                    if c0['post'] == []:
                        continue
                    else:
                        for mid0 in c0['post']:
                            mid = [i for i in mid0 if i not in new_pre]
                            c1 = {'pre':new_pre,'mid':mid,'post':post_combinations(mid,dd,self.nqubits-len(new_pre+mid))}
                            update.append(c1)
            init = update
        return list(set(collect))
    
    def collect_all_subgraph_in_parallel(self):
        """Collects all possible subgraph combinations for all nodes in the graph in parallel.

        Returns:
            list[tuple]:  A list of tuples, each representing a unique combination of nodes that 
                     form subgraphs for all nodes in the graph.
        """
        collect_all = []
        with Pool(processes = self.ncore) as pool:
            res = pool.map(partial(self.get_one_node_subgraph),self.graph.nodes())
        for collect in res:
            collect_all += collect
        return collect_all

    def get_one_subgraph_info(self,nodes:tuple|list):
        """Retrieves information about a specified subgraph.
        
        This method generates a subgraph from the given list of nodes, calculates the degree of each node within the subgraph, 
        and computes the mean and variance of the edge weights (fidelity) in the subgraph.It returns the subgraph information 
        only if the mean fidelity meets the specified threshold.

        Args:
            nodes (tuple|list): A list of nodes that define the subgraph.

        Returns:
            tuple or None: A tuple containing the nodes, their degrees, mean fidelity, and variance of fidelity 
                           if the mean fidelity is greater than or equal to `fidelity_mean_threshold`. Otherwise, returns None.
        """
        subgraph = self.graph.subgraph(nodes)
        subgraph_degree = dict(subgraph.degree())
        subgraph_fidelity = np.array([self.edge_fidelitys[(min(edge),max(edge))] for edge in subgraph.edges])
        fidelity_mean = np.mean(subgraph_fidelity)
        fidelity_var  = np.var(subgraph_fidelity)  
        if fidelity_mean >= self.fidelity_mean_threshold:
            nodes_info = (nodes,subgraph_degree,fidelity_mean,fidelity_var)
            return nodes_info
        else:
            return None
     
    def collect_all_subgraph_info_in_parallel(self):
        """Collects information about all subgraphs in parallel.

        Returns:
            list: A list of results, where each entry corresponds to the information of a subgraph. 
        """
        all_subgraph = self.collect_all_subgraph_in_parallel()
        with Pool(processes = self.ncore) as pool:
            res = pool.map(partial(self.get_one_subgraph_info),all_subgraph)
        return res  

    def classify_all_subgraph_according_topology(self) -> tuple[list,list,list,list]:
        """
        Classify the collected subgraphs based on their topological structure into four categories.

        This function sorts the subgraphs into the following four categories:
        1. Linear and connected, with all nodes in the same row of the chip.
        2. Linear and connected, with nodes not in the same row.
        3. Contains a cycle within the subgraph.
        4. Non-linear and connected, where some nodes have more than three edges.
    
        Returns:
            tuple[list, list, list, list]: A tuple containing four lists, each corresponding 
            to one of the four categories of subgraphs.
        """

        linear_subgraph_list  = []
        nonlinear_subgraph_list = []
        all_subgraph_info = self.collect_all_subgraph_info_in_parallel()

        for subgraph_info in filter(lambda x: x is not None, all_subgraph_info):
            nodes,subgraph_degree,fidelity_mean,fidelity_var = subgraph_info
            nodes_info = (nodes, fidelity_mean, fidelity_var)
            if max(subgraph_degree.values()) <= 2:
                linear_subgraph_list.append(nodes_info)
            else:
                nonlinear_subgraph_list.append(nodes_info)
        return linear_subgraph_list,nonlinear_subgraph_list
    
    def sort_subgraph_according_mean_fidelity(self, num:int=1,  printdetails: bool = True):
        """Sort each of the four subgraph categories based on the main of fidelity on the edges (couplers), 
        in ascending order.

        Args:
            printdetails (bool, optional): If True, print details of the sorting process. Defaults to True.

        Returns:
            tuple[list, list, list, list]: Four sorted lists, each corresponding to one of the four 
            subgraph categories, with subgraphs sorted by edge fidelity variance.
        """
        linear_subgraph_list, nonlinear_subgraph_list = self.classify_all_subgraph_according_topology()
        linear_subgraph_list_sort = sorted(linear_subgraph_list,key=lambda x: x[1],reverse=True)
        nonlinear_subgraph_list_sort = sorted(nonlinear_subgraph_list,key=lambda x: x[1],reverse=True)
        if printdetails:
            print(len(linear_subgraph_list_sort),len(nonlinear_subgraph_list_sort))
            print('The average fidelity is arranged in descending order,only print the first ten.')
            length = self.nqubits*5+22

            print('{:<3} | {:^{}} | {:^{}} '.format(\
                'idx','subgraph with linear topology',length,'subgraph with nonlinear topology',length))
            for i, (linear,nonlinear) in enumerate(zip_longest(linear_subgraph_list_sort,nonlinear_subgraph_list_sort, fillvalue=' ')):
                if i >= len(linear_subgraph_list_sort):
                    linear = ('(                  )',0.0,0.0)
                if i >= len(nonlinear_subgraph_list_sort):
                    nonlinear = ('(                  )',0.0,0.0)
                if i <= num:
                    print('{:<3} | {:<{}} {:<10.6f} {:<10.6f} | {:<{}} {:<10.6f} {:<10.6f} '\
                          .format(i, \
                                  str(linear[0]),self.nqubits*5,linear[1],linear[2],\
                                  str(nonlinear[0]),self.nqubits*5,nonlinear[1],nonlinear[2])\
                                  )
                    
        return linear_subgraph_list_sort[:num],nonlinear_subgraph_list_sort[:num]
    
    def sort_subgraph_according_var_fidelity(self, num:int = 1, printdetails: bool = True):
        """
        Sort each of the four subgraph categories based on the variance of fidelity on the edges (couplers), 
        in ascending order.
    
        This function sorts the subgraphs within each category (from the previous classification) by the 
        variance of fidelity across the edges in each subgraph, from lowest to highest.
    
        Args:
            printdetails (bool, optional): If True, print details of the sorting process. Defaults to True.
    
        Returns:
            tuple[list, list, list, list]: Four sorted lists, each corresponding to one of the four 
            subgraph categories, with subgraphs sorted by edge fidelity variance.
        """
        linear_subgraph_list, nonlinear_subgraph_list = self.classify_all_subgraph_according_topology()
        linear_subgraph_list_sort = sorted(linear_subgraph_list,key=lambda x: x[2])
        nonlinear_subgraph_list_sort = sorted(nonlinear_subgraph_list,key=lambda x: x[2])
        
        if printdetails:
            print(len(linear_subgraph_list_sort),len(nonlinear_subgraph_list_sort))
            print('The average fidelity is arranged in descending order, only print the first ten.')
            length = self.nqubits*5+22

            print('{:<3} | {:^{}} | {:^{}} '.format(\
                'idx','subgraph with linear topology',length,'subgraph with nonlinear topology',length))
            for i, (linear,nonlinear) in enumerate(zip_longest(linear_subgraph_list_sort, nonlinear_subgraph_list_sort, fillvalue=' ')):
                if i >= len(linear_subgraph_list_sort):
                    linear = ('(                  )',0.0,0.0)
                if i >= len(nonlinear_subgraph_list_sort):
                    nonlinear = ('(                  )',0.0,0.0)
                
                if i <= num:
                    print('{:<3} | {:<{}} {:<10.6f} {:<10.6f} | {:<{}} {:<10.6f} {:<10.6f} '\
                          .format(i, \
                                  str(linear[0]),self.nqubits*5,linear[1],linear[2],\
                                  str(nonlinear[0]),self.nqubits*5,nonlinear[1],nonlinear[2])\
                                  )

        return linear_subgraph_list_sort[:num], nonlinear_subgraph_list_sort[:num]
    
    def select_qubit_from_backend(self,):
        # 当线路中只有一个qubit时，挑选单比特门保真度最大的比特

        for nodes in nx.connected_components(self.graph):
            if len(nodes) > 1:
                subgraph = self.graph.subgraph(nodes)
                break
        node_fidelity_dic = nx.get_node_attributes(subgraph,'fidelity')
        sorted_dict = dict(sorted(node_fidelity_dic.items(), key=lambda item: item[1], reverse=True))
        qubit = list(sorted_dict.keys())[0]
        return qubit, sorted_dict[qubit]

    def select_layout_from_backend(self,
                      key: Literal['fidelity_mean', 'fidelity_var'] = 'fidelity_var',
                      topology: Literal['linear', 'nonlinear'] = 'linear',
                      printdetails: bool = False):
        """
        Select a qubit layout based on the given performance metric and topology.
    
        This function chooses a layout for the quantum circuit from the available subgraphs based on 
        the specified key (performance metric) and topology type.
    
        Args:
            key (Literal['fidelity_mean', 'fidelity_var'], optional): The performance metric to use for 
                selecting the layout. Either the mean fidelity ('fidelity_mean') or fidelity variance 
                ('fidelity_var'). Defaults to 'fidelity_var'.
            topology (Literal['cycle', 'linear1', 'linear', 'nonlinear'], optional): The desired topology 
                of the layout. It can be 'cycle', 'linear1' (connected, in the same row), 'linear' (connected, 
                not necessarily in the same row), or 'nonlinear'. Defaults to 'linear1'.
            printdetails (bool, optional): If True, prints details about the selected layout. Defaults to False.
    
        Returns:
            list: A list of qubits representing the selected layout.
        """
        if key == 'fidelity_mean':
            linear_list,nonlinear_list = self.sort_subgraph_according_mean_fidelity(printdetails=printdetails)
        elif key == 'fidelity_var':
            linear_list,nonlinear_list = self.sort_subgraph_according_var_fidelity(printdetails=printdetails)
        
        if topology == 'linear':
            if len(linear_list) == 0:
                print(f'There is no {self.nqubits} qubits that meets both key = {key} and topology = {topology}. Please change the conditions.')
                return [] #exit(1)
            else:
                return linear_list[0][0]
        elif topology == 'nonlinear':
            if len(nonlinear_list) == 0:
                print(f'There is no {self.nqubits} qubits that meets both key = {key} and topology = {topology}. Please change the conditions.')
                return [] #exit(1)
            else:
                return nonlinear_list[0][0]
    
    def select_layout(self,
                      target_qubits:list = [], 
                      use_chip_priority: bool = True, 
                      select_criteria: dict = {'key':'fidelity_var','topology':'linear'},
                        ):
        
        if target_qubits != []:
            if len(target_qubits) != self.nqubits:
                raise(ValueError(f'The number of qubits {len(target_qubits)} in target_qubits does not match the number of qubits {self.nqubits} in the circuit.'))
            # check qubits existance and fidelity 
            subgraph = self.graph.subgraph(target_qubits).copy()
            subgraph.graph["normal_order"] = target_qubits
            for node in target_qubits:
                if subgraph.has_node(node):
                    fidelity = nx.get_node_attributes(subgraph,'fidelity')[node]
                    if fidelity == 0.:
                        raise(ValueError(f'The physical qubit {node} in target_qubits has a single-qubit gate fidelity of {fidelity}.')) 
                else:
                    raise(ValueError(f'The physical qubit {node} in target_qubits does not exit'))
            # check edge fidelity
            is_connected = nx.is_connected(subgraph)
            if is_connected is False:
                raise(ValueError(f'The physical qubit layout {target_qubits} constructed from target_qubits is not connected.'))  
            for _, fidelity in nx.get_edge_attributes(subgraph,'fidelity').items(): # it will be []
                if fidelity == 0.:
                    is_connected = False
                if is_connected is False:
                    raise(ValueError(f'The physical qubit layout {target_qubits} constructed from target_qubits is not connected.'))  
            coupling_map = list(subgraph.edges)
            print(f'Physical qubits layout {target_qubits} are user-defined, with the corresponding coupling being {coupling_map}.')       

            if len(subgraph.edges())>0:     
                subgraph_fidelity = np.array([self.edge_fidelitys[(min(edge),max(edge))] for edge in subgraph.edges])
                fidelity_mean = np.mean(subgraph_fidelity)
                fidelity_var  = np.var(subgraph_fidelity)  
                print(f'The average fidelity of the coupler(s) between the selected qubits is {fidelity_mean}, and the variance of the fidelity is {fidelity_var}.')
            return subgraph
        if use_chip_priority: # 如果列表中没有满足的比特则启动筛选，如果是单比特则保留原比特，不再筛选，todos:把筛选机制转成数据库
            priority_qubits_list = self.priority_qubits
            for qubits in priority_qubits_list:
                if len(qubits) == self.nqubits:
                    subgraph = self.graph.subgraph(qubits).copy()
                    subgraph.graph["normal_order"] = qubits
                    if nx.is_connected(subgraph):
                        coupling_map = list(subgraph.edges)
                        print(f'Physical qubits layout {list(qubits)} are derived from the chip backend priority qubits, with the corresponding coupling being {coupling_map}.')
                        if len(subgraph.edges())>0: 
                            subgraph_fidelity = np.array([self.edge_fidelitys[(min(edge),max(edge))] for edge in subgraph.edges])
                            fidelity_mean = np.mean(subgraph_fidelity)
                            fidelity_var  = np.var(subgraph_fidelity)  
                            print(f'The average fidelity of the coupler(s) between the selected qubits is {fidelity_mean}, and the variance of the fidelity is {fidelity_var}.')
                        return subgraph
            print(f'No priority qubits with {self.nqubits} qubits found. it will check the select_criteria for search')

        if self.nqubits == 1:
            qubit, fidelity = self.select_qubit_from_backend()
            #The selected qubit has the highest single-qubit gate fidelity.
            print(f'The selected physical qubit {qubit} is 	recommend, with single-qubit gate fidelity {fidelity}')
            subgraph = self.graph.subgraph([qubit]).copy()
            subgraph.graph["normal_order"] = [qubit]
            return subgraph
        elif 1 < self.nqubits <= self.algorithm_switch_threshold:
            key_first = select_criteria['key']
            topology_first = select_criteria['topology']
            all_keys = ['fidelity_var','fidelity_mean']
            all_topologys = ['linear','nonlinear']
            all_keys.remove(key_first)
            all_topologys.remove(topology_first)
            sorted_keys = [key_first,] + all_keys
            sorted_topologys = [topology_first,] + all_topologys
            physical_qubits_layout = []
            for key, topology in product(sorted_keys,sorted_topologys):
                physical_qubits_layout = self.select_layout_from_backend(key=key,topology=topology)
                if physical_qubits_layout != []:
                    break
            if physical_qubits_layout == []:
                raise(ValueError(f'Unable to find a suitable layout. If this message appears, please contact the developer for assistance.'))
            physical_qubits_layout = list(physical_qubits_layout)
            subgraph = self.graph.subgraph(physical_qubits_layout).copy()
            subgraph.graph["normal_order"] = physical_qubits_layout
            coupling_map = list(subgraph.edges)
            print(f'Physical qubits layout {physical_qubits_layout} are selected by the Transpile algorithm using key = {key} and topology = {topology}, \nwith the corresponding coupling being {coupling_map}.')
            subgraph_fidelity = np.array([self.edge_fidelitys[(min(edge),max(edge))] for edge in subgraph.edges])
            fidelity_mean = np.mean(subgraph_fidelity)
            fidelity_var  = np.var(subgraph_fidelity)  
            print(f'The average fidelity of the coupler(s) between the selected qubits is {fidelity_mean}, and the variance of the fidelity is {fidelity_var}.')              
            return subgraph
        elif self.nqubits > self.algorithm_switch_threshold:
            physical_qubits_layout = self.get_BFS_layout()
            subgraph = self.graph.subgraph(physical_qubits_layout).copy()
            subgraph.graph["normal_order"] = physical_qubits_layout
            coupling_map = list(subgraph.edges)
            print(f'Physical qubits layout {physical_qubits_layout} are selected by BFS algorithm with the corresponding coupling being {coupling_map}.')
            subgraph_fidelity = np.array([self.edge_fidelitys[(min(edge),max(edge))] for edge in subgraph.edges])
            fidelity_mean = np.mean(subgraph_fidelity)
            fidelity_var  = np.var(subgraph_fidelity)  
            print(f'The average fidelity of the coupler(s) between the selected qubits is {fidelity_mean}, and the variance of the fidelity is {fidelity_var}.')  
            return subgraph
        else:
            raise(ValueError('Wrong qubits error!'))

    # large qubit layour    
    def get_one_component(self,thres=0.90):
        def edge_filter(u,v):
            return self.graph[u][v].get("fidelity") >= thres
        subgraph_view = nx.subgraph_view(self.graph,filter_edge=edge_filter)
        filtered_graph =  nx.Graph(subgraph_view)

        components = list(nx.connected_components(filtered_graph))
        for comp in components:
            if len(comp)>=self.nqubits:
                return filtered_graph.subgraph(comp)
        raise(ValueError(f'The user circuit requires {self.nqubits} qubits exceeds the qubit capacity of the largest connected subgraph.'))
    
    def get_BFS_layout(self):
        """ Perform a breadth-first search (BFS) on the graph starting from the start node,
        collecting up to `nqubits` unique nodes including the start node.

        Returns:
            list: A list of up to `nqubits` unique nodes, discovered in BFS order.
        """
        # self.graph = chip_backend.graph #chip_backend.edge_filtered_graph(thres=0.95)

        one_subgraph = self.get_one_component()
        start_node = np.random.choice(list(one_subgraph.nodes))

        # if self.priority_qubits is None:
        #     start_node = np.random.choice(list(one_subgraph.nodes))
        # else:
        #     priority_qubits_list = list(set(i for sublist in self.priority_qubits for i in sublist))
        #     start_node = np.random.choice(priority_qubits_list)

        visited = set([start_node])
        queue = [(start_node, 0)]  
    
        while queue and len(visited) < self.nqubits:
            current_node, depth = queue.pop(0)  
            if depth >= self.nqubits - 1:
                continue
            for neighbor in one_subgraph.neighbors(current_node):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, depth + 1))
                    if len(visited) == self.nqubits:
                        break
        return list(visited)
